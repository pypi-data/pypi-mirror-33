
import json

version_json = '''
{"date": "2018-07-12T13:58:06.723000", "full-revisionid": "5b6d983a8c16c79338a1479eec0fc71d80be757e", "dirty": false, "version": "0.15.0.post2", "error": null}'''  # END VERSION_JSON


def get_versions():
    return json.loads(version_json)

