# Print json if there is a decode error.
import json

old_init = json.JSONDecodeError.__init__


def new_init(self, *k, **kw):
    old_init(self, *k, **kw)
    print(f'json was: "{k[1]}"')


json.JSONDecodeError.__init__ = new_init
