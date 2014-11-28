# This program is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation; version 2 of the License.
# 
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
# 
# Author: Eugene Kin Chee Yip
# Date:   14 June 2009

try:
    NO_CJSON = False
    import	cjson
except ImportError:
    NO_CJSON = True
    import json
import	copy

class Chart(dict):
    # Dictionary for replacing attribute names
    replaceKeyDictionary =	{
        "on_show": "on-show",			"on_click": "on-click",
        "start_angle": "start-angle",
        
        "threeD": "3d",					"tick_height": "tick-height",
        "grid_colour": "grid-colour",	"tick_length": "tick-length",
    
        "dot_style": "dot-style",		"dot_size": "dot-size",
        "halo_size": "halo-size",

    "line_style": "line-style",		"outline_colour": "outline-colour",
    "fill_alpha": "fill-alpha",		"gradient_fill": "gradient-fill",
    }

    # Redefine to allow for nested attributes.
    # E.g. when calling the leaf attribute, text, in chart.title.text
    #      without previously defining the branch attribute, title.
    def __getattribute__(self, key):
        try:
            return dict.__getattribute__(self, key)
        except AttributeError:
            self.__dict__[key] = Chart()
            return dict.__getattribute__(self, key)
    
    
    # This copy function is called when we want to get all the attributes of the 
    # chart instance so we can pass it off to cjson to create the JSON string.
    # Recursive trick to get leaf attributes.  Have to be careful of list types.
    # Also, replace certain underscored keys.
    # E.g. getting the leaf attribute, text, from the parent Chart instance where a  
    #      previous assignment was to chart.title.text
    def __copy__(self):
        attributes = dict()
        for key, value in self.__dict__.items():
            if isinstance(value, list):
                attributes[self.replaceKey(key)] = [copy.copy(item) for item in value]
            else:
                attributes[self.replaceKey(key)] = copy.copy(value)
        return attributes

    # If key has an underscore, replace with a dash.
    # Python does not allow dash in object names.
    def replaceKey(self, key):
        if (key in self.replaceKeyDictionary):
            return self.replaceKeyDictionary[key]
        else:
            return key

    # Encode the chart attributes as JSON
    def create(self):
        attributes = copy.copy(self)
        if NO_CJSON:
            return json.dumps(attributes)
        else:
            return cjson.encode(attributes)

class Element(Chart):
    def __init__(self, type = None, colour = None, text = None, fontsize = None, values = None, axis='left', alpha=1):
        self.type = type
        self.colour = colour
        self.text = text
        self.fontsize = fontsize
        self.values = values
        self.axis = axis
        self.alpha = alpha

# Line Charts
class Line(Element):
    def __init__(self, colour = None, text = None, fontsize = None, values = None, axis= 'left'):
        Element.__init__(self, 'line', colour, text, fontsize, values, axis)
        #self.dot_style.tip = tip

class Line_Dot(Element):
    def __init__(self, colour = None, text = None, fontsize = None, values = None, axis= 'left', width= None, dot_size= None, dot_colour = None):
        Element.__init__(self, 'line', colour, text, fontsize, values, axis)
        self.dot_style.type = "dot"
        self.width = width
        self.style.dot_size = dot_size
        self.style.colour = dot_colour
        #self.style.tip = tip

class Line_Hollow(Element):
    def __init__(self, colour = None, text = None, fontsize = None, values = None, axis= 'left', dot_size= None, dot_colour = None):
        Element.__init__(self, 'line', colour, text, fontsize, values, axis)
        #self.style.type = "hollow-dot"
        self.dot_style.type = "solid-dot"
        self.dot_style.dot_size = dot_size
        self.dot_style.colour = dot_colour
        self.dot_style.halo_size = 1 
        #self.style.tip = tip

# Bar Charts
class Bar(Element):
    def __init__(self, colour = None, text = None, fontsize = None, values = None, alpha=1):
        Element.__init__(self, 'bar', colour, text, fontsize, values, alpha)

class Bar_Filled(Element):
    def __init__(self, colour = None, text = None, fontsize = None, values = None, outline_colour = None):
        Element.__init__(self, 'bar_filled', colour, text, fontsize, values)
        if outline_colour:
            self.outline_colour = outline_colour

class Bar_Glass(Element):
    def __init__(self, colour = None, text = None, fontsize = None, values = None, axis= 'left', alpha=1):
        Element.__init__(self, 'bar_glass', colour, text, fontsize, values, axis, alpha)

class Bar_3d(Element):
    def __init__(self, colour = None, text = None, fontsize = None, values = None, axis= 'left'):
        Element.__init__(self, 'bar_3d', colour, text, fontsize, values, axis)

class Bar_Sketch(Element):
    def __init__(self, colour = None, text = None, fontsize = None, values = None, outline = None):
        Element.__init__(self, 'bar_sketch', colour, text, fontsize, values)
        if outline:
            self.elements[0]['outline-colour'] = outline

class HBar(Element):
    def __init__(self, colour = None, text = None, fontsize = None, values = None):
        Element.__init__(self, 'hbar', colour, text, fontsize, values)

class Bar_Stack(Element):
    def __init__(self, colour = None, text = None, fontsize = None, values = None, colours = None):
        Element.__init__(self, 'bar_stack', colour, text, fontsize, values)
        if colours:
            self.elements[0]['colours'] = colours
