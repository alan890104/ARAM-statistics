import sqlite3
import os
import typing

class DBAgent():
    def __init__(self, path:os.PathLike=None) -> None:
        sqlite3.register_adapter(bool, lambda val: int(val))
        def dict_factory(cursor, row):
            d = {}
            for idx, col in enumerate(cursor.description):
                d[col[0]] = row[idx]
            return d
        if path==None: path = "LOL.db"
        self.__con = sqlite3.connect("LOL.db")
        self.__con.row_factory = dict_factory
        self.__cur = self.__con.cursor()

    def __del__(self):
        self.__con.close()

    def _CreateTableUser(self) -> None:
        self.__cur.execute("CREATE TABLE IF NOT EXISTS users( \
                    LineId TEXT PRIMARY KEY,\
                    accoundId TEXT UNIQUE,\
                    LineName TEXT NOT NULL UNIQUE,\
                    LOLName TEXT NOT NULL UNIQUE ) ")
        self.__con.commit()

    def _CreateTableELO(self) -> None:
        self.__cur.execute("CREATE TABLE  IF NOT EXISTS elo(\
                    accoundId TEXT PRIMARY KEY,\
                    gameMode TEXT NOT NULL,\
                    sqltime TIMESTAMP DEFAULT CURRENT_TIMESTAMP NOT NULL,\
                    FOREIGN KEY (accoundId) REFERENCES users (accoundId) )")
        self.__con.commit()

    def _CreateTableGame(self) -> None:
        self.__cur.execute("CREATE TABLE IF NOT EXISTS game(\
                    gameId TEXT NOT NULL,\
                    accountId TEXT NOT NULL,\
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
        
    def _InsertUser(self) -> None:
        pass

    def _InsertELO(self) -> None:
        pass

    def _InsertGame(self,param: typing.Iterable) -> None:
        self.__cur.execute("INSERT INTO game VALUES ({})".format(",".join("?"*len(param))) ,param)
        self.__con.commit()
    
    def _InsertManyGame(self, param: typing.Iterable) -> None:
        assert isinstance(param[0],list) or isinstance(param[0],tuple),"param should be 2d list or tuple."
        self.__cur.executemany("INSERT INTO game VALUES ({})".format(",".join("?"*len(param[0]))) ,param)
        self.__con.commit()

    def Query(self, sql: str, param: list=[]) -> list:
        self.__cur.execute(sql,param)
        return self.__cur.fetchall()

if __name__ == "__main__":
    pass