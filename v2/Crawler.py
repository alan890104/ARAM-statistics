import os
import re
import random
import time
from bs4 import BeautifulSoup
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import NoSuchElementException
class ELOHelper:
    def __init__(self, webdriver_path: os.PathLike=None) -> None:
        '''
        ### The webdriver can only be CHROME
        '''
        options = webdriver.ChromeOptions()
        options.add_experimental_option("excludeSwitches", ["enable-automation"])
        options.add_experimental_option('useAutomationExtension', False)
        options.add_argument("--disable-blink-features=AutomationControlled")
        if webdriver_path==None: 
            if os.path.isfile("chromedriver.exe"):
                webdriver_path = "chromedriver.exe"
            else:
                raise Exception("\033[91mDefault webdriver path: chromedriver.exe not exist.\033[0m")
        self.driver = webdriver.Chrome(executable_path=webdriver_path,options=options)

    def __del__(self) -> None:
        self.driver.close()
        self.driver.quit()

    def __scrap(self,URL: str) -> str:
        '''
        Get ELO url and return html
        '''
        SleepTime = random.randint(1,2)
        time.sleep(SleepTime)
        self.driver.get(url=URL)
        SleepTime = random.randint(7,9)
        time.sleep(SleepTime)
        # Find and click 隱分走勢
        ELOButton = self.driver.find_element_by_xpath('//*[@id="tabs"]/ul/li[8]/a')
        ELOButton.click()
        WebDriverWait(self.driver, 20).until(EC.presence_of_element_located((By.CLASS_NAME, "label-danger")))
        # Scroll down the page to button
        time.sleep(1)
        self.driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
        # return html source
        time.sleep(1)
        return self.driver.page_source

    def close(self) -> None:
        self.driver.close()
        self.driver.quit()

    def GetOverAllELO(self,UserDict: dict) -> list:
        '''
        Get all history (average) elo by multiple accountId
        ### Parameter
        - UserDict: get this term by GetUserDict() in DB.DBAgent()
            - key: accountId
            - value: LOLName  

        ### Return
        - list of list to initialize ELO table in database
        '''
        ReturnList = list()
        for accountId in UserDict:
            URL = "https://lol.moa.tw/summoner/show/{}".format(UserDict[accountId])
            # Acess HTML
            try:
                page_source = self.__scrap(URL)
            except:
                print("Scrap Error on",UserDict[accountId])
                continue
            # Parse HTML by BS
            Source = BeautifulSoup(page_source,'html.parser')
            Titles = [_.text for _ in Source.find_all('div',class_="label-primary") if _.text!="過往名稱"]

            ELORaw = re.findall('data: \[(.*?)]', page_source)
            TimeRaw = re.findall('labels: \[(.*?)]', page_source)

            TimeLine = list()
            for i in range(len(TimeRaw)):
                r = list(map(int,TimeRaw[i].split(',')))
                TimeLine.append(r)

            ELOResult = list()
            for i in range(len(ELORaw)):
                if (i+1)%2==0 and (i+1)%4!=0:
                    r = list(map(int,ELORaw[i].split(',')))
                    ELOResult.append(r)

            
            for i,title in enumerate(Titles):
                for sqltime,score in zip(TimeLine[i],ELOResult[i]):
                    ReturnList.append([accountId,title,score,sqltime])

        return ReturnList

    def GetLatestELO(self,UserDict: dict) -> list:
        '''
        Similar to GetOverALlELO but only return the latest info
        '''
        ReturnList = list()
        for accountId in UserDict:
            URL = "https://lol.moa.tw/summoner/show/{}".format(UserDict[accountId])
            # Acess HTML
            try:
                page_source = self.__scrap(URL)
            except:
                print("Scrap Error on",UserDict[accountId])
                continue
            # Parse HTML by BS
            Source = BeautifulSoup(page_source,'html.parser')
            Titles = [_.text for _ in Source.find_all('div',class_="label-primary") if _.text!="過往名稱"]
            LatestScore = [_.text.split()[-1] for _ in Source.find_all('div',class_="label-danger")]

            TimeRaw = re.findall('labels: \[(.*?)]', page_source)

            TimeLine = list()
            for i in range(len(TimeRaw)):
                r = int(TimeRaw[i].split(',')[-1])
                TimeLine.append(r)

            for title, score, sqltime in zip(Titles,LatestScore,TimeLine):
                ReturnList.append([accountId,title,score,sqltime])

        return ReturnList


if __name__=="__main__":
    # GetELO("alankingdom",'chromedriver.exe')
    with open("tmp.html",'r',encoding='utf-8') as F:
        page_source = F.read()
    
    Source = BeautifulSoup(page_source,'html.parser')
    Titles = [_.text for _ in Source.find_all('div',class_="label-primary") if _.text!="過往名稱"]

    ELORaw = re.findall('data: \[(.*?)]', page_source)
    TimeRaw = re.findall('labels: \[(.*?)]', page_source)

    TimeLine = list()
    for i in range(len(TimeRaw)):
        r = list(map(int,TimeRaw[i].split(',')))
        TimeLine.append(r)

    ELOResult = list()
    for i in range(len(ELORaw)):
        if (i+1)%2==0 and (i+1)%4!=0:
            r = list(map(int,ELORaw[i].split(',')))
            ELOResult.append(r)

    for i,title in enumerate(Titles):
        for sqltime,score in zip(TimeLine[i],ELOResult[i]):
            print(title,score,sqltime)