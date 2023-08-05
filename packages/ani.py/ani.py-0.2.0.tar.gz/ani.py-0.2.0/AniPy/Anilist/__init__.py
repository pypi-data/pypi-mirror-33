from AniPy.Anilist.get import Get
from AniPy.Anilist.search import Search

import requests
import time

class Anilist:

    def __init__(self, cid=None, csecret=None, credentials=None):
        self.settings = {
            "header": {
                "Content-Type": "application/json",
                "User-Agent": "ani.py (git.widmer.me/project/multimedia/ani.py)",
                "Accept": "application/json"
            },
            'authurl': 'https://anilist.co/api',
            'apiurl': 'https://graphql.anilist.co',
            'cid': cid,
            'csecret': csecret,
            'token': credentials
        }
        self.session = requests.session()

        self.search = Search(self.settings, self)
        self.get = Get(self.settings, self)

        self.remaining = 90
        self.limit = 90
        self.reset = time.time()

    def request(self, *args, **kwargs):
        if self.remaining >= 2 and self.reset > time.time():
            sleep_time = 0.67 - ((1.0 / self.limit * self.remaining) * 0.67)
            sleep_time = min(sleep_time, self.reset - time.time())
        else:
            sleep_time = self.reset - time.time() + 0.01
        time.sleep(max(sleep_time, 0))

        r = self.session.post(*args, **kwargs)

        self.limit = int(r.headers.get("x-ratelimit-limit"))
        self.remaining = int(r.headers.get("x-ratelimit-remaining"))
        self.reset = int(r.headers.get("X-RateLimit-Reset"))

        print(self.remaining, "/", self.limit, ",", self.reset, time.time())

        if r.status_code == 429:
            return self.request(retry_once=False, *args, **kwargs)

        return r
