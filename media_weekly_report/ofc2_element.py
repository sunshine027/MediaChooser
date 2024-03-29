
class element(dict):
    def __init__(self, type=None, alpha=None, colour=None, text=None, fontsize=None, values=None):
        self.set_type(type)
        self.set_alpha(alpha)
        self.set_colour(colour)
        self.set_text(text)
        self.set_fontsize(fontsize)
        self.set_values(values)

    def set_type(self, type):
        if type:
            self['type'] = type

    def set_alpha(self, alpha):
        if alpha:
            self['alpha'] = alpha

    def set_colour(self, colour):
        if colour:
            self['colour'] = colour

    def set_text(self, text):
        if text:
            self['text'] = text

    def set_fontsize(self, fontsize):
        if fontsize:
            self['font-size'] = fontsize

    def set_values(self, values):
        if values:
            self['values'] = values

class Line(element):
    def __init__(self, type=None, alpha=None, colour=None, text=None, fontsize=None, values=None):
        element.__init__(self, 'line', alpha, colour, text, fontsize, values)

class Bar(element):
    def __init__(self, type=None, alpha=None, colour=None, text=None, fontsize=None, values=None):
        element.__init__(self, 'bar', alpha, colour, text, fontsize, values)

class BarStack(element):
    def __init__(self, type=None, alpha=None, colour=None, text=None, fontsize=None, values=None):
        element.__init__(self, 'bar_stack', alpha, colour, text, fontsize, values)
