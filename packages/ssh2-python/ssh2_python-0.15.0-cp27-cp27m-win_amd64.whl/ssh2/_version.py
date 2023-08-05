
import json

version_json = '''
{"date": "2018-06-25T12:35:10.294000", "full-revisionid": "2f9d9d4111dc748d426789aa70ca0911e8ad04f6", "dirty": false, "version": "0.15.0", "error": null}'''  # END VERSION_JSON


def get_versions():
    return json.loads(version_json)

