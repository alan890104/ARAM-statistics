import os
import time
from bs4 import BeautifulSoup
from selenium import webdriver

def GetELO(player: str,path: os.PathLike):
    try:
        url = "https://lol.moa.tw/summoner/show/{}".format(player)
        username = os.getenv("USERNAME")
        userProfile = "C:\\Users\\" + username + "\\AppData\\Local\\Google\\Chrome\\User Data\\Default"
        Options = webdriver.ChromeOptions()
        Options.add_argument("user-data-dir={}".format(userProfile))
        Options.add_argument('disable-infobars')
        Options.add_argument("--disable-notifications")
        Options.add_argument('--window-size=1920,1080')
        # Options.add_argument("--headless")
        Options.add_argument("--incognito")
        Options.add_argument('--disable-dev-shm-usage')
        Options.add_experimental_option("excludeSwitches", ["enable-automation"])
        Options.add_experimental_option('useAutomationExtension', False)
        Options.add_argument("--disable-blink-features=AutomationControlled")

        driver = webdriver.Chrome(executable_path=path,options=Options)
        driver.get(url)
        time.sleep(20)
        # driver.implicitly_wait(20)
        ELOButton = driver.find_element_by_xpath('//*[@id="tabs"]/ul/li[8]/a')
        ELOButton.click()
        print('click success')
        time.sleep(5)
        driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
        print('scroll success')
        time.sleep(5)
        soup = BeautifulSoup(driver.page_source,'html_parser')
        with open("tmp.html",'w') as F:
            F.write(str(driver.page_source))
        # gameMode = []
        # for mode in driver.find_elements_by_class_name('label label-primary'):
        #     if len(mode.text)>0:
        #         gameMode.append(mode.text)
        # score = driver.find_elements_by_class_name('label label-danger')
        driver.quit()

    except Exception as e:
        print('The error is : ',e)

if __name__=="__main__":
    GetELO("alankingdom",'webdriver\chromedriver.exe')