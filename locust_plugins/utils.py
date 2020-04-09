import json


def print_json_on_decode_fail():
    old_init = json.JSONDecodeError.__init__

    def new_init(self, *k, **kw):
        old_init(self, *k, **kw)
        print(f'json was: "{k[1]}"')

    json.JSONDecodeError.__init__ = new_init  # type: ignore
