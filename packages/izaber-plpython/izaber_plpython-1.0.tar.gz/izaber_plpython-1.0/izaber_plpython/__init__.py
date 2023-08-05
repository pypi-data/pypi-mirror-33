import os
import importlib

import izaber
from izaber import config, app_config, autoloader
from izaber.startup import request_initialize, initializer
from izaber.log import log
from izaber.plpython.base import IPLPY

autoloader.add_prefix('izaber.plpython')

__version__ = '1.0'

CONFIG_BASE = """
"""

def reload_base():
    importlib.reload(izaber.plpython.base)
    from izaber.plpython.base import IPLPY
    return IPLPY

def init_plpy(plpy_globals,reload=False):
    global IPLPY
    if reload or plpy_globals['GD'].get('always_reload'):
        IPLPY = reload_base()
    return IPLPY(plpy_globals)


@initializer('plpython')
def load_config(**kwargs):
    request_initialize('config',**kwargs)
    request_initialize('logging',**kwargs)
    config.config_amend_(CONFIG_BASE)


"""

CREATE OR REPLACE FUNCTION fn_always_reload(active boolean)
RETURNS TEXT AS
$$
    from izaber.plpython import init_plpy
    iplpy = init_plpy(globals())
    if active is None:
        iplpy.always_reload(True)
    else:
        iplpy.always_reload(active)

$$
LANGUAGE plpython3u;
SELECT fn_always_reload();

CREATE OR REPLACE FUNCTION fn_test_load()
RETURNS TEXT AS
$$
    from izaber.plpython import init_plpy
    iplpy = init_plpy(globals())
    p = iplpy.q("select id from product_product limit 1")[0]
    return str(p)
$$
LANGUAGE plpython3u;
SELECT fn_test_load();


CREATE OR REPLACE FUNCTION fn_test_load()
RETURNS TEXT AS
$$
    from izaber.plpython.zerp import init_plpy
    iplpy = init_plpy(globals())
    p = iplpy.q("select id from product_product limit 1")[0]
    return str(p)
$$
LANGUAGE plpython3u;
SELECT fn_test_load();

"""
