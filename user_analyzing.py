from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.keys import Keys
from opencc import OpenCC
import requests,json
from scipy import stats

with open('hero_kda.json',encoding='utf8') as sgs:
    hero_kda = json.load(sgs)

def player(name):
    try:
        url = "https://matchhistory.tw.leagueoflegends.com/zh/#page/landing-page"
        options = webdriver.ChromeOptions()
        options.add_argument('disable-infobars')
        options.add_argument('--window-size=1920,1080')
        options.add_argument("--headless")
        driver = webdriver.Chrome(options=options)
        driver.header_overrides = {
            'Referer': 'referer_string',
        }
        driver.get(url)
        driver.implicitly_wait(10)
        input_box = driver.find_element_by_xpath('//*[@id="player-search-4-name"]')
        input_box.click()
        input_box.send_keys(name)
        input_box.send_keys(Keys.RETURN)
        driver.implicitly_wait(10)

        map_type = [x.text for x in driver.find_elements_by_class_name('map-mode-mode')]
        game_type = ["一般" if x.text=="" else "排位" for x in driver.find_elements_by_class_name('map-mode-queue') ]
        champ = [x.text for x in driver.find_elements_by_class_name('champion-nameplate-name')]
        kda = [x.text.split('/') for x in driver.find_elements_by_class_name('kda-plate-kda')]
        #during = [x.text for x in driver.find_elements_by_class_name('date-duration-duration')]
        #win = driver.find_elements_by_class_name('game-summary-victory')
        driver.quit()
        s = "\n"
        my_kda=[]
        for i in range(len(map_type)):
            s+="{} {} {} {}\n".format(map_type[i],game_type[i],champ[i],'/'.join(kda[i]))

        for x,y in zip(kda,champ):
            my_kda.append(round((float(x[0])+float(x[2]))/(float(x[1])+1)-hero_kda[y],2))

        tStat, pValue = stats.ttest_ind( my_kda, [float(0) for _ in range(len(map_type))], equal_var = False) #run independent sample T-Test
        print(tStat, pValue)
        s+='-------------\n[隊友分析]\n'
        if pValue<0.01:
            if tStat>0: s+="狀態: 優質隊友\n提醒: 小心搶頭、保KDA"
            else : s+="狀態: 雷包\n提醒: 建議跳GAME"
        elif pValue<0.1:
            if tStat>0: s+="狀態: 好隊友\n提醒: 無"
            else : s+="狀態: 有點菜\n提醒: 可能會戳"
        else:
            if tStat>0: s+="狀態: 普通\n提醒: 不足以影響成敗"
            else : s+="狀態: 不穩定\n提醒: 不足以影響成敗"
        print(s)
    except Exception as e:
        print(e)


player('alankingdom')