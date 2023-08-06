# encoding: utf-8

import os
import sys
import copy
import importlib
import logging_helper
from collections import MutableMapping
from fdutil.list_tools import filter_list
from fdutil.path_tools import ensure_path_exists
from ..config.intercept import InterceptConfig
from ..config.constants import UpdaterPathConstant, UpdaterConstant


logging = logging_helper.setup_logging()


class InterceptUpdaters(MutableMapping):

    def __init__(self):

        cfg = InterceptConfig()

        # Ensure plugin path exists
        ensure_path_exists(os.path.join(cfg.plugins_path, u'updaters'))

        self._updater_paths = [
            {
                UpdaterPathConstant.search_path: os.path.join(cfg.plugins_path, u'updaters'),
                UpdaterPathConstant.module_root: u'intercept_plugins.updaters'
            },  # Plugin path
        ]

        # Add additional configured modifier paths
        for pth in cfg.updater_paths:
            _module = importlib.import_module(pth)

            pth_cfg = {
                UpdaterPathConstant.search_path: os.path.dirname(_module.__file__),
                UpdaterPathConstant.module_root: pth
            }

            self._updater_paths.append(pth_cfg)

        self.registered_updaters = {}
        self.loaded_updaters = []

        # Discover modifiers
        self.discover_all_updaters()

        pass

    def load_all_updaters(self):

        for updater in self.registered_updaters:
            self.load_updater(updater)

    def discover_all_updaters(self):

        for path in self._updater_paths:

            search_path = path.get(UpdaterPathConstant.search_path)
            import_sys_path = path.get(UpdaterPathConstant.search_path).split(os.sep)
            module_root = path.get(UpdaterPathConstant.module_root)

            # Work out the path that should be added to sys.path
            for d in module_root.split(u'.')[::-1]:
                if import_sys_path[-1] == d:
                    import_sys_path.pop()

            import_sys_path = os.sep.join(import_sys_path)

            # Add updaters path to sys path so we can import from the configured directory
            # Note: modules at top of updater paths list cannot be overridden by updater paths
            # further down the list.  Therefore you CANNOT override built-in updaters!
            if import_sys_path not in sys.path:
                sys.path.append(import_sys_path)

            # Load modifiers from all configured updater paths
            self.__discover_updaters(search_path,
                                     updater_root=module_root)

        # Check whether we found any modifiers
        if len(self.registered_updaters) == 0:
            logging.info(u'No updaters found')

    def __discover_updaters(self,
                            dir_path,
                            updater_root=u'',
                            folder=u''):

        # Check updater path is a directory
        if os.path.isdir(dir_path):
            # Get contents of folder
            module_dir_list = os.listdir(dir_path)

            # Filter the list to drop init & python compiled files
            module_dir_list = filter_list(module_dir_list,
                                          [u'__init__', u'.pyc'],
                                          exclude=True)

            # Filter the list to get only directories
            filtered_module_dir_list = filter_list(copy.deepcopy(module_dir_list),
                                                   [u'.py'],
                                                   exclude=True)

            # Filter the list to get loose updaters
            filtered_module_file_list = filter_list(copy.deepcopy(module_dir_list),
                                                    [u'.py'])

            # Register updaters in this dir
            for updater in filtered_module_file_list:
                self.register_updater(updater_root=updater_root,
                                      updater_path=os.path.join(dir_path, updater),
                                      folder=folder)

            # Register updaters in sub-dirs
            for path in filtered_module_dir_list:
                new_dir = path.split(os.sep).pop()
                key = new_dir if not folder else u'{key}.{dir}'.format(key=key,
                                                                       dir=new_dir)
                self.__discover_updaters(dir_path=os.path.join(dir_path, path),
                                         updater_root=updater_root,
                                         folder=key)
        else:
            logging.error(u'Updater path {pth} is not a directory!'.format(pth=dir_path))

    def register_updater(self,
                         updater_root,
                         updater_path,
                         folder):

        updater_name = updater_path.split(os.sep).pop().replace(u'.py', u'')

        module_key = (u'{folder}.{module}'.format(folder=folder,
                                                  module=updater_name))
        # Check whether this updater has already been registered.
        if module_key not in self.registered_updaters:
            # Not registered yet so register the updater.
            self.registered_updaters[module_key] = {
                UpdaterConstant.updater_name: updater_name,
                UpdaterConstant.updater_path: updater_path,
                UpdaterConstant.module_path: (u'{root}.{module_key}'.format(root=updater_root,
                                                                            module_key=module_key))
                }

        else:
            # Updater already registered, check whether this is the same or a different
            # updater as the one already registered.
            u = self.registered_updaters[updater_name]

            if updater_path == u[UpdaterConstant.updater_path]:
                logging.debug(u'Updater {n} is already registered!'.format(n=updater_name))

            else:
                logging.warning(u'Not loading updater "{m}" from "{pth}" as another updater with '
                                u'this name has already been registered!'.format(m=updater_name,
                                                                                 pth=updater_path))

    def load_updater(self,
                     updater):

        # if isinstance(updater, Updater):
        #     updater = u'{h}.{m}'.format(h=updater[UpdaterConstant.handler],
        #                                 m=updater[UpdaterConstant.modifier])

        try:
            upd = self.registered_updaters[updater]

        except KeyError:
            logging.warning(u'Cannot load Updater {m}. Updater not registered!'.format(m=updater))

        else:

            logging.debug(u'Loading Updater "{upd}".  '
                          u'Updater path: {pth}'.format(upd=upd[UpdaterConstant.updater_name],
                                                        pth=upd[UpdaterConstant.updater_path]))

            # Check whether this updater has already been loaded, then either load/reload it.
            if updater not in self.loaded_updaters:
                self.__import_updater_module(updater_key=updater,
                                             updater_path=upd[UpdaterConstant.module_path])

            else:
                logging.debug(u'Updater "{n}" is already loaded, '
                              u'Reloading.'.format(n=upd[UpdaterConstant.updater_name]))

                reload(upd[UpdaterConstant.module])
                self.__validate_updater(updater_key=updater,
                                        updater_module=upd[UpdaterConstant.module],
                                        updater_module_path=upd[UpdaterConstant.module_path])

    def __import_updater_module(self,
                                updater_key,
                                updater_path):

        try:
            updater_module = importlib.import_module(updater_path)

        except ImportError as err:
            logging.exception(u'Could not load modifier "{m}". {err}'
                              .format(m=updater_path,
                                      err=err))
        else:
            # Updater module imported to lets instantiate the updater
            self.__validate_updater(updater_key=updater_key,
                                    updater_module=updater_module,
                                    updater_module_path=updater_path)

    def __validate_updater(self,
                           updater_key,
                           updater_module,
                           updater_module_path):

        try:
            # Ensure update function exists for update
            _ = updater_module.update

        except (AttributeError, NameError):
            logging.error(u'Updater {updater} not loaded as it does not contain a function '
                          u'called "update"'.format(updater=updater_module_path))
        else:
            self.registered_updaters[updater_key][UpdaterConstant.module] = updater_module

            if updater_key not in self.loaded_updaters:
                self.loaded_updaters.append(updater_key)

            logging.debug(u'Updater loaded: {upd} - {u}'.format(upd=updater_module_path,
                                                                u=self.registered_updaters[updater_key]))

    def run_updaters(self):
        self.load_all_updaters()
        updated_scenarios = []
        for updater in self.registered_updaters.values():
            try:
                func = updater[UpdaterConstant.module].update
            except (KeyError, AttributeError):
                pass  # Ignore non-update modules
            else:
                try:
                    updates = func()
                except Exception as e:
                    logging.exception(e)
                else:
                    if updates is None:
                        continue
                    elif isinstance(updates, list):
                        updated_scenarios.extend(updates)
                    else:
                        updated_scenarios.append(updates)
        return updated_scenarios

    def __getitem__(self, item):
        return self.registered_updaters[item]

    def __setitem__(self, item, value):
        self.registered_updaters[item] = value

    def __delitem__(self, item):
        del self.registered_updaters[item]

    def __iter__(self):
        return iter(self.registered_updaters)

    def __len__(self):
        return len(self.registered_updaters)
