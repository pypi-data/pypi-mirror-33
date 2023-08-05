
import json

version_json = '''
{"date": "2018-06-25T13:07:12.535895", "dirty": false, "error": null, "full-revisionid": "2f9d9d4111dc748d426789aa70ca0911e8ad04f6", "version": "0.15.0"}'''  # END VERSION_JSON


def get_versions():
    return json.loads(version_json)

