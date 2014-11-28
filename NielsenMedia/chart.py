#! /usr/bin/env python
#coding=utf-8

from OpenFlashChart import Chart
import math, time

class Element(Chart):
    def __init__(self, type = None, alpha = None, colour = None, text = None, fontsize = None, values = None):
        self.type = type
        self.alpha = alpha
        self.colour = colour
        self.text = text
        self.fontsize = fontsize
        self.values = values

# Line Charts
class Line(Element):
    def __init__(self, alpha = None, colour = None, text = None, fontsize = None, values = None):
        Element.__init__(self, 'line', alpha, colour, text, fontsize, values)

class Line_Dot(Element):
    def __init__(self, alpha = None, colour = None, text = None, fontsize = None, values = None, width= None, dot_size= None, dot_colour = None):
        Element.__init__(self, 'line', alpha, colour, text, fontsize, values)
        self.dot_style.type = "dot"
        self.width = width
        self.dot_style.dot_size = dot_size
        self.dot_style.colour = dot_colour
        
class Line_Hollow(Element):
    def __init__(self, alpha = None, colour = None, text = None, fontsize = None, values = None, dot_size= None, dot_colour = None):
        Element.__init__(self, 'line', alpha, colour, text, fontsize, values)
        self.dot_style.type = "hollow-dot"
        self.dot_style.dot_size = dot_size
        self.dot_style.colour = dot_colour

# Bar Charts
class Bar(Element):
    def __init__(self, alpha = None, colour = None, text = None, fontsize = None, values = None):
        Element.__init__(self, 'bar', alpha, colour, text, fontsize, values)
        
class Bar_Filled(Element):
    def __init__(self, alpha = None, colour = None, text = None, fontsize = None, values = None, outline_colour = None):
        Element.__init__(self, 'bar_filled', alpha, colour, text, fontsize, values)
        if outline_colour:
            self.outline_colour = outline_colour

class Bar_Glass(Element):
    def __init__(self, alpha = None, colour = None, text = None, fontsize = None, values = None):
        Element.__init__(self, 'bar_glass', alpha, colour, text, fontsize, values)

class Bar_3d(Element):
    def __init__(self, alpha = None, colour = None, text = None, fontsize = None, values = None):
        Element.__init__(self, 'bar_3d', alpha, colour, text, fontsize, values)

class Bar_Sketch(Element):
    def __init__(self, alpha = None, colour = None, text = None, fontsize = None, values = None, outline = None):
        Element.__init__(self, 'bar_sketch', alpha, colour, text, fontsize, values)
        if outline:
            self.elements[0]['outline-colour'] = outline

class HBar(Element):
    def __init__(self, alpha = None, colour = None, text = None, fontsize = None, values = None):
        Element.__init__(self, 'hbar', alpha, colour, text, fontsize, values)

class Bar_Stack(Element):
    def __init__(self, alpha = None, colour = None, text = None, fontsize = None, values = None, colours = None):
        Element.__init__(self, 'bar_stack', alpha, colour, text, fontsize, values)
        if colours:
            self.elements[0]['colours'] = colours

chart = Chart()
chart.y_axis.min = 0
chart.y_axis.max = 20
chart.y_axis.font_size = 10
chart.title.text = "Three lines example"

element1 = Line(None, "#FA1345", "Line", 10, [19,17,19,19,17,19,17,17,14,14,17,16])
element2 = Line_Dot(None, "#DFC329", "Line_Dot", 10, [3,4,5,6,5,4,3,2,1,4,5], 4, 5, "#FA1345")
element3 = Line_Hollow(None, "#cccccc", "Line_Hollow", 10, [1,3,4,5,6,5,4,3,2,1,4,5], 5, "#FA1345")

element4 = Bar(None, "#ecb211", "Bar", 10, [19,17,19,19,17,19,17,17,14,14,17,16])
element5 = Bar_Filled(None, "#E2D66A", "Bar_Filled", 10, [9, 8, 7, 6, 5, 4, 3, 2, 1 ], "#fff")
element6 = Bar_Glass(None, None, "Bar_Glass", 10, [1,9, 8, 7, 6, 5, 4, 3, 2, 1 ])

chart.elements = [element1, element2, element3, element4, element5, element6]