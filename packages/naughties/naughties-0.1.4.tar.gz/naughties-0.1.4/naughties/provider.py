from faker.providers import BaseProvider

import json
import random
import sys

NAUGHTY_LIST = []
with open("%s/blns.json" % sys.prefix) as naughties:
    NAUGHTY_LIST = json.load(naughties)

class NaughtyProvider(BaseProvider):

    def naughty_string(self):
        return random.choice(NAUGHTY_LIST)
