from string import Template

import datetime

import ofc2
from ofc2_element import Line, Bar, BarStack


jstpl = Template('swfobject.embedSWF("/static_files/open-flash-chart.swf","$title", "$width", "$height", "$flash_ver", "expressInstall.swf", {"data-file": "$data_src"});\n')
dvtpl = Template('<h1>$title</h1><div id="$title"></div><br/>\n')

class Chart(object):
    type = ''
    title = 'chart'

    width=400
    height=200
    flash_ver='9.0.0'

    data_src = None

    chart = None

    def index(self):
        return self.chart.encode()

    def __init__(self, type, name):
        self.title = name
        self.data_src='../ofc_json_data/'+name

    def get_js(self):
        return jstpl.substitute(title=self.title, width=self.width, height=self.height, flash_ver = self.flash_ver, data_src = self.data_src)
    
    def get_div(self):
        return dvtpl.substitute(title=self.title)

class BarChart(Chart):
    def __init__(self, type, name):
        Chart.__init__(self, type, name)

        # create the bar element and set its values
        element = Bar(values=[9,8,7,6,5,4,3,2,1])

        # create the chart and set its title
        self.chart = ofc2.open_flash_chart(title=str(datetime.datetime.now()))
        self.chart.add_element(element)

class BarStackChart(Chart):
    def __init__(self, type, name):
        Chart.__init__(self, type, name)

        # create the bar element and set its values
        element = BarStack(values=[ [ 2.5, 5 ], [ 7.5 ], [ 5, { 'val': 5, 'colour': '#ff0000' } ], [ 2, 2, 2, 2, { "val": 2, 'colour': '#ff00ff' } ] ])

        # create the chart and set its title
        self.chart = ofc2.open_flash_chart(title=str(datetime.datetime.now()))
        self.chart.set_y_axis(min=0, max=14, steps=7)
        self.chart.set_x_axis(labels=['a', 'b', 'c', 'd'])
        self.chart.add_element(element)

class LineChart(Chart):
    def __init__(self, type, name):
        Chart.__init__(self, type, name)

        # create the bar element and set its values
        element = Line(values=[9,8,7,6,5,4,3,2,1])

        # create the chart and set its title
        self.chart = ofc2.open_flash_chart(title=str(datetime.datetime.now()))
        self.chart.add_element(element)


xhtml_template = """
<html xmlns="http://www.w3.org/1999/xhtml">
    <script type="text/javascript" src="/static_files/swfobject.js"></script>
    <script type="text/javascript">
        $js
    </script>
<head>

<title>$title</title>

</head>

<body>
    $body
</body>

</html>
"""

class OFC2Demo(object):
    tpl = Template(xhtml_template)
    swfobjs = ''
    divs = ''

    linechart = LineChart('line_chart', 'linechart') # var name must be the same as the second param
    barchart = BarChart('bar_chart', 'barchart') # var name must be the same as the second param
    barstackchart = BarStackChart('bar_stack', 'barstackchart') # var name must be the same as the second param

    def index(self):
        self.load_charts()
        response = self.tpl.substitute(title='Open Flash Charts 2 - Python Library Demo', js=self.swfobjs, body=self.divs)
        return response
 
    def load_charts(self):
        self.swfobjs = ''
        self.divs = ''
        self.add_chart(self.linechart)
        self.add_chart(self.barchart)
        self.add_chart(self.barstackchart)

    def add_chart(self, chart):
        self.swfobjs += chart.get_js()
        self.divs += chart.get_div()


'''
cherrypy.quickstart(OFC2Demo(), '/', 'cherrypy.conf')
'''

