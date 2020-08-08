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
from opencc import OpenCC
from pypinyin import Style, pinyin
import re

all_champion_id = {
    "安妮": "1",
    "歐拉夫": "2",
    "加里歐": "3",
    "逆命":"4",
    "卡牌":"4",
    "趙信":"5",
    "烏爾加特": "6",
    "勒布朗":"7",
    "弗拉迪米爾": "8",
    "血鬼": "8",
    "費德提克": "9",
    "凱爾": "10",
    "易大師":"11",
    "亞歷斯塔": "12",
    "雷茲": "13",
    "賽恩": "14",
    "希維爾": "15",
    "索拉卡": "16",
    "提摩": "17",
    "崔絲塔娜": "18",
    "沃維克": "19",
    "努努":"20",
    "努努和威朗普":"20",
    "好運姐":"21",
    "艾希": "22",
    "泰達米爾": "23",
    "賈克斯": "24",
    "魔甘娜": "25",
    "極靈": "26",
    "辛吉德": "27",
    "伊芙琳": "28",
    "圖奇": "29",
    "卡爾瑟斯": "30",
    "死歌": "30",
    "科加斯":"31",
    "阿姆姆": "32",
    "拉姆斯": "33",
    "艾妮維亞": "34",
    "薩科": "35",
    "蒙多醫生":"36",
    "蒙多":"36",
    "索娜": "37",
    "卡薩丁": "38",
    "伊瑞莉雅": "39",
    "珍娜": "40",
    "剛普朗克": "41",
    "庫奇": "42",
    "卡瑪": "43",
    "塔里克": "44",
    "維迦": "45",
    "特朗德": "48",
    "斯溫": "50",
    "凱特琳": "51",
    "布里茨": "53",
    "墨菲特": "54",
    "卡特蓮娜": "55",
    "夜曲": "56",
    "茂凱": "57",
    "雷尼克頓": "58",
    "嘉文四世":"59",
    "伊莉絲": "60",
    "奧莉安娜": "61",
    "悟空":"62",
    "布蘭德": "63",
    "李星":"64",
    "汎": "67",
    "藍寶": "68",
    "卡莎碧雅": "69",
    "史加納": "72",
    "漢默丁格": "74",
    "納瑟斯": "75",
    "奈德麗": "76",
    "烏迪爾": "77",
    "波比": "78",
    "古拉格斯": "79",
    "潘森": "80",
    "伊澤瑞爾": "81",
    "魔鬥凱薩": "82",
    "約瑞科": "83",
    "阿卡莉": "84",
    "凱能": "85",
    "蓋倫": "86",
    "雷歐娜": "89",
    "馬爾札哈": "90",
    "塔隆": "91",
    "雷玟": "92",
    "寇格魔":"96",
    "慎": "98",
    "拉克絲": "99",
    "齊勒斯": "101",
    "希瓦娜": "102",
    "阿璃": "103",
    "葛雷夫": "104",
    "飛斯": "105",
    "弗力貝爾": "106",
    "雷葛爾": "107",
    "法洛士": "110",
    "納帝魯斯": "111",
    "維克特": "112",
    "史瓦妮": "113",
    "菲歐拉": "114",
    "希格斯": "115",
    "露璐": "117",
    "達瑞文": "119",
    "赫克林": "120",
    "卡力斯": "121",
    "達瑞斯": "122",
    "杰西": "126",
    "麗珊卓": "127",
    "黛安娜": "131",
    "葵恩": "133",
    "星朵拉": "134",
    "翱銳龍獸": "136",
    "慨影": "141",
    "柔依": "142",
    "枷蘿": "143",
    "凱莎": "145",
    "吶兒": "150",
    "札克": "154",
    "犽宿": "157",
    "威寇茲": "161",
    "塔莉雅": "163",
    "卡蜜兒": "164",
    "布郎姆": "201",
    "燼": "202",
    "鏡爪": "203",
    "吉茵珂絲": "222",
    "貪啃奇": "223",
    "姍娜": "235",
    "路西恩": "236",
    "劫": "238",
    "克雷德": "240",
    "艾克": "245",
    "姬亞娜": "246",
    "菲艾": "254",
    "厄薩斯": "266",
    "娜米": "267",
    "阿祈爾": "268",
    "悠咪": "350",
    "瑟雷西": "412",
    "伊羅旖": "420",
    "雷珂煞": "421",
    "埃爾文": "427",
    "克黎思妲": "429",
    "巴德": "432",
    "銳空": "497",
    "剎雅": "498",
    "鄂爾": "516",
    "賽勒斯": "517",
    "亞菲利歐": "523",
    "妮可": "518",
    "派克": "555",
    "賽特": "875",
    "莉莉亞": "876"
}

win_rate = {
    "安妮": "51.84%",
    "歐拉夫": "47.38%",
    "加里歐": "53.60%",
    "逆命": "50.80%",
    "趙信": "48.44%",
    "烏爾加特": "52.25%",
    "勒布朗": "46.45%",
    "弗拉迪米爾": "50.21%",
    "費德提克": "54.87%",
    "凱爾": "53.55%",
    "易大師": "47.18%",
    "亞歷斯塔": "55.40%",
    "雷茲": "48.51%",
    "賽恩": "53.67%",
    "希維爾": "55.05%",
    "索拉卡": "49.13%",
    "提摩": "50.30%",
    "崔絲塔娜": "47.14%",
    "沃維克": "49.35%",
    "努努和威朗普": "47.70%",
    "好運姐": "52.37%",
    "艾希": "54.98%",
    "泰達米爾": "49.23%",
    "賈克斯": "46.63%",
    "魔甘娜": "53.22%",
    "極靈": "47.15%",
    "辛吉德": "52.54%",
    "伊芙琳": "44.53%",
    "圖奇": "48.54%",
    "卡爾瑟斯": "54.10%",
    "科加斯": "50.89%",
    "阿姆姆": "55.85%",
    "拉姆斯": "48.08%",
    "艾妮維亞": "46.58%",
    "薩科": "53.23%",
    "蒙多醫生": "53.21%",
    "索娜": "56.33%",
    "卡薩丁": "46.51%",
    "伊瑞莉雅": "46.41%",
    "珍娜": "52.18%",
    "剛普朗克": "47.79%",
    "庫奇": "47.41%",
    "卡瑪": "47.77%",
    "塔里克": "50.69%",
    "維迦": "50.63%",
    "特朗德": "52.51%",
    "斯溫": "56.47%",
    "凱特琳": "56.57%",
    "布里茨": "50.75%",
    "墨菲特": "49.41%",
    "卡特蓮娜": "45.81%",
    "夜曲": "47.35%",
    "茂凱": "55.57%",
    "雷尼克頓": "49.11%",
    "嘉文四世": "47.06%",
    "伊莉絲": "46.93%",
    "奧莉安娜": "51.04%",
    "悟空": "51.09%",
    "布蘭德": "50.87%",
    "李星": "45.62%",
    "汎": "47.26%",
    "藍寶": "45.33%",
    "卡莎碧雅": "48.90%",
    "史加納": "50.22%",
    "漢默丁格": "52.16%",
    "納瑟斯": "53.03%",
    "奈德麗": "49.24%",
    "烏迪爾": "48.72%",
    "波比": "45.68%",
    "古拉格斯": "46.33%",
    "潘森": "45.27%",
    "伊澤瑞爾": "53.53%",
    "魔鬥凱薩": "48.22%",
    "約瑞科": "51.23%",
    "阿卡莉": "46.61%",
    "凱能": "48.98%",
    "蓋倫": "50.25%",
    "雷歐娜": "54.11%",
    "馬爾札哈": "52.16%",
    "塔隆": "46.53%",
    "雷玟": "49.75%",
    "寇格魔": "53.46%",
    "慎": "47.86%",
    "拉克絲": "53.25%",
    "齊勒斯": "53.53%",
    "希瓦娜": "46.78%",
    "阿璃": "50.48%",
    "葛雷夫": "50.81%",
    "飛斯": "47.37%",
    "弗力貝爾": "46.49%",
    "雷葛爾": "45.79%",
    "法洛士": "50.12%",
    "納帝魯斯": "53.64%",
    "維克特": "50.67%",
    "史瓦妮": "46.07%",
    "菲歐拉": "46.51%",
    "希格斯": "54.80%",
    "露璐": "49.35%",
    "達瑞文": "46.02%",
    "赫克林": "47.85%",
    "卡力斯": "47.73%",
    "達瑞斯": "51.60%",
    "杰西": "48.44%",
    "麗珊卓": "51.02%",
    "黛安娜": "51.64%",
    "葵恩": "46.60%",
    "星朵拉": "46.44%",
    "翱銳龍獸": "47.59%",
    "慨影": "48.15%",
    "柔依": "45.34%",
    "枷蘿": "53.48%",
    "凱莎": "47.27%",
    "吶兒": "48.31%",
    "札克": "48.44%",
    "犽宿": "48.68%",
    "威寇茲": "52.28%",
    "塔莉雅": "45.67%",
    "卡蜜兒": "46.17%",
    "布郎姆": "46.76%",
    "燼": "53.49%",
    "鏡爪": "44.94%",
    "吉茵珂絲": "53.45%",
    "貪啃奇": "45.29%",
    "姍娜": "53.27%",
    "路西恩": "48.09%",
    "劫": "48.72%",
    "克雷德": "46.62%",
    "艾克": "46.30%",
    "姬亞娜": "47.37%",
    "菲艾": "46.57%",
    "厄薩斯": "47.15%",
    "娜米": "53.14%",
    "阿祈爾": "46.78%",
    "悠咪": "45.11%",
    "瑟雷西": "47.57%",
    "伊羅旖": "51.19%",
    "雷珂煞": "48.35%",
    "埃爾文": "52.01%",
    "克黎思妲": "48.74%",
    "巴德": "44.95%",
    "銳空": "48.81%",
    "剎雅": "47.10%",
    "鄂爾": "52.05%",
    "賽勒斯": "46.87%",
    "妮可": "52.15%",
    "亞菲利歐": "46.39%",
    "派克": "44.97%",
    "賽特": "52.34%",
    "莉莉亞": "44.11%"
}
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
TOBOPOMOFO ={
    "ㄢㄋㄧ": "安妮",
    "ㄡㄌㄚㄈㄨ": "歐拉夫",
    "ㄐㄧㄚㄌㄧㄡ": "加里歐",
    "ㄋㄧㄇㄧㄥ": "逆命",
    "ㄓㄠㄒㄧㄣ": "趙信",
    "ㄨㄦㄐㄧㄚㄊㄜ": "烏爾加特",
    "ㄌㄟㄅㄨㄌㄤ": "勒布朗",
    "ㄌㄜㄅㄨㄌㄤ": "勒布朗",
    "ㄈㄨㄌㄚㄉㄧㄇㄧㄦ": "弗拉迪米爾",
    "ㄈㄟㄉㄜㄊㄧㄎㄜ": "費德提克",
    "ㄎㄞㄦ": "凱爾",
    "ㄧㄉㄚㄕ": "易大師",
    "ㄧㄚㄌㄧㄙㄊㄚ": "亞歷斯塔",
    "ㄌㄟㄗ": "雷茲",
    "ㄙㄞㄣ": "賽恩",
    "ㄒㄧㄨㄟㄦ": "希維爾",
    "ㄙㄨㄛㄌㄚㄎㄚ": "索拉卡",
    "ㄊㄧㄇㄛ": "提摩",
    "ㄘㄨㄟㄙㄊㄚㄋㄚ": "崔絲塔娜",
    "ㄨㄛㄨㄟㄎㄜ": "沃維克",
    "ㄋㄨㄋㄨ": "努努",
    "ㄋㄨㄋㄨㄏㄜㄨㄟㄌㄤㄆㄨ": "努努和威朗普",
    "ㄏㄠㄩㄣㄐㄧㄝ": "好運姐",
    "ㄞㄒㄧ": "艾希",
    "ㄊㄞㄉㄚㄇㄧㄦ": "泰達米爾",
    "ㄐㄧㄚㄎㄜㄙ": "賈克斯",
    "ㄇㄛㄍㄢㄋㄚ": "魔甘娜",
    "ㄐㄧㄌㄧㄥ": "極靈",
    "ㄒㄧㄣㄐㄧㄉㄜ": "辛吉德",
    "ㄧㄈㄨㄌㄧㄣ": "伊芙琳",
    "ㄊㄨㄑㄧ": "圖奇",
    "ㄎㄚㄦㄙㄜㄙ": "卡爾瑟斯",
    "ㄎㄜㄐㄧㄚㄙ": "科加斯",
    "ㄚㄇㄨㄇㄨ": "阿姆姆",
    "ㄌㄚㄇㄨㄙ": "拉姆斯",
    "ㄞㄋㄧㄨㄟㄧㄚ": "艾妮維亞",
    "ㄙㄚㄎㄜ": "薩科",
    "ㄇㄥㄉㄨㄛㄧㄕㄥ": "蒙多醫生",
    "ㄙㄨㄛㄋㄚ": "索娜",
    "ㄎㄚㄙㄚㄉㄧㄥ": "卡薩丁",
    "ㄧㄖㄨㄟㄌㄧㄧㄚ": "伊瑞莉雅",
    "ㄓㄣㄋㄚ": "珍娜",
    "ㄍㄤㄆㄨㄌㄤㄎㄜ": "剛普朗克",
    "ㄎㄨㄑㄧ": "庫奇",
    "ㄎㄚㄇㄚ": "卡瑪",
    "ㄊㄚㄌㄧㄎㄜ": "塔里克",
    "ㄨㄟㄐㄧㄚ": "維迦",
    "ㄊㄜㄌㄤㄉㄜ": "特朗德",
    "ㄙㄨㄣ": "斯溫",
    "ㄎㄞㄊㄜㄌㄧㄣ": "凱特琳",
    "ㄅㄨㄌㄧㄘ": "布里茨",
    "ㄇㄛㄈㄟㄊㄜ": "墨菲特",
    "ㄎㄚㄊㄜㄌㄧㄢㄋㄚ": "卡特蓮娜",
    "ㄧㄝㄑㄩ": "夜曲",
    "ㄇㄠㄎㄞ": "茂凱",
    "ㄌㄟㄋㄧㄎㄜㄉㄨㄣ": "雷尼克頓",
    "ㄐㄧㄚㄨㄣㄙㄕ": "嘉文四世",
    "ㄧㄌㄧㄙ": "伊莉絲",
    "ㄠㄌㄧㄢㄋㄚ": "奧莉安娜",
    "ㄨㄎㄨㄥ": "悟空",
    "ㄅㄨㄌㄢㄉㄜ": "布蘭德",
    "ㄌㄧㄒㄧㄥ": "李星",
    "ㄈㄢ": "汎",
    "ㄌㄢㄅㄠ": "藍寶",
    "ㄎㄚㄕㄚㄅㄧㄧㄚ": "卡莎碧雅",
    "ㄕㄐㄧㄚㄋㄚ": "史加納",
    "ㄏㄢㄇㄛㄉㄧㄥㄍㄜ": "漢默丁格",
    "ㄋㄚㄙㄜㄙ": "納瑟斯",
    "ㄋㄞㄉㄜㄌㄧ": "奈德麗",
    "ㄨㄉㄧㄦ": "烏迪爾",
    "ㄅㄛㄅㄧ": "波比",
    "ㄍㄨㄌㄚㄍㄜㄙ": "古拉格斯",
    "ㄆㄢㄙㄣ": "潘森",
    "ㄧㄗㄜㄖㄨㄟㄦ": "伊澤瑞爾",
    "ㄇㄛㄉㄡㄎㄞㄙㄚ": "魔鬥凱薩",
    "ㄩㄝㄖㄨㄟㄎㄜ": "約瑞科",
    "ㄚㄎㄚㄌㄧ": "阿卡莉",
    "ㄎㄞㄋㄥ": "凱能",
    "ㄍㄞㄌㄨㄣ": "蓋倫",
    "ㄌㄟㄡㄋㄚ": "雷歐娜",
    "ㄇㄚㄦㄓㄚㄏㄚ": "馬爾札哈",
    "ㄊㄚㄌㄨㄥ": "塔隆",
    "ㄌㄟㄨㄣ": "雷玟",
    "ㄎㄡㄍㄜㄇㄛ": "寇格魔",
    "ㄕㄣ": "慎",
    "ㄌㄚㄎㄜㄙ": "拉克絲",
    "ㄑㄧㄌㄟㄙ": "齊勒斯",
    "ㄑㄧㄌㄜㄙ": "齊勒斯",
    "ㄒㄧㄨㄚㄋㄚ": "希瓦娜",
    "ㄚㄌㄧ": "阿璃",
    "ㄍㄜㄌㄟㄈㄨ": "葛雷夫",
    "ㄈㄟㄙ": "飛斯",
    "ㄈㄨㄌㄧㄅㄟㄦ": "弗力貝爾",
    "ㄌㄟㄍㄜㄦ": "雷葛爾",
    "ㄈㄚㄌㄨㄛㄕ": "法洛士",
    "ㄋㄚㄉㄧㄌㄨㄙ": "納帝魯斯",
    "ㄨㄟㄎㄜㄊㄜ": "維克特",
    "ㄕㄨㄚㄋㄧ": "史瓦妮",
    "ㄈㄟㄡㄌㄚ": "菲歐拉",
    "ㄒㄧㄍㄜㄙ": "希格斯",
    "ㄌㄨㄌㄨ": "露璐",
    "ㄉㄚㄖㄨㄟㄨㄣ": "達瑞文",
    "ㄏㄜㄎㄜㄌㄧㄣ": "赫克林",
    "ㄎㄚㄌㄧㄙ": "卡力斯",
    "ㄉㄚㄖㄨㄟㄙ": "達瑞斯",
    "ㄐㄧㄝㄒㄧ": "杰西",
    "ㄌㄧㄕㄢㄓㄨㄛ": "麗珊卓",
    "ㄉㄞㄢㄋㄚ": "黛安娜",
    "ㄎㄨㄟㄣ": "葵恩",
    "ㄒㄧㄥㄉㄨㄛㄌㄚ": "星朵拉",
    "ㄠㄖㄨㄟㄌㄨㄥㄕㄡ": "翱銳龍獸",
    "ㄎㄞㄧㄥ": "慨影",
    "ㄖㄡㄧ": "柔依",
    "ㄐㄧㄚㄌㄨㄛ": "枷蘿",
    "ㄎㄞㄕㄚ": "凱莎",
    "ㄋㄚㄦ": "吶兒",
    "ㄓㄚㄎㄜ": "札克",
    "ㄧㄚㄙㄨ": "犽宿",
    "ㄨㄟㄎㄡㄗ": "威寇茲",
    "ㄊㄚㄌㄧㄧㄚ": "塔莉雅",
    "ㄎㄚㄇㄧㄦ": "卡蜜兒",
    "ㄅㄨㄌㄤㄇㄨ": "布郎姆",
    "ㄐㄧㄣ": "燼",
    "ㄐㄧㄥㄓㄠ": "鏡爪",
    "ㄐㄧㄥㄓㄨㄚ": "鏡爪",
    "ㄐㄧㄧㄣㄎㄜㄙ": "吉茵珂絲",
    "ㄊㄢㄎㄣㄑㄧ": "貪啃奇",
    "ㄕㄢㄋㄚ": "姍娜",
    "ㄌㄨㄒㄧㄣ": "路西恩",
    "ㄐㄧㄝ": "劫",
    "ㄎㄜㄌㄟㄉㄜ": "克雷德",
    "ㄞㄎㄜ": "艾克",
    "ㄐㄧㄧㄚㄋㄚ": "姬亞娜",
    "ㄈㄟㄞ": "菲艾",
    "ㄜㄙㄚㄙ": "厄薩斯",
    "ㄋㄚㄇㄧ": "娜米",
    "ㄚㄑㄧㄦ": "阿祈爾",
    "ㄧㄡㄇㄧ": "悠咪",
    "ㄙㄜㄌㄟㄒㄧ": "瑟雷西",
    "ㄧㄌㄨㄛㄧ": "伊羅旖",
    "ㄌㄟㄎㄜㄕㄚ": "雷珂煞",
    "ㄞㄦㄨㄣ": "埃爾文",
    "ㄎㄜㄌㄧㄙㄉㄚ": "克黎思妲",
    "ㄅㄚㄉㄜ": "巴德",
    "ㄖㄨㄟㄎㄨㄥ": "銳空",
    "ㄕㄚㄧㄚ": "剎雅",
    "ㄔㄚㄧㄚ": "剎雅",
    "ㄜㄦ": "鄂爾",
    "ㄙㄞㄌㄟㄙ": "賽勒斯",
    "ㄙㄞㄌㄜㄙ": "賽勒斯",
    "ㄧㄚㄈㄟㄌㄧㄡ": "亞菲利歐",
    "ㄋㄧㄎㄜ": "妮可",
    "ㄆㄞㄎㄜ": "派克",
    "ㄙㄞㄊㄜ": "賽特",
    "ㄧㄚㄋㄧㄥ": "犽凝",
    "ㄌㄧㄌㄧㄧㄚ": "莉莉亞"
}

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
        s = "\n"
        for i in range(len(map_type)):
            s+="{} {} {} {}\n".format(map_type[i],game_type[i],champ[i],kda[i])
        s+="[{}場平均勝率為{}]".format(len(champ),str(round((len(win)/len(champ))*100,2))+"%")
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
# 處理訊息
@handler.add(MessageEvent, message=TextMessage)
def handle_message(event):
    if '玩家' in event.message.text:
        try:
            player_name = event.message.text.split()[1]
            player(player_name)
        except:
            pass
    elif '符文' in event.message.text:
        try:
            MSG=event.message.text.split()[0]
            msg = ''.join([''.join(tmp) for tmp in pinyin(MSG, style=Style.BOPOMOFO, strict=False)])
            pattern = re.compile("ˇ|ˋ|ˊ")
            k = pattern.sub('',msg)
            Build(TOBOPOMOFO[k])
        except:
            pass
    elif '技能' in event.message.text:
        try:
            MSG=event.message.text.split()[0]
            msg = ''.join([''.join(tmp) for tmp in pinyin(MSG, style=Style.BOPOMOFO, strict=False)])
            pattern = re.compile("ˇ|ˋ|ˊ")
            k = pattern.sub('',msg)
            skill_order(TOBOPOMOFO[k])
        except:
            pass
    elif '裝備' in event.message.text:
        try:
            MSG=event.message.text.split()[0]
            msg = ''.join([''.join(tmp) for tmp in pinyin(MSG, style=Style.BOPOMOFO, strict=False)])
            pattern = re.compile("ˇ|ˋ|ˊ")
            k = pattern.sub('',msg)
            equipment(TOBOPOMOFO[k])
        except:
            pass
    elif '逸儒' in event.message.text:
        lineNotifyMessage('逸儒真難看')
    elif '煜倫' in event.message.text:
        lineNotifyMessage('帥到發芬')
    elif '昕翰' in event.message.text:
        lineNotifyMessage('吸蛤褲老頭')
    elif '犽凝' in event.message.text:
        lineNotifyMessage('像極了愛情')
    elif '最低' in event.message.text or '最爛' in event.message.text:
        d = {k: v for k, v in sorted(win_rate.items(), key=lambda item: item[1])}
        s = '\n前五爛的英雄是:\n'
        for i,ele in enumerate(d):
            if i>4: break
            s+='\n'+str(i+1)+'. '+ele+' '+win_rate[ele]
        lineNotifyMessage(s)
    elif '最高' in event.message.text or '最強' in event.message.text:
        d = {k: v for k, v in sorted(win_rate.items(), key=lambda item: item[1],reverse=True)}
        s = '\n前五強的英雄是:'
        for i,ele in enumerate(d):
            if i>4: break
            s+='\n'+str(i+1)+'. '+ele+' '+win_rate[ele]
        lineNotifyMessage(s)
    else:
        try:
            for x in win_rate:

                name = ''.join([''.join(tmp) for tmp in pinyin(x, style=Style.BOPOMOFO, strict=False)])
                msg = ''.join([''.join(tmp) for tmp in pinyin(event.message.text, style=Style.BOPOMOFO, strict=False)])
                pattern = re.compile("ˇ|ˋ|ˊ")
                name = pattern.sub('',name)
                msg = pattern.sub('',msg)

                if name in msg:
                    lineNotifyMessage(x+'的勝率是: '+win_rate[x])
                    break
        except:
            pass
        

    

@app.route('/')
def index():
    return 'ALAN BOT HELLO WORLD~' #for debug

import os
if __name__ == "__main__":
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port)