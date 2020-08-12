from selenium import webdriver
from selenium.webdriver.chrome.options import Options

def aram(id):
    url = "https://lol.moa.tw/summoner/show/"+id
    options = webdriver.ChromeOptions()
    options.add_argument('disable-infobars')
    #options.add_argument("--headless")
    driver = webdriver.Chrome(options=options)
    driver.get(url)
 
    ARAM_button = driver.find_element_by_xpath('//*[@id="tabs"]/ul/li[6]/a')
    ARAM_button.click() 
    driver.implicitly_wait(10)
    S10 = driver.find_element_by_xpath('//*[@id="tabs"]/ul/li[6]/ul/li[1]/a')
    S10.click()
    driver.implicitly_wait(10)


    for i in range(1,50,2):
        try:
            champ_name = driver.find_element_by_xpath('//*[@id="tabs-aggaram-10"]/table/tbody/tr[{}]/th/h3/div[1]'.format(str(i))).text
            champ_kda = driver.find_element_by_xpath('//*[@id="tabs-aggaram-10"]/table/tbody/tr[{}]/th/h3/div[2]'.format(str(i))).text
            champ_count = driver.find_element_by_xpath('//*[@id="tabs-aggaram-10"]/table/tbody/tr[{}]/th/h3/div[3]'.format(str(i))).text
            champ_table = driver.find_element_by_xpath('//*[@id="tabs-aggaram-10"]/table/tbody/tr[{}]/td/table'.format(str(i+1)))
            win_rate = champ_table.find_element_by_xpath('tbody/tr[1]/td[7]')
            print(champ_name,champ_kda,champ_count,win_rate.text)
        except:
            pass

    driver.implicitly_wait(10)
    driver.quit()


aram('逸儒君')