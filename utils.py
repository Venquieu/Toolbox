class Struct(object):
    def __init__(self, **kwargs):
        self.__dict__.update(kwargs)

    @property
    def map(self):
        return self.__dict__
    
    @property
    def attri(self):
        return list(self.__dict__.keys())
    
    def __repr__(self):
        return str(self.__dict__)
