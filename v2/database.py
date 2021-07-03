import datetime
import os
import typing
import sqlite3
from datetime import timedelta

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
    
    def GetUserDict(self, reverse=False) -> dict:
        '''
        ### Parameter
        - reverse
            - True  : a mapping from name to accountId
            - False : a mapping from accountId to name
        '''
        self.__cur.execute("SELECT * FROM users")
        if reverse:
            return { _['LOLName']:_['accountId'] for _ in self.__cur.fetchall()}
        else:
            return { _['accountId']:_['LOLName'] for _ in self.__cur.fetchall()}

    def GetIdByUsers(self) -> list:
        self.__cur.execute("SELECT DISTINCT accountId FROM users")
        return [ _['accountId'] for _ in self.__cur.fetchall()]

    def GetIdByGame(self) -> list:
        '''### This function will depreciate at next version\n
           ### Use GetIdByUsers() instead.
        '''
        print('\033[93m'+"GetIdByGame will Depreciate at next version. Use GetIdByUsers() instead."+'\033[0m')
        self.__cur.execute("SELECT DISTINCT accountId FROM game")
        return [ _['accountId'] for _ in self.__cur.fetchall()]

    def GetRecentGameIds(self,accountId: str, size: int=20) -> list:
        self.__cur.execute("SELECT gameId FROM game WHERE accountId=? ORDER BY gameCreation DESC",[accountId,])
        return [ _['gameId'] for _ in self.__cur.fetchmany(size)]

    def GetWinRateByCond(self,accountId: str, category=False, threshold=10, **kwargs) -> dict:
        '''
        ### Parameters:
        - accountId : your id
        - category:
            - True  : Return winrate corresponding to gameMode(need to more than threshold)
            - False : Return overall winrate
        - gameCreation : INT specify the game create after param in milliseconds
        - gameDuration : INT specify the gameduration shorter than the param in senconds
        - teamId: INT 100(blue) 200(red)
        - championId : INT
        - role : str
        - lane : str
        '''
        condition = " accountId=? "
        if "gameCreation" in kwargs:
            condition += " AND gameCreation>? "
        if "gameDuration" in kwargs:
            condition += " AND gameDuration<? "
        if "teamId" in kwargs:
            condition += " AND teamId=? "
        if "championId" in kwargs:
            condition += " AND championId=? "
        if "role" in kwargs:
            condition += " AND role=? "
        if "lane" in kwargs:
            condition += " AND lane=? "

        input_param = [accountId]
        input_param.extend(list(kwargs.values()))

        if not category:
            self.__cur.execute("SELECT ROUND((CAST(SUM(win) AS FLOAT)/CAST(COUNT(win) AS FLOAT)),4) as ratio FROM game\
                WHERE {}".format(condition),input_param)
            return {"all":self.__cur.fetchone()['ratio']}
        else:
            self.__cur.execute("SELECT gameMode,ROUND((CAST(SUM(win) AS FLOAT)/CAST(COUNT(win) AS FLOAT)),4) as ratio FROM game\
                WHERE {} GROUP BY gameMode HAVING COUNT(win)>{} ORDER BY ratio DESC".format(condition,threshold),input_param)
            return { _['gameMode']:_['ratio'] for _ in self.__cur.fetchall() }

    def GetTotalPlayingTime(self,accountId: str) -> datetime.timedelta:
        '''### Total playing time in second'''
        self.__cur.execute("SELECT SUM(gameDuration) as time FROM game WHERE accountId=?",[accountId,])
        return timedelta(seconds=self.__cur.fetchone()['time'])

if __name__ == "__main__":
    pass