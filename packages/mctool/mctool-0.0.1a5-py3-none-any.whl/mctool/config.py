class Config(object):
    def __init__(self, **kwargs):
        for key in kwargs:
            setattr(self, str(key), kwargs[key])
