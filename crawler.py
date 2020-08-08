import requests,time
from bs4 import BeautifulSoup
import json
from multiprocessing import Pool      
url = 'https://lol.garena.tw/game/champion/'
all_champion_id = {
        1: "Annie",
        2: "Olaf",
        3: "Galio",
        4: "TwistedFate",
        5: "XinZhao",
        6: "Urgot",
        7: "Leblanc",
        8: "Vladimir",
        9: "Fiddlesticks",
        10: "Kayle",
        11: "MasterYi",
        12: "Alistar",
        13: "Ryze",
        14: "Sion",
        15: "Sivir",
        16: "Soraka",
        17: "Teemo",
        18: "Tristana",
        19: "Warwick",
        20: "Nunu",
        21: "MissFortune",
        22: "Ashe",
        23: "Tryndamere",
        24: "Jax",
        25: "Morgana",
        26: "Zilean",
        27: "Singed",
        28: "Evelynn",
        29: "Twitch",
        30: "Karthus",
        31: "Chogath",
        32: "Amumu",
        33: "Rammus",
        34: "Anivia",
        35: "Shaco",
        36: "DrMundo",
        37: "Sona",
        38: "Kassadin",
        39: "Irelia",
        40: "Janna",
        41: "Gangplank",
        42: "Corki",
        43: "Karma",
        44: "Taric",
        45: "Veigar",
        48: "Trundle",
        50: "Swain",
        51: "Caitlyn",
        53: "Blitzcrank",
        54: "Malphite",
        55: "Katarina",
        56: "Nocturne",
        57: "Maokai",
        58: "Renekton",
        59: "JarvanIV",
        60: "Elise",
        61: "Orianna",
        62: "MonkeyKing",
        63: "Brand",
        64: "LeeSin",
        67: "Vayne",
        68: "Rumble",
        69: "Cassiopeia",
        72: "Skarner",
        74: "Heimerdinger",
        75: "Nasus",
        76: "Nidalee",
        77: "Udyr",
        78: "Poppy",
        79: "Gragas",
        80: "Pantheon",
        81: "Ezreal",
        82: "Mordekaiser",
        83: "Yorick",
        84: "Akali",
        85: "Kennen",
        86: "Garen",
        89: "Leona",
        90: "Malzahar",
        91: "Talon",
        92: "Riven",
        96: "KogMaw",
        98: "Shen",
        99: "Lux",
        101: "Xerath",
        102: "Shyvana",
        103: "Ahri",
        104: "Graves",
        105: "Fizz",
        106: "Volibear",
        107: "Rengar",
        110: "Varus",
        111: "Nautilus",
        112: "Viktor",
        113: "Sejuani",
        114: "Fiora",
        115: "Ziggs",
        117: "Lulu",
        119: "Draven",
        120: "Hecarim",
        121: "Khazix",
        122: "Darius",
        126: "Jayce",
        127: "Lissandra",
        131: "Diana",
        133: "Quinn",
        134: "Syndra",
        136: "AurelionSol",
        141: "Kayn",
        142: "Zoe",
        143: "Zyra",
        145: "Kaisa",
        150: "Gnar",
        154: "Zac",
        157: "Yasuo",
        161: "Velkoz",
        163: "Taliyah",
        164: "Camille",
        201: "Braum",
        202: "Jhin",
        203: "Kindred",
        222: "Jinx",
        223: "TahmKench",
        235: "Senna",
        236: "Lucian",
        238: "Zed",
        240: "Kled",
        245: "Ekko",
        246: "Qiyana",
        254: "Vi",
        266: "Aatrox",
        267: "Nami",
        268: "Azir",
        350: "Yuumi",
        412: "Thresh",
        420: "Illaoi",
        421: "Rek'Sai",
        427: "Ivern",
        429: "Kalista",
        432: "Bard",
        497: "Rakan",
        498: "Xayah",
        516: "Ornn",
        517: "Sylas",
        523: "Aphelios",
        518: "Neeko",
        555: "Pyke",
        875: "Sett",
        876: "Lillia"
    }


champ_id = {v: str(k) for k, v in all_champion_id.items()}



def web(url):
    headers = {'user-agent': 'Mozilla/5.0 (Macintosh Intel Mac OS X 10_13_4) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/66.0.3359.181 Safari/537.36'}
    res = requests.get(url,headers=headers)
    soup = BeautifulSoup(res.text, 'html.parser')
    CN_css = 'body > div.wrapper > div.main > div.main-c > div.champintro-w > div > div.champintro-stats-w > div > div.champintro-stats__info > div > div.champintro-stats__info-name-w > div.champintro-stats__info-name > span.champion_name'
    EN_css = 'body > div.wrapper > div.main > div.main-c > div.champintro-w > div > div.champintro-stats-w > div > div.champintro-stats__info > div > div.champintro-stats__info-name-w > div.champintro-stats__info-name > span.champintro-stats__info-name-en'
    try:
        CN_name = soup.select(CN_css)[0].text
        EN_name = soup.select(EN_css)[0].text
        print(CN_name)
        return [CN_name,champ_id[EN_name]]
    except Exception as e:
        print(e ,'    '+url)
    time.sleep(0.5)

if __name__=='__main__':
    Champion = []
    for i in all_champion_id:
        Champion.append(url+all_champion_id[i])
    pool = Pool()
    ans = pool.map(web,Champion)
    pool.close()  
    pool.join()
    D = {}
    for x in ans:
        try:
            D[x[0]] = x[1]
        except:
            pass
    
    with open('r1.txt','w',encoding='utf8') as f:
        f.write(str(D))
    with open('r2.json','w',encoding='utf8') as g:
        json.dump(D,g,ensure_ascii=False,indent=4)
