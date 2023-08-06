
class ArgParser:
    @staticmethod
    def _dust_parse(obj):
        return obj

    @staticmethod
    def eval(string):
        return eval('ArgParser.' + string)
