from faker.providers import BaseProvider

import json
import random

NAUGHTY_LIST = []
with open("blns.json") as naughties:
    NAUGHTY_LIST = json.load(naughties)

fake = Faker()

class NaughtyProvider(BaseProvider):

    def naughty_string(self):
        return random.choice(NAUGHTY_LIST)
