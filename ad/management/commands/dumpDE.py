import cx_Oracle

usrname = 'blade'
usrpwd = 'blade@media'
db_dsn = '''(DESCRIPTION=(ADDRESS_LIST=(ADDRESS=(PROTOCOL=TCP)(HOST=211.94.190.64)(PORT=1521)))(CONNECT_DATA=(SERVER=DEDICATED)(SERVICE_NAME=dart)))'''

db = cx_Oracle.connect(usrname, usrpwd, db_dsn)


cursor = db.cursor()


def get_clicks_by_campaign(campid, flightnumber):
    global cursor
    sql_str = '''
            select flt.id, s.eventtype, s.eventcount, s.startdate 
            from ADMANAGER65.NG_SUM_FIXED s, ADMANAGER65.NG_FLIGHTS flt 
            where s.FLIGHTID = flt.ID  and flt.ORDERID = %s and flt.FLIGHTNUMBER = %d
        '''%(str(campid), flightnumber)
    cursor.execute(sql_str)
    return cursor.fetchall()

def get_flights_by_campaign(campid):
    global cursor
    sql_srt = '''
            select flt.id, flt.NAME, flt.flightnumber 
            from admanager65.ng_flights flt 
            where flt.orderid=%s
        '''%str(campid)
    cursor.execute(sql_srt)
    return cursor.fetchall()

def get_campaign_by_flightid(flg_id):
    sql_srt = '''
            select ins.id, ins.name, adv.name, ins.startdate, ins.enddate, ins.creationdate, ins.exchangeratedate
            from admanager65.ng_insertionorders ins, admanager65.ng_advertisers adv, admanager65.ng_flights flg
            where ins.id = flg.orderid and ins.ADVERTISERID = adv.id and flg.id = %d
        '''%(flg_id)
    cursor.execute(sql_srt)
    return cursor.fetchall()


if __name__ == '__main__':
    cursor.execute(
            '''
    select ins.id, ins.name, adv.name, ins.startdate, ins.enddate, ins.creationdate, ins.exchangeratedate
    from admanager65.ng_insertionorders ins, admanager65.ng_advertisers adv, admanager65.ng_flights flg
    where ins.id = flg.orderid and ins.ADVERTISERID = adv.id and flg.id = 36040
            '''
        )

    for r in cursor.fetchall():
        for i in r:
            print type(i), i
            try:
                print i.date()
            except:
                pass
