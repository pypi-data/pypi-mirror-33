import importlib

from pyjuhelpers.basicconfig import Config

import pkg_resources
config_file = pkg_resources.resource_filename(__name__,"config.yaml")





from anycsv.config import _config as _anycsvconfig
_config=_anycsvconfig

_config = Config(config_file=config_file)
_config.merge(init=_config)

pyyacpconfig = _config.pyyacp
anycsvconfig = _config.anycsv




#overwrite anycsvconfig
#import anycsv
#anycsv.config.anycsvconfig = _config.anycsv
