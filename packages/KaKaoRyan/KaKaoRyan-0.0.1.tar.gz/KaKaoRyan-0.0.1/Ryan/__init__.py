from Ryan.exceptions import (ParamError, ScheamError,
                            RequiredError,)

class Param:
    def __init__(self, *args, **kwargs):
        self.types = []
        self.scheam = None
        if not args:
            raise ParamError('未接收到参数')
        if isinstance(args[0], dict):
            self.scheam = args[0]
            self.types.append(dict)
            return
        if isinstance(args[0], list):
            self.scheam = args[0]
            self.types.append(list)
            return
        for arg in args:
            if arg.__class__ is type:
                self.types.append(arg)
        if not self.types:
            raise ScheamError('无指定结构')

    def validate(self, data, key=None):
        if self.types and data.__class__ not in self.types:
            raise ParamError('{}不符合输入要求'.format(data.__class__))
        if self.scheam:
            if isinstance(self.scheam[0], dict):
                Ryan(self.scheam).validate(data)
            elif isinstance(self.scheam, list):
                for index, d in enumerate(data):
                    Ryan(self.scheam[index]).validate(d)
            return True

        return True


class Required(Param):
    def __init__(self, *args, **kwargs):
        if args:
            super(Required, self).__init__(*args, **kwargs)
        else:
            super(Required, self).__init__()

    def validate(self, data, key=None):
        if key not in data.keys():
            raise RequiredError('key错误')
        else:
            super().validate(data[key], key)


class Optional(Param):
    def validate(self, data, key=None):
        if key in data.keys():
            super().validate(data[key], key)


class Ryan:
    def __init__(self, *args, **kwargs):
        self.scheam = args[0]
        self.is_dict = True

        if not args:
            raise ParamError('未接收到参数')
        if isinstance(args[0], dict):
            for _, v in self.scheam.items():
                if not issubclass(v.__class__, Param):
                    raise ScheamError('结构错误')
        else:
            self.scheam = args
            self.is_dict = False

    def validate(self, data):
        if not self.is_dict:
            return Param(*self.scheam).validate(data)
        if isinstance(data, dict):
            for k, v in self.scheam.items():
                if isinstance(v, Optional) and k not in data.keys():
                    continue
                try:
                    v.validate(data, k)
                except:
                    raise RequiredError('验证失败')
                    return False

        return True

if __name__ == '__main__':
    s = {
        'k1': Required(int),
        'k2': Optional(str),
    }

    d = {
        'k1': 3,
        'k2': '22',
    }
    print(Ryan(s).validate(d))