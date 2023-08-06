class QueryBuilder(object):
    def __init__(self):
        self.data = {}

    def name(self, value):
        self.data = {'or': (self.data, {'name': value})}
        return self
