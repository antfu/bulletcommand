
class Module:

    def __init__(self, name, basic_help=None, helpes=None):
        self.name = name.lower().strip()
        self.bot = None
        self.basic_help = basic_help
        self.helpes = helpes or {}

    def immerse(self, func):
        return self.bot.immerse(func)

    def handler(self, body, push):
        pass