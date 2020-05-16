from django.utils.functional import cached_property

class cached_classproperty(cached_property):
    def __init__(self, *args, **kwargs):
        super(cached_classproperty, self).__init__(*args, **kwargs)
        self.cache = {}

    def clear(self):
        self.cache.clear()

    def __get__(self, instance, cls=None):
        if cls is None:
            cls = type(instance)

        cache = self.cache
        if cls in cache:
            return cache[cls]

        res = self.func(cls)
        cache[cls] = res
        return res
