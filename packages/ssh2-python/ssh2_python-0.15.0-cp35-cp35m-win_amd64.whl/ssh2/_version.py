
import json

version_json = '''
{"error": null, "dirty": false, "version": "0.15.0", "full-revisionid": "2f9d9d4111dc748d426789aa70ca0911e8ad04f6", "date": "2018-06-25T12:53:48.676066"}'''  # END VERSION_JSON


def get_versions():
    return json.loads(version_json)

