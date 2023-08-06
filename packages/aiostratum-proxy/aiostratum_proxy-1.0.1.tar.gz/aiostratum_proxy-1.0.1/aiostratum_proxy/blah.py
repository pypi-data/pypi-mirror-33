class Blah:
    d = {'key': 'value'}

    def get_stuff(self, extra=''):
        value = self.d.get('key', '')
        print('value1', value)
        value = ".".join([s for s in [value, extra] if len(s)])
        print('value2', value)
        return value