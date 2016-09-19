from botbullet import Module

class EvalModule(Module):
    def __init__(self, **kwargs):
        super().__init__('eval', **kwargs)
        # make a list of safe functions
        safe_list = ['math','acos', 'asin', 'atan', 'atan2',
                     'ceil', 'cos', 'cosh', 'degrees', 'e', 'exp',
                     'fabs', 'floor', 'fmod', 'frexp', 'hypot', 'ldexp', 'log',
                     'log10', 'modf', 'pi', 'pow', 'radians', 'sin',
                     'sinh', 'sqrt', 'tan', 'tanh']
        # use the list to filter the local namespace
        safe_dict = dict([ (k, locals().get(k, None)) for k in safe_list ])
        # add any needed builtins back in.
        safe_dict['abs'] = abs

        self._scope = safe_dict

        self._exec('from math import *')

    def _eval(self, text):
        try:
            result = eval(text, self._scope)
            if result != None:
                return str(result)
            else:
                return None
        except Exception as e:
            return 'Error: ' + str(e)

    def _exec(self, text):
        try:
            exec(text, self._scope)
            return None
        except Exception as e:
            return 'Error: ' + str(e)

    def reply(self, body):
        if body.startswith('%'):
            body = body[1:]
            result = self._exec(body)
        else:
            result = self._eval(body)
        if result:
            self.bot.reply(result)

    def immerse_handler(self, body, push):
        if not body or body.lower() == 'exit':
            push.reply('Leaving immerse mode','Eval')
            push.delete()
        else:
            self.reply(body)
            self.immerse(self.immerse_handler)

    def handler(self, body, push):
        if not body:
            self.immerse(self.immerse_handler)
            push.reply('Entering immerse mode','Eval')
            push.delete()
        else:
            self.reply(body)

export = EvalModule
