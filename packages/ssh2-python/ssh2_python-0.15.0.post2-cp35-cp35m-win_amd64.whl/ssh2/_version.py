
import json

version_json = '''
{"error": null, "version": "0.15.0.post2", "date": "2018-07-12T14:20:59.380188", "full-revisionid": "5b6d983a8c16c79338a1479eec0fc71d80be757e", "dirty": false}'''  # END VERSION_JSON


def get_versions():
    return json.loads(version_json)

