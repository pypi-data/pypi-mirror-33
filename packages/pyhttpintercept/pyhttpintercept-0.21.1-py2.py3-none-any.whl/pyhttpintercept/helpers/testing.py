# encoding: utf-8

import json
import requests
from logging_helper import setup_logging
from ..config.constants import ModifierConstant, ScenarioConstant, INTERCEPT_SCENARIO_CONFIG
from ..config.intercept_scenarios import (Modifier,
                                          register_scenario_config)
logging = setup_logging()

CFG_ROOT = u'{k}.{c}'.format(k=INTERCEPT_SCENARIO_CONFIG,
                             c=u'dummy')
MOD_ROOT = u'{k}.{m}'.format(k=CFG_ROOT,
                             m=ScenarioConstant.modifiers)


def run_ad_hoc_modifier(module,
                        request=None,
                        response=None,
                        filter='',
                        override='',
                        params=''):
    """
    Runs an intercept modifier standalone

    :param module: python module object
    :param request: Supply if the request needs to be made
    :param response: Supply if the request/response object is already known
    :param filter: string
    :param override: string
    :param params: json string or an object that can be json.dumps-ed
    :return:
    """
    if not response:
        response = requests.get(request)

    if not request:
        request = response.url

    if isinstance(params, (list, dict, int, float)):
        params = json.dumps(params)

    cfg = register_scenario_config()

    cfg[CFG_ROOT] = {
        ScenarioConstant.modifiers: [
            {
                ModifierConstant.handler: "",
                ModifierConstant.modifier: "",
                ModifierConstant.active: False,
                ModifierConstant.filter: "",
                ModifierConstant.override: "",
                ModifierConstant.params: ""
            }
        ],
        ScenarioConstant.description: u'FOR DEBUG: DO NOT USE / CHANGE'
    }

    modifier = Modifier(cfg_fn=register_scenario_config,
                        cfg_root=MOD_ROOT,
                        key=0)
    modifier.update({ModifierConstant.params: params,
                     ModifierConstant.filter: filter,
                     ModifierConstant.override: override})
    try:
        module.modify(request=request,
                      response=response,
                      modifier=modifier)
    except Exception as e:
        logging.exception(e)

    del cfg[CFG_ROOT]

    return response
