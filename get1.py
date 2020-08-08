import requests,json
from bs4 import BeautifulSoup

url = 'https://lol.moa.tw/Statistic/version/450/1015'
headers = {'user-agent': 'Mozilla/5.0 (Macintosh Intel Mac OS X 10_13_4) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/66.0.3359.181 Safari/537.36'}
res = requests.get(url,headers=headers)
soup = BeautifulSoup(res.text, 'html.parser')
D = {}
for i in range(1,150):
    s = soup.select('#table-text > tbody > tr:nth-child({})'.format(str(i)))
    data = s[0].text.split()
    D[data[0]]=data[-1]

with open('win_rate.json','w',encoding='utf8') as g:
    json.dump(D,g,ensure_ascii=False,indent=4)