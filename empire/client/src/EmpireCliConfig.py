from typing import Dict

import yaml


class EmpireCliConfig(object):
    def __init__(self):
        self.yaml: Dict = {}
        with open("./empire/client/config.yaml", 'r') as stream:
            try:
                self.yaml = yaml.safe_load(stream)
            except yaml.YAMLError as exc:
                print(exc)
                self.yaml = {}


empire_config = EmpireCliConfig()
