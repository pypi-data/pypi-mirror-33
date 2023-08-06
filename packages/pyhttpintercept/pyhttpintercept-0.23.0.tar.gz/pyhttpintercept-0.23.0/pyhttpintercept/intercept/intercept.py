# encoding: utf-8

import copy
import socket
import requests
from pprint import pformat
import logging_helper
from logging_helper import LogLines
from apiutil.endpoints import APIConfig
from networkutil.addressing import get_my_addresses
from ..server.response import Response
from ..config.constants import HandlerConstant, ModifierConstant, HandlerTypeConstant
from ..exceptions import NoHandlersFound, NoActiveModifiers, CircularReference
from ..methods.request_shared import RequestShared

logging = logging_helper.setup_logging()


class InterceptRequest(RequestShared):

    def __init__(self,
                 scenarios=None,
                 *args,
                 **kwargs):

        self._api_config = APIConfig()

        super(InterceptRequest, self).__init__(*args,
                                               **kwargs)

        self._scenarios = scenarios

        # make handlers & modifiers easier to access
        self._handlers = self._scenarios.handlers
        self._modifiers = self._scenarios.modifiers

        self.intercepted = False

        self.timeout = self._request.server.request_timeout
        logging.debug(u'request_timeout:{rt}'.format(rt=self.timeout))

    # Intercept
    def intercept_request(self):

        #  Make Modifications to URI
        #  TODO: part of this functionality should be moved to redirect request handler

        modified_uri = self.__modify(response=None,
                                     kind=HandlerTypeConstant.uri,
                                     separator=u'MODIFY URI')

        modified_uri = modified_uri if modified_uri is not None else self.request_uri

        if modified_uri != self.request_uri:
            self.request_uri = modified_uri
            logging.info(self.prefix_message(u'Modified URI: {uri}'.format(uri=self.request_uri)))

        self.modified_headers = self.__modify(response=None,
                                              kind=HandlerTypeConstant.request_headers,
                                              separator=u'RESPONSE HEADERS')

        # Check for and get canned response
        #  TODO: this functionality should be moved to hosting request handler!
        response = self.__modify(response=None,
                                 kind=HandlerTypeConstant.canned,
                                 separator=u'CHECK FOR CANNED RESPONSE')

        # Get a real response if there is no canned response configured
        if response is None:
            response = self.__make_actual_request()
            logging.info(u'Status code:{sc}'.format(sc=response.status_code))

        # Make Modifications to response
        modified_response = self.__modify(response=response,
                                          kind=HandlerTypeConstant.body,
                                          separator=u'MODIFY RESPONSE')

        response = modified_response if modified_response is not None else response

        # Make Modifications to headers
        # logging.info(self.prefix_message(u'Original Headers: {h}'.format(h=response.headers)))

        modified_headers = self.__modify(response=response,
                                         kind=HandlerTypeConstant.response_headers,
                                         separator=u'RESPONSE HEADERS')

        # Prepare response
        self.response = Response(request=self._request,
                                 uri=self.request_uri,
                                 response=response)
        self.response.prepare_headers(modified_headers=modified_headers if modified_headers is not None else {})

        return self.response, self.intercepted

    def __make_actual_request(self):

        logging.debug(self._get_debug_separator(u'MAKE REAL REQUEST'))

        # Ensure request is not circular!
        host = self.request_host.split(u':')[0]

        try:
            host_address = socket.gethostbyname(host)

        except socket.gaierror as err:
            raise LookupError(u'Could not resolve {host} to an address. '
                              u'The address may not be available on this interface. '
                              u'Socket error: {err}'.format(host=host,
                                                            err=err))

        if host_address not in get_my_addresses():
            # Get real response from server
            method = self.response._request.command

            # TODO: Are there some headers we will want to strip out?
            #       e.g. If-Modified-Since or If-None-Match,
            #       maybe Connection: Keep-Alive
            #       Note: can now strip out headers using headers.request.remove_headers

            headers = {k: v
                       for k, v in iter(self._request.headers.dict.items())}

            headers_with_case = {k.lower(): k
                                 for k in [h.split(u':')[0] for h in self._request.headers.headers]}

            # Modify host header as it could be used server side to
            # redirect to a different endpoint.
            headers[u'host'] = self.request_uri.split(u'/')[2]

            if self.modified_headers is not None:
                headers.update(self.modified_headers)  # Already lower-cased

            # Restore header case. This should not be necessary, but have seen some
            # servers reject messages with lower cased headers.
            headers = {headers_with_case.get(k, k): v
                       for k, v in iter(headers.items())
                       if v is not None}

            return requests.request(method=method,
                                    url=self.request_uri,
                                    timeout=self.timeout,
                                    headers=headers,
                                    **self.response._request.parameters)  # required for POST, PUT data.
        else:
            raise CircularReference(u'Error making request! Requested url resolves to this server!')

    def __modify(self,
                 response,
                 kind,
                 separator=u''):

        logging.debug(self._get_debug_separator(separator))

        modified = None
        request = self.request_uri
        headers = {}

        # Make Modifications to response
        try:
            # Get handlers for this request
            handlers = self.get_handlers_for_request(request=request,
                                                     kind=kind,
                                                     host=self.request_host)

            LogLines(level=logging_helper.DEBUG,
                     log_lines=handlers)

            # Process handlers for this request
            for handler in handlers:

                try:
                    modifiers = self.get_modifiers_for_handler(handler[HandlerConstant.name])

                    if kind in (HandlerTypeConstant.uri,
                                HandlerTypeConstant.canned):
                        request = handler[HandlerConstant.instance].handle_request(request=request,
                                                                                   response=response,
                                                                                   client=self.client_address,
                                                                                   modifiers=modifiers)

                    elif kind in (HandlerTypeConstant.request_headers,
                                  HandlerTypeConstant.response_headers):
                        headers = handler[HandlerConstant.instance].handle_request(request=request,
                                                                                   response=response,
                                                                                   client=self.client_address,
                                                                                   modifiers=modifiers)
                    else:
                        response = handler[HandlerConstant.instance].handle_request(request=request,
                                                                                    response=response,
                                                                                    client=self.client_address,
                                                                                    modifiers=modifiers)

                except NoActiveModifiers as err:
                    pass
                    # logging.debug(self.prefix_message(u'No modifiers found!: {err}'.format(err=err)))

            # Return the appropriate value
            if kind in (HandlerTypeConstant.uri, HandlerTypeConstant.canned):
                return request

            elif kind in (HandlerTypeConstant.request_headers,
                          HandlerTypeConstant.response_headers):
                return headers

        except NoHandlersFound as err:
            logging.debug(self.prefix_message(err))

        except Exception as err:
            logging.exception(self.prefix_message(err))

        return modified

    def get_handlers_for_request(self,
                                 request,
                                 host,
                                 kind=None):
        handlers = []

        # Get the handlers for this request
        if kind in [HandlerTypeConstant.uri,
                    HandlerTypeConstant.canned,
                    HandlerTypeConstant.request_headers,
                    HandlerTypeConstant.response_headers]:

            try:
                handlers = self.get_handlers_for_kind(kind)

            except NoActiveModifiers:
                pass
                # logging.debug(self.prefix_message(u'No active modifiers found for {kind} handler.'.format(kind=kind)))

            except NoHandlersFound as err:
                pass
                # logging.debug(self.prefix_message(err))

        else:
            try:
                handlers.extend(self.get_handlers_for_uri(uri=request))

            except NoActiveModifiers:
                pass
                # logging.debug(self.prefix_message(u'No active modifiers found for uri lookup handler.'))

            except NoHandlersFound as err:
                pass
                logging.debug(self.prefix_message(err))

        # logging.debug(self.prefix_message(u'Handlers: {handlers}'.format(handlers=handlers)))

        if len(handlers) == 0:
            raise NoHandlersFound(u'No handlers found for {uri} or {kind}!'.format(uri=request,
                                                                                   kind=kind))

        return handlers

    def get_handlers_for_uri(self,
                             uri=None):
        try:
            api_family, _api_name, _api_endpoint_name = self._api_config.apis.get_endpoint_for_request(uri)

        except LookupError as err:
            api_family = u'*'
            _api_name = u'Wildcard'
            _api_endpoint_name = u'Wildcard'

        log = LogLines(level=logging_helper.DEBUG,
                       log_lines=[u'get_handlers_for_uri',
                                  u'',
                                  u'{uri}'.format(uri=uri),
                                  u'',
                                  u'API Config:',
                                  u'    API Family: {api_family}'.format(api_family=api_family),
                                  u'    API Name: {_api_name}'.format(_api_name=_api_name),
                                  u'    API Endpoint name: {_api_endpoint_name}'.format(_api_endpoint_name=_api_endpoint_name),
                                  u''])

        try:
            handlers = []

            for handler in self._handlers.values():
                handler_matches = handler.get(HandlerConstant.api) in [api_family,
                                                                       u'*']

                log.append(u'Handler API ({handler_api}) {r} API Family ({api_family})'
                           .format(handler_api=handler.get(HandlerConstant.api),
                                   api_family=api_family,
                                   r={True: "==",
                                      False: "!="}[handler_matches]))

                log.extend([u'Handler:',
                            u'{handler}'.format(handler=pformat(handler, indent=4)),
                            u''])

                if handler_matches:
                    if handler[HandlerConstant.instance].can_you_handle(uri):
                        handlers.append(handler)

            return handlers

        except Exception as err:
            logging.exception(self.prefix_message(err))
            raise Exception(u'Unknown exception while getting handlers for {uri}'.format(uri=uri))

    # This appears to be deprecated!
    def get_handlers_for_host(self,
                              host):
        try:
            apis = [reference[u'api'] for reference in self._api_config.environments.get_host_references(host=host)]
            logging.debug(apis)

            handlers = []
            for handler in self._handlers.values():
                if handler.get(HandlerConstant.api) in apis:
                    handlers.append(handler)

            return handlers

        except Exception as err:
            logging.exception(self.prefix_message(err))
            raise Exception(u'Unknown exception while getting handlers for {host}'
                            .format(host=host))

    def get_handlers_for_kind(self,
                              kind):
        handlers = []

        # logging.debug(u'Looking for {kind} handler.'.format(kind=kind))

        try:
            if kind in [h.name for h in self._scenarios.scenario_handlers]:
                handlers.append(self._handlers[kind])

            return handlers

        except AttributeError as err:
            logging.exception(self.prefix_message(err))
            raise AttributeError(u'AttributeError while getting handlers for {kind}. '
                                 u'Check the pyhttpintercept_intercept_handlers.json '
                                 u'for the handler '.format(kind=kind))

        except Exception as err:
            logging.exception(self.prefix_message(err))
            raise Exception(u'Unknown exception while getting handlers for {kind}'.format(kind=kind))

    def get_modifiers_for_handler(self,
                                  handler_name):

        logging.debug(self._get_debug_separator(u'GET MODIFIERS {hn}'.format(hn=handler_name)))

        modifiers = []
        logging_helper.debug(self._scenarios.scenario_modifiers)
        for modifier in self._scenarios.scenario_modifiers:
            if modifier[ModifierConstant.handler] == handler_name:
                logging.debug(u'Copying {handler}.{mname}'
                              .format(handler=modifier.handler,
                                      mname=modifier))
                modifiers.append(copy.deepcopy(modifier))  # TODO: Why do we need deepcopy here??
        logging.debug(u'deep copying complete')

        # For each modifier retreive the loaded module and add it to the modifier
        # TODO: There is probably a better way to integrate the modifier config & loaded module config!
        for i, mod in enumerate(modifiers):
            mod_key = u'{h}.{m}'.format(h=mod.handler,
                                        m=mod.modifier)
            try:
                setattr(modifiers[i],
                        ModifierConstant.module,
                        self._modifiers[mod_key][ModifierConstant.module])
            except KeyError as e:
                logging.exception(e)
                logging.info(self._modifiers[mod_key])
                raise e

        # logging.debug(self.prefix_message(u'Modifiers: {m}'.format(m=modifiers)))

        if len(modifiers) == 0:
            raise NoActiveModifiers(u'No active modifiers found for {handler}!'.format(handler=handler_name))
        else:
            log_lines = logging_helper.LogLines(level=logging_helper.DEBUG,
                                                log_lines=self.prefix_message(u'Active modifiers:'))
            log_lines.append([m.raw_items for m in modifiers])

        return modifiers
