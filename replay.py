from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.keys import Keys
import requests,json,time,datetime
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

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

def player_datail(name):
    url = "https://matchhistory.tw.leagueoflegends.com/zh/#page/landing-page"
    options = webdriver.ChromeOptions()
    options.add_argument('disable-infobars')
    options.add_argument('--window-size=1920,1080')
    options.add_argument("--headless")
    options.add_argument("--incognito")
    driver = webdriver.Chrome(options=options)
    driver.get(url)
    driver.implicitly_wait(10)
    input_box = driver.find_element_by_xpath('//*[@id="player-search-4-name"]')
    input_box.click()
    input_box.send_keys(name)
    input_box.send_keys(Keys.RETURN)
    driver.implicitly_wait(10)


    reply = '\n[玩家: {}]\n\n'.format(name)
    RAN = range(5)
    for ii in RAN:
        stri = str(ii+1)+'.\n'
        block = driver.find_elements_by_class_name('game-summary')
        #print(block)
        champ_name = block[ii].find_element_by_class_name('champion-nameplate-name').text
        mode = block[ii].find_element_by_class_name('mode').text
        game_during = block[ii].text.split()[-2]
        x = datetime. datetime. strptime(game_during, "%M:%S")
        mins = datetime.timedelta(minutes=x.minute,seconds=x.second).total_seconds()/60
        #block[ii].click()
        driver.execute_script("arguments[0].click();", block[ii])
        """ for data in block:
            print(data.text.split())
            data.click() """
        stats = driver.find_elements_by_xpath("//*[contains(text(), '各項數據')]")[0]
        driver.execute_script("arguments[0].click();", stats)
        #stats.click()
        group_kills = float(driver.find_elements_by_class_name('kills')[2].text)
        You = {}
        summory = driver.find_elements_by_class_name('current-user')
        current_user = summory[2:]
        for label,num_data in zip(driver.find_elements_by_class_name('grid-label'),current_user):
            You[label.text] = num_data.text.replace('-','0')

        OUT = {}
        You['KDA'] = [int(x) for x in You['KDA'].split('/')]
        OUT['英雄'] = champ_name
        OUT['地圖'] = mode
        OUT['擊殺／死亡／助攻'] = You['KDA']
        OUT['每分鐘輸出']=str(round(float(You['對英雄造成總傷害'][:-1])/mins,2))+'k'
        OUT['每分鐘擊殺士兵'] = str(round((int(You['擊殺士兵'])+int(You['擊殺中立士兵數']))/mins,2))+'隻'
        """ OUT['對英雄造成物理傷害']=You['對英雄造成物理傷害']
        OUT['對英雄造成魔法傷害']=You['對英雄造成魔法傷害']
        OUT['對英雄造成真實傷害']=You['對英雄造成真實傷害'] """
        OUT['治療傷害']=You['治療傷害']
        OUT['受到傷害']=You['受到傷害']
        try:
            OUT['擊殺參與率'] = str(round(  float(You['KDA'][2]+You['KDA'][0])*100/group_kills,2 ))+'%'
        except:
            OUT['擊殺參與率'] = "0%"
        if mode=='召喚峽谷':
            try:   
                OUT['野區入侵率'] = str(round((int(You['擊殺中立士兵數'])-int(You['在己方野區擊殺中立野怪']))*100/int(You['擊殺中立士兵數']),2))+'%'
            except:
                OUT['野區入侵率'] = "0%"
        OUT['每分鐘擊殺士兵'] = str(round((int(You['擊殺士兵'])+int(You['擊殺中立士兵數']))/mins,2))+'隻'
        OUT['金錢使用率'] = str(round(float(You['花費金錢'][:-1])/float(You['獲得金錢'][:-1])*100,2))+'%'
        if mode=='召喚峽谷':
            OUT['視野布置'] = str(int(You['放置偵查守衛'])*3+int(You['摧毀偵查守衛'])*2)+'分'
        
        for x in OUT:
            if x=='擊殺／死亡／助攻':stri+="{:　<9}{}/{}/{}\n".format(x,OUT[x][0],OUT[x][1],OUT[x][2])
            else: stri+="{:　<9}{}\n".format(x,OUT[x])
        reply+=stri
        if ii<len(RAN):reply+="\n"
        driver.execute_script("window.history.go(-1)")
        driver.implicitly_wait(10)
    driver.quit()
    
    print(reply)
    lineNotifyMessage(reply.rstrip())
        

player_datail('alankingdom')