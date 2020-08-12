import requests,json,re
from bs4 import BeautifulSoup
from multiprocessing import Pool

class bp():
    with open('CH2EN.json',encoding='utf8') as gsdgf:
        CH2EN = json.load(gsdgf)

    def web(self,name):
        url = "https://www.leagueofgraphs.com/zh/champions/stats/{}".format(self.CH2EN[name])
        print(url)
        headers = {'user-agent': 'Mozilla/5.0 (Macintosh Intel Mac OS X 10_13_4) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/66.0.3359.181 Safari/537.36'}
        res = requests.get(url,headers=headers)
        soup = BeautifulSoup(res.text, 'html.parser')
        PICK = "#mainContent > div:nth-child(1) > div:nth-child(1) > div > div"
        BAN = "#mainContent > div:nth-child(1) > div:nth-child(3) > div > div"
        try:
            P = soup.select(PICK)[0].text.split()[0]
            B = soup.select(BAN)[0].text.split()[0]
            r_list = [name]
            r_list.append(P)
            r_list.append(B)
            print(r_list)
            return r_list
            
        except Exception as e:
            print(e)
        
    def bp_main(self):
        Champion = []
        for i in self.CH2EN:
            Champion.append(i)
        pool = Pool()
        ans = pool.map(self.web,Champion)
        pool.close()  
        pool.join()
        BANN = {}
        PICKK = {}
        for x in ans:
            try:
                PICKK[x[0]] = x[1]
                BANN[x[0]] = x[2]
            except:
                pass

        o_BAN = {k:v for k,v in sorted(BANN.items(), key=lambda item: float(item[1].replace('%','')),reverse=True)}
        o_PICK = {k:v for k,v in sorted(PICKK.items(), key=lambda item: float(item[1].replace('%','')),reverse=True)}

        with open('pick.json','w',encoding='utf8') as ff:
            json.dump(o_PICK,ff,ensure_ascii=False,indent=4)
        with open('ban.json','w',encoding='utf8') as gg:
            json.dump(o_BAN,gg,ensure_ascii=False,indent=4)


if __name__=='__main__':
    name = bp()
    name.bp_main()