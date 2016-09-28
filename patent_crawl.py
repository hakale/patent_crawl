import requests
import json
from bs4 import BeautifulSoup
from collections import OrderedDict
import re
import time
import random
import queue

regex = {
    'patent_name': re.compile(r'(?<=<h1>).*?(?=</h1>)'),
    'serial_num': re.compile(r'(?<=授权公告号：).*?(?=</li>)'),
    'announce_date': re.compile(r'(?<=授权公告日：).*?(?=</li>)'),
    'apply_announ_sria': re.compile(r'(?<=申请公布号：).*?(?=</li>)'),
    'apply_announ_date': re.compile(r'(?<=申请公布日：).*?(?=</li>)'),
    'apply_serial': re.compile(r'(?<=申请号：).*?(?=</li>)'),
    'apply_date': re.compile(r'(?<=申请日：).*?(?=</li>)'),
    'apply_peop': re.compile(r'(?<=专利权人：).*?(?=</li>)'),
    'inventor': re.compile(r'(?<=发明人：).*?(?=</li>)'),
    'address': re.compile(r'(?<=地址：).*?(?=</li>)'),
    'classification_code': re.compile(r'(?<=分类号：).*?(?=</li>)'),
    'class_add_on': re.compile(r'(?<=全部</a><div style="display:none;">).*?(?=</div>)'),
    'abstract': re.compile(r'(?<=</span>).*?(?=</span>)'),
    'src': re.compile(r'(?<=\ssrc=")[^"]+'),
    'apply_p': re.compile(r'(?<=申请人：).*?(?=</li>)'),
    
}

host = 'http://epub.sipo.gov.cn/patentoutline.action'
pageNow = 1
param = {'strWhere': "OPD=BETWEEN['2013.10.01','2013.10.02']", 'pageSize': 10, 'pageNow': pageNow}
user_agent_list = [
        "Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/537.1 (KHTML, like Gecko) Chrome/22.0.1207.1 Safari/537.1"
        "Mozilla/5.0 (X11; CrOS i686 2268.111.0) AppleWebKit/536.11 (KHTML, like Gecko) Chrome/20.0.1132.57 Safari/536.11",
        "Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/536.6 (KHTML, like Gecko) Chrome/20.0.1092.0 Safari/536.6",
        "Mozilla/5.0 (Windows NT 6.2) AppleWebKit/536.6 (KHTML, like Gecko) Chrome/20.0.1090.0 Safari/536.6",
        "Mozilla/5.0 (Windows NT 6.2; WOW64) AppleWebKit/537.1 (KHTML, like Gecko) Chrome/19.77.34.5 Safari/537.1",
        "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/536.5 (KHTML, like Gecko) Chrome/19.0.1084.9 Safari/536.5",
        "Mozilla/5.0 (Windows NT 6.0) AppleWebKit/536.5 (KHTML, like Gecko) Chrome/19.0.1084.36 Safari/536.5",
        "Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/536.3 (KHTML, like Gecko) Chrome/19.0.1063.0 Safari/536.3",
        "Mozilla/5.0 (Windows NT 5.1) AppleWebKit/536.3 (KHTML, like Gecko) Chrome/19.0.1063.0 Safari/536.3",
        "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_8_0) AppleWebKit/536.3 (KHTML, like Gecko) Chrome/19.0.1063.0 Safari/536.3",
        "Mozilla/5.0 (Windows NT 6.2) AppleWebKit/536.3 (KHTML, like Gecko) Chrome/19.0.1062.0 Safari/536.3",
        "Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/536.3 (KHTML, like Gecko) Chrome/19.0.1062.0 Safari/536.3",
        "Mozilla/5.0 (Windows NT 6.2) AppleWebKit/536.3 (KHTML, like Gecko) Chrome/19.0.1061.1 Safari/536.3",
        "Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/536.3 (KHTML, like Gecko) Chrome/19.0.1061.1 Safari/536.3",
        "Mozilla/5.0 (Windows NT 6.1) AppleWebKit/536.3 (KHTML, like Gecko) Chrome/19.0.1061.1 Safari/536.3",
        "Mozilla/5.0 (Windows NT 6.2) AppleWebKit/536.3 (KHTML, like Gecko) Chrome/19.0.1061.0 Safari/536.3",
        "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/535.24 (KHTML, like Gecko) Chrome/19.0.1055.1 Safari/535.24",
        "Mozilla/5.0 (Windows NT 6.2; WOW64) AppleWebKit/535.24 (KHTML, like Gecko) Chrome/19.0.1055.1 Safari/535.24",
        'Mozilla/5.0 (Windows NT 10.0; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/53.0.2785.116 Safari/537.36'
       ]

headers = {'Host': 'epub.sipo.gov.cn',
            'Connection': 'keep-alive',
            'Content-Length': '242',
            'Cache-Control': 'max-age=0',
            'Origin': 'http://epub.sipo.gov.cn',
            'Upgrade-Insecure-Requests': '1',
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/53.0.2785.116 Safari/537.36',
            'Content-Type': 'application/x-www-form-urlencoded',
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
            'Referer': 'http://epub.sipo.gov.cn/patentoutline.action',
            'Accept-Encoding': 'gzip, deflate',
            'Accept-Language': 'zh-CN,zh;q=0.8,en-US;q=0.6,en;q=0.4',
            'Cookie': 'GRIDSUMID=9151d52c660249469c036fcbd787c09a'
}
proxies = {
    'http': 'socks5://127.0.0.1:1080',
    'https': 'socks5://127.0.0.1:1080'
}
r = requests.post(host, data=param)
web_text  = r.text
max_page = re.findall(r'<a>...</a>.*?</a>', web_text)[0]
max_page = int(re.findall(r'(?<=>)\d+(?=<)', max_page)[0])
#print(max_page)
#print(type(max_page))
file = open('xx.json', 'wt', encoding='utf-8')
un_finish_list = list(range(1, max_page + 1))
while un_finish_list:
    pageNow = un_finish_list[0]
    un_finish_list.remove(pageNow)
    time.sleep(1 + random.randint(0, 5))
    headers['User-Agent'] = random.choice(user_agent_list)
    param = {'strWhere': "OPD=BETWEEN['2013.10.01','2013.10.02']", 'pageSize': 10, 'pageNow': pageNow}
    try:
        r = requests.post(host, data=param, headers=headers)
    except requests.exceptions.ConnectionError:
        time.sleep(1 * 60)
        try:
            r = requests.post(host, data=param, headers=headers)
        except requests.exceptions.ConnectionError:
            un_finish_list.append(pageNow)
            print(pageNow)
            continue
    web_text  = r.text
    soup = BeautifulSoup(web_text, "lxml")
    for i in soup.find_all('div', class_="cp_box"):
        patent = OrderedDict()
        text = re.sub(r'\n', '', str(i))
        patent['专利名称'] = regex['patent_name'].findall(text)
        patent['授权公告号'] = regex['serial_num'].findall(text)
        patent['授权公告日'] = regex['announce_date'].findall(text)
        patent['申请公布号'] = regex['apply_announ_sria'].findall(text)
        patent['申请公布日'] = regex['apply_announ_date'].findall(text)
        patent['申请号'] = regex['apply_serial'].findall(text)
        patent['申请日'] = regex['apply_date'].findall(text)
        patent['申请人'] = regex['apply_p'].findall(text)
        patent['专利权人'] = regex['apply_peop'].findall(text)
        patent['发明人'] = regex['inventor'].findall(text)
        patent['地址'] = regex['address'].findall(text)
        patent['分类号'] = regex['classification_code'].findall(text)
        patent['分类号附加数据'] = regex['class_add_on'].findall(text)
        #patent['代理人'] = regex['patent_name'].findall()
        patent['摘要'] = regex['abstract'].findall(text)
        patent['缩略图'] = regex['src'].findall(text)
        for key, value in patent.items():
            if value:
                patent[key] = re.sub(r'<.*?>', '', patent[key][0].strip())
            else:
                patent[key] = None
        #print(type(i))
        result = json.dumps(patent,ensure_ascii=False, sort_keys=True, indent=4)
        print(result, file=file)
        print(patent['申请号'])
    file.flush()
file.close()