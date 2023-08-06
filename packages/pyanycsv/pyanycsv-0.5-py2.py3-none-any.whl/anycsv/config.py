


from pyjuhelpers.basicconfig import Config

import pkg_resources
config_file = pkg_resources.resource_filename(__name__,"config.yaml")

_config = Config(config_file=config_file)
anycsvconfig = _config.anycsv