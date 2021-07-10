import asyncio
import aiohttp
import Database
import AccessGameData as AGD
from Crawler import ELOHelper
import Database as DB
import time

async def _GetRequest(url,session):
    try:
        async with session.get(url) as response:
            res = await response.json()
        return res
    except Exception as e:
        print(e)

async def _Master(URLs):
    '''
    Request Json file in parallel
    '''
    async with aiohttp.ClientSession() as session:
        ret = await asyncio.gather(*[_GetRequest(url, session) for url in URLs])
    return ret

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
                time.sleep(0.5)
            except IndexError:
                print(user_dict[accountId],'Finish')
                break
            except Exception as e:
                print(e)
                ERRORS.append([user_dict[accountId],idx])
    if len(ERRORS)!=0:
        AGD.JsonWrite({"errors":ERRORS},'log.json')

def _TeamInitializer(amount: int=5) -> None:
    '''
    ### Initialize the database with team statistics
    '''
    assert amount>0 and amount<=5 and isinstance(amount,int), "\033[91m int Amount>0 && Amount<=20 \033[0m" 
    Agent = DB.DBAgent()
    if Agent.CheckTableExist("teamstats"):
        raise Exception("\033[91m Table 'teamstats' already exist, please drop it first. \033[0m")
    Agent._CreateTableTeamStats()
    asyncio.set_event_loop_policy(asyncio.WindowsSelectorEventLoopPolicy()) # Need to use in window
    URLs = [AGD.GPREFIX+"stats/game/TW/"+str(GameId) for GameId in Agent.GetAllGameId()]
    for i in range(0,len(URLs),amount):
        print("This is time",i)
        URLChunk = URLs[i:i+amount]
        result = asyncio.run(_Master(URLChunk))
        for detail in result:
            try:
                stats = AGD.GameDetailReader(detail).format_list()
                Agent._InsertTeamStats(stats)
            except:
                print(detail)
        time.sleep(0.3)
    
def _ELOInitializer() -> None:
    '''
    ### Initialize the database with team statistics
    '''
    Agent = DB.DBAgent()
    if Agent.CheckTableExist("elo"):
        raise Exception("\033[91m Table 'elo' already exist, please drop it first. \033[0m")
    Agent._CreateTableELO()
    UserDict = Agent.GetUserDict()
    Helper = ELOHelper()
    InsertList = Helper.GetOverAllELO(UserDict)
    if len(InsertList)>0:
        Agent._InsertManyELO(InsertList)

def _Initializer() -> None:
    _UserInitializer()
    _GameInitializer()
    _TeamInitializer()
    _ELOInitializer()

def UpdateGameTeamTable(Agent: Database.DBAgent, amount: int=20, logging: bool=False) -> None:
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
    6. Update name if change
    6. Backup to tmp folder
    '''
    assert amount>0 and amount<=20 and isinstance(amount,int), "\033[91m int Amount>0 && Amount<=20 \033[0m"
    UserDict = Agent.GetUserDict()
    # Update game table
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
                if not Agent.CheckUserGameIdExist(id,gameid):
                    print(gameid," insertion!")
                    idx = NewData.index(gameid)
                    Agent._InsertGame(history_list[idx])
                    count+=1
                else:
                    if logging: print("Gameid:",gameid," is already exists!")
            if count<20: break
        print(UserDict[id],"Finish")

    # Update teamstats table
    for gameId in Agent.GetMissTeamStats():
        print("Teamstats add {}".format(gameId))
        detail = AGD.GetSingleGameDetail(gameId)
        TeamStats =  AGD.GameDetailReader(detail).format_list()
        Agent._InsertTeamStats(TeamStats)
        time.sleep(0.3)

    # Update users table
    for id in UserDict:
        history = AGD.GetPlayerHistory(id,0,1)
        player = AGD.HistoryReader(history).playerinfo()
        if player["summonerName"]!=UserDict[id]:
            print("Change {} to {}".format(UserDict[id],player["summonerName"]))
            Agent._UpdateUserName(id,player["summonerName"])
        time.sleep(0.1)

def UpdateVersion() -> None:
    '''
    if version != newversion:  
    1. update champion
    2. update item
    3. update spellname
    4. update __version__
    '''
    with open("__version__.py",'r') as F:
        OldVersion = F.read()
    CurrentVersion = AGD.GetVersion()
    if CurrentVersion!=OldVersion:
        with open("__version__.py",'w') as F:
            F.write('__version__ = "{}" '.format(CurrentVersion))
    Champ = AGD.GetChampName(CurrentVersion)
    Item  = AGD.GetItemName(CurrentVersion)
    spell = AGD.GetSpellName(CurrentVersion)
    AGD.JsonWrite(Champ,"static\champion.json")
    AGD.JsonWrite(Item,"static\item.json")
    AGD.JsonWrite(spell,"static\spell.json")
        
def UpdateELO() -> None:
    '''
    ### Initialize the database with team statistics
    '''
    Agent = DB.DBAgent()
    UserDict = Agent.GetUserDict()
    Helper = ELOHelper()
    InsertList = [_ for _ in Helper.GetLatestELO(UserDict) if not Agent.CheckELORecordExist(_[0],_[1],_[3])]
    if len(InsertList)>0:
        print("Detect Change on ELO, start to insert.")
        Agent._InsertManyELO(InsertList)

if __name__=="__main__":
    Agent = DB.DBAgent()
    UpdateGameTeamTable(Agent)
    # UpdateELO()