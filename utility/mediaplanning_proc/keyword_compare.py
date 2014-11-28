#! /usr/bin/env python
#coding=utf-8

from pyExcelerator import *
import xlrd 
#import time
#import sys

#start_time = time.time()

book1 = xlrd.open_workbook('first.xls')
book2 = xlrd.open_workbook('second.xls')

newbook = Workbook()
newsheet = newbook.add_sheet('compare result')

b1_data = []
b2_data = []

sheet_order = 1
for sheet_name in book1.sheet_names():
    if sheet_order == 3:
        sheet = book1.sheet_by_name(sheet_name)
        for i in xrange(sheet.nrows):
            b1_data.append(sheet.row_values(i)[0])
    sheet_order += 1
    
sheet_order = 1
for sheet_name in book2.sheet_names():
    if sheet_order == 3:
        sheet = book2.sheet_by_name(sheet_name)
        for i in xrange(sheet.nrows):
            b2_data.append(sheet.row_values(i))
    sheet_order += 1
    
column_num = len(b2_data[0])
for i in xrange(len(b2_data)):
    if b2_data[i][0] in b1_data:
        for j in xrange(column_num):
            newsheet.write(i, j, b2_data[i][j])
    else:
        for j in xrange(column_num):
            newsheet.write(i, j+column_num, b2_data[i][j])

newbook.save('compare_results.xls')

#print time.time() - start_time