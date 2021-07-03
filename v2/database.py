import sqlite3
import os

class DBAgent():
    def __init__(self, path:os.PathLike=None) -> None:
        if path==None: path = "LOL.db"
        self.__con = sqlite3.connect("LOL.db")
        self.__cur = self.__con.cursor()

    def __del__(self):
        self.__cur.close()
        self.__con.close()

    def _CreateTableUser(self) -> None:
        self.__cur.execute("CREATE TABLE IF NOT EXISTS users(\
                    LineId TEXT PRIMARY KEY\
                    accoundId TEXT UNIQUE\
                    LineName TEXT NOT NULL UNIQUE\
                    LOLName TEXT NOT NULL UNIQUE)")
        self.__con.commit()

    def _CreateTableELO(self) -> None:
        self.__cur.execute("CREATE TABLE  IF NOT EXISTS elo(\
                    accoundId TEXT PRIMARY KEY\
                    gameMode TEXT NOT NULL,\
                    sqltime TIMESTAMP DEFAULT CURRENT_TIMESTAMP NOT NULL\
                    FOREIGN KEY (accoundId) REFERENCES users (accoundId) )")
        self.__con.commit()

    def _CreateTableGame(self) -> None:
        self.__cur.execute("CREATE TABLE IF NOT EXISTS game(\
                    gameId TEXT NOT NULL,\
                    accountId TEXT NOT NULL\
                    gameMode TEXT NOT NULL,\
                    gameVersion TEXT NOT NULL,\
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
                    firstBloodKill BOOL NOT NULL,\
                    firstTowerKill BOOL NOT NULL,\
                    PRIMARY KEY (gameId,accountId) )")
        self.con.commit()
                    
    def _CreateAllTables(self) -> None:
        self.__CreateTableUser()
        self.__CreateTableELO()
        self.__CreateTableGame()
        
    def _InsertUser(self) -> None:
        pass

    def _InsertELO(self) -> None:
        pass

    def _InsertGame(self) -> None:
        pass

    def Query(self, sql: str, param: list=None) -> list:
        try:
            if param==None:
                self.__cur.execute(sql)
            else:
                self.__cur.execute(sql,param)
            return self.__cur.fetchall()
        except sqlite3.Error:
            raise

if __name__ == "__main__":
    pass
