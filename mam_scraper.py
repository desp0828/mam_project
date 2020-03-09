#!/usr/bin/env python
# coding: utf-8

# In[1]:


import requests
from bs4 import BeautifulSoup
import numpy as np

import datetime
import os
import sys
import pymssql
import subprocess

import re
import urllib  
import urllib2


# In[2]:


headers={
    'authority':'www.ccilindia.com',
    'method':'POST',
    'path': '/FPI_ARCV.aspx',
    'scheme': 'https',
    'accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.9',
    'accept-encoding': 'gzip, deflate, br',
    'accept-language': 'en-GB,en-US;q=0.9,en;q=0.8,zh-CN;q=0.7,zh;q=0.6',
    'cache-control': 'max-age=0',
    'content-length': '29709',
    'content-type': 'application/x-www-form-urlencoded',
    'origin': 'https://www.ccilindia.com',
    'referer': 'https://www.ccilindia.com/FPI_ARCV.aspx',
    'sec-fetch-mode': 'navigate',
    'sec-fetch-site': 'same-origin',
    'sec-fetch-user': '?1',
    'upgrade-insecure-requests': '1',
    'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/79.0.3945.130 Safari/537.36'
    
}
postdata = {
    '__EVENTTARGET': 'drpArchival',
    '__EVENTARGUMENT':'', 
    '__LASTFOCUS':'', 
    '__VIEWSTATE': '',
    '__VIEWSTATEGENERATOR': 'E08232C2',
    '__VIEWSTATEENCRYPTED':'', 
    '__EVENTVALIDATION': '',
    'drpArchival': 'NA'
}

datels=[]
date_file = ""
cwd = ""
pagels=['grdFPISWH$ctl19$ctl00','grdFPISWH$ctl19$ctl01',
        'grdFPISWH$ctl19$ctl02','grdFPISWH$ctl19$ctl03','grdFPISWH$ctl19$ctl014']

def changeHiddenValue(soup):      #each time we post to the url, these value must be stored for next time post
    global postdata
    vietmp=soup.find_all(id="__VIEWSTATE")[0]['value']
    evetmp=soup.find_all(id="__EVENTVALIDATION")[0]['value']
    postdata['__VIEWSTATE'] = vietmp
    postdata['__EVENTVALIDATION'] = evetmp 


def getData(date,page):
    global postdata   
    postdata['drpArchival'] = date
    postdata['__EVENTTARGET'] = page
    url = 'https://www.ccilindia.com/FPI_ARCV.aspx'
    data = requests.post(url, headers=headers, data=postdata).text
    soup = BeautifulSoup(data,'html.parser')
    changeHiddenValue(soup)
    sec = soup.findAll("table",{"id":"grdFPISWH"})
    tab = sec[0]
    kp=[]
    for tr in tab.findAll('td'):
        kp.append(tr.getText())
    kp=kp[5:-1]
    tb=[]
    for i in range(0,len(kp),5):
        tbi = kp[i:i+5]
        date_format = datetime.datetime.strptime(date, '%d-%b-%Y').date()
        tbi.append(date_format)
        tb.append(tbi)
    return(tb)




def newTable():
    global date_file
    global datels
    global cwd
    global pagels
    #date file
    fp = open(date_file,'w+')
    for each in datels: 
        fp.write(each)
        fp.write('\n')
    fp.close()
    #sw_data file
    sw_data_file = cwd + '/sw_data.txt'
    fw = open(sw_data_file,'w+')
    for i in datels:
        for j in pagels:
            push_table = getData(i,j)
            for each in push_table:
                rowtxt = '{},{},{},{},{},{}'.format(each[0],each[1],each[2],each[3],each[4],each[5])
                fw.write(rowtxt)
                fw.write('\n')
    fw.close()
         



def addTable(rec_date):
    global datels
    global cwd
    global pagels
    #date file
    fp = open(date_file,'w+')
    for each in datels: 
        fp.write(each)
        fp.write('\n')
    fp.close()
    #new_sw_data file    
    new_sw_data_file = cwd + '/sw_data_add.txt'
    fn = open(new_sw_data_file,'w+')
    for each_rec_date in rec_date:
        for j in pagels:
            push_table = getData(each_rec_date,j)
            for each in push_table:
                rowtxt = '{},{},{},{},{},{}'.format(each[0],each[1],each[2],each[3],each[4],each[5])
                fn.write(rowtxt)
                fn.write('\n')
    fn.close()
        
def get_hiddenvalue(url):         #we firstly store the value gotten by 'urllib2.Request', and use it for the first time post
    request=urllib2.Request(url)
    reponse=urllib2.urlopen(request)
    resu=reponse.read()
    VIEWSTATE =re.findall(r'<input type="hidden" name="__VIEWSTATE" id="__VIEWSTATE" value="(.*?)" />', resu,re.I)
    EVENTVALIDATION =re.findall(r'input type="hidden" name="__EVENTVALIDATION" id="__EVENTVALIDATION" value="(.*?)" />', resu,re.I)
    return VIEWSTATE[0],EVENTVALIDATION[0]

def test():
    global postdata 
    global date_file
    global datels
    global cwd
    global pagels
    url = 'https://www.ccilindia.com/FPI_ARCV.aspx'

    vie,eve=get_hiddenvalue(url)
    postdata['__VIEWSTATE']=vie
    postdata['__EVENTVALIDATION']=eve
    data = requests.post(url, headers=headers, data=postdata).text     #the first time post
    soup = BeautifulSoup(data,'html.parser')
    changeHiddenValue(soup)
    date = soup.findAll("option")

    #check whether the website is updated, check the date list is enough
    for each in date:
        datels.append(each.getText())
    datels=datels[1:]
    cwd = os.getcwd()
    date_file = cwd + '/date.txt'
    date_exist = os.path.isfile(date_file)
    if date_exist == True:
        fp = open(date_file,'r+')
    else:
        fp = open(date_file,'w+')
    datetx = fp.readlines()
    fp.close()
    date_pre = []
    for each in datetx:
        each = each.replace('\n','')
        date_pre.append(each)
    if date_pre == datels:     #there is no updates
        return('None')
    elif len(date_pre) == 0:       #the first time we run this program, add all data to sql
        newTable()
        return('sw_data.txt')
    else:                    #there are some updates, only insert updates
        rec_date=list(set(datels).difference(set(date_pre)))
        addTable(rec_date)
        return('sw_data_add.txt')


    
if __name__=="__main__":
    upload_file = test()
    if upload_file == 'None':
        sys.exit()
    else:
        BCPin="bcp <tablename> in " + upload_file + " -S <servername/ip> -U <your_username> -P <your_password> -f mam.fmt"
        result_code=subprocess.call(BCPin,shell=True)
        print (result_code)

#db.close()

