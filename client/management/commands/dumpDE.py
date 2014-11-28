#encoding=utf8
import pyodbc

de_db = pyodbc.connect('DRIVER={Oracle};SERVER=211.94.190.64;DATABASE=dart;UID=mediachooser_read;PWD=read_mediachooser;')

#db = cx_Oracle.connect(usrname, usrpwd, db_dsn)


#cursor = de_db.cursor()



def get_from_ng_sum_fixed_click(flight_id,startdate):
    #global cursor
    cursor = de_db.cursor() 
    sql_str = 'select CLICKS from admanager65.ng_sum_fixed_h where  flightid =%s and startdate =to_date(\'%s\',\'YYYY-MM-DD\')' % (flight_id,startdate)
    
    try:
	cursor.execute(sql_str)
    	print 'sql_srt',sql_str
	#print ''cursor.fetchall()
    	return cursor.fetchone()
    except:
	return None 







