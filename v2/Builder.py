import Database
import AccessGameData as AGD
import Database as DB
import time
import os

def _UserInitializer() -> None:
    '''
    ### Initialize the database with users data
    '''
    namelist=['alankingdom','WhiteClover','7184奇異博士','X嘻哈酷老頭兒X','fgjyh','freaksega','西巴西巴蠢','接頭霸王Karyl']
    Agent = Database.DBAgent()
    if Agent.CheckTableExist("users"):
        raise Exception("\033[91m Table 'users' already exist, please drop it first. \033[0m")
    Agent._CreateTableUser()
    for name in namelist:
        id = AGD.GetAccountID(name)
        Agent._InsertUser([id,name])
        print(name)
        time.sleep(0.1)

def _GameInitializer(amount: int=20) -> None:
    '''
    ### Initialize the database with game data
    '''
    assert amount>0 and amount<=20 and isinstance(amount,int), "\033[91m int Amount>0 && Amount<=20 \033[0m"
    Agent = Database.DBAgent()
    if Agent.CheckTableExist("game"):
        raise Exception("\033[91m Table 'game' already exist, please drop it first. \033[0m")
    Agent._CreateTableGame()
    user_dict = Agent.GetUserDict()
    ERRORS = []
    for accountId in user_dict:
        for idx in range(0,10000,amount):
            try:
                history = AGD.GetPlayerHistory(accountId,idx,idx+amount)
                history_list = AGD.HistoryReader(history).format_list()
                Agent._InsertManyGame(history_list)
                time.sleep(0.1)
            except IndexError:
                print(user_dict[accountId],'Finish')
                break
            except Exception as e:
                print(e)
                ERRORS.append([user_dict[accountId],idx])
    if len(ERRORS)!=0:
        AGD.JsonWrite({"errors":ERRORS},'log.json')

def _TeamInitializer() -> None:
    Agent = Database.DBAgent()
    if Agent.CheckTableExist("teamstats"):
        raise Exception("\033[91m Table 'teamstats' already exist, please drop it first. \033[0m")
    Agent._CreateTableTeamStats()
    user_dict = Agent.GetUserDict()
    ERRORS = {}
    TeamStats = []
    for accountId in user_dict:
        gameid_list = Agent.GetRecentGameIds(accountId,size=-1)
        for gameid in gameid_list:
            try:
                detail = AGD.GetSingleGameDetail(gameid)
                data = AGD.GameDetailReader(detail).format_list()
                TeamStats.extend(data)
            except Exception as e:
                ERRORS[gameid] = e
            finally:
                time.sleep(0.1)
        print(user_dict[accountId],"finish")
    Agent._InsertTeamStats(TeamStats)
    if len(ERRORS)>0: AGD.JsonWrite(ERRORS,'log/TeamInitError.json')

def _Initializer() -> None:
    _UserInitializer()
    _GameInitializer()
    _TeamInitializer()

def UpdateDatabase(Agent: Database.DBAgent, amount: int=20, logging: bool=True) -> None:
    '''
    ### To update the game table EVERY INTERVAL
    ### Parameter
    - Agent  : Database.DBAgent()
    - amount : Size to query new data (DEFAULT MAX 20)
    - logging : Print Noisy Message (DEFAULT True)
    #### Step:
    1. Get accountId from database
    2. Format into list
    3. Check if gameid in list
    4. Write into game table
    5. Load TeamStats
    6. Backup to tmp folder
    '''
    assert amount>0 and amount<=20 and isinstance(int,amount), "\033[91m int Amount>0 && Amount<=20 \033[0m"
    UserDict = Agent.GetUserDict()
    NewGameIds = []
    for id in UserDict:
        begin=0
        while True:
            history = AGD.GetPlayerHistory(id,begin,begin+amount)
            begin+=amount
            HR = AGD.HistoryReader(history)
            history_list = HR.format_list()
            NewData      = HR.gameids()
            count = 0
            for gameid in NewData:
                if not Agent.CheckGameIdExist(gameid):
                    print(gameid," insertion!")
                    idx = NewData.index(gameid)
                    Agent._InsertGame(history_list[idx])
                    count+=1
                    NewGameIds.append(gameid)
                else:
                    if logging: print("Gameid:",gameid," is already exists!")
            if count<20: break
        print(UserDict[id],"Finish")
    TeamStats = [] 
    for gameId in NewGameIds:
        detail = AGD.GetSingleGameDetail(gameId)
        TeamStats.extend(AGD.GameDetailReader(detail).format_list())
    Agent._InsertTeamStats(TeamStats)
    Agent._Backup()

    
if __name__=="__main__":
    Agent = Database.DBAgent()
    Agent._Query("DROP TABLE IF EXISTS teamstats")
    # Agent._Query("SELECT * FROM teamstats")
    # _TeamInitializer()