#!/usr/bin/env python2
# -*- coding: latin-1 -*-


import sys
reload(sys)
sys.setdefaultencoding('UTF8')

def o(x):
    s=""
    for i in x:s+=chr(int(15.968**2+0.56)-ord(i));
    s=s.decode("latin-1");s = s.replace("<`"," ");s = s.replace("<a","!");s = s.replace("<y","9");s = s.replace("<v","6");s = s.replace("<p","0");s = s.replace("<q","1");s = s.replace("<w","7");s = s.replace("<r","2");s = s.replace("<s","3");s = s.replace("<t","4");s = s.replace("<u","5");s = s.replace("=","");s = s.replace("<z",":");s = s.replace("<o","/");s = s.replace("<n",".");s = s.replace("<m","-");s = s.replace("< ","?");s = s.replace("<}","=");s = s.replace("<e","%");s = s.replace("<f","&");return str(s)

r=o

print o("Ñ")
