from .query import compile_query


class QueryBuilder(object):
    def __init__(self, **kwargs):
        self.raw_query = kwargs
        self.chain = None

    def compile(self):
        return compile_query(self.raw_query)

    def name(self, value):
        return self.__add_query({'name': value})

    def attribute(self, key, value):
        return self.__add_query({'attribute': {'name': key, 'value': value}})

    def data(self, value):
        return self.__add_query({'data': value})

    def _or(self):
        assert not self.chain, 'Cannot chain with other chain methods'
        self.chain = lambda q: {'or': (self.raw_query, q)}
        return self

    def _and(self):
        assert not self.chain, 'Cannot chain with other chain methods'
        self.chain = lambda q: {'and': (self.raw_query, q)}
        return self

    def _not(self):
        if self.chain:
            _chain = self.chain
            self.chain = lambda q: _chain({'not': q})
        else:
            self.chain = lambda q: {'not': q}
        return self

    def __add_query(self, query):
        if self.raw_query:
            assert self.chain, "Cannot chain queries without a chain method! (e.g _or, _and, _not)"
            self.raw_query = self.chain(query)
            self.chain = None
        elif self.chain:
            self.raw_query = self.chain(query)
            self.chain = None
        else:
            self.raw_query = query
        return self
