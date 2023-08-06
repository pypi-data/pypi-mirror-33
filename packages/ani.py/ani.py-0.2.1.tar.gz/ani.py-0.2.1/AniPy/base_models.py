import copy
import sys


class ResourceContainer:
    def __init__(self, anilist, *args, **kwargs):
        self._anilist = anilist

    def require_all(self, recursive=False):
        for key in self.fields():
            if not isinstance(getattr(self, key), RequireFetch):
                continue

            if is_model(getattr(self, key).type.__name__):
                if recursive:
                    getattr(self, key[1:]).require_all(recursive)

                continue

            getattr(self, key[1:])

    def _load(self, element):
        return False

    def fields(self):
        return retrieve_required_fields(self)

    def fill(self, jsd, jsd_key):
        if isinstance(jsd, dict):
            for key in jsd:
                if isinstance(getattr(self, "_" + key), RequireFetch):
                    filled = getattr(self, "_" + key).fill(jsd[key], key, parent=self)
                    if filled is not None:
                        setattr(self, "_" + key, filled)
                elif is_model(getattr(self, "_" + key)):
                    getattr(self, "_" + key).fill(jsd[key], key, parent=self)
                else:
                    setattr(self, "_" + key, jsd[key])
        if isinstance(jsd, list):
            results = []
            for element in jsd:
                instance = copy.deepcopy(self)
                instance.fill(element, jsd_key)
                results.append(instance)
            return results

    def query(self):
        fields = self.fields()
        result = "{\n"
        for field in fields.values():
            if field.field is not None:
                result += field.field + "\n"
                if is_model(field.type.__name__):
                    result += field.instance.query()
        result += "}\n"
        return result


class Resource(ResourceContainer):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

    def fetch(self):
        raise NotImplementedError()

    def _load(self, element):
        return True


class RequireFetch:
    def __init__(self, type=None, field=None):
        self.type = type
        self.field = field
        self.instance = None
        if field is not None:
            self.instance = type()

    def fill(self, jsd, jsd_key, parent=None):
        if is_model(self.type.__name__):
            if self.instance is None:
                if is_model(self.type.__name__):
                    self.instance = self.type(parent._anilist)
                else:
                    self.instance = self.type()
            if not isinstance(jsd, list):
                result = self.instance.fill(jsd, jsd_key)
            else:
                result = []
                instance = self.instance
                for jsd_element in jsd:
                    element = copy.deepcopy(instance)
                    element.fill(jsd_element, jsd_key)
                    result.append(element)

                return result

            if result is not None:
                self.instance = result
            setattr(parent, "_" + (self.field if self.field is not None else jsd_key), self.instance)
        else:
            setattr(parent, "_" + (self.field if self.field is not None else jsd_key), jsd)


def is_model(type):
    if type is None:
        return False

    type = type[0].upper() + type[1:]
    return getattr(sys.modules["AniPy.Anilist.models"], type, False)


def retrieve_required_fields(model):
    fields = [a for a in model.__dir__() if a.startswith("_") and not a.startswith("__")]

    result = {}

    for field in fields:
        field_data = getattr(model, field)
        if isinstance(field_data, RequireFetch):
            result[field] = field_data

    return result
