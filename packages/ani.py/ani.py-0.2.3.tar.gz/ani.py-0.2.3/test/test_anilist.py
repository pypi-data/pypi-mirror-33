from unittest import TestCase

from AniPy.Anilist import Anilist
from AniPy.Anilist.models import Media


class TestAnilist(TestCase):

    @classmethod
    def setUpClass(cls):
        cls.anilist = Anilist()

    def test_simple(self):
        anime = Media(self.anilist, 279)
        self.assertEqual(anime.idMal, 279)
        self.assertEqual(anime.isAdult, False)
        self.assertEqual(anime.isFavourite, False)
        self.assertEqual(anime.isLicensed, True)

    def test_prepare_shallow(self):
        anime = Media(self.anilist, 279)
        anime.prepare()
        self.assertNotEqual(anime.idMal, 279)
        self.assertNotEqual(anime.type, "ANIME")
        self.assertNotEqual(anime.format, "TV")
        self.assertNotEqual(anime.status, "FINISHED")
        self.assertNotEqual(anime.isLicensed, True)
        self.assertNotEqual(anime.description, """Tired of writing riddles for children, Yamaoka Momosuke plans on gathering spooky and gruesome stories and publishing them in an anthology called Hyakumonogatari ("One Hundred Tales"). While researching these old myths and legends he comes across a mysterious trio who call themselves the Ongyou. They are detectives who are investigating the legends to reveal their truths...and bring those in the wrong to justice. Each time Momosuke meets the Ongyou he must face horrible truths and battle with his morals, but he's seeing things he shouldn't be seeing... <br><br>\n(Source: ANN)""")
        self.assertNotEqual(anime.season, "FALL")
        self.assertNotEqual(anime.episodes, 13)
        self.assertNotEqual(anime.duration, 24)
        self.assertNotEqual(anime.chapters, None)
        self.assertNotEqual(anime.volumes, None)
        self.assertNotEqual(anime.countryOfOrigin, "JP")
        self.assertNotEqual(anime.isLicensed, True)
        self.assertNotEqual(anime.source, None)
        self.assertNotEqual(anime.hashtag, None)
        self.assertNotEqual(anime.bannerImage, None)
        self.assertNotEqual(anime.averageScore, 65)
        self.assertNotEqual(anime.meanScore, 68)
        self.assertNotEqual(anime.trending, 0)
        self.assertNotEqual(anime.favourites, 11)
        self.assertNotEqual(anime.isFavourite, False)
        self.assertNotEqual(anime.isAdult, False)
        self.assertNotEqual(anime.siteUrl, "https://anilist.co/anime/279")
        self.assertNotEqual(anime.autoCreateForumThread, False)

        anime.fetch()

        self.assertEqual(anime.idMal, 279)
        self.assertEqual(anime.type, "ANIME")
        self.assertEqual(anime.format, "TV")
        self.assertEqual(anime.status, "FINISHED")
        self.assertEqual(anime.isLicensed, True)
        self.assertEqual(anime.description, """Tired of writing riddles for children, Yamaoka Momosuke plans on gathering spooky and gruesome stories and publishing them in an anthology called Hyakumonogatari ("One Hundred Tales"). While researching these old myths and legends he comes across a mysterious trio who call themselves the Ongyou. They are detectives who are investigating the legends to reveal their truths...and bring those in the wrong to justice. Each time Momosuke meets the Ongyou he must face horrible truths and battle with his morals, but he's seeing things he shouldn't be seeing... <br><br>\n(Source: ANN)""")
        self.assertEqual(anime.season, "FALL")
        self.assertEqual(anime.episodes, 13)
        self.assertEqual(anime.duration, 24)
        self.assertEqual(anime.chapters, None)
        self.assertEqual(anime.volumes, None)
        self.assertEqual(anime.countryOfOrigin, "JP")
        self.assertEqual(anime.isLicensed, True)
        self.assertEqual(anime.source, None)
        self.assertEqual(anime.hashtag, None)
        self.assertEqual(anime.bannerImage, None)
        self.assertEqual(anime.averageScore, 65)
        self.assertEqual(anime.meanScore, 68)
        self.assertEqual(anime.trending, 0)
        self.assertEqual(anime.favourites, 11)
        self.assertEqual(anime.isFavourite, False)
        self.assertEqual(anime.isAdult, False)
        self.assertEqual(anime.siteUrl, "https://anilist.co/anime/279")
        self.assertEqual(anime.autoCreateForumThread, False)

    def test_prepare_deep(self):
        anime = Media(self.anilist, 345)
        anime.prepare()
        self.assertNotEqual(anime.title.english, "Emma: A Victorian Romance")

        anime.fetch()
        self.assertEqual(anime.title.english, "Emma: A Victorian Romance")

    def test_start_and_end_date(self):
        anime = Media(self.anilist, 632)
        anime.prepare()
        self.assertNotEqual(anime.startDate.year, 2001)
        self.assertNotEqual(anime.endDate.day, 14)

        anime.fetch()

        self.assertEqual(anime.startDate.year, 2001)
        self.assertEqual(anime.endDate.day, 14)

    def test_cover_image(self):
        anime = Media(self.anilist, 123)
        anime.prepare()
        self.assertNotEqual(anime.coverImage.large, "https://cdn.anilist.co/img/dir/anime/reg/123.jpg")
        self.assertNotEqual(anime.coverImage.medium, "https://cdn.anilist.co/img/dir/anime/med/123.jpg")

        anime.fetch()

        self.assertEqual(anime.coverImage.large, "https://cdn.anilist.co/img/dir/anime/reg/123.jpg")
        self.assertEqual(anime.coverImage.medium, "https://cdn.anilist.co/img/dir/anime/med/123.jpg")

    def test_tags(self):
        test_data = [
            ('Shounen', 'Target demographic is teenage and young adult males.', False),
            ('Post-Apocalyptic', 'Partly or completely set in a world or civilization after a global disaster.', False),
            ('Guns', 'Prominently features the use of guns in combat.', False),
            ('Survival', 'Centers around the struggle to live in spite of extreme obstacles.', False),
        ]

        anime = Media(self.anilist, 25)
        anime.prepare()
        self.assertNotEqual(anime.tags.name, "")
        self.assertNotEqual(anime.tags.description, "")
        self.assertNotEqual(anime.tags.isAdult, "")

        anime.fetch()

        for index, test_element in enumerate(test_data):
            self.assertEqual(anime.tags[index].name, test_element[0])
            self.assertEqual(anime.tags[index].description, test_element[1])
            self.assertEqual(anime.tags[index].isAdult, test_element[2])

    def test_external_links(self):
        test_data = [
            (1552, 'http://www.funimation.com/shows/desert-punk/videos/episodes', 'Funimation'),
            (1967, 'http://www.hulu.com/desert-punk', 'Hulu'),
            (6614, 'http://www.crunchyroll.com/desert-punk', 'Crunchyroll')

        ]
        anime = Media(self.anilist, 25)
        anime.prepare()

        self.assertNotEqual(anime.externalLinks.id, 1)
        self.assertNotEqual(anime.externalLinks.url, "")
        self.assertNotEqual(anime.externalLinks.site, "")

        anime.fetch()

        for index, test_element in enumerate(test_data):
            self.assertEqual(anime.externalLinks[index].id, test_element[0])
            self.assertEqual(anime.externalLinks[index].url, test_element[1])
            self.assertEqual(anime.externalLinks[index].site, test_element[2])

    def test_streaming_episodes(self):
        test_data = [
            ('Episode 1 - Asteroid Blues', 'https://img1.ak.crunchyroll.com/i/spire2-tmb/e3a45e86c597fe16f02d29efcadedcd81473268732_full.jpg', 'http://www.crunchyroll.com/cowboy-bebop/episode-1-asteroid-blues-719653', 'Crunchyroll'),
            ('Episode 2 - Stray Dog Strut', 'https://img1.ak.crunchyroll.com/i/spire3-tmb/0eea0ce5c2a92b72fd633e5cbabd17b81473277532_full.jpg', 'http://www.crunchyroll.com/cowboy-bebop/episode-2-stray-dog-strut-719655', 'Crunchyroll'),
            ('Episode 3 - Honky Tonk Women', 'https://img1.ak.crunchyroll.com/i/spire4-tmb/f007ab7cb899b5ca83b8e8d07a1067d51473125168_full.jpg', 'http://www.crunchyroll.com/cowboy-bebop/episode-3-honky-tonk-women-719475', 'Crunchyroll'),
            ('Episode 4 - Gateway Shuffle', 'https://img1.ak.crunchyroll.com/i/spire4-tmb/8395f1edb9b86ec69777bdd84a9bf7921473115214_full.jpg', 'http://www.crunchyroll.com/cowboy-bebop/episode-4-gateway-shuffle-719477', 'Crunchyroll'),
            ('Episode 5 - Ballad of Fallen Angels', 'https://img1.ak.crunchyroll.com/i/spire3-tmb/180d486bb9c563491f417eea1985c1de1473112114_full.jpg', 'http://www.crunchyroll.com/cowboy-bebop/episode-5-ballad-of-fallen-angels-719479', 'Crunchyroll'),
            ('Episode 6 - Sympathy for the Devil', 'https://img1.ak.crunchyroll.com/i/spire1-tmb/24668be96b09d1356709e04a3daa161f1473114965_full.jpg', 'http://www.crunchyroll.com/cowboy-bebop/episode-6-sympathy-for-the-devil-719481', 'Crunchyroll'),
            ('Episode 7 - Heavy Metal Queen', 'https://img1.ak.crunchyroll.com/i/spire2-tmb/d2d71facab3a707cd6480df47c78c2fe1473112459_full.jpg', 'http://www.crunchyroll.com/cowboy-bebop/episode-7-heavy-metal-queen-719483', 'Crunchyroll'),
            ('Episode 8 - Waltz for Venus', 'https://img1.ak.crunchyroll.com/i/spire4-tmb/c82f024aa8e91377f1fd1f31a732ed211473138815_full.jpg', 'http://www.crunchyroll.com/cowboy-bebop/episode-8-waltz-for-venus-719485', 'Crunchyroll'),
            ('Episode 9 - Jamming with Edward', 'https://img1.ak.crunchyroll.com/i/spire2-tmb/48d53aa4330ef9268c31db12def817ae1473113990_full.jpg', 'http://www.crunchyroll.com/cowboy-bebop/episode-9-jamming-with-edward-719487', 'Crunchyroll'),
            ('Episode 10 - Ganymede Elegy', 'https://img1.ak.crunchyroll.com/i/spire2-tmb/0b1fe4247b00a2a96cd724c978f2e9301473126093_full.jpg', 'http://www.crunchyroll.com/cowboy-bebop/episode-10-ganymede-elegy-719489', 'Crunchyroll'),
            ('Episode 11 - Toys in the Attic', 'https://img1.ak.crunchyroll.com/i/spire1-tmb/77098545eaa70378a9ef1cdd995015641473117569_full.jpg', 'http://www.crunchyroll.com/cowboy-bebop/episode-11-toys-in-the-attic-719491', 'Crunchyroll'),
            ('Episode 12 - Jupiter Jazz (part 1)', 'https://img1.ak.crunchyroll.com/i/spire3-tmb/cd71c0f3bcf0cb5559d0939e583daf361473118196_full.jpg', 'http://www.crunchyroll.com/cowboy-bebop/episode-12-jupiter-jazz-part-1-719493', 'Crunchyroll'),
            ('Episode 13 - Jupiter Jazz (part 2)', 'https://img1.ak.crunchyroll.com/i/spire2-tmb/e289707b5fc232b037a3e7d0e2a7959c1473119423_full.jpg', 'http://www.crunchyroll.com/cowboy-bebop/episode-13-jupiter-jazz-part-2-719495', 'Crunchyroll'),
            ('Episode 14 - Bohemian Rhapsody', 'https://img1.ak.crunchyroll.com/i/spire3-tmb/44580eb7cc5740f63f3170265de80b561473120654_full.jpg', 'http://www.crunchyroll.com/cowboy-bebop/episode-14-bohemian-rhapsody-719499', 'Crunchyroll'),
            ('Episode 15 - My Funny Valentine', 'https://img1.ak.crunchyroll.com/i/spire1-tmb/efb53c03f2ec8c0470275bb3cd32c6aa1473119912_full.jpg', 'http://www.crunchyroll.com/cowboy-bebop/episode-15-my-funny-valentine-719503', 'Crunchyroll'),
            ('Episode 16 - Black Dog Serenade', 'https://img1.ak.crunchyroll.com/i/spire2-tmb/c4138c03816a57f8e28e112875767dff1473121102_full.jpg', 'http://www.crunchyroll.com/cowboy-bebop/episode-16-black-dog-serenade-719505', 'Crunchyroll'),
            ('Episode 17 - Mushroom Samba', 'https://img1.ak.crunchyroll.com/i/spire3-tmb/2140460e2f69b8a124f812b31b2f0e991473122552_full.jpg', 'http://www.crunchyroll.com/cowboy-bebop/episode-17-mushroom-samba-719517', 'Crunchyroll'),
            ('Episode 18 - Speak Like a Child', 'https://img1.ak.crunchyroll.com/i/spire2-tmb/22ab56e337990440b8b3dde252b64b321473122227_full.jpg', 'http://www.crunchyroll.com/cowboy-bebop/episode-18-speak-like-a-child-719519', 'Crunchyroll'),
            ('Episode 19 - Wild Horses', 'https://img1.ak.crunchyroll.com/i/spire1-tmb/3288ad0b33dcfc5e1af91497d280b4fe1473124229_full.jpg', 'http://www.crunchyroll.com/cowboy-bebop/episode-19-wild-horses-719521', 'Crunchyroll'),
            ('Episode 20 - Pierrot Le Fou', 'https://img1.ak.crunchyroll.com/i/spire3-tmb/785ef5c25a046832b3513089c6f3d9941473123758_full.jpg', 'http://www.crunchyroll.com/cowboy-bebop/episode-20-pierrot-le-fou-719523', 'Crunchyroll'),
            ('Episode 21 - Boogie Woogie Feng Shui', 'https://img1.ak.crunchyroll.com/i/spire2-tmb/13dbb524b4b6bbc4cd1d36719d789b2f1473126565_full.jpg', 'http://www.crunchyroll.com/cowboy-bebop/episode-21-boogie-woogie-feng-shui-719525', 'Crunchyroll'),
            ('Episode 22 - Cowboy Funk', 'https://img1.ak.crunchyroll.com/i/spire1-tmb/c71fbb3f7b06b6747208d3d966aaa1b91473125734_full.jpg', 'http://www.crunchyroll.com/cowboy-bebop/episode-22-cowboy-funk-719527', 'Crunchyroll'),
            ('Episode 23 - Brain Scratch', 'https://img1.ak.crunchyroll.com/i/spire3-tmb/0d7ddcae6489ee5aae1c2cccf09f73991473126176_full.jpg', 'http://www.crunchyroll.com/cowboy-bebop/episode-23-brain-scratch-719529', 'Crunchyroll'),
            ('Episode 24 - Hard Luck Woman', 'https://img1.ak.crunchyroll.com/i/spire4-tmb/9d2308b354746a3fb84152526b195e1c1473128052_full.jpg', 'http://www.crunchyroll.com/cowboy-bebop/episode-24-hard-luck-woman-719531', 'Crunchyroll'),
            ('Episode 25 - The Real Folk Blues (part 1)', 'https://img1.ak.crunchyroll.com/i/spire2-tmb/7e9bb2a05eb81b701cdf115710d659291473127483_full.jpg', 'http://www.crunchyroll.com/cowboy-bebop/episode-25-the-real-folk-blues-part-1-719533', 'Crunchyroll'),
            ('Episode 26 - The Real Folk Blues (part 2)', 'https://img1.ak.crunchyroll.com/i/spire1-tmb/191b230426f0b0e6568b4ca6edab47321473136587_full.jpg', 'http://www.crunchyroll.com/cowboy-bebop/episode-26-the-real-folk-blues-part-2-719537', 'Crunchyroll')
        ]

        anime = Media(self.anilist, 1)
        anime.prepare()

        self.assertNotEqual(anime.streamingEpisodes.title, "")
        self.assertNotEqual(anime.streamingEpisodes.thumbnail, "")
        self.assertNotEqual(anime.streamingEpisodes.url, "")
        self.assertNotEqual(anime.streamingEpisodes.site, "")

        anime.fetch()

        for index, test_element in enumerate(test_data):
            self.assertEqual(anime.streamingEpisodes[index].title, test_element[0])
            self.assertEqual(anime.streamingEpisodes[index].thumbnail, test_element[1])
            self.assertEqual(anime.streamingEpisodes[index].url, test_element[2])
            self.assertEqual(anime.streamingEpisodes[index].site, test_element[3])

    def test_rankings(self):
        test_data = [
            'RATED',
            'POPULAR',
            'RATED',
            'POPULAR',
        ]

        anime = Media(self.anilist, 63)
        anime.prepare()

        self.assertNotEqual(anime.rankings.rank, "")
        self.assertNotEqual(anime.rankings.type, "")

        anime.fetch()

        for index, test_element in enumerate(test_data):
            self.assertEqual(anime.rankings[index].type, test_element)

    def test_require_all(self):
        anime = Media(self.anilist, 1)
        anime.prepare()
        anime.title.require_all()

        anime.fetch()

        self.assertEqual(anime.title.romaji, "Cowboy Bebop")
        self.assertEqual(anime.title.english, "Cowboy Bebop")
        self.assertEqual(anime.title.native, "カウボーイビバップ")
        self.assertEqual(anime.title.userPreferred, "Cowboy Bebop")

        anime.prepare()
        anime.require_all()
        anime.fetch()

    def tests_stats(self):
        anime = Media(self.anilist, 254)
        anime.prepare()

        self.assertNotEqual(anime.stats.scoreDistribution.score, 0)
        self.assertNotEqual(anime.stats.scoreDistribution.amount, 0)
        self.assertNotEqual(anime.stats.statusDistribution.status, "")
        self.assertNotEqual(anime.stats.statusDistribution.amount, 0)

        anime.fetch()

        self.assertNotEqual(len(anime.stats.scoreDistribution), 0)
        for distribution in anime.stats.scoreDistribution:
            self.assertIsInstance(distribution.score, int)
            self.assertIsInstance(distribution.amount, int)

        self.assertNotEqual(len(anime.stats.statusDistribution), 0)
        for distribution in anime.stats.statusDistribution:
            self.assertIsInstance(distribution.status, str)
            self.assertIsInstance(distribution.amount, int)

    def test_studios(self):
        test_data = [
            (True, 14, 'Sunrise', 'https://anilist.co/studio/14', False),
            (False, 23, 'Bandai Visual', 'https://anilist.co/studio/23', False),
            (False, 233, 'Bandai Entertainment', 'https://anilist.co/studio/233', False)
        ]

        anime = Media(self.anilist, 1)
        anime.prepare()
        self.assertNotEqual(anime.studios.isMain, True)
        self.assertNotEqual(anime.studios.id, 1)
        self.assertNotEqual(anime.studios.name, "")
        self.assertNotEqual(anime.studios.siteUrl, "")
        self.assertNotEqual(anime.studios.isFavourite, False)

        anime.fetch()

        for index, test_element in enumerate(test_data):
            self.assertEqual(anime.studios[index].isMain, test_element[0])
            self.assertEqual(anime.studios[index].id, test_element[1])
            self.assertEqual(anime.studios[index].name, test_element[2])
            self.assertEqual(anime.studios[index].siteUrl, test_element[3])
            self.assertEqual(anime.studios[index].isFavourite, test_element[4])

    def test_relations(self):
        test_data = [
            (30173, 'Cowboy Bebop'), (30174, 'Cowboy Bebop Shooting Star'),
            (5, "Cowboy Bebop: Knockin' on Heaven's Door"), (17205, "Ein's Summer Vacation"),
            (4037, 'Cowboy Bebop Session XX')
        ]

        anime = Media(self.anilist, 1)
        anime.prepare()
        self.assertNotEqual(anime.relations.node.title.english, "")

        anime.fetch()

        for index, test_element in enumerate(test_data):
            self.assertEqual(anime.relations[index].id, test_element[0])
            self.assertEqual(anime.relations[index].title.english, test_element[1])

    def test_search_anime(self):
        test_data = [
            (5114, 'Fullmetal Alchemist: Brotherhood'),
            (6421, 'Fullmetal Alchemist: Brotherhood OVA Collection'),
            (7902, 'Fullmetal Alchemist: Brotherhood: 4-Koma Theater'),
            (121, 'Fullmetal Alchemist'),
            (430, 'Fullmetal Alchemist: The Movie - Conqueror of Shamballa'),
            (664, 'Fullmetal Alchemist: Reflections'),
            (908, 'Fullmetal Alchemist: Premium OVA Collection'),
            (9135, 'Fullmetal Alchemist: The Sacred Star of Milos'),
            (10842, 'Fullmetal Alchemist: Milos no Seinaru Hoshi Specials')
        ]
        alchemist = self.anilist.search.anime("Fullmetal Alchemist")

        for index, test_element in enumerate(test_data):
            self.assertEqual(alchemist[index].id, test_element[0])
            self.assertEqual(alchemist[index].title.english, test_element[1])

    def test_character(self):
        test_data = [
            ('スパイク・スピーゲル', 'https://cdn.anilist.co/img/dir/character/reg/1.jpg', 'https://anilist.co/character/1'),
            ('フェイ・バレンタイン', 'https://cdn.anilist.co/img/dir/character/reg/2.jpg', 'https://anilist.co/character/2'),
            ('ジェット・ブラック', 'https://cdn.anilist.co/img/dir/character/reg/3-qWQuUys71EP6.jpg', 'https://anilist.co/character/3'),
            ('アイン', 'https://cdn.anilist.co/img/dir/character/reg/4.jpg', 'https://anilist.co/character/4'),
            ('エドワード・ウォン・ハウ・ペペル・チブルスキー4世', 'https://cdn.anilist.co/img/dir/character/reg/16.jpg', 'https://anilist.co/character/16'),
            ('ビシャス', 'https://cdn.anilist.co/img/dir/character/reg/2734.jpg', 'https://anilist.co/character/2734'),
            ('ジュリア', 'https://cdn.anilist.co/img/dir/character/reg/2735.jpg', 'https://anilist.co/character/2735'),
            ('グレン', 'https://cdn.anilist.co/img/dir/character/reg/2736.jpg', 'https://anilist.co/character/2736'),
            ('パンチ', 'https://cdn.anilist.co/img/dir/character/reg/6693.jpg', 'https://anilist.co/character/6693'),
            ('ジュディ', 'https://cdn.anilist.co/img/dir/character/reg/6694.jpg', 'https://anilist.co/character/6694'),
            ('アップルデリー・シニズ・ヘサップ・リュトフェン', 'https://cdn.anilist.co/img/dir/character/reg/13249.jpg', 'https://anilist.co/character/13249'),
            ('コフィ', 'https://cdn.anilist.co/img/dir/character/reg/15713.jpg', 'https://anilist.co/character/15713'),
            ('ロンデス', 'https://cdn.anilist.co/img/dir/character/reg/18441.jpg', 'https://anilist.co/character/18441'),
            (None, 'https://cdn.anilist.co/img/dir/character/reg/19117.jpg', 'https://anilist.co/character/19117'),
            ('ブル', 'https://cdn.anilist.co/img/dir/character/reg/19118.jpg', 'https://anilist.co/character/19118'),
            ('ウェン', 'https://cdn.anilist.co/img/dir/character/reg/19119.jpg', 'https://anilist.co/character/19119'),
            ('ウダイ', 'https://cdn.anilist.co/img/dir/character/reg/23611.jpg', 'https://anilist.co/character/23611'),
            ('ロコ', 'https://cdn.anilist.co/img/dir/character/reg/23686.jpg', 'https://anilist.co/character/23686'),
            ('リンド', 'https://cdn.anilist.co/img/dir/character/reg/23687.jpg', 'https://anilist.co/character/23687'),
            ('アンディ・フォン・デ・オニアテ', 'https://cdn.anilist.co/img/dir/character/reg/23740.jpg', 'https://anilist.co/character/23740'),
            ('東風', 'https://cdn.anilist.co/img/dir/character/reg/29313.jpg', 'https://anilist.co/character/29313'),
            ('ハキム', 'https://cdn.anilist.co/img/dir/character/reg/29559.jpg', 'https://anilist.co/character/29559'),
            ('カテリーナ', 'https://cdn.anilist.co/img/dir/character/reg/30572.jpg', 'https://anilist.co/character/30572'),
            ('シン', 'https://cdn.anilist.co/img/dir/character/reg/35870.jpg', 'https://anilist.co/character/35870'),
            ('メイファ', 'https://cdn.anilist.co/img/dir/character/reg/36364.jpg', 'https://anilist.co/character/36364')
        ]
        anime = Media(self.anilist, 1)
        anime.prepare()
        self.assertNotEqual(anime.characters.name.native, "")
        self.assertNotEqual(anime.characters.image.large, "")
        self.assertNotEqual(anime.characters.siteUrl, "")

        anime.fetch()

        for index, test_element in enumerate(test_data):
            self.assertEqual(anime.characters[index].name.native, test_element[0])
            self.assertEqual(anime.characters[index].image.large, test_element[1])
            self.assertEqual(anime.characters[index].siteUrl, test_element[2])

    def test_staff(self):
        test_data = [
            ('ADR Director', 'Mary Elizabeth', 'ENGLISH'),
            ('Theme Song Arrangement', 'Yoko', 'JAPANESE'),
            ('Music', 'Yoko', 'JAPANESE'),
            ('Theme Song Composition', 'Yoko', 'JAPANESE'),
            ('Script', 'Shinichiro', 'JAPANESE'),
            ('Director', 'Shinichiro', 'JAPANESE'),
            ('Storyboard  (Eps. 1, 2, 5, 9, 17, 25, 26)', 'Shinichiro', 'JAPANESE'),
            ('Script', 'Michiko', 'JAPANESE'),
            ('Original Creator', 'Hajime', 'JAPANESE'),
            ('Series Composition', 'Keiko', 'JAPANESE'),
            ('Script', 'Keiko', 'JAPANESE'),
            ('Script  (ep 18)', 'Shoji', 'JAPANESE'),
            ('Storyboard', 'Tensai', 'JAPANESE'),
            ('Storyboard  (ep 18)', 'Junichi', 'JAPANESE'),
            ('Script', 'Yamaguchi', 'JAPANESE'),
            ('Script', 'Dai', 'JAPANESE'),
            ('Music  (Guitar)', 'Tsuneo', 'JAPANESE'),
            ('Storyboard  (ep 16)', 'Shigeyasu', 'JAPANESE'),
            ('Producer', 'Masahiko', 'JAPANESE'),
            ('Inserted Song Performance  (episode 7)', 'Masaaki', 'JAPANESE'),
            ('Key Animation  (eps 1, 5, 9, 12, 15, 18-20, 22, 24-26)', 'Yutaka', 'JAPANESE'),
            ('Production Coordination', 'Kenji', 'JAPANESE'),
            ('Theme Song Performance  (ep 24)', 'Steve', 'JAPANESE'),
            ('Character Design', 'Toshihiro', 'JAPANESE'),
            ('Chief Animation Director  (ep 25)', 'Toshihiro', 'JAPANESE')
        ]

        anime = Media(self.anilist, 1)
        anime.prepare()
        self.assertNotEqual(anime.staff.role, "")
        self.assertNotEqual(anime.staff.name.first, "")
        self.assertNotEqual(anime.staff.language, "")

        anime.fetch()

        for index, test_element in enumerate(test_data):
            self.assertEqual(anime.staff[index].role, test_element[0])
            self.assertEqual(anime.staff[index].name.first, test_element[1])
            self.assertEqual(anime.staff[index].language, test_element[2])