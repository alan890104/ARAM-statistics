import Database
import AccessGameData as AGD
import Database as DB
import time

def _GameCrawler(amount: int=20):
    '''
    ### Initialize the database with game data
    '''
    assert amount>0 and amount<=20, "\033[91m Amount>0 && Amount<=20 \033[0m"
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

def _UserCrawler():
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

def _Initializer():
    _UserCrawler()
    _GameCrawler()

def UpdateGameData(Agent: Database.DBAgent) -> None:
    '''
    ### To update the game table EVERY INTERVAL
    #### Step:
    1. Get accountId from database
    2. Format into list
    3. Check if gameid in list
    4. Write into game table
    '''
    UserDict = Agent.GetUserDict()
    for id in UserDict:
        begin=0
        while True:
            history = AGD.GetPlayerHistory(id,begin,begin+20)
            begin+=20
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
                else:
                    print("Gameid:",gameid," is already exists!")
            if count<20: break
        print(UserDict[id],"Finish")


    
if __name__=="__main__":
    pass