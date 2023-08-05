

class Color:
    @staticmethod
    def underline(string):
        return '\033[4m' + str(string) + '\033[0m'

    @staticmethod
    def light(string):
        return '\033[2m' + str(string) + '\033[0m'

    @staticmethod
    def red(string):
        return '\033[31m' + str(string) + '\033[0m'

    @staticmethod
    def green(string):
        return '\033[32m' + str(string) + '\033[0m'

    @staticmethod
    def orange(string):
        return '\033[33m' + str(string) + '\033[0m'

    @staticmethod
    def blue(string):
        return '\033[34m' + str(string) + '\033[0m'

    @staticmethod
    def pink(string):
        return '\033[35m' + str(string) + '\033[0m'

    @staticmethod
    def light_blue(string):
        return '\033[36m' + str(string) + '\033[0m'

    @staticmethod
    def white(string):
        return '\033[37m' + str(string) + '\033[0m'

    @staticmethod
    def purple(string):
        return '\033[95m' + str(string) + '\033[0m'
