#   coding=gb2312
import xlrd
import glob
import  re 
from os import path, walk, tmpnam, mkdir, getcwd
import datetime
import cPickle

DATAPATH   = './data'
OUTPUTPATH = './temp_dat'

__cur_xls_fn = ''

def get_base_row(sh):
    for i in xrange(sh.nrows):
        tl = sh.row_values(i)
        if (u'单位' in tl) and (u'投放量' in tl):
            return i
    else:
        return -1


def get_end_row(sh):
    dl = get_date_dct(sh).keys()
    dl.sort()
    col = dl[-1] + 1
    for i in xrange(sh.nrows-1, get_base_row(sh) +2 , -1):
        if type(0.1) == type(sh.cell_value(i, col)):
            return i
        else:
            continue
    else:
        return -1


def get_base_col(sh):
    base_row = sh.row_values(get_base_row(sh))
    for n, col in enumerate(base_row):
        if col != '':
            return n


def get_date_dct(sh):
    '''
        return a dict, column as key, a tuple: ((year, month), day, weekday) as value.
    '''
    __s_date = datetime.date(1899, 12, 31).toordinal() - 1
    def _getdate(date):
        if isinstance(date, float):
            date = int(date)
        d = datetime.date.fromordinal(__s_date + date)
        return (d.year, d.month)


    base_row = get_base_row(sh)
    dates = range(1, 32)

    c2d_dct = {}

    for col in xrange(sh.ncols):
        wk_day = sh.cell_value(base_row+1, col)
        day    = sh.cell_value(base_row+2, col) 
        if  day in dates:
            month_col = col
            while '' == sh.cell_value(base_row, month_col):
                month_col -= 1
            
            _month = sh.cell_value(base_row, month_col)
            try:
                c2d_dct[col] = (_getdate(_month), int(day), upper(wk_day))
            except:
                month = re.findall(r'\d+', _month)
                if month:
                    month = month[-1]
                    c2d_dct[col] = ((None, int(month)), int(day), upper(wk_day))
                else:
                    c2d_dct[col] = ((), int(day), upper(wk_day))

    return c2d_dct


def get_flight_dct(sh, pth=None):
    flt_dct = {}
    try: date_dct = get_date_dct(sh)
    except: raise Exception('DATE infomation could not be found.')
    base_row = get_base_row(sh)
    base_col = get_base_col(sh)

    if base_row < 0:
        raise Exception('BASE_LINE was not found')

    flt_dct['flights'] = []

    def _find_upwards(rw, cl):
        v = sh.cell_value(rw, cl)
        while '' == v:
            rw -= 1
            v = sh.cell_value(rw, cl)
        return v

    for row in xrange(base_row+3, sh.nrows):
        tmp_dct = {'URLs':[], 'DATEs':[]}

        for col in xrange(base_col, sh.ncols):
            if col in date_dct:
                tmp_dct['DATEs'].append(date_dct[col])
                continue # next col
            k = sh.cell_value(base_row, col)
            v = sh.cell_value(row, col)

            if u'投放量' == k and '' == v:
                break


            if k in tmp_dct:
                raise Exception("adding SAME FILED '%s' to flight dict."%k.encode('gb2312'))

            try:
                if u'网站' == k:
                    tmp_dct[k] = _find_upwards(row, col)
                elif k.startswith(u'折后总价'):
                    tmp_dct[u'折后总价'] = v
                elif k.startswith(u'刊例单价'):
                    tmp_dct[u'刊例单价'] = v
                elif k.startswith(u'刊例总价'):
                    tmp_dct[u'刊例总价'] = v
                elif k.startswith(u'网站总价'):
                    tmp_dct[u'网站总价'] = v
                elif k.startswith(u'折后单价') or k.startswith(u'折后价格'):
                    tmp_dct[u'折后单价'] = v
                elif u'广告位置' == k:
                    tmp_dct[k] = _find_upwards(row, col)
                elif k != '': 
                    tmp_dct[k] = v

            except:
                pass


            try: 
                if re.match(r'^http', v, re.I):
                    tmp_dct['URLs'].append(v)
            except:
                pass

        else:
            if not u'网站' in tmp_dct:
                tmp_bw = sh.row_values(base_row) 
                try:    tmp_col = tmp_bw.index(u'频道')
                except: tmp_col = tmp_bw.index(u'广告位置') 

                if 0 == tmp_col:
                    raise Exception('SITE was not found')

                tmp_col -= 1
                tmp_dct[u'网站'] = _find_upwards(row, tmp_col)
            
            flight_number = row - base_row + 1
            flt_dct['flights'].append((flight_number, tmp_dct))


    flt_dct['extra'] = [sh.name]
    for row in xrange(0, base_row):
        for col in xrange(0, sh.ncols):
            cur_value = sh.cell_value(row, col)
            if 0 != len(cur_value):
                flt_dct['extra'].append(cur_value)  #cur_value must be a Unicode string.

    if pth:
        flt_dct['name'] = path.splitext(
                    path.split(pth)[-1]
                )[0]                                # remember to APPEND year's infomation later ...
        flt_dct['extra'].append(path.realpath(pth)) # year's infomatino maybe here ...


    return flt_dct


def foreach_xls(func, msg='message', datapath=DATAPATH):
    '''
        func: callback function, accept one argument.

        this function only be used in UNIT TEST.
    '''
    global __cur_xls_fn
    log = open('./Exceptions.log', 'a')
    log.write('\n%s\n'%datetime.datetime.now().isoformat())
    excp_sum = 0
    file_sum = 0
    for t, d, f in walk(datapath):
        for i in f:
            if re.match(r'.*\.xls$', i, re.I):
                file_sum += 1
                try:
                    __cur_xls_fn = path.join(t, i)
                    #print '%s\n%s'%(__cur_xls_fn, msg)
                    sh = xlrd.open_workbook(__cur_xls_fn).sheets()[0]
                    func(sh)
                except Exception, e:
                    excp_sum += 1
                    log.write('\t%s\n\tException:\n\t\t%s\n\n'%(__cur_xls_fn, e.message))
                print
    log.write('%d erros in %d files\n'%(excp_sum, file_sum))


def get_all_dict(datapath=DATAPATH, ofpath=OUTPUTPATH):
    '''
        get data-dicts of all xls files.
    '''
    ofpath = path.realpath(ofpath)
    dt_dir = datetime.datetime.now().isoformat().replace(':', '-')
    mkdir('%s/%s'%(ofpath, dt_dir))

    def _get(sh):
        global __cur_xls_fn
        dct = get_flight_dct(sh, pth=__cur_xls_fn)
        ofname = path.join(ofpath, dt_dir, tmpnam().replace('\\',''))

        cPickle.dump(dct, open(ofname, 'wb'))

    foreach_xls(_get)


def get_campaigns(ofpath=OUTPUTPATH):
    campaigns = []

    def _is_valid_campaign(t_dict):
        for flt_num, flt in t_dict['flights']:
            for url in flt['URLs']:
                tmp_url = re.search(r'campaignid=(\d+)', url, re.I)
                if tmp_url:
                    t_dict['CmpgnID'] = int(tmp_url.group(1))
                    return True
        else:
            return False

    for t, d, f in walk(ofpath):
        for i in f:
            fn = path.join(t, i)
            print fn
            tmp_dict = cPickle.load(open(fn, 'rb'))
            if _is_valid_campaign(tmp_dict):
                campaigns.append(tmp_dict)

    return campaigns


def test_get_end_row():
    def test(sh):
        print get_end_row(sh)
        raw_input()
    foreach_xls(test, 'end_row')


def test_get_flight_dct():
    def test(sh):
        dct = get_flight_dct(sh)
        #test for get URLs
        for n, row in dct['flights']:
            if 'URLs' in row:
                for url in row['URLs']:
                    print url
                else:
                    pass
        for e in dct['extra']:
            print e
        print 
        
    foreach_xls(test, 'FLIGHT dict')


def test_get_date_dct():
    def test(sh):
        print get_date_dct(sh)
    foreach_xls(test, 'DATE dict')


def test_get_base_row():
    def test(sh):
        print get_base_row(sh)
    foreach_xls(test, 'base ROW number')


if __name__ == '__main__':
    import sys

    #test_get_date_dct()
    #test_get_flight_dct()
    #test_get_end_row()
    import sys

    if 'd' in sys.argv:
        get_all_dict()

