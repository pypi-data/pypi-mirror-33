
import json

version_json = '''
{"version": "0.15.0.post2", "date": "2018-07-12T14:12:20.250109", "dirty": false, "error": null, "full-revisionid": "5b6d983a8c16c79338a1479eec0fc71d80be757e"}'''  # END VERSION_JSON


def get_versions():
    return json.loads(version_json)

