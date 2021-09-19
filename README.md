# LOL Statistics 

[![hackmd-github-sync-badge](https://hackmd.io/lTFPJuA6Rn-kpDqh8slQww/badge)](https://hackmd.io/lTFPJuA6Rn-kpDqh8slQww)

## 使用說明
- **簡介**: 沒錯!把所有英雄聯盟的資料庫挖出來，就看看誰才是雷包!


- **指令**(越上方者優先判定): 

    |指令|內容|
    |-----|----|
    |@register **<玩家名稱>** |連結LINE帳號與召喚師名稱|
    |@echo|呼叫使用者功能列表|

## 圖例
* echo   
    ![@ehco](https://github.com/alan890104/ARAM-statistics/blob/master/v2/Image/welcome.png)   
* best   
    ![@best](https://github.com/alan890104/ARAM-statistics/blob/master/v2/Image/best.png)   
* item   
    ![@item](https://github.com/alan890104/ARAM-statistics/blob/master/v2/Image/item.png)   
* time   
    ![@time](https://github.com/alan890104/ARAM-statistics/blob/master/v2/Image/time.png)   

## 主架構
* <font color="green">綠色</font>未完成 <font color="red">紅色</font>待修改 <font color="orange">橘色</font>重點項目
```graphviz
digraph hierarchy {

		nodesep=1.0 // increases the separation between nodes
		
		node [color=Black,fontname=Courier,shape=box] //All nodes will this shape and colour
		edge [color=Blue, style=dashed] //All the lines look like this

		Line應用程式->{遊戲內資訊  玩家資訊[color="orange"] }
		遊戲內資訊->{英雄資訊 版本快訊}
		玩家資訊->{隱分趨勢 對戰分析 對戰預測 浪費人生計算機}
        英雄資訊->{選用率[color="black"] 勝率[color="black"] 推薦裝備[color="black"]}
        對戰分析->{個人強勢英雄 愛用道具 當季最佳紀錄 找剪頭仔[color="black"]}
		{rank=same;英雄資訊 版本快訊[color="black"] 隱分趨勢[color="black"] 對戰分析 對戰預測[color="red"]}  // Put them on the same level
}
```
## 設計宗旨
* 減少使用者輸入頻率(EX:用按鈕顯示)  
* 增加常用指令速度(EX: 顯示常用指令)  
* 以**玩家為本體**設計 遊戲內資訊可以減少  

## APIs
### 基礎
- [X] 取得英雄名稱與id  
- [X] 取得商品名稱與id  
- [X] 取得召喚師技能名稱與id  
- [X] 遊戲版本取得  
- [X] LOL ID 取得  
- [X] 遊玩歷史紀錄取得  

### 進階
- [x] 玩家遊玩紀錄 
- [x] 個人強勢英雄計算與輸出 
- [x] 愛用道具計算與輸出
- [x] 當季最佳紀錄計算與輸出
- [x] 隨機冷知識(?  你知道嗎?alankingdom在藍方的勝率更高!隱分和藍紅兩方的關係?
- [x] pytesseract轉換圖像中文字 以利預測(尚未上傳)
- [x] 機器學習勝率預測模型改良(尚未上傳)

## Line前端介面
- [X] FLEX Message  

## Tables
* 使用者資料表  
```sql
CREATE TABLE users(
    accountId TEXT UNIQUE,// LOL account id    
    LOLName TEXT NOT NULL UNIQUE
)
```
* Line連動資料表  
```sql
CREATE TABLE line(
    LineId TEXT UNIQUE,// Line account id    
    LOLName TEXT NOT NULL UNIQUE
)
```
* 隱藏積分資料表  
```sql
CREATE TABLE elo(
    accountId TEXT NOT NULL,
    title TEXT NOT NULL, //哪種模式(這是中文 會跟其他的table不一樣)
    score INT NOT NULL, //隱分分數
    sqltime DATETIME NOT NULL, //更新的時間   
    PRIMARY KEY(accountId,gameMode,sqltime),
    FOREIGN KEY (accoundId) REFERENCES users (accoundId)
    ON DELETE CASCADE
    ON UPDATE CASCADE )
)
```
* 遊玩歷史紀錄資料表  
```sql
CREATE TABLE game(
    gameId INT,
    accountId INT FOREIGN KEY,
    gameMode TEXT NOT NULL, --ARAM/CLASSIC/ONEFORALL/URF/NEXUSBLITZ/KINGPORO/TUTORIAL_MODULE_1/TUTORIAL_MODULE_2
    gameType TEXT NOT NULL, --ex: "MATCHED_GAME"
    gameVersion TEXT NOT NULL,
    gameCreation DATETIME NOT NULL,
    gameDuration INT NOT NULL
    teamId INT NOT NULL, --100(blue) or 200(red)
    championId INT NOT NULL,
    win BOOL NOT NULL,
    items TEXT NOT NULL, --EX: " 1001 1002 1003 0 0 0 0 "
    kills INT NOT NULL,
    deaths INT NOT NULL,
    assists INT NOT NULL,
    largestKillingSpree INT NOT NULL,
    largestMultiKill INT NOT NULL,
    doubleKills INT NOT NULL,
    tripleKills INT NOT NULL,
    quadraKills INT NOT NULL,
    pentaKills INT NOT NULL,
    unrealKills INT NOT NULL,
    totalDamageDealt INT NOT NULL,
    totalHeal INT NOT NULL,
    totalDamageTaken INT NOT NULL,
    damageSelfMitigated INT NOT NULL,
    damageDealtToObjectives INT NOT NULL,
    timeCCingOthers INT NOT NULL,
    visionScore INT NOT NULL,
    goldEarned INT NOT NULL,
    totalMinionsKilled INT NOT NULL,
    buildingKills INT NOT NULL,
    champLevel INT NOT NULL,
    firstBloodKill BOOL NOT NULL,
    firstTowerKill BOOL NOT NULL,
    firstInhibitorKill BOOl NOT NULL,
    role TEXT, --DUO_SUPPORT/DUO/SOLO/DUO_CARRY/NONE
    lane TEXT, --MIDDLE/JUNGLE/TOP/BOTTOM/NONE
    PRIMARY KEY(gameId,accountId)
)
```
* 遊玩團隊紀錄資料表
```sql 
CREATE TABLE teamstats(
    gameId INT NOT NULL,
    teamId INT NOT NULL,
    baronKills BOOL NOT NULL,
    dominionVictoryScore INT NOT NULL,
    dragonKills INT NOT NULL,
    firstBaron BOOL NOT NULL,
    firstDragon  BOOL NOT NULL,
    firstInhibitor BOOL NOT NULL,
    firstRiftHerald BOOL NOT NULL,
    firstTower BOOL NOT NULL,
    inhibitorKills BOOL NOT NULL,
    riftHeraldKills INT NOT NULL,
    towerKills INT NOT NULL,
    vilemawKills INT NOT NULL,
    totalDamage INT NOT NULL,
    totalKills INT NOT NULL,
    PRIMARY KEY(gameId,teamId)
)
```
## 版本資訊   
* v2   
  - 2021.07.04.01  資料庫填充完成  
   
* v1  
  - 2020.08.07.24  注音近似  *ex: 口格摩會自動更正為寇格魔*  
  - 2020.08.08.01  圖片回傳版面更新  
  - 2020.08.08.02  更新提示字  
  - 2020.08.09.01  增加bp功能  
  - 2020.08.09.02  heroku config:add TZ="Asia/Taipei"  
  - 2020.08.10.01  APScheduler自動爬蟲  
  - 2020.08.15.01  加入隱藏積分  

