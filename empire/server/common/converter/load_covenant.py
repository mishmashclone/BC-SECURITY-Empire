import yaml
from typing import Dict, List


def _convert_covenant_to_empire(covenant_dict: Dict, file_path: str):
    return {
        'name': covenant_dict['Name'],
        'authors': [covenant_dict['Author']['Handle']],
        'description': covenant_dict['Description'],
        'language': covenant_dict['Language'].lower(),
        'compatible_dot_net_versions': covenant_dict['CompatibleDotNetVersions'],
        'script': covenant_dict['Code'],
        'options': _convert_covenant_options_to_empire(covenant_dict['Options']),
        'compiler_yaml': yaml.dump([covenant_dict], sort_keys=False)
    }


def _convert_covenant_options_to_empire(options: List[Dict]):
    empire_options = [{'name': 'Agent',
                       'value': '',
                       'description': 'Agent to run module on.',
                       'required': True,
                       'suggested_values': []
                       }]
    for option in options:
        empire_options.append({
            'name': option['Name'],
            'value': option['Value'],
            'description': option['Description'],
            'required': not option['Optional'],
            'suggested_values': option['SuggestedValues']
        })

    return empire_options
