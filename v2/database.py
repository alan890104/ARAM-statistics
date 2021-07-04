import os
import typing
import sqlite3
from datetime import timedelta,datetime

class DBAgent():
    def __init__(self, path:os.PathLike=None) -> None:
        '''
        ### Parameters:
        - path: specify db file path, if None, then use LOL.db as default.
        '''
        sqlite3.register_adapter(bool, lambda val: int(val))
        if path==None: path = "LOL.db"
        self.__con = sqlite3.connect("LOL.db")
        self.__con.row_factory = self.dict_factory
        self.__cur = self.__con.cursor()

    def __del__(self):
        self.__con.close()

    def dict_factory(self,cursor,row):
        d = {}
        for idx, col in enumerate(cursor.description):
            d[col[0]] = row[idx]
        return d

    def _ListExistTable(self) -> dict:
        self.__cur.execute("SELECT name FROM sqlite_master WHERE type='table'")
        return [ _['name'] for _ in self.__cur.fetchall()]
        
    def _CreateTableUser(self) -> None:
        self.__cur.execute("CREATE TABLE IF NOT EXISTS users( \
                            accountId INT UNIQUE PRIMARY KEY,\
                            LOLName TEXT NOT NULL UNIQUE ) ")
        self.__con.commit()

    def _CreateTableELO(self) -> None:
        self.__cur.execute("CREATE TABLE  IF NOT EXISTS elo(\
                    accoundId INT PRIMARY KEY,\
                    gameMode TEXT NOT NULL,\
                    sqltime TIMESTAMP DEFAULT CURRENT_TIMESTAMP NOT NULL,\
                    FOREIGN KEY (accoundId) REFERENCES users (accoundId) )")
        self.__con.commit()

    def _CreateTableGame(self) -> None:
        self.__cur.execute("CREATE TABLE IF NOT EXISTS game(\
                    gameId INT NOT NULL,\
                    accountId INT NOT NULL,\
                    gameMode TEXT NOT NULL,\
                    gameType TEXT NOT NULL,\
                    gameVersion TEXT NOT NULL,\
                    gameCreation DATETIME NOT NULL,\
                    gameDuration INT NOT NULL,\
                    teamId INT NOT NULL,\
                    championId INT NOT NULL,\
                    win INT NOT NULL,\
                    items TEXT NOT NULL,\
                    kills INT NOT NULL,\
                    deaths INT NOT NULL,\
                    assists INT NOT NULL,\
                    largestKillingSpree INT NOT NULL,\
                    largestMultiKill INT NOT NULL,\
                    doubleKills INT NOT NULL,\
                    tripleKills INT NOT NULL,\
                    quadraKills INT NOT NULL,\
                    pentaKills INT NOT NULL,\
                    unrealKills INT NOT NULL,\
                    totalDamageDealt INT NOT NULL,\
                    totalHeal INT NOT NULL,\
                    totalDamageTaken INT NOT NULL,\
                    timeCCingOthers INT NOT NULL,\
                    visionScore INT NOT NULL,\
                    goldEarned INT NOT NULL,\
                    totalMinionsKilled INT NOT NULL,\
                    buildingKills INT NOT NULL,\
                    champLevel INT NOT NULL,\
                    firstBloodKill BOOL NOT NULL,\
                    firstTowerKill BOOL NOT NULL,\
                    role TEXT,\
                    lane TEXT,\
                    PRIMARY KEY (gameId,accountId) )")
        self.__con.commit()
                    
    def _CreateAllTables(self) -> None:
        self._CreateTableUser()
        self._CreateTableELO()
        self._CreateTableGame()
        
    def _DestroyTableUser(self) -> None:
        self.__cur.execute("DROP TABLE IF EXISTS users")
        self.__con.commit()

    def _InsertUser(self,param: typing.Iterable) -> None:
        self.__cur.execute("INSERT INTO users VALUES ({})".format(",".join("?"*len(param))) ,param)
        self.__con.commit()

    def _InsertELO(self,param: typing.Iterable) -> None:
        self.__cur.execute("INSERT INTO elo VALUES ({})".format(",".join("?"*len(param))) ,param)
        self.__con.commit()

    def _InsertGame(self,param: typing.Iterable) -> None:
        self.__cur.execute("INSERT INTO game VALUES ({})".format(",".join("?"*len(param))) ,param)
        self.__con.commit()
    
    def _InsertManyGame(self, param: typing.Iterable) -> None:
        assert isinstance(param[0],list) or isinstance(param[0],tuple),"param should be 2d list or tuple."
        self.__cur.executemany("INSERT INTO game VALUES ({})".format(",".join("?"*len(param[0]))) ,param)
        self.__con.commit()

    def _Query(self, sql: str, param: list=[]) -> dict:
        self.__cur.execute(sql,param)
        return self.__cur.fetchall()
    
    def CheckTableExist(self, TableName: str) -> bool:
        '''
        ### Return
        - True:  table exists
        - False:  table not exists
        '''
        self.__cur.execute("SELECT name FROM sqlite_master WHERE type='table' AND name=?",[TableName,])
        return self.__cur.fetchone()!=None

    def CheckGameIdExist(self,gameId: int) -> bool:
        '''
        ### Return
        - True:  gameId exists
        - False:  gameId not exists
        '''
        self.__cur.execute("SELECT * FROM game WHERE gameId=?",[gameId,])
        return self.__cur.fetchone()!=None

    def GetUserDict(self, reverse=False) -> dict:
        '''
        ### Parameter
        - reverse
            - True  : a mapping from name to accountId
            - False : a mapping from accountId to name (DEFUALT)
        '''
        self.__cur.execute("SELECT * FROM users")
        if reverse:
            return { _['LOLName']:_['accountId'] for _ in self.__cur.fetchall()}
        else:
            return { _['accountId']:_['LOLName'] for _ in self.__cur.fetchall()}

    def GetIdByUsers(self) -> list:
        ''' Return a list with accountIds'''
        self.__cur.execute("SELECT DISTINCT accountId FROM users")
        return [ _['accountId'] for _ in self.__cur.fetchall()]

    def GetIdByGame(self) -> list:
        '''### This function will depreciate at product version\n
           ### Use GetIdByUsers() or GetUserDict() instead.
        '''
        print('\033[93m'+"GetIdByGame will Depreciate at product version. Use GetIdByUsers() or GetUserDict() instead."+'\033[0m')
        self.__cur.execute("SELECT DISTINCT accountId FROM game")
        return [ _['accountId'] for _ in self.__cur.fetchall()]

    def GetLatestGameId(self) -> list:
        self.__cur.execute("SELECT gameId, gameCreation FROM game ORDER BY gameCreation DESC")
        result = self.__cur.fetchone()
        return {result["gameId"]: datetime.utcfromtimestamp(result['gameCreation']/1000).strftime("%Y/%m/%d %H:%M:%S") }

    def GetRecentGameIds(self,accountId: str, size: int=20) -> list:
        self.__cur.execute("SELECT gameId FROM game WHERE accountId=? ORDER BY gameCreation DESC",[accountId,])
        return [ _['gameId'] for _ in self.__cur.fetchmany(size)]

    def GetWinRateByCond(self,accountId: str, category=False, threshold: int=10, **kwargs) -> dict:
        '''
        ### Parameters:
        - accountId : your id
        - category:
            - True  : Return winrate corresponding to gameMode(need to more than threshold)
            - False : Return overall winrate (DEFAULT)
        - theshold : unsigned int (look up category: True) DEFULT 10
        - gameMode : str , if gameMode is not None, category will be True
        - gameType : str  DEFAULT "MATCHED_GAME"
        - gameVersion : str DEFAULT all versions in database ex: 
        - gameCreation : INT specify the game create after param in milliseconds
        - gameDuration : INT specify the gameduration shorter than the param in seconds
        - teamId: INT 100(blue) 200(red)
        - championId : INT 
        - role : str DUO_SUPPORT/DUO/SOLO/DUO_CARRY/NONE
        - lane : str MIDDLE/JUNGLE/TOP/BOTTOM/NONE
        - sort : str 'gameMode' or 'ratio' (work when category=True)
        '''
        
        condition = " accountId=? "
        input_param = [accountId]
        if "gameType" in kwargs:
            condition += " AND gameType=? "
            input_param.append(kwargs["gameType"])
        else: # Set MATCHED_GAME as default (電腦場不計)
            condition += " AND gameType='MATCHED_GAME' " 
        if "gameMode" in kwargs:
            category = True
            condition += " AND gameMode=?"
            input_param.append(kwargs["gameMode"])
        if "gameVersion" in kwargs:
            condition += " AND gameVersion=? "
            input_param.append(kwargs["gameVersion"])
        if "gameCreation" in kwargs:
            condition += " AND gameCreation>=? "
            input_param.append(kwargs["gameCreation"])
        if "gameDuration" in kwargs:
            condition += " AND gameDuration<=? "
            input_param.append(kwargs["gameDuration"])
        if "teamId" in kwargs:
            condition += " AND teamId=? "
            input_param.append(kwargs["teamId"])
        if "championId" in kwargs:
            condition += " AND championId=? "
            input_param.append(kwargs["championId"])
        if "role" in kwargs:
            condition += " AND role=? "
            input_param.append(kwargs["role"])
        if "lane" in kwargs:
            condition += " AND lane=? "
            input_param.append(kwargs["lane"])
        if category and "sort" in kwargs and kwargs['sort']=='ratio':
            order_way = " ORDER BY ratio DESC "
        else:
            order_way = " ORDER BY gameMode "

        if not category:
            self.__cur.execute("SELECT COUNT(*) as total, ROUND((CAST(SUM(win) AS FLOAT)/CAST(COUNT(win) AS FLOAT)),4) as ratio FROM game\
                WHERE {}".format(condition),input_param)
            return self.__cur.fetchall()[0]
        else:
            self.__cur.execute("SELECT gameMode,COUNT(*) as total,ROUND((CAST(SUM(win) AS FLOAT)/CAST(COUNT(win) AS FLOAT)),4) as ratio FROM game\
                WHERE {} GROUP BY gameMode HAVING COUNT(win)>{} {}".format(condition,threshold,order_way),input_param)
            return { _['gameMode']:{"ratio":_['ratio'],"total":_["total"]} for _ in self.__cur.fetchall() }

    def GetTotalPlayingTime(self,accountId: str) -> timedelta:
        '''### Total playing time in second'''
        self.__cur.execute("SELECT SUM(gameDuration) as time FROM game WHERE accountId=?",[accountId,])
        return timedelta(seconds=self.__cur.fetchone()['time'])

    def GetDamageImportance(self,accountId: str, category=False, threshold: int=10, **kwargs) -> dict:
        '''
        ### Parameters:
        - accountId : your id
        - category:
            - True  : Return DamageImportance corresponding to gameMode(need to more than threshold)
            - False : Return overall DamageImportance (DEFAULT)
        - theshold : unsigned int (look up category: True) DEFULT 10
        - gameMode : str , if gameMode is provided, category set to True
        - gameType : str  DEFAULT "MATCHED_GAME"
        - gameVersion : str DEFAULT all versions in database ex: 
        - gameCreation : INT specify the game create after param in milliseconds
        - gameDuration : INT specify the gameduration shorter than the param in seconds
        - teamId: INT 100(blue) 200(red)
        - championId : INT 
        - role : str DUO_SUPPORT/DUO/SOLO/DUO_CARRY/NONE
        - lane : str MIDDLE/JUNGLE/TOP/BOTTOM/NONE
        - sort : str 'gameMode' or 'ratio' (work when category=True)
        '''
        
        condition = " game.accountId=? "
        input_param = [accountId]
        if "gameType" in kwargs:
            condition += " AND gameType=? "
            input_param.append(kwargs["gameType"])
        else: # Set MATCHED_GAME as default (電腦場不計)
            condition += " AND gameType='MATCHED_GAME' " 
        if "gameMode" in kwargs:
            category = True
            condition += " AND gameMode=?"
            input_param.append(kwargs["gameMode"])
        if "gameVersion" in kwargs:
            condition += " AND gameVersion=? "
            input_param.append(kwargs["gameVersion"])
        if "gameCreation" in kwargs:
            condition += " AND gameCreation>=? "
            input_param.append(kwargs["gameCreation"])
        if "gameDuration" in kwargs:
            condition += " AND gameDuration<=? "
            input_param.append(kwargs["gameDuration"])
        if "teamId" in kwargs:
            condition += " AND teamId=? "
            input_param.append(kwargs["teamId"])
        if "championId" in kwargs:
            condition += " AND championId=? "
            input_param.append(kwargs["championId"])
        if "role" in kwargs:
            condition += " AND role=? "
            input_param.append(kwargs["role"])
        if "lane" in kwargs:
            condition += " AND lane=? "
            input_param.append(kwargs["lane"])
        if category and "sort" in kwargs and kwargs['sort']=='ratio':
            order_way = " ORDER BY ratio DESC "
        else:
            order_way = " ORDER BY gameMode "
        
        if not category:
            self.__cur.execute("SELECT CAST(SUM(totalDamageDealt*(win*2-1)) AS FLOAT) / SUM(kills) as ratio\
                FROM game WHERE {}".format(condition),input_param)
        else:
            self.__cur.execute("SELECT gameMode, CAST(SUM(totalDamageDealt*(win*2-1)) AS FLOAT) / SUM(kills) as ratio\
                FROM game WHERE {} GROUP BY gameMode HAVING COUNT(win)>{} {}".format(condition,threshold,order_way),input_param)
        return self.__cur.fetchone()

    def GetSpecializeChampion(self,accountId: str, gameMode:str,size: int=3,threshold: int=20) -> dict:
        '''
        Get user specialization champion
        ### Parameter
        - gameMode: specify gameMode. ARAM/CLASSIC/ONEFORALL/URF/NEXUSBLITZ/KINGPORO
        - size: the amout of output. DEFAULT 3
        - threshold: winrate calculate threshold. DEFAULT 30
        ### Return
        - key: champion id
        - value: winrate
        '''
        assert isinstance(threshold,int) and threshold>0,"threshold is an non-zero integer"
        param_list = [accountId,gameMode]
        year_ago = round((datetime.now() - timedelta(days=365)).timestamp()*1000)
        condition = " accountId=? AND gameType='MATCHED_GAME' AND gameDuration>=900 AND gameCreation>={} AND gameMode=? ".format(year_ago)
        self.__cur.execute("SELECT championId, ROUND(CAST(SUM(win) AS FLOAT)/COUNT(win),4) as ratio FROM game\
        WHERE {} GROUP BY championId HAVING COUNT(win)>{}  AND ratio>=0.5 ORDER BY ratio DESC".format(condition,threshold),param_list)
        return {_['championId']:_['ratio'] for _ in self.__cur.fetchmany(size)}

    def GetSpecializeLane(self,accountId: str, size: int=3,threshold: int=20) -> dict:
        '''
        Get user specialization lane
        ### Parameter
        - gameMode: specify gameMode. ARAM/CLASSIC/ONEFORALL/URF/NEXUSBLITZ/KINGPORO
        - size: the amout of output. DEFAULT 3
        - threshold: winrate calculate threshold. DEFAULT 30
        ### Return
        - key: lane
        - value: winrate
        '''
        assert isinstance(threshold,int) and threshold>0,"threshold is an non-zero integer"
        param_list = [accountId]
        year_ago = round((datetime.now() - timedelta(days=365)).timestamp()*1000)
        condition = " accountId=? AND gameType='MATCHED_GAME' AND gameDuration>=900 AND gameCreation>={} AND gameMode='CLASSIC' ".format(year_ago)
        self.__cur.execute("SELECT lane, ROUND(CAST(SUM(win) AS FLOAT)/COUNT(win),4) as ratio FROM game\
        WHERE {} GROUP BY lane HAVING COUNT(win)>{}  AND ratio>=0.5 ORDER BY ratio DESC".format(condition,threshold),param_list)
        return {_['lane']:_['ratio'] for _ in self.__cur.fetchmany(size)}

    def GetBestKDA(self,accountId: str) -> dict:
        self.__cur.execute("SELECT gameId,gameCreation,gameDuration ,gameMode,championId ,\
        ROUND(AVG( CAST( (kills+assists) AS FLOAT) /  (CASE WHEN deaths==0 THEN 1 ELSE deaths END) ),2) as kda\
        FROM game WHERE accountId=? AND gameType='MATCHED_GAME' AND gameMode in ('CLASSIC','URF','ARAM','ONEFORALL') \
        GROUP BY championId,gameMode ORDER BY kda DESC",[accountId])
        return self.__cur.fetchall()[0]

def _tWinRate():
    Agent = DBAgent()
    UserDict = Agent.GetUserDict()
    print("###########ALL############")
    for id in UserDict:
        winrate = Agent.GetWinRateByCond(id)
        print(UserDict[id],winrate)
    print("\n##########CATEGORY############")
    for id in UserDict:
        winrate = Agent.GetWinRateByCond(id,category=True)
        print(UserDict[id],winrate)
    print("\n##########BLUE TEAM############")
    for id in UserDict:
        winrate = Agent.GetWinRateByCond(id,teamId=100)
        print(UserDict[id],winrate)
    print("\n##########15min############")
    for id in UserDict:
        winrate = Agent.GetWinRateByCond(id,gameDuration=60*15)
        print(UserDict[id],winrate)
    print("\n##########BOTTOM LANE############")
    for id in UserDict:
        winrate = Agent.GetWinRateByCond(id,lane="BOTTOM",gameMode='ARAM')
        print(UserDict[id],winrate)
    print()

def _tPlayingTime():
    Agent = DBAgent()
    UserDict = Agent.GetUserDict()
    for id in UserDict:
        time = Agent.GetTotalPlayingTime(id)
        print(UserDict[id],time)

def _tDamageImportance():
    Agent = DBAgent()
    UserDict = Agent.GetUserDict()
    for id in UserDict:
        time = Agent.GetDamageImportance(id,category=True)
        print(UserDict[id],time)

def _tSpecializationChamp():
    import AccessGameData as AGD
    version = AGD.GetVersion()
    champ = AGD.GetChampName(version)
    Agent = DBAgent()
    UserDict = Agent.GetUserDict()
    print("###########ARAM#############")
    for id in UserDict:
        sp = Agent.GetSpecializeChampion(id,gameMode='ARAM')
        if len(sp)>0: print(UserDict[id],':')
        for champid in sp:
            print("\t{}: {}".format(champ[champid][1],sp[champid]))
    print("###########一般對戰#############")
    for id in UserDict:
        sp = Agent.GetSpecializeChampion(id,gameMode='CLASSIC')
        if len(sp)>0: print(UserDict[id],':')
        for champid in sp:
            print("\t{}: {}".format(champ[champid][1],sp[champid]))
    print("###########阿福快打#############")
    for id in UserDict:
        sp = Agent.GetSpecializeChampion(id,gameMode='URF')
        if len(sp)>0: print(UserDict[id],':')
        for champid in sp:
            print("\t{}: {}".format(champ[champid][1],sp[champid]))

def _tSpecializationLane():
    Agent = DBAgent()
    UserDict = Agent.GetUserDict()
    print("###########一般對戰 專精路線#############")
    for id in UserDict:
        sp = Agent.GetSpecializeLane(id)
        if len(sp)>0: print(UserDict[id],':')
        for lane in sp:
            print("\t{}: {}".format(lane,sp[lane]))

def _tKDA():
    Agent = DBAgent()
    UserDict = Agent.GetUserDict()
    print("###########KDA#############")
    for id in UserDict:
        print(UserDict[id],Agent.GetBestKDA(id))

if __name__ == "__main__":
    pass