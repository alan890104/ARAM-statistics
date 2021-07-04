import Database
import AccessGameData as AGD
import datetime
import time
def _GameCrawler():
    '''
    ### Initialize the database with game data
    '''
    Agent = Database.DBAgent()
    Agent._CreateTableGame()
    ERRORS = []
    for name in ['alankingdom','WhiteClover','7184奇異博士','X嘻哈酷老頭兒X']:
        accountId = AGD.GetAccountID(name)
        for idx in range(0,10000,20):
            try:
                history = AGD.GetPlayerHistory(accountId,idx,idx+20)
                history_list = AGD.HistoryReader(history).format_list()
                Agent._InsertManyGame(history_list)
                time.sleep(0.1)
            except Exception as e:
                print(e)
                ERRORS.append([name,idx])
    if len(ERRORS)!=0:
        AGD.JsonWrite({"errors":ERRORS},'log.json')

def _UserCrawler():
    '''
    ### Initialize the database with users data
    '''
    namelist=['alankingdom','WhiteClover','7184奇異博士','X嘻哈酷老頭兒X']
    Agent = Database.DBAgent()
    Agent._CreateTableUser()
    for name in namelist:
        id = AGD.GetAccountID(name)
        Agent._InsertUser([id,name])
        print(name)
        time.sleep(0.1)

def UpdateGameData(Agent: Database.DBAgent):
    '''
    ### To update the game table EVERY INTERVAL
    #### Step:
    1. Get accountId from database
    2. Format into list
    3. Find the difference by new - old
    4. Write into game table
    '''
    IdList = Agent.GetIdByUsers()
    KeepQuery = True
    for id in IdList:
        OldData = Agent.GetRecentGameIds(id)
        while KeepQuery:
            history = AGD.GetPlayerHistory(id)
            HR = AGD.HistoryReader(history)
            history_list = HR.format_list()
            NewData      = HR.gameids()
            diff = list(set(NewData)-set(OldData))
            # Don't need to get history since all match
            if len(diff)==0:  KeepQuery = False 
            for gameid in diff:
                idx = NewData.index(gameid)
                Agent._InsertGame(history_list[idx])

if __name__=="__main__":
    pass

