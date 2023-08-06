import copy

from AniPy.base_models import RequireFetch, Resource, ResourceContainer, is_model
from AniPy.helper import auto_fetch


class Image(ResourceContainer):
    _large = RequireFetch(str)
    _medium = RequireFetch(str)

    @auto_fetch
    def large(self):
        return self._large

    @auto_fetch
    def medium(self):
        return self._medium


class Name(ResourceContainer):
    _first = RequireFetch(str)
    _last = RequireFetch(str)
    _native = RequireFetch(str)
    _alternative = RequireFetch(str)

    @auto_fetch
    def first(self):
        return self._first

    @auto_fetch
    def last(self):
        return self._last

    @auto_fetch
    def native(self):
        return self._native

    @auto_fetch
    def alternative(self):
        return self._alternative


class Studio(ResourceContainer):
    _id = RequireFetch(int)
    _name = RequireFetch(str)
    _siteUrl = RequireFetch(str)
    _isFavourite = RequireFetch(str)
    _favourites = RequireFetch(int)
    _isMain = RequireFetch(bool)

    @auto_fetch
    def id(self):
        return self._id

    @auto_fetch
    def name(self):
        return self._name

    @auto_fetch
    def siteUrl(self):
        return self._siteUrl

    @auto_fetch
    def isFavourite(self):
        return self._isFavourite

    @auto_fetch
    def favourites(self):
        return self._favourites

    @auto_fetch
    def isMain(self):
        return self._isMain

    def fill(self, jsd, jsd_key):
        if "edges" in jsd:
            jsd = jsd["edges"]
            results = []
            for element in jsd:
                node = element.pop("node")
                element.update(node)
                instance = copy.deepcopy(self)
                instance.fill(element, jsd_key)
                results.append(instance)
            return results
        else:
            super().fill(jsd, jsd_key)

    def query(self):
        fields = self.fields()
        field_is_main = fields.pop("_isMain")

        result = "{\n"
        result += "edges {"
        if field_is_main.field is not None:
            result += field_is_main.field + "\n"
            if is_model(field_is_main.type.__name__):
                result += field_is_main.instance.query()

        result += "node {\n"

        for field in fields.values():
            if field.field is not None:
                result += field.field + "\n"
                if is_model(field.type.__name__):
                    result += field.instance.query()
        result += "}\n}\n}\n"
        return result


class ScoreDistribution(ResourceContainer):
    _score = RequireFetch(int)
    _amount = RequireFetch(int)

    @auto_fetch
    def score(self):
        return self._score

    @auto_fetch
    def amount(self):
        return self._amount


class StatusDistribution(ResourceContainer):
    _status = RequireFetch(str)
    _amount = RequireFetch(int)

    @auto_fetch
    def status(self):
        return self._status

    @auto_fetch
    def amount(self):
        return self._amount


class Stats(ResourceContainer):
    _scoreDistribution = RequireFetch(ScoreDistribution)
    _statusDistribution = RequireFetch(StatusDistribution)

    @auto_fetch
    def scoreDistribution(self):
        return self._scoreDistribution

    @auto_fetch
    def statusDistribution(self):
        return self._statusDistribution


class Ranking(ResourceContainer):
    _id = RequireFetch(int)
    _rank = RequireFetch(int)
    _type = RequireFetch(str)
    _format = RequireFetch(str)
    _year = RequireFetch(int)
    _season = RequireFetch(str)
    _allTime = RequireFetch(bool)
    _context = RequireFetch(str)

    @auto_fetch
    def id(self):
        return self._id

    @auto_fetch
    def rank(self):
        return self._rank

    @auto_fetch
    def type(self):
        return self._type

    @auto_fetch
    def format(self):
        return self._format

    @auto_fetch
    def year(self):
        return self._year

    @auto_fetch
    def season(self):
        return self._season

    @auto_fetch
    def allTime(self):
        return self._allTime

    @auto_fetch
    def context(self):
        return self._context


class StreamingEpisode(ResourceContainer):
    _title = RequireFetch(str)
    _thumbnail = RequireFetch(str)
    _url = RequireFetch(str)
    _site = RequireFetch(str)

    @auto_fetch
    def title(self):
        return self._title

    @auto_fetch
    def thumbnail(self):
        return self._thumbnail

    @auto_fetch
    def url(self):
        return self._url

    @auto_fetch
    def site(self):
        return self._site


class ExternalLink(ResourceContainer):
    _id = RequireFetch(int)
    _url = RequireFetch(str)
    _site = RequireFetch(str)

    @auto_fetch
    def id(self):
        return self._id

    @auto_fetch
    def url(self):
        return self._url

    @auto_fetch
    def site(self):
        return self._site


class Tag(ResourceContainer):
    _id = RequireFetch(int)
    _name = RequireFetch(str)
    _description = RequireFetch(str)
    _category = RequireFetch(str)
    _rank = RequireFetch(int)
    _isGeneralSpoiler = RequireFetch(bool)
    _isMediaSpoiler = RequireFetch(bool)
    _isAdult = RequireFetch(bool)

    @auto_fetch
    def id(self):
        return self._id

    @auto_fetch
    def name(self):
        return self._name

    @auto_fetch
    def description(self):
        return self._description

    @auto_fetch
    def category(self):
        return self._category

    @auto_fetch
    def rank(self):
        return self._rank

    @auto_fetch
    def isGeneralSpoiler(self):
        return self._isGeneralSpoiler

    @auto_fetch
    def isMediaSpoiler(self):
        return self._isMediaSpoiler

    @auto_fetch
    def isAdult(self):
        return self._isAdult


class StartDate(ResourceContainer):
    _year = RequireFetch(int)
    _month = RequireFetch(int)
    _day = RequireFetch(int)

    @auto_fetch
    def year(self):
        return self._year

    @auto_fetch
    def month(self):
        return self._month

    @auto_fetch
    def day(self):
        return self._day


EndDate = StartDate


class Title(ResourceContainer):
    _romaji = RequireFetch(str)
    _english = RequireFetch(str)
    _native = RequireFetch(str)
    _userPreferred = RequireFetch(str)

    @auto_fetch
    def romaji(self):
        return self._romaji

    @auto_fetch
    def english(self):
        return self._english

    @auto_fetch
    def native(self):
        return self._native

    @auto_fetch
    def userPreferred(self):
        return self._userPreferred


class Media(Resource):
    def __init__(self, anilist=None, id=None):
        Resource.__init__(self, anilist=anilist, id=id)

        self._prepare = False

        self._id = id
        if id is None:
            self._id = RequireFetch(int, field="id")

        self._idMal = RequireFetch(int)
        self._type = RequireFetch(str)
        self._format = RequireFetch(str)
        self._status = RequireFetch(str)
        self._isLicensed = RequireFetch(bool)
        self._description = RequireFetch(str)
        self._season = RequireFetch(str)
        self._episodes = RequireFetch(int)
        self._duration = RequireFetch(int)
        self._chapters = RequireFetch(int)
        self._volumes = RequireFetch(int)
        self._countryOfOrigin = RequireFetch(str)
        self._isLicensed = RequireFetch(int)
        self._source = RequireFetch(str)
        self._hashtag = RequireFetch(str)
        self._updatedAt = RequireFetch(int)
        self._bannerImage = RequireFetch(str)
        self._averageScore = RequireFetch(int)
        self._meanScore = RequireFetch(int)
        self._popularity = RequireFetch(int)
        self._trending = RequireFetch(int)
        self._favourites = RequireFetch(int)
        self._isFavourite = RequireFetch(bool)
        self._isAdult = RequireFetch(bool)
        self._siteUrl = RequireFetch(str)
        self._autoCreateForumThread = RequireFetch(bool)

        self._title = RequireFetch(Title)
        self._startDate = RequireFetch(StartDate)
        self._endDate = RequireFetch(EndDate)
        self._coverImage = RequireFetch(Image)

        self._tags = RequireFetch(Tag)
        self._externalLinks = RequireFetch(ExternalLink)
        self._streamingEpisodes = RequireFetch(StreamingEpisode)
        self._rankings = RequireFetch(Ranking)
        self._stats = RequireFetch(Stats)
        self._studios = RequireFetch(Studio)
        self._relations = RequireFetch(Relation)

        self._characters = RequireFetch(Character)
        self._staff = RequireFetch(Staff)

    def fetch(self):
        self._prepare = False
        self._anilist.get.fetch(self)

    def prepare(self):
        self._prepare = True

    def _load(self, element):
        return not self._prepare

    @auto_fetch
    def id(self):
        return self._id

    @auto_fetch
    def idMal(self):
        return self._idMal

    @auto_fetch
    def type(self):
        return self._type

    @auto_fetch
    def format(self):
        return self._format

    @auto_fetch
    def status(self):
        return self._status

    @auto_fetch
    def isLicensed(self):
        return self._isLicensed

    @auto_fetch
    def description(self):
        return self._description

    @auto_fetch
    def season(self):
        return self._season

    @auto_fetch
    def episodes(self):
        return self._episodes

    @auto_fetch
    def duration(self):
        return self._duration

    @auto_fetch
    def chapters(self):
        return self._chapters

    @auto_fetch
    def volumes(self):
        return self._volumes

    @auto_fetch
    def countryOfOrigin(self):
        return self._countryOfOrigin

    @auto_fetch
    def isLicensed(self):
        return self._isLicensed

    @auto_fetch
    def source(self):
        return self._source

    @auto_fetch
    def hashtag(self):
        return self._hashtag

    @auto_fetch
    def updatedAt(self):
        return self._updatedAt

    @auto_fetch
    def bannerImage(self):
        return self._bannerImage

    @auto_fetch
    def averageScore(self):
        return self._averageScore

    @auto_fetch
    def meanScore(self):
        return self._meanScore

    @auto_fetch
    def popularity(self):
        return self._popularity

    @auto_fetch
    def trending(self):
        return self._trending

    @auto_fetch
    def favourites(self):
        return self._favourites

    @auto_fetch
    def isFavourite(self):
        return self._isFavourite

    @auto_fetch
    def isAdult(self):
        return self._isAdult

    @auto_fetch
    def siteUrl(self):
        return self._siteUrl

    @auto_fetch
    def autoCreateForumThread(self):
        return self._autoCreateForumThread

    @auto_fetch
    def title(self):
        return self._title

    @auto_fetch
    def startDate(self):
        return self._startDate

    @auto_fetch
    def endDate(self):
        return self._endDate

    @auto_fetch
    def coverImage(self):
        return self._coverImage

    @auto_fetch
    def tags(self):
        return self._tags

    @auto_fetch
    def externalLinks(self):
        return self._externalLinks

    @auto_fetch
    def streamingEpisodes(self):
        return self._streamingEpisodes

    @auto_fetch
    def rankings(self):
        return self._rankings

    @auto_fetch
    def stats(self):
        return self._stats

    @auto_fetch
    def studios(self):
        return self._studios

    @auto_fetch
    def relations(self):
        return self._relations

    @auto_fetch
    def characters(self):
        return self._characters

    @auto_fetch
    def staff(self):
        return self._staff


class Relation(ResourceContainer):
    _relationType = RequireFetch(str)
    _node = RequireFetch(Media)

    @auto_fetch
    def relationType(self):
        return self._relationType

    @auto_fetch
    def node(self):
        return self._node

    def query(self):
        fields = self.fields()
        field_relation_type = fields.pop("_relationType")

        result = "{\n"
        result += "edges {"
        if field_relation_type.field is not None:
            result += field_relation_type.field + "\n"
            if is_model(field_relation_type.type.__name__):
                result += field_relation_type.instance.query()

        for field in fields.values():
            if field.field is not None:
                result += field.field + "\n"
                if is_model(field.type.__name__):
                    result += field.instance.query()
        result += "}\n}\n"
        return result

    def fill(self, jsd, jsd_key):
        if "edges" in jsd:
            jsd = jsd["edges"]
            results = []
            for element in jsd:
                node = element.pop("node")
                instance = copy.deepcopy(self.node)
                instance.fill(node, jsd_key)
                results.append(instance)
            return results
        else:
            super().fill(jsd, jsd_key)


class Character(ResourceContainer):
    _id = RequireFetch(int)
    _name = RequireFetch(Name)
    _image = RequireFetch(Image)
    _description = RequireFetch(str)
    _isFavourite = RequireFetch(bool)
    _favourites = RequireFetch(int)
    _siteUrl = RequireFetch(str)

    @auto_fetch
    def id(self):
        return self._id

    @auto_fetch
    def name(self):
        return self._name

    @auto_fetch
    def image(self):
        return self._image

    @auto_fetch
    def description(self):
        return self._description

    @auto_fetch
    def isFavourite(self):
        return self._isFavourite

    @auto_fetch
    def favourites(self):
        return self._favourites

    @auto_fetch
    def siteUrl(self):
        return self._siteUrl

    def fill(self, jsd, jsd_key):
        if "edges" in jsd:
            jsd = jsd["edges"]
            results = []
            for element in jsd:
                node = element.pop("node")

                # if "media" in node:
                #     node["media"] = node["media"]["nodes"]

                element.update(node)
                instance = copy.deepcopy(self)
                instance.fill(element, jsd_key)
                results.append(instance)
            return results
        else:
            self._name = copy.deepcopy(self._name)
            self._image = copy.deepcopy(self._image)
            super(Character, self).fill(jsd, jsd_key)

    def query(self):
        fields = self.fields()
        # field_media = fields.pop("_media")

        result = "{\n"
        result += "edges {"
        result += "node {\n"

        for field in fields.values():
            if field.field is not None:
                result += field.field + "\n"
                if is_model(field.type.__name__):
                    result += field.instance.query()

        # if field_media.field is not None:
        #     result += field_media.field + " {\nnodes"
        #     if is_model(field_media.type.__name__):
        #         result += field_media.instance.query()
        #
        #     result += "}\n"
        result += "}\n}\n}\n"

        return result


class Staff(ResourceContainer):
    _id = RequireFetch(int)
    _role = RequireFetch(str)
    _name = RequireFetch(Name)
    _language = RequireFetch(str)
    _image = RequireFetch(Image)
    _description = RequireFetch(str)
    _isFavourite = RequireFetch(bool)
    _favourites = RequireFetch(int)
    _siteUrl = RequireFetch(str)

    @auto_fetch
    def id(self):
        return self._id

    @auto_fetch
    def role(self):
        return self._role

    @auto_fetch
    def name(self):
        return self._name

    @auto_fetch
    def language(self):
        return self._language

    @auto_fetch
    def image(self):
        return self._image

    @auto_fetch
    def description(self):
        return self._description

    @auto_fetch
    def isFavourite(self):
        return self._isFavourite

    @auto_fetch
    def favourites(self):
        return self._favourites

    @auto_fetch
    def siteUrl(self):
        return self._siteUrl

    def fill(self, jsd, jsd_key):
        if "edges" in jsd:
            jsd = jsd["edges"]
            results = []
            for element in jsd:
                node = element.pop("node")

                if "role" in element:
                    node["role"] = element["role"]

                element.update(node)
                instance = copy.deepcopy(self)
                instance.fill(element, jsd_key)
                results.append(instance)
            return results
        else:
            self._name = copy.deepcopy(self._name)
            self._image = copy.deepcopy(self._image)
            super(Staff, self).fill(jsd, jsd_key)

    def query(self):
        fields = self.fields()
        # field_media = fields.pop("_media")

        result = "{\n"
        result += "edges {"

        role_field = fields.pop("_role")

        if role_field.field is not None:
            result += role_field.field + "\n"
            if is_model(role_field.type.__name__):
                result += role_field.instance.query()

        result += "node {\n"

        for field in fields.values():
            if field.field is not None:
                result += field.field + "\n"
                if is_model(field.type.__name__):
                    result += field.instance.query()
        result += "}\n}\n}\n"

        return result
