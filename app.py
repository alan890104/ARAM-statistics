# -*- coding: UTF-8 -*-
from flask import Flask, request, abort
import psycopg2
from bs4 import BeautifulSoup
import requests
from linebot import (LineBotApi, WebhookHandler)
from linebot.exceptions import (InvalidSignatureError)
from linebot.models import *
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By
from opencc import OpenCC
from pypinyin import Style, pinyin
import re,json,os,datetime
from scipy import stats


#don't change except new champion release
with open('all_champion_id.json',encoding='utf8') as yeee:
    all_champion_id = json.load(yeee)
#don't change except new champion release
with open('CH2EN.json',encoding='utf8') as fjsme:
    CH2EN = json.load(fjsme)
#don't change except new champion release
with open('TOBOPOMOFO.json',encoding='utf8') as pids:
    TOBOPOMOFO = json.load(pids) 
#need to change -> link = hero_kda_winrate.py
with open('hero_kda.json',encoding='utf8') as sgs:
    hero_kda = json.load(sgs)
#need to change -> link = hero_kda_winrate.py
with open('win_rate.json',encoding='utf8') as qres:
    win_rate = json.load(qres)
#need to change -> link = bp.py
with open('ban.json',encoding='utf8') as qrdfe:
    ban = json.load(qrdfe)
#need to change -> link = bp.py
with open('pick.json',encoding='utf8') as ddsdd:
    pick = json.load(ddsdd)

app = Flask(__name__)

CAT  = 'EWT4cb9WdtK01g2tUmBYW0aP9dh6ZFDXkWNj5tOpuHTCd4mq0GXcQU3MQBKjkNWI6PpwX3FVDZcS/To1P7JaDuV4Cjat0tM3XHrTGPEw2f87s24wj240Av4OC3hHKj/b5RMuoFkb9fer+hhaGRGkBwdB04t89/1O/w1cDnyilFU='
CS = 'b0acb66c427385514a21b13406a65018'
# Channel Access Token
line_bot_api = LineBotApi(CAT)
# Channel Secret
handler = WebhookHandler(CS)

@app.route("/callback", methods=['POST'])
def callback():
    # get X-Line-Signature header value
    signature = request.headers['X-Line-Signature']
    # get request body as text
    body = request.get_data(as_text=True)
    app.logger.info("Request body: " + body)
    # handle webhook body
    try:
        handler.handle(body, signature)
    except InvalidSignatureError:
        abort(400)
    return 'OK'

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

def player_datail(name,receiver=None):
    url = "https://matchhistory.tw.leagueoflegends.com/zh/#page/landing-page"
    options = webdriver.ChromeOptions()
    options.add_argument('disable-infobars')
    options.add_argument('--window-size=1920,1080')
    options.add_argument("--headless")
    options.add_argument("--incognito")
    options.add_argument('--disable-dev-shm-usage')
    driver = webdriver.Chrome(options=options)
    driver.get(url)
    driver.implicitly_wait(10)
    input_box = driver.find_element_by_xpath('//*[@id="player-search-4-name"]')
    input_box.click()
    input_box.send_keys(name)
    input_box.send_keys(Keys.RETURN)
    driver.implicitly_wait(10)
    print('INPUT SUCCESS')
    reply = '\n[玩家: {}]\n\n'.format(name)
    RAN = range(5)
    for ii in RAN:
        stri = str(ii+1)+'.\n'
        block = driver.find_elements_by_class_name('game-summary')
        depth = block[ii]
        champ_name = depth.find_element_by_class_name('champion-nameplate-name').text
        mode = depth.find_element_by_class_name('mode').text
        game_during = depth.text.split()[-2]
        x = datetime. datetime. strptime(game_during, "%M:%S")
        mins = datetime.timedelta(minutes=x.minute,seconds=x.second).total_seconds()/60
        print('mins SUCCESS')
        depth.click()
        driver.implicitly_wait(10)
        print('goto statistics SUCCESS')
        WebDriverWait(driver, 10).until(EC.element_to_be_clickable((By.XPATH, "//*[contains(text(), '各項數據')]"))).click()
        print('goto all datas SUCCESS')
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

def update_app(userId):
    if userId=='Uea3f780dd528bcb2ff99fcaa1287d3f5':
        version=None
        with open('my_app_version.txt',encoding='utf8') as aqf:
                version = aqf.read()
        NOW = datetime.datetime.now().strftime("%Y-%m-%d")
        if version==None or version != NOW:
            lineNotifyMessage('即將開始更新...')
            os.system("python hero_kda_winrate.py")
            os.system("python bp.py")
            os.system("python draw.py")
            lineNotifyMessage('聯盟資料更新完成')
            with open('my_app_version.txt','w',encoding='utf8') as aqrsdf:
                aqrsdf.write(NOW)
        else:
            lineNotifyMessage('\n已是最新的版本:'+version)
    else:
        lineNotifyMessage('\n你沒有執行此指令的權限')

def player(name):
    try:
        url = "https://matchhistory.tw.leagueoflegends.com/zh/#page/landing-page"
        options = webdriver.ChromeOptions()
        options.add_argument('disable-infobars')
        options.add_argument('--window-size=1920,1080')
        options.add_argument("--headless")
        options.add_argument("--incognito")
        options.add_argument('--disable-dev-shm-usage')
        driver = webdriver.Chrome(options=options)
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
        #money = [x.text for x in driver.find_elements_by_class_name('income-gold')]
        #during = [x.text for x in driver.find_elements_by_class_name('date-duration-duration')]
        #win = driver.find_elements_by_class_name('game-summary-victory')
        #date = [x.text for x in driver.find_elements_by_class_name('date-duration-date')]
        driver.quit()
        s = "\n[{}的戰績]\n".format(name)
        my_kda=[]
        for i in range(len(map_type)):
            s+="{} {} {} {}\n".format(map_type[i],game_type[i],champ[i],'/'.join(kda[i]))

        for x,y in zip(kda,champ):
            my_kda.append(round((float(x[0])+float(x[2]))/(float(x[1])+1)-hero_kda[y],2))

        tStat, pValue = stats.ttest_ind(my_kda, [float(0) for _ in range(len(map_type))], equal_var = False) #run independent sample T-Test
        
        s+='-------------------------------\n[隊友分析]\n'
        if pValue<0.01:
            if tStat>0: s+="稱號: 尊爵不凡牛逼隊友\n說明: 小心搶頭、保KDA"
            else : s+="稱號: 吃屎雷包\n說明: 建議跳GAME"
        elif pValue<0.3:
            if tStat>0: s+="稱號: 永恆榮耀\n說明: 遲早也會變戳"
            else : s+="稱號: 滿身菜味\n說明: 對 他快變成雷包了"
        else:
            if tStat>0: s+="稱號: 泛泛之輩\n說明: KDA和他的人生一樣普通"
            else : s+="稱號: 中人以下\n說明: 比一般玩家爛一點"
        lineNotifyMessage(s)
    except Exception as e:
        print(e)

def skill_order(CH):
    try:
        EN = CH2EN[CH]
        url = "https://www.leagueofgraphs.com/zh/champions/builds/{}/aram".format(EN)
        chrome_options = webdriver.ChromeOptions()
        chrome_options = webdriver.ChromeOptions()
        chrome_options.binary_location = os.environ.get("GOOGLE_CHROME_BIN")
        chrome_options.add_argument("--headless") #無頭模式
        #chrome_options.add_argument('--window-size=1920,1080')
        chrome_options.add_argument("--disable-dev-shm-usage")
        chrome_options.add_argument("--no-sandbox")
        driver = webdriver.Chrome(executable_path=os.environ.get("CHROMEDRIVER_PATH"), chrome_options=chrome_options)
        driver = webdriver.Chrome(chrome_options=chrome_options,executable_path='/app/.chromedriver/bin/chromedriver')
        driver.get(url)
        driver.implicitly_wait(10)
        main_equip = driver.find_element_by_xpath('//*[@id="mainContent"]/div/div[1]/a[2]/div/div[1]')
        main_equip.screenshot('skill_order.png')
        driver.quit()
        lineNotifyMessage("\n["+CH+"技能次序]",'skill_order.png')
    except:
        pass

def equipment(CH):
    try:
        EN = CH2EN[CH]
        url = "https://www.leagueofgraphs.com/zh/champions/builds/{}/aram".format(EN)
        chrome_options = webdriver.ChromeOptions()
        chrome_options = webdriver.ChromeOptions()
        chrome_options.binary_location = os.environ.get("GOOGLE_CHROME_BIN")
        chrome_options.add_argument("--headless") #無頭模式
        chrome_options.add_argument('--window-size=1920,1080')
        chrome_options.add_argument("--disable-dev-shm-usage")
        chrome_options.add_argument("--no-sandbox")
        driver = webdriver.Chrome(executable_path=os.environ.get("CHROMEDRIVER_PATH"), chrome_options=chrome_options)
        driver = webdriver.Chrome(chrome_options=chrome_options,executable_path='/app/.chromedriver/bin/chromedriver')
        driver.get(url)
        driver.implicitly_wait(10)
        main_equip = driver.find_element_by_xpath('//*[@id="mainContent"]/div/div[1]/a[3]/div/div[1]/div[2]/div[1]')
        main_equip.screenshot('equip.png')
        driver.quit()
        lineNotifyMessage("\n["+CH+"核心裝備]",'equip.png')
    except:
        pass

def Build(CH):
    try:
        EN = CH2EN[CH]
        url = "https://www.leagueofgraphs.com/zh/champions/builds/{}/aram".format(EN)
        chrome_options = webdriver.ChromeOptions()
        chrome_options = webdriver.ChromeOptions()
        chrome_options.binary_location = os.environ.get("GOOGLE_CHROME_BIN")
        chrome_options.add_argument("--headless") #無頭模式
        chrome_options.add_argument('--window-size=1920,1080')
        chrome_options.add_argument("--disable-dev-shm-usage")
        chrome_options.add_argument("--no-sandbox")
        driver = webdriver.Chrome(executable_path=os.environ.get("CHROMEDRIVER_PATH"), chrome_options=chrome_options)
        driver = webdriver.Chrome(chrome_options=chrome_options,executable_path='/app/.chromedriver/bin/chromedriver')
        driver.get(url)

        driver.implicitly_wait(10)
        skill_1 = driver.find_element_by_xpath('//*[@id="mainContent"]/div/div[2]/div[3]/div/a/div/div[1]/img[1]').get_attribute("alt")
        skill_2 = driver.find_element_by_xpath('//*[@id="mainContent"]/div/div[2]/div[3]/div/a/div/div[1]/img[2]').get_attribute("alt")
        print("召喚師技能 : "+ skill_1,skill_2)
        
        rune = driver.find_element_by_xpath('//*[@id="mainContent"]/div/div[2]/a/div/div[2]').text
        cc = OpenCC('s2tw')
        rune = cc.convert(rune)
        print(rune)

        #driver.execute_script("window.scrollTo(0,300)")
        pic = driver.find_element_by_xpath('//*[@id="mainContent"]/div/div[2]/a/div/div[1]')
        
        pic.screenshot('rune.png')
        lineNotifyMessage("\n["+CH+"推薦符文]\n召喚師技能 : "+ skill_1+' '+skill_2+'\n'+rune,'rune.png')
        driver.quit()
    except :
        pass

#開啟小幫手
with open('settings.json',encoding='utf8') as f:
    settings = json.load(f)['help']

# 處理訊息
@handler.add(MessageEvent, message=TextMessage)
def handle_message(event):
    global settings
    if event.message.text == "版本更新":
        userId = event.source.user_id
        update_app(userId)
    elif event.message.text == "aram閉嘴" and settings==1:
        lineNotifyMessage('\n我錯了嗎?!\n如果你想再次開啟\n請輸入"aram說話"')
        settings = 0
        with open('settings.json','w',encoding='utf8') as g:
            json.dump({"help":settings},g,ensure_ascii=False,indent=4)
    elif event.message.text == "aram說話" and settings==0:
        lineNotifyMessage('\n話')
        settings = 1
        with open('settings.json','w',encoding='utf8') as g:
            json.dump({"help":settings},g,ensure_ascii=False,indent=4)
    elif event.message.text == "說明":
        lineNotifyMessage('查看指令說明:\nhttps://hackmd.io/@alankingdom/S1ZYT3i-w')
    elif event.message.text == "禁用率最高":
        lineNotifyMessage('禁用率前五名','Ban_rank.png')
    elif event.message.text == "選用率最高":
        lineNotifyMessage('選用率前五名','Pick_rank.png')
    elif 'bp' in event.message.text:
        try:
            s=""
            hero_name = event.message.text.split()[0]
            msg = ' '.join([''.join(tmp) for tmp in pinyin(hero_name, style=Style.BOPOMOFO, strict=False)])
            pattern = re.compile("ˇ|ˋ|ˊ")
            k = pattern.sub('',msg)
            s+='\n[{}的bp]'.format(TOBOPOMOFO[k])
            s+='\n禁用率:'+ban[TOBOPOMOFO[k]]
            s+='\n選用率:'+pick[TOBOPOMOFO[k]]
            lineNotifyMessage(s)
        except:
            pass
    elif '玩家' in event.message.text[:2]:
        MSG = event.message.text.split()
        if len(MSG)==3 and MSG[2]=='分析':
            try:
                lineNotifyMessage('正在轉換數據...')
                print(MSG[1].strip())
                player_datail(MSG[1].strip())
            except Exception as e:
                print(e)
        elif len(MSG)==2:
            try:
                player_name = MSG[1].strip()
                player(player_name)
            except:
                pass
    elif '符文' in event.message.text[-2:]:
        try:
            MSG=event.message.text.split()[0]
            msg = ' '.join([''.join(tmp) for tmp in pinyin(MSG, style=Style.BOPOMOFO, strict=False)])
            pattern = re.compile("ˇ|ˋ|ˊ")
            k = pattern.sub('',msg)
            Build(TOBOPOMOFO[k])
        except:
            pass
    elif '技能' in event.message.text[-2:]:
        try:
            MSG=event.message.text.split()[0]
            msg = ' '.join([''.join(tmp) for tmp in pinyin(MSG, style=Style.BOPOMOFO, strict=False)])
            pattern = re.compile("ˇ|ˋ|ˊ")
            k = pattern.sub('',msg)
            skill_order(TOBOPOMOFO[k])
        except:
            pass
    elif '裝備' in event.message.text[-2:]:
        try:
            MSG=event.message.text.split()[0]
            msg = ' '.join([''.join(tmp) for tmp in pinyin(MSG, style=Style.BOPOMOFO, strict=False)])
            pattern = re.compile("ˇ|ˋ|ˊ")
            k = pattern.sub('',msg)
            equipment(TOBOPOMOFO[k])
        except:
            pass
    elif '逸儒' == event.message.text:
        lineNotifyMessage('逸儒真難看')
    elif '煜倫' == event.message.text:
        lineNotifyMessage('帥到發芬')
    elif '昕翰' == event.message.text:
        lineNotifyMessage('吸蛤褲老頭')
    elif '犽凝' == event.message.text:
        lineNotifyMessage('像極了愛情')
    elif '勝率最低'== event.message.text:
        d = {k: v for k, v in sorted(win_rate.items(), key=lambda item: item[1])}
        s = '\n前五爛的英雄是:\n'
        for i,ele in enumerate(d):
            if i>4: break
            s+='\n'+str(i+1)+'. '+ele+' '+win_rate[ele]
        lineNotifyMessage(s)
    elif '勝率最高' == event.message.text:
        d = {k: v for k, v in sorted(win_rate.items(), key=lambda item: item[1],reverse=True)}
        s = '\n前五強的英雄是:'
        for i,ele in enumerate(d):
            if i>4: break
            s+='\n'+str(i+1)+'. '+ele+' '+win_rate[ele]
        lineNotifyMessage(s)
    elif '勝率' in event.message.text[-2:]:
        for x in win_rate:
            try:
                name = ' '.join([''.join(tmp) for tmp in pinyin(x, style=Style.BOPOMOFO, strict=False)])
                msg = ' '.join([''.join(tmp) for tmp in pinyin(event.message.text, style=Style.BOPOMOFO, strict=False)])
                pattern = re.compile("ˇ|ˋ|ˊ")
                name = pattern.sub('',name)
                msg = pattern.sub('',msg)

                if name in msg:
                    lineNotifyMessage(x+'的勝率是: '+win_rate[x])
                    break
            except:
                pass
    else:
        if settings==1:
            lineNotifyMessage('\n這個指令我看不懂QQ\n輸入"說明"可以看到完整指令\n如果不希望看到這則通知\n則輸入"aram閉嘴"')
        


@app.route('/')
def index():
    return 'ALAN BOT HELLO WORLD~' #for debug

import os
if __name__ == "__main__":
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port)