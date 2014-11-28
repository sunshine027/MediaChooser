#coding=utf-8

from string import *
import unicodedata

def  get_hz_string_width(text):  

     s = 0   
     for  ch  in  text:  
         if  isinstance(ch, unicode):  
             if  unicodedata.east_asian_width(ch)!=  'Na' :   
                 s += 2   
             else :  
                 s += 1   
         else :  
             s += 1   
     return  s  


def  get_hz_sub_string(text,startat,sub_len= None ):  

     s = []  
     pos = 0   
     for  ch  in  text:  
         if  pos >= startat:  
             s.append(ch)  
         if  isinstance(ch, unicode):  
             if  unicodedata.east_asian_width(ch)!=  'Na' :   
                 pos += 2   
             else :  
                 pos += 1   
         else :  
             pos += 1   
         if  sub_len!= None   and  get_hz_string_width( '' .join(s))>=sub_len:  
             break      
     return   '' .join(s)


def insert_line_feed(my_str,interval,line_feed= "<br>" ):  

     if  len(my_str)== 0 :   
         return  ""  

     n = int((get_hz_string_width(my_str)-1 )/interval)+ 1   
     str_list = []  
     k = 1   
     pos_start = 0   
     while  k <= n:  
         sub_str = get_hz_sub_string(my_str,pos_start,interval)   
         str_list.append(sub_str)  
         k = k + 1   
         pos_start = pos_start + get_hz_string_width(sub_str)  

     return  line_feed.join(str_list)


def wrap_text_block(text,line_length,do_trim=True):

    if len(text) > 15:
        text = text[:15]
    if do_trim:
        str_list = split(text.rstrip(),'<br>')
    else:    
        str_list = split(text,'<br>')

    #检测末尾空行的开始位置
    text_to_line = -1
    if do_trim:
        i = len(str_list)-1
        while i > 0:
            line_str = str_list[i]
            if len(line_str.strip())==0:
                text_to_line = i
                i -= 1
            else:
                break     

    new_str_list = []
    i = 0
    for obj in str_list:
        if do_trim and i == text_to_line:
            break
        new_str_list += split(insert_line_feed(obj,line_length),'<br>')
        i += 1

    return u''+'<br>'.join(new_str_list)
    
def wrap_text(l) :
    return [wrap_text_block(i,4) for i in l]
