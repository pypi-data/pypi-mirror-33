
import json

version_json = '''
{"full-revisionid": "2f9d9d4111dc748d426789aa70ca0911e8ad04f6", "version": "0.15.0", "error": null, "dirty": false, "date": "2018-06-25T12:41:12.888046"}'''  # END VERSION_JSON


def get_versions():
    return json.loads(version_json)

