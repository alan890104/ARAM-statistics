from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.keys import Keys
from opencc import OpenCC
import requests

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
        kda = [x.text for x in driver.find_elements_by_class_name('kda-plate-kda')]
        #money = [x.text for x in driver.find_elements_by_class_name('income-gold')]
        #during = [x.text for x in driver.find_elements_by_class_name('date-duration-duration')]
        win = driver.find_elements_by_class_name('game-summary-victory')
        #date = [x.text for x in driver.find_elements_by_class_name('date-duration-date')]
        driver.quit()
        s = ""
        for i in range(len(map_type)):
            s+="{} {} {} {}\n".format(map_type[i],game_type[i],champ[i],kda[i])
        s+="[{}場平均勝率為{}]".format(len(champ),str(round((len(win)/len(champ))*100,2))+"%")
        print(s)
        return s
    except Exception as e:
        print(e)

def lineNotifyMessage(msg, picURI=None):
    url = "https://notify-api.line.me/api/notify"
    headers = {
        "Authorization": "Bearer " + 'sBpS9wjlA9EeY1pmntt3zloI7ewWNfDqfFP67A5o3cI'
    }
    payload = {'message': msg}
    if picURI!=None:
        files = {'imageFile': open(picURI, 'rb')}
        requests.post(url, headers = headers, params = payload, files = files)
    else:
        requests.post("https://notify-api.line.me/api/notify", headers = headers, params = payload)
