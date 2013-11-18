#/usr/bin/python

import binascii
import ConfigParser
#import httplib2
import urllib2
import urllib
import smtplib
import uuid
from email.mime.text import MIMEText
import cookielib
import json

def send_mail(to_list,sub,content):
      '''
     send_mail("aaa@126.com","sub","content")
     '''
      me='accounts-noreply@playsnail.com'
      msg = MIMEText(content)
      msg['Subject'] = sub
      msg['From'] = me
      msg['To'] = to_list
      try:
         s = smtplib.SMTP()
 #       s.set_debuglevel(True)
         s.connect(config.get('MAIL','host'),25)        
         s.starttls()
         s.login(config.get('MAIL','user'),config.get('MAIL','pass'))
         s.sendmail(me, to_list.split(','), msg.as_string())
         s.close()
         return True
      except Exception, e:
         print str(e)
         return False

def gen_rundom():
     uid = str(uuid.uuid4())
     uid_str = uid.split('-')[0]
     return uid_str

def common_url_test(url,args_data,opener,errorUrls):
    if len(args_data) == 0:
        resp = opener.open(url)
    else:
        encode_args_data = urllib.urlencode(args_data)
        resp = opener.open(url,encode_args_data)
    result_str = resp.read()
    print 'result :', result_str ,'get url :',resp.geturl(),' args:',args_data
    if parse_rslt(result_str) == 'failiure':
       print 'failiure' 
       errorUrls.add(url)
    return opener

def parse_rslt(rslt):
    rslt_dic = json.loads(rslt)
    if 0 != rslt_dic['code'] and 1 != rslt_dic['code'] and 2 != rslt_dic['code']:
        return 'failiure'
    else:
        return 'OK'

def test_register(opener,errorUrls):
    config.read('account.cfg')
    url = config.get('REGISTER_URL','url')
    args = config.get('REGISTER_URL','args')
    args = eval(args)
    uid_str = gen_rundom()
    c_account = uid_str + '@snail.com'
    s_nick_name = uid_str
    args.update({'cAccount':c_account})
    args.update({'sNickname':s_nick_name})
    common_url_test(url,args,opener,errorUrls)
     
        
if __name__ == '__main__':
     config = ConfigParser.RawConfigParser()
     config.read('monitor.cfg')
     sections = config.sections()
     errorUrls = set([])
     cj = cookielib.CookieJar()
     opener = urllib2.build_opener(urllib2.HTTPCookieProcessor(cj))
     for section in sections:
        dic = config.items(section)
        url = dic[0][1]
        args_data = eval(dic[1][1])
        common_url_test(url,args_data,opener,errorUrls)
     test_register(opener,errorUrls)
     if len(errorUrls) > 0:
        message = '[ERROR] error urls in this automation test : ' + ','.join(errorUrls)
        addresses = config.get('MAIL','address')
        subject = 'News from playsnail monitor'
        send_mail(addresses,subject,message)
