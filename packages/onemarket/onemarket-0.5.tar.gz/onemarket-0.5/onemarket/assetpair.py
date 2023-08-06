class AssetPair(object):
    def __init__(self, base, quote):
        self.__base = base
        self.__quote = quote

    def base(self):
        return self.__base

    def quote(self):
        return self.__quote

    @staticmethod
    def from_json(data):
        return AssetPair(data['base'], data['quote'])

    def to_json(self):
        return {
            'base': self.base(),
            'quote': self.quote()
        }

    def __str__(self):
        return "%s%s" % (self.__base, self.__quote)

    def __hash__(self):
        return hash((self.__base, self.__quote))

    def __eq__(self, other):
        return isinstance(other, self.__class__) and other.__base == self.__base and other.__quote == self.__quote
