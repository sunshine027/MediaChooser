#! /usr/bin/env python
#coding=utf-8

cpc_color, click_color, media_price_color, weekend_color, campaign_cpc_color = '#0f70d3', '#92D050', "#0f70d3", '#9A0000', '#BF3EFF'
bar_num = 20


def write_amdata_xml(x, y_left, y_right=None, average=None, name='tmp.xml', x_trans=False):

    import xml.etree.ElementTree as ET
    root = ET.Element('chart')
    series = ET.SubElement(root, 'series')
    i = 1
    if x_trans:
        x = axis2labels_noweekend(x)
        
    for k in x:
        value = ET.SubElement(series, 'value')
        value.attrib['xid'] = '%s' % i
        value.text = '%s' % k
        i += 1
    
    graphs = ET.SubElement(root, 'graphs')
    
    i = 1
    left_graph = ET.SubElement(graphs, 'graph')
    left_graph.attrib['gid'] = '1'
    #cpc_graph.attrib['title'] = 'cpc'
    left_graph.attrib['color'] = cpc_color
    for c in y_left:
        value = ET.SubElement(left_graph, 'value')
        value.attrib['xid'] = '%s' % i
        if c:
            value.text = '%.2f' % float(c)
        else:
            value.text = '%s' % c
        i += 1
    
    if y_right:
        i = 1
        right_graph = ET.SubElement(graphs, 'graph')
        right_graph.attrib['gid'] = '2'
        #click_graph.attrib['title'] = 'click'
        right_graph.attrib['color'] = click_color
        for cd in y_right:
            value = ET.SubElement(right_graph, 'value')
            value.attrib['xid'] = '%s' % i
            value.text = '%s' % cd
            i += 1
    
    if average:
        i = 1
        average_graph = ET.SubElement(graphs, 'graph')
        average_graph.attrib['gid'] = '3'
        #click_graph.attrib['title'] = 'click'
        average_graph.attrib['color'] = campaign_cpc_color
        for t in average:
            value = ET.SubElement(average_graph, 'value')
            value.attrib['xid'] = '%s' % i
            value.text = '%s' % t
            i += 1
    
    tree = ET.ElementTree(root)
    
    from django.conf import settings
    import os
    name = os.path.join(settings.ROOT, 'mc_media','amchart','data',name)
    tree.write(name)
    return 1

def write_dict_xml(x,dict,name, trans_data=None):
    
    import xml.etree.ElementTree as ET
    root = ET.Element('chart')
    series = ET.SubElement(root, 'series')
    i = 1
    
    if trans_data:
        x = axis2labels_noweekend(x)
        
    for k in x:
        value = ET.SubElement(series, 'value')
        value.attrib['xid'] = '%s' % i
        value.text = '%s' % k
        i += 1
    
    graphs = ET.SubElement(root, 'graphs')
    
    for k in dict.keys():
        i = 1
        graph = ET.SubElement(graphs, 'graph')
        #graph.attrib['gid'] = '%s' % i
        #graph.attrib['color'] = cpc_color
        graph.attrib['title'] = k
        graph.attrib['balloon_text'] = "{title}:{value}" 
        j = 1
        for c in dict[k]:
            value = ET.SubElement(graph, 'value')
            value.attrib['xid'] = '%s' % j
            if c:
                value.text = '%.2f' % float(c)
            else:
                value.text = '%s' % c
            j +=1
        i += 1
    
    tree= ET.ElementTree(root)
    
    from django.conf import settings
    import os
    name = os.path.join(settings.ROOT, 'mc_media','amchart','data',name)
    tree.write(name)
    return 1

def write_bar_xml(dict_data, name):
    import xml.etree.ElementTree as ET
    root = ET.Element('chart')
    series = ET.SubElement(root, 'series')
    i = 1
    
    keys, values = _sort_dict_by_value(dict_data)
    
    for k in keys:
        value = ET.SubElement(series, 'value')
        value.attrib['xid'] = '%s' % i
        value.text = '%s' % k
        i += 1
    
    i = 1
    graphs = ET.SubElement(root, 'graphs')
    graph = ET.SubElement(graphs, 'graph')
    graph.attrib['color'] = cpc_color
    graph.attrib['gid'] = '1'
    for k in keys:
        
        #graph.attrib['gid'] = '%s' % i
        #graph.attrib['title'] = k
        #graph.attrib['balloon_text'] = "{title}:{value}"
        
        value = ET.SubElement(graph, 'value')
        value.attrib['xid'] = '%s' % i
        #value.attrib['url'] = 'javascript:bar_1()'
        #if c:
        #    value.text = '%.2f' % float(c)
        #else:
        value.text = '%.2f' % dict_data[k]
        i += 1
    
    tree= ET.ElementTree(root)
    
    from django.conf import settings
    import os
    name = os.path.join(settings.ROOT, 'mc_media','amchart','data',name)
    tree.write(name)
    return 1

def write_bar_withid_xml(dict_data, id_dict, name):
    import xml.etree.ElementTree as ET
    root = ET.Element('chart')
    series = ET.SubElement(root, 'series')
    i = 1
    
    keys, values = _sort_dict_by_value(dict_data)
    
    for k in keys:
        if i>= bar_num:
            continue
        value = ET.SubElement(series, 'value')
        value.attrib['xid'] = '%s' % i
        value.text = '%s' % k
        i += 1
    
    i = 1
    graphs = ET.SubElement(root, 'graphs')
    graph = ET.SubElement(graphs, 'graph')
    graph.attrib['color'] = cpc_color
    graph.attrib['gid'] = '1'
    for k in keys:
        
        if i>bar_num:
            continue
        #graph.attrib['gid'] = '%s' % i
        #graph.attrib['title'] = k
        #graph.attrib['balloon_text'] = "{title}:{value}"
        
        value = ET.SubElement(graph, 'value')
        value.attrib['xid'] = '%s' % i
        value.attrib['url'] = 'javascript:bar_1(%s)' % id_dict[k]
        #if c:
        #    value.text = '%.2f' % float(c)
        #else:
        value.text = '%.2f' % dict_data[k]
        i += 1
    
    tree= ET.ElementTree(root)
    
    from django.conf import settings
    import os
    name = os.path.join(settings.ROOT, 'mc_media','amchart','data',name)
    tree.write(name)
    return 1

def write_bar1_xml(keys, values, media, channel_ids, name):
    import xml.etree.ElementTree as ET
    root = ET.Element('chart')
    
    series = ET.SubElement(root, 'series')
    
    labels = ET.SubElement(root, 'labels')
    label = ET.SubElement(labels, 'label')
    align = ET.SubElement(label, 'align')
    align.text = 'center'
    text = ET.SubElement(label, 'text')
    text.text = media.c_name
    y = ET.SubElement(label, 'y')
    y.text = '20'
    
    i = 1
    
    #keys, values = _sort_dict_by_value(dict_data)
    
    for k in keys:
        if i >= bar_num:
            continue
        value = ET.SubElement(series, 'value')
        value.attrib['xid'] = '%s' % i
        value.text = '%s' % k
        i += 1
    
    #i = 1
    graphs = ET.SubElement(root, 'graphs')
    graph = ET.SubElement(graphs, 'graph')
    graph.attrib['color'] = cpc_color
    graph.attrib['gid'] = '1'
    for i,v in enumerate(values):
        
        if i>bar_num:
            continue
        
        #graph.attrib['gid'] = '%s' % i
        #graph.attrib['title'] = k
        #graph.attrib['balloon_text'] = "{title}:{value}"
        
        value = ET.SubElement(graph, 'value')
        value.attrib['xid'] = '%s' % (i+1)
        value.attrib['url'] = 'javascript:bar_2(%s,%s)' % (channel_ids[i], media.id)
        #if c:
        #    value.text = '%.2f' % float(c)
        #else:
        value.text = '%.2f' % v
        #i += 1
    
    tree= ET.ElementTree(root)
    
    from django.conf import settings
    import os
    name = os.path.join(settings.ROOT, 'mc_media','amchart','data',name)
    tree.write(name)
    return 1

def write_bar2_xml(adforms, cpc_data, media, channel, name):
    import xml.etree.ElementTree as ET
    root = ET.Element('chart')
    
    series = ET.SubElement(root, 'series')
    
    labels = ET.SubElement(root, 'labels')
    label = ET.SubElement(labels, 'label')
    align = ET.SubElement(label, 'align')
    align.text = 'center'
    text = ET.SubElement(label, 'text')
    text.text = media.c_name + '-' + channel
    y = ET.SubElement(label, 'y')
    y.text = '20'
    
    i = 1
    
    #keys, values = _sort_dict_by_value(dict_data)
    
    #for k in keys:
    #    value = ET.SubElement(series, 'value')
    #    value.attrib['xid'] = '%s' % i
    #    value.text = '%s' % k
    #    i += 1
    
    #i = 1
    graphs = ET.SubElement(root, 'graphs')
    graph = ET.SubElement(graphs, 'graph')
    graph.attrib['color'] = cpc_color
    graph.attrib['gid'] = '1'
    for i,v in enumerate(cpc_data):
        value1 = ET.SubElement(series, 'value')
        value1.attrib['xid'] = '%s' % (i+1)
        value1.text = '%s' % adforms[i]
        #graph.attrib['gid'] = '%s' % i
        #graph.attrib['title'] = k
        #graph.attrib['balloon_text'] = "{title}:{value}"
        
        value = ET.SubElement(graph, 'value')
        value.attrib['xid'] = '%s' % (i+1)
        #if c:
        #    value.text = '%.2f' % float(c)
        #else:
        value.text = '%.2f' % v
        #i += 1
    
    tree= ET.ElementTree(root)
    
    from django.conf import settings
    import os
    name = os.path.join(settings.ROOT, 'mc_media','amchart','data',name)
    tree.write(name)
    return 1
    

def write_ampie_xml(x,y,name):
    import xml.etree.ElementTree as ET
    root = ET.Element('pie')
    
    for i,k in enumerate(x):
        value = ET.SubElement(root, 'slice')
        value.attrib['title'] = '%s' % k
        value.text = '%s' % y[i]
    
    tree= ET.ElementTree(root)
    
    from django.conf import settings
    import os
    name = os.path.join(settings.ROOT, 'mc_media','amchart','data',name)
    tree.write(name)
    return 1

def axis2labels_noweekend(axis):
    """ change x-axis to date without 'year', then to label. eg: 2009-09-09 -> 09-09  """
    labels = []
    date_no_year = lambda x: ('-').join(str(x).split('-')[1:])
    for x in axis:
        labels.append(date_no_year(x))
    return labels
    
def _sort_dict_by_value(dict_data, reverse=False):
    """ sort a dict by value, return keys and value """
    keys = []
    values = []
    if type(dict_data) != type({}):
        return None
    else:
        for k, v in sorted(dict_data.items(), key=lambda x: x[1], reverse=reverse):
            keys.append(k)
            values.append(v)
    return keys, values