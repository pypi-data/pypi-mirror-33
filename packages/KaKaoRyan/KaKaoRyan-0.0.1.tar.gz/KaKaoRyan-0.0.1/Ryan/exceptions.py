class ParamError(Exception):
    def __init__(self, *args):
        super(ParamError, self).__init__(*args)


class ScheamError(Exception):
    def __init__(self, *args):
        super(ScheamError, self).__init__(*args)


class RequiredError(Exception):
    def __init__(self, *args):
        super(RequiredError, self).__init__(*args)

