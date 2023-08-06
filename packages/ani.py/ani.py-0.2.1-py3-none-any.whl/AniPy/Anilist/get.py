import json
import time

from AniPy.errors import AniPyImplementationError


class Get:
    def __init__(self, settings, anilist):
        self.settings = settings
        self.anilist = anilist

    def fetch(self, element):
        request = element.query()

        request = """\
        query($id: Int) {
        """ + type(element).__name__ + """(id: $id, type: ANIME)
        """ + request + "}"

        vars = {"id": element.id}

        r = self.anilist.request(self.settings["apiurl"],
                                 headers=self.settings["header"],
                                 json={"query": request, "variables": vars})

        jsd = json.loads(r.text)

        if len(jsd.get("errors", [])) > 0:
            print(request)
            raise AniPyImplementationError(str(jsd["errors"][0]))

        return element.fill(jsd["data"][type(element).__name__], "")
