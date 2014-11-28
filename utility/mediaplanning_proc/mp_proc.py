#! /usr/bin/env python
#coding=utf-8

import xlrd 
import re

c_book = xlrd.open_workbook('for_test.xls')

c_sheet = c_book.sheet_by_index(0)

code_index = -1
code_re = re.compile(r'^http://.*')
delink_list = []

# 获取'代码'/'广告代码'列，如无，给出警告
for i in xrange(c_sheet.nrows):
    for j in xrange(c_sheet.ncols):
        if c_sheet.cell_value(i, j) == u'代码' or c_sheet.cell_value(i, j) == u'广告代码':
#            print 'code is here!', i, j#
            code_index = j
if code_index == -1:
    print 'status: no code!'

# 获取包含DE link的列
for i in xrange(c_sheet.nrows):
    cont = c_sheet.cell_value(i, code_index)
    re_ret = code_re.search(cont)
    if re_ret is not None:
        delink_list.append(i)

# 获取网站/广告位置/广告形式/广告规格/单位/折扣/折后单价/折后总价
website_index = [-1, -1]
position_index = [-1, -1]
adform_index = [-1, -1]
size_index = [-1, -1]
unit_index = [-1, -1]
discount_index = [-1, -1]
price_index = [-1, -1]
totalprice_index = [-1, -1]

try:
    for i in xrange(delink_list[0]):
        for j in xrange(c_sheet.ncols):
            if c_sheet.cell_type(i, j) == xlrd.XL_CELL_TEXT:
                c_v = c_sheet.cell_value(i, j)
                if c_v == u'网站':
                    website_index = [i, j]
                elif c_v == u'广告位置':
                    position_index = [i, j]
                elif c_v == u'广告形式':
                    adform_index = [i, j]
                elif c_v == u'广告规格':
                    size_index = [i, j]
                elif c_v == u'单位':
                    unit_index = [i, j]
                elif c_v == u'折扣':
                    discount_index = [i, j]
                elif c_v == u'折后单价':
                    price_index = [i, j]
                elif c_v == u'折后总价':
                    totalprice_index = [i, j]
                else:
                    pass
except Exception, e:
    print e.message

# 检查这几个重要参数是否在同一行出现
if website_index[0]==position_index[0]==adform_index[0]==size_index[0]==unit_index[0]==discount_index[0]==price_index[0]==totalprice_index[0]:
    print 'There r in the same row!'

# 获取日期信息
date_row = website_index[0]
date_re = re.compile(r'^\d{4}年\d{1,2}月')
date_dict = {}
for j in xrange(c_sheet.ncols):
#    print c_sheet.cell_value(date_row, j), c_sheet.cell_type(date_row, j)
    if c_sheet.cell_type(date_row, j) == xlrd.XL_CELL_DATE or c_sheet.cell_type(date_row, j) == xlrd.XL_CELL_NUMBER:
        month_tuple = xlrd.xldate_as_tuple(c_sheet.cell_value(date_row, j), 0)
        print c_sheet.cell_value(date_row, j)
        for day_row in xrange(date_row+1, date_row+3):
            if c_sheet.cell_type(day_row, j) == xlrd.XL_CELL_NUMBER:
                # 在单元格类型为NUMBER的情况下，check俩个点：1，数值是递增的，且在1~31之间；2，同列date_row所在行的单元格无数据
                date_dict[j] = (month_tuple[0], month_tuple[1], c_sheet.cell_value(day_row, j))
                continue_stat = True
                for day_col in xrange(j+1, c_sheet.ncols):
                    if c_sheet.cell_type(day_row, day_col-1) == xlrd.XL_CELL_NUMBER and continue_stat:
                        if c_sheet.cell_value(day_row, day_col) > c_sheet.cell_value(day_row, day_col-1) and 1 <= c_sheet.cell_value(day_row, day_col) <= 31:
                            print c_sheet.cell_value(day_row, day_col)
                            date_dict[day_col] = (month_tuple[0], month_tuple[1], c_sheet.cell_value(day_row, day_col))
                        else:
                            continue_stat = False

#    if c_sheet.cell_type(date_row, j) == xlrd.XL_CELL_TEXT:
#        if date_re.search(c_sheet.cell_value(date_row, j)) is not None:
#            print j
    
# 将有网站名称的列存储起来
website_rowlist = []
for i in xrange(website_index[0]+1, c_sheet.nrows):
    if c_sheet.cell_value(i, website_index[1]) is not None and c_sheet.cell_value(i, website_index[1]) is not '':
        website_rowlist.append(i)

# 确保包含DE LINK的行对应的网站都有域名，如果出现没有DOMAIN的情形，则让数据组同事补上一个特定命名的域名
domain_re = re.compile(r'[a-zA-Z0-9][-a-zA-Z0-9]{0,62}(\.[a-zA-Z0-9][-a-zA-Z0-9]{0,62})+\.?')

# 获取到网站的DOMAIN
for i in website_rowlist:
    ret = domain_re.search(c_sheet.cell_value(i, website_index[1]))
    if ret is not None:
        print c_sheet.cell_value(i, website_index[1])[ret.start():ret.end()]

# 函数：对含有DE LINK的row进行获取website的操作
def get_website(row_index):
    for i in xrange(len(website_rowlist)):
        if website_rowlist[i] <= row_index < website_rowlist[i+1]:
            return c_sheet.cell_value(website_rowlist[i], website_index[1]).strip()

#print date_dict
#print website_index[1], position_index[1], adform_index[1], size_index[1], unit_index[1], discount_index[1], price_index[1], totalprice_index[1]

for it in xrange(len(delink_list)):
    print get_website(delink_list[it]), c_sheet.cell_value(delink_list[it], position_index[1]).strip(), c_sheet.cell_value(delink_list[it], adform_index[1]).strip(), c_sheet.cell_value(delink_list[it], size_index[1]).strip(), c_sheet.cell_value(delink_list[it], unit_index[1]).strip().lower()
    if c_sheet.cell_type(delink_list[it], discount_index[1]) is not xlrd.XL_CELL_NUMBER:
        print 'Free', 'Free', 'Free'
    else:
        print c_sheet.cell_value(delink_list[it], discount_index[1]) or 'Free', c_sheet.cell_value(delink_list[it], price_index[1]) or 'Free', c_sheet.cell_value(delink_list[it], totalprice_index[1]) or 'Free'
#    for key in date_dict.keys():
#        if c_sheet.cell_type(delink_list[it], key) == xlrd.XL_CELL_NUMBER:
#            if c_sheet.cell_value(delink_list[it], key) > 0:
#                print date_dict[key]

print len(delink_list)
