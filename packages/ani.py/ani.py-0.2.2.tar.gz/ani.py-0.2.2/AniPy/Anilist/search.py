import json

from AniPy.Anilist.models import Media


class Search:
    def __init__(self, settings, anilist):
        self.settings = settings
        self.anilist = anilist

    def anime(self, term, page=1, perpage=25):
        query_string = """\
        query ($query: String, $page: Int, $perpage: Int) {
            Page (page: $page, perPage: $perpage) {
                pageInfo {
                    total
                    currentPage
                    lastPage
                    hasNextPage
                }
                media (search: $query, type: ANIME) {
                    id
                    title {
                        romaji
                        english
                    }
                    coverImage {
                        large
                    }
                    averageScore
                    popularity
                    episodes
                    season
                    hashtag
                    isAdult
                }
            }
        }
        """
        vars = {"query": term, "page": page, "perpage": perpage}
        r = self.anilist.request(self.settings['apiurl'],
                                 headers=self.settings['header'],
                                 json={'query': query_string, 'variables': vars})
        jsd = r.text

        try:
            jsd = json.loads(jsd)
        except ValueError:
            return None
        else:
            media = jsd["data"]["Page"]["media"]
            result = []
            for element in media:
                media_element = Media(anilist=self.anilist)
                media_element.fill(element, "")
                result.append(media_element)
            return result
