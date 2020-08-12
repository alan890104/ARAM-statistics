import requests,json,re
from bs4 import BeautifulSoup
from multiprocessing import Pool

class hero_kda_winrate():
    with open('CH2EN.json',encoding='utf8') as gsdgf:
        CH2EN = json.load(gsdgf)

    def web(self,name):
        url = "https://www.leagueofgraphs.com/zh/champions/stats/{}/silver/aram".format(self.CH2EN[name])
        print(url)
        headers = {'user-agent': 'Mozilla/5.0 (Macintosh Intel Mac OS X 10_13_4) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/66.0.3359.181 Safari/537.36'}
        res = requests.get(url,headers=headers)
        soup = BeautifulSoup(res.text, 'html.parser')
        k_d_a = "#mainContent > div:nth-child(2) > div:nth-child(2) > div.box.box-padding.number-only-chart.text-center > div.number"
        win_rate = "#mainContent > div:nth-child(1) > div:nth-child(2) > div > div"
        try:
            K = soup.select(k_d_a)[0].text.replace('/',"").split()
            F = soup.select(win_rate)[0].text.split()[0]
            r_list = [name]
            r_list.extend(K)
            r_list.append(F)
            print(r_list)
            return r_list
        except Exception as e:
            print(e)

    def hero_kda_winrate_main(self):
        Champion = []
        for i in self.CH2EN:
            Champion.append(i)
        pool = Pool()
        ans = pool.map(self.web,Champion)
        pool.close()  
        pool.join()
        KD = {}
        WD = {}
        for x in ans:
            try:
                KD[x[0]] = round(( float(x[1])+float(x[3]) )/ (float(x[2])+1),2)
                WD[x[0]] = str(x[4])
            except:
                pass
        with open('hero_kda.json','w',encoding='utf8') as ff:
            json.dump(KD,ff,ensure_ascii=False,indent=4)
        with open('win_rate.json','w',encoding='utf8') as gg:
            json.dump(WD,gg,ensure_ascii=False,indent=4)

if __name__=='__main__':
    HO = hero_kda_winrate()
    HO.hero_kda_winrate_main()