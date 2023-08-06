import sys

from AniPy.base_models import RequireFetch


def auto_fetch(func):
    def wrapper(self, *args, **kwargs):
        result = func(self, *args, **kwargs)

        if not isinstance(result, RequireFetch):
            return result

        result.field = func.__name__
        if not self._load(result):

            if getattr(sys.modules["AniPy.Anilist.models"], result.type.__name__, False):
                if result.instance is None:
                    result.instance = result.type(self._anilist)

                    prepare = getattr(result.instance, "prepare", False)
                    if prepare:
                        prepare()

                return result.instance

            else:

                return result.type

        self.fetch()
        result = func(self, *args, **kwargs)
        if isinstance(result, RequireFetch):
            raise NotImplementedError("The fild " + str(func) + " is not included in fetch()")

        return result
    return property(wrapper)
