from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from opencc import OpenCC
import requests

CH2EN={
    "安妮": "annie",
    "歐拉夫": "olaf",
    "加里歐": "galio",
    "逆命": "twistedfate",
    "趙信": "xinzhao",
    "烏爾加特": "urgot",
    "勒布朗": "leblanc",
    "弗拉迪米爾": "vladimir",
    "費德提克": "fiddlesticks",
    "凱爾": "kayle",
    "易大師": "masteryi",
    "亞歷斯塔": "alistar",
    "雷茲": "ryze",
    "賽恩": "sion",
    "希維爾": "sivir",
    "索拉卡": "soraka",
    "提摩": "teemo",
    "崔絲塔娜": "tristana",
    "沃維克": "warwick",
    "努努": "nunu",
    "努努和威朗普": "nunu",
    "好運姐": "missfortune",
    "艾希": "ashe",
    "泰達米爾": "tryndamere",
    "賈克斯": "jax",
    "魔甘娜": "morgana",
    "極靈": "zilean",
    "辛吉德": "singed",
    "伊芙琳": "evelynn",
    "圖奇": "twitch",
    "卡爾瑟斯": "karthus",
    "科加斯": "chogath",
    "阿姆姆": "amumu",
    "拉姆斯": "rammus",
    "艾妮維亞": "anivia",
    "薩科": "shaco",
    "蒙多醫生": "drmundo",
    "索娜": "sona",
    "卡薩丁": "kassadin",
    "伊瑞莉雅": "irelia",
    "珍娜": "janna",
    "剛普朗克": "gangplank",
    "庫奇": "corki",
    "卡瑪": "karma",
    "塔里克": "taric",
    "維迦": "veigar",
    "特朗德": "trundle",
    "斯溫": "swain",
    "凱特琳": "caitlyn",
    "布里茨": "blitzcrank",
    "墨菲特": "malphite",
    "卡特蓮娜": "katarina",
    "夜曲": "nocturne",
    "茂凱": "maokai",
    "雷尼克頓": "renekton",
    "嘉文四世": "jarvaniv",
    "伊莉絲": "elise",
    "奧莉安娜": "orianna",
    "悟空": "monkeyking",
    "布蘭德": "brand",
    "李星": "leesin",
    "汎": "vayne",
    "藍寶": "rumble",
    "卡莎碧雅": "cassiopeia",
    "史加納": "skarner",
    "漢默丁格": "heimerdinger",
    "納瑟斯": "nasus",
    "奈德麗": "nidalee",
    "烏迪爾": "udyr",
    "波比": "poppy",
    "古拉格斯": "gragas",
    "潘森": "pantheon",
    "伊澤瑞爾": "ezreal",
    "魔鬥凱薩": "mordekaiser",
    "約瑞科": "yorick",
    "阿卡莉": "akali",
    "凱能": "kennen",
    "蓋倫": "garen",
    "雷歐娜": "leona",
    "馬爾札哈": "malzahar",
    "塔隆": "talon",
    "雷玟": "riven",
    "寇格魔": "kogmaw",
    "慎": "shen",
    "拉克絲": "lux",
    "齊勒斯": "xerath",
    "希瓦娜": "shyvana",
    "阿璃": "ahri",
    "葛雷夫": "graves",
    "飛斯": "fizz",
    "弗力貝爾": "volibear",
    "雷葛爾": "rengar",
    "法洛士": "varus",
    "納帝魯斯": "nautilus",
    "維克特": "viktor",
    "史瓦妮": "sejuani",
    "菲歐拉": "fiora",
    "希格斯": "ziggs",
    "露璐": "lulu",
    "達瑞文": "draven",
    "赫克林": "hecarim",
    "卡力斯": "khazix",
    "達瑞斯": "darius",
    "杰西": "jayce",
    "麗珊卓": "lissandra",
    "黛安娜": "diana",
    "葵恩": "quinn",
    "星朵拉": "syndra",
    "翱銳龍獸": "aurelionsol",
    "慨影": "kayn",
    "柔依": "zoe",
    "枷蘿": "zyra",
    "凱莎": "kaisa",
    "吶兒": "gnar",
    "札克": "zac",
    "犽宿": "yasuo",
    "威寇茲": "velkoz",
    "塔莉雅": "taliyah",
    "卡蜜兒": "camille",
    "布郎姆": "braum",
    "燼": "jhin",
    "鏡爪": "kindred",
    "吉茵珂絲": "jinx",
    "貪啃奇": "tahmkench",
    "姍娜": "senna",
    "路西恩": "lucian",
    "劫": "zed",
    "克雷德": "kled",
    "艾克": "ekko",
    "姬亞娜": "qiyana",
    "菲艾": "vi",
    "厄薩斯": "aatrox",
    "娜米": "nami",
    "阿祈爾": "azir",
    "悠咪": "yuumi",
    "瑟雷西": "thresh",
    "伊羅旖": "illaoi",
    "雷珂煞": "reksai",
    "埃爾文": "ivern",
    "克黎思妲": "kalista",
    "巴德": "bard",
    "銳空": "rakan",
    "剎雅": "xayah",
    "鄂爾": "ornn",
    "賽勒斯": "sylas",
    "亞菲利歐": "aphelios",
    "妮可": "neeko",
    "派克": "pyke",
    "賽特": "sett",
    "犽凝": "yone",
    "莉莉亞": "lillia"
}

def lineNotify(msg, picURI=None):
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

def Build(CH):
    try:
        EN = CH2EN[CH]
        url = "https://www.leagueofgraphs.com/zh/champions/builds/{}/aram".format(EN)
        options = webdriver.ChromeOptions()
        options.add_argument('disable-infobars')
        options.add_argument("--headless")
        """ chrome_prefs = {}
        options.experimental_options["prefs"] = chrome_prefs
        chrome_prefs["profile.default_content_settings"] = {"images": 2} """
        driver = webdriver.Chrome(options=options)
        driver.header_overrides = {
            'Referer': 'referer_string',
        }
        driver.get(url)

        driver.implicitly_wait(10)
        skill_1 = driver.find_element_by_xpath('//*[@id="mainContent"]/div/div[2]/div[3]/div/a/div/div[1]/img[1]').get_attribute("alt")
        skill_2 = driver.find_element_by_xpath('//*[@id="mainContent"]/div/div[2]/div[3]/div/a/div/div[1]/img[2]').get_attribute("alt")
        print("召喚師技能 : "+ skill_1,skill_2)
        
        rune = driver.find_element_by_xpath('//*[@id="mainContent"]/div/div[2]/a/div/div[2]').text
        cc = OpenCC('s2tw')
        rune = cc.convert(rune)
        print(rune)

        driver.execute_script("window.scrollTo(0,300)")
        pic = driver.find_element_by_xpath('//*[@id="mainContent"]/div/div[2]/a/div/div[1]')
        
        pic.screenshot('pic.png')
        lineNotify("\n["+CH+"推薦符文]\n召喚師技能 : "+ skill_1+' '+skill_2+'\n'+rune,'pic.png')
        driver.quit()
    except :
        pass

Build('黛安娜')