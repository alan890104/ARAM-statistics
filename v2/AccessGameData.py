# reference:
'''
https://github.com/nxhdev2002/checkLOLMatchHistory/blob/9a005e76791acf13ce71017f71ffaa0cff364413/lolmatchhistory.js
'''
import os
import json
from sys import int_info, version
import typing
import requests

Tier = {0:"鐵牌Ⅳ",671:"鐵牌Ⅲ",712:"鐵牌Ⅱ",754:"鐵牌Ⅰ",834:"銅牌Ⅳ",937:"銅牌Ⅲ",1018:"銅牌Ⅱ",1073:"銅牌Ⅰ",1127:"銀牌Ⅳ",1196:"銀牌Ⅲ",1259:"銀牌Ⅱ",1306:"銀牌Ⅰ",1594:"金牌Ⅳ",1722:"金牌Ⅲ",1781:"金牌Ⅱ",1867:"金牌Ⅰ",1926:"白金Ⅳ",2019:"白金Ⅲ",2163:"白金Ⅱ",2222:"白金Ⅰ",2435:"鑽石Ⅳ",2537:"鑽石Ⅲ",2586:"鑽石Ⅱ",2650:"鑽石Ⅰ",2713:"大師",2803:"宗師",2876:"菁英"}

GPREFIX = "https://acs-garena.leagueoflegends.com/v1/"
DPREFIX = "https://ddragon.leagueoflegends.com/"

def GetVersion() -> str:
    '''Get LOL current version'''
    res = requests.get(DPREFIX+"api/versions.json")
    return res.json()[0]
    
def GetChampName(version: str) -> dict:
    '''
    Get champion name  
    ### Parameters
    version: str  
        - Current version from function GetVersion()  
    
    ### Returns
    - dict  
        - key: int
        - value: list [EN,zh_TW]
    '''
    res = requests.get(DPREFIX+"cdn/{}/data/zh_TW/champion.json".format(version))
    info = res.json()
    ret = dict()
    for champ in info['data']:
        key = info['data'][champ]['key']
        name_EN = info['data'][champ]['id']
        name_zhTW = info['data'][champ]['name']
        ret[int(key)] = [name_EN,name_zhTW]
    return ret

def GetItemName(version: str) -> dict:
    '''
    Get item name  
    ### Parameters
    version: str  
        - Current version from function GetVersion()  
    
    ### Returns
    - dict  
        - key: int
        - value: item name in zh_TW 
    '''
    res = requests.get(DPREFIX+"cdn/{}/data/zh_TW/item.json".format(version))
    info = res.json()
    ret = dict()
    for id in info['data']:
        ret[int(id)] = info['data'][id]['name']
    return ret

def GetSpellName(version: str) -> dict:
    '''
    Get spell name  
    ### Parameters
    version: str  
        - Current version from function GetVersion()  
    
    ### Returns
    - dict  
        - key: int
        - value: list [EN,zh_TW]
    '''
    res = requests.get(DPREFIX+"cdn/{}/data/zh_TW/summoner.json".format(version))
    info = res.json()
    ret = dict()
    for skill in info['data']:
        obj = info['data'][skill]
        ret[int(obj['key'])] = [obj['id'],obj['name']]
    return ret

def GetChampDetail(version: str, ChampName: str) -> dict:
    res = requests.get(DPREFIX+"cdn/{}/data/zh_TW/champion/{}.json".format(version,ChampName))
    return res.json()

def _DownloadProfileIcon(version: str, id: int) -> None:
    res = requests.get(DPREFIX+"cdn/{}/img/profileicon/{}.png".format(version,id),stream=True)
    if res.status_code==200:
        with open("ProfileIcon/{}.png".format(id),'wb') as F:
            for chunk in res: 
                F.write(chunk)

def _DownloadChampImg(version: str, ChampName: str) -> None:
    res = requests.get(DPREFIX+"cdn/{}/img/champion/{}.png".format(version,ChampName),stream=True)
    if res.status_code==200:
        with open("ChampImg/{}.png".format(ChampName),'wb') as F:
            for chunk in res: 
                F.write(chunk)

def _DownloadItemImg(version: str, id: int) -> None:
    res = requests.get(DPREFIX+"cdn/{}/img/item/{}.png".format(version,id),stream=True)
    if res.status_code==200:
        with open("ItemImg/{}.png".format(id),'wb') as F:
            for chunk in res: 
                F.write(chunk)

def _DownloadSpell(version: str, SpellName: str) -> None:
    res = requests.get(DPREFIX+"cdn/{}/img/spell/{}.png".format(version,SpellName),stream=True)
    if res.status_code==200:
        with open("Spell/{}.png".format(SpellName),'wb') as F:
            for chunk in res: 
                F.write(chunk)

def _DownloadChampSkin(version: str, ChampName: str) -> None:
    detail = GetChampDetail(version,ChampName)
    Latest_Skin_idx = detail["data"][ChampName]["skins"][-1]["num"]
    res = requests.get(DPREFIX+"cdn/img/champion/loading/{}_{}.jpg".format(ChampName,Latest_Skin_idx),stream=True)
    if res.status_code==200:
        with open("ChampSkin/{}.jpg".format(ChampName),'wb') as F:
            for chunk in res: 
                F.write(chunk)

def _EncodeURI(name: str) -> str:
    '''Same as EncodeURI in JavaScript'''
    return requests.utils.quote(name.encode('utf-8'), safe='~@#$&()*!+=:;,.?/\'')

def GetAccountID(name: str) -> typing.Union[str,None]:
    '''
    Get account id by user name 
    ### Parameters
    name: str  
        - Your name in LOL. ex: 7184奇異博士 
    
    ### Returns
    - str:
        - account id 
    
    - None
        - If user do not exist
    '''
    try:
        res = requests.get(GPREFIX+"players?name="+_EncodeURI(name)+"&region=TW")
        AccountID = res.json()["accountId"]
        return AccountID
    except:
        return None

def GetPlayerHistory(AccountId: int, Begin=0, End=20)-> dict:
    '''
    Get player history with a specify amount
    ### Parameters
    - AccountId: int  
        - The output of GetAccountID()
    - Begin: int  
        - The start index, default 0
    - End: int  
        - The last index, default 20
    
    ### Returns
    - dict  
        - player history
    
    ### Raise
    - When begin>End
    '''
    assert Begin>=0 and Begin<=End, "Begin is less than or equal to End."
    res = requests.get(GPREFIX+"stats/player_history/TW/{}?begIndex={}&endIndex={}".format(AccountId,Begin,End))
    return res.json()
        
def GetSingleGameDetail(GameId: int)-> dict:
    res = requests.get(GPREFIX+"stats/game/TW/"+str(GameId))
    return res.json()

def GetGameTimeline(GameId: int)-> dict:
    res = requests.get(GPREFIX+"stats/game/TW/{}/timeline".format(GameId))
    return res.json()

def GetELO():
    pass
    # r = scraper.get("https://lol.moa.tw/match/show/1941288255/16803530")
    # return r.text

def ELOTransform(Tier: dict,value: int) -> str:
    '''
    ### Parameter
    - ref : a dict of reference tier
    - value : your ELO (隱分)

    ### Return
    - str : your tier
    '''
    key = list(Tier.keys())
    left = 0
    right = len(key)-1
    while left<right:
        mid = (left+right)//2
        if value>key[mid]:
            left = mid+1
        elif value<key[mid]:
            right = mid
        else:
            return Tier[key[mid]]
    return Tier[key[left]] if left==0 or value>=key[left] else Tier[key[left-1]]

def JsonWrite(data: dict, filename: os.PathLike, mode='w') -> None:
    print("\033[93mWarning: Python Json dump will convert int keys into string.\033[0m")
    with open(filename,mode,encoding='utf-8') as F:
        json.dump(data,F,ensure_ascii=False,indent=4, sort_keys=True,)

def JsonRead(filename: os.PathLike, mode='r') -> dict:
    with open(filename,mode,encoding='utf-8') as F:
        data = json.load(F)
    return data

class HistoryReader():
    def __init__(self,history: dict) -> None:
        '''### Parse the result from GetPlayerHistory() function '''
        self.platformId = history['platformId'] if 'platformId' in history else 'TW'
        self.accountId = history['accountId']
        self.games = self._Games(**history['games'])
        self.shownQueues = history['shownQueues']
    def form(self) -> dict:
        '''format important attribute'''
        obj = dict()
        obj['accountId'] = self.accountId
        obj['playerName'] = self.playerName()
        game_list = list()
        for g in self.games.games:
            game_info = dict()
            game_info['gameId'] = g.gameId
            game_info['gameMode'] = g.gameMode
            game_info['gameVersion'] = g.gameVersion
            game_info['gameCreation'] = g.gameCreation
            game_info['gameDuration'] = g.gameDuration
            game_info['teamId'] = g.participants.teamId
            game_info['championId'] = g.participants.championId
            stats_dict = dict()
            stats = g.participants.stats
            stats_dict['win'] = stats.win
            stats_dict['item'] = [stats.__dict__['item{}'.format(x)] for x in range(7)]
            stats_dict['kda'] = (stats.kills,stats.deaths,stats.assists)
            stats_dict['largestKillingSpree'] = stats.largestKillingSpree
            stats_dict['largestMultiKill'] = stats.largestMultiKill
            stats_dict['doubleKills'] = stats.doubleKills
            stats_dict['tripleKills'] = stats.tripleKills
            stats_dict['quadraKills'] = stats.quadraKills
            stats_dict['pentaKills'] = stats.pentaKills
            stats_dict['unrealKills'] = stats.unrealKills
            stats_dict['totalDamageDealt'] = stats.totalDamageDealt
            stats_dict['largestCriticalStrike'] = stats.largestCriticalStrike
            stats_dict['totalHeal'] = stats.totalHeal
            stats_dict['visionScore'] = stats.visionScore
            stats_dict['timeCCingOthers'] = stats.timeCCingOthers
            stats_dict['totalDamageTaken'] = stats.totalDamageTaken
            stats_dict['goldEarned'] = stats.goldEarned
            stats_dict['totalMinionsKilled'] = stats.neutralMinionsKilled+stats.totalMinionsKilled
            stats_dict['buildingKills'] = stats.turretKills+stats.inhibitorKills
            stats_dict['champLevel'] = stats.champLevel
            stats_dict['firstBloodKill'] = stats.firstBloodKill
            stats_dict['firstTowerKill'] = stats.firstTowerKill
            game_info['stats'] = stats_dict
            game_list.append(game_info)
        obj['gamelist'] = game_list
        return obj   
    def format_list(self) -> list:
        '''### DESIGN FOR -> INSERT INTO GAME TABLE
        - format important attribute '''
        game_list = list()
        for g in self.games.games:
            game_info = list()
            game_info.append(g.gameId)
            game_info.append(self.accountId)
            game_info.append(g.gameMode)
            game_info.append(g.gameType)
            game_info.append(g.gameVersion)
            game_info.append(g.gameCreation)
            game_info.append(g.gameDuration)
            game_info.append(g.participants.teamId)
            game_info.append(g.participants.championId)
            stats = g.participants.stats
            game_info.append(stats.win)
            game_info.append(" ".join([str(stats.__dict__['item{}'.format(x)]) for x in range(7)]))
            game_info.append(stats.kills)
            game_info.append(stats.deaths)
            game_info.append(stats.assists)
            game_info.append(stats.largestKillingSpree)
            game_info.append(stats.largestMultiKill)
            game_info.append(stats.doubleKills)
            game_info.append(stats.tripleKills)
            game_info.append(stats.quadraKills)
            game_info.append(stats.pentaKills)
            game_info.append(stats.unrealKills)
            game_info.append(stats.totalDamageDealt)
            game_info.append(stats.totalHeal)
            game_info.append(stats.totalDamageTaken)
            game_info.append(stats.timeCCingOthers)
            game_info.append(stats.visionScore)            
            game_info.append(stats.goldEarned)
            game_info.append(stats.neutralMinionsKilled+stats.totalMinionsKilled)
            game_info.append(stats.turretKills+stats.inhibitorKills)
            game_info.append(stats.champLevel)
            game_info.append(stats.firstBloodKill)
            game_info.append(stats.firstTowerKill)
            game_info.append(g.participants.timeline.role)
            game_info.append(g.participants.timeline.lane)
            game_list.append(game_info)
        return game_list   
    def result(self) -> list:
        '''Win or Lose list of all games'''
        return [self.games.games[x].participants.stats.win for x in range(self.__len__())]
    def playerinfo(self) -> dict:
        '''Return summonerName, summonerId and accountId'''
        play = self.games.games[0].participantIdentities.player
        return {"summonerName":play.summonerName,"summonerId":play.summonerId,"accountId":play.accountId}
    def versions(self) -> list:
        '''Get the version list of all games'''
        return list(set([self.games.games[x].gameVersion for x in range(self.__len__())]))
    def gameids(self) -> list:
        '''Return all gameids'''
        return [self.games.games[x].gameId for x in range(self.__len__())]
    def totalGames(self) -> int:
        '''Return game count'''
        return self.games.gameCount
    def index(self) -> tuple:
        '''Return tuple (Start index, End index)'''
        return (self.games.gameIndexBegin,self.games.gameIndexEnd)
    def totalPlayingTime(self) -> int:
        '''Return total playing time in second'''
        interval = self.games.gameIndexEnd-self.games.gameIndexBegin
        return sum([self.games.games[x].gameDuration for x in range(interval)])
    def __len__(self):
        return self.games.gameIndexEnd-self.games.gameIndexBegin
    class _Games:
        def __init__(self,**kwargs) -> None:
            self.gameIndexBegin = kwargs['gameIndexBegin']
            self.gameIndexEnd = kwargs['gameIndexEnd']
            self.gameTimestampBegin = kwargs['gameTimestampBegin']
            self.gameTimestampEnd = kwargs['gameTimestampEnd']
            self.gameCount = kwargs['gameCount']
            self.games = [self._SingleGameReader(**k) for k in kwargs['games']]
        class _SingleGameReader:
            def __init__(self,**kwargs) -> None:
                self.gameId = None
                self.platformId = None
                self.gameCreation = None
                self.gameDuration = None
                self.queueId = None
                self.mapId = None
                self.seasonId = None
                self.gameVersion = None
                self.gameMode = None
                self.gameType = None
                for x in kwargs:
                    self.__dict__[x] = kwargs[x]
                self.participants = self._Participants(**kwargs['participants'][0])
                self.participantIdentities = self._ParticipantIdentities(kwargs['participantIdentities'][0]['participantId'],kwargs['participantIdentities'][0]['player'])
            class _Participants:
                def __init__(self,**kwargs) -> None:
                    self.participantId = kwargs['participantId']
                    self.teamId = kwargs['teamId']
                    self.championId = kwargs['championId']
                    self.spell1Id = kwargs['spell1Id']
                    self.spell2Id = kwargs['spell2Id']
                    self.stats = self._StatsReader(**kwargs['stats'])
                    self.timeline = self._TimelineReader(**kwargs['timeline'])
                class _StatsReader:
                    def __init__(self,**kwargs) -> None:
                        '''
                        ### Attribute
                        - participantId
                        - win: bool
                        - item0~6
                        - kills
                        - deaths
                        - assists
                        - largestKillingSpree
                        - largestMultiKill
                        - killingSprees
                        - longestTimeSpentLiving
                        - doubleKills
                        - tripleKills
                        - quadraKills
                        - pentaKills
                        - unrealKills
                        - totalDamageDealt
                        - magicDamageDealt
                        - physicalDamageDealt
                        - trueDamageDealt
                        - largestCriticalStrike
                        - totalDamageDealtToChampions
                        - magicDamageDealtToChampions
                        - physicalDamageDealtToChampions
                        - trueDamageDealtToChampions
                        - totalHeal
                        - totalUnitsHealed
                        - damageSelfMitigated
                        - damageDealtToObjectives
                        - damageDealtToTurrets
                        - visionScore
                        - timeCCingOthers
                        - totalDamageTaken
                        - magicalDamageTaken
                        - physicalDamageTaken
                        - trueDamageTaken
                        - goldEarned
                        - goldSpent
                        - turretKills
                        - inhibitorKills
                        - totalMinionsKilled
                        - neutralMinionsKilled
                        - totalTimeCrowdControlDealt
                        - champLevel
                        - visionWardsBoughtInGame
                        - sightWardsBoughtInGame
                        - firstBloodKill
                        - firstBloodAssist
                        - firstTowerKill
                        - firstTowerAssist
                        - firstInhibitorKill
                        - firstInhibitorAssist
                        - combatPlayerScore
                        - objectivePlayerScore
                        - totalPlayerScore
                        - totalScoreRank
                        - playerScore0~9
                        - perk0~5[Var1~3]
                        - perkPrimaryStyle
                        - perkSubStyle
                        - statPerk0~2
                        '''
                        self.firstBloodKill = False
                        self.firstInhibitorKill = False
                        self.firstTowerKill = False
                        for x in kwargs:
                            self.__dict__[x] = kwargs[x]
                class _TimelineReader:
                    '''
                    ### Attribute:
                    - participantId
                    - creepsPerMinDeltas
                    - xpPerMinDeltas
                    - goldPerMinDeltas
                    - csDiffPerMinDeltas
                    - xpDiffPerMinDeltas
                    - damageTakenPerMinDeltas
                    - damageTakenDiffPerMinDeltas
                    - role
                    - lane
                    '''
                    def __init__(self,**kwargs) -> None:
                        self.role = None
                        self.lane = None
                        for x in kwargs:
                            self.__dict__[x] = kwargs[x]
            class _ParticipantIdentities:
                def __init__(self,participantId,player_info) -> None:
                    '''
                    ### Attributes
                    - participantId: It is meaningless. its value will always be 0.
                    - player: A player object
                    '''
                    self.participantId = participantId 
                    self.player = self.Player(**player_info)
                class Player:
                    def __init__(self,**kwargs) -> None:
                        '''
                        ### Attribute:
                        - "platformId",  
                        - "accountId" ,  
                        - "summonerName",  
                        - "summonerId" ,  
                        - "currentPlatformId",  
                        - "currentAccountId",  
                        - "matchHistoryUri",  
                        - "profileIcon":   
                        '''
                        for x in kwargs:
                            self.__dict__[x] = kwargs[x]

class TimeLineReader():
    def __init__(self,timeline: dict) -> None:
        '''
        ### Read Time line data and display.
        '''
        self.frame_interval = timeline['frameInterval']
        self.frame = [self.OneFrameReader(x) for x in timeline['frames']]
    def display(self,f: typing.Callable=None):
        '''Simulate the timeline with transfer function f'''
        if f==None: f = lambda x: "player"+str(x)
        print("==========================")
        print("= Game Total Time: {}min =".format(len(self.frame)))
        print("==========================")
        for x in self.frame:
            print("[{}]min - ".format(round(x.timestamp/60000)))
            tmp_x = x.events
            tmp_x.reverse()
            for e in tmp_x:
                timestamp = round((x.timestamp/60000-e.timestamp/60000)*60,3)
                if e.type=='ITEM_PURCHASED':
                    print("\t{} purchased item id-{} at {}s".format(f(e.participantId),e.itemId,timestamp))
                elif e.type=='ITEM_DESTROYED':
                    print("\t{} destroted item id-{} at {}s".format(f(e.participantId),e.itemId,timestamp))
                elif e.type=='CHAMPION_KILL':
                    print("\t{} killed {} in ({},{}) at {}s".format(f(e.killerId),f(e.victimId),e.position['x'],e.position['y'],timestamp))
            print()
            for ptf in x.ptframe:
                try:
                    print("\t{} at ({},{}):".format(f(ptf.participantId),ptf.position['x'],ptf.position['y']))
                    print("\t\t- level: {}".format(ptf.level))
                    print("\t\t- totalGold: {}".format(ptf.totalGold))
                    print("\t\t- currentGold: {}".format(ptf.currentGold))
                    print("\t\t- minionsKilled: {}".format(ptf.minionsKilled))
                except:
                    pass
    class OneFrameReader:
        def __init__(self, frame:dict) -> None:
            self.ptframe = [self.ParticipantFrames(**x) for x in frame['participantFrames'].values()]
            self.timestamp = frame['timestamp']
            self.events = [self.Events(**x) for x in frame['events']]
        class ParticipantFrames:
            def __init__(self,**kwargs) -> None:
                '''
                - participantId
                - position  dict{'x':0,'y':0}
                - currentGold
                - totalGold
                - level 
                - xp 
                - minionsKilled 
                - jungleMinionsKilled
                - dominionScore 
                - teamScore
                '''
                for x in kwargs:
                    self.__dict__[x] = kwargs[x]
        class Events:
            def __init__(self,**kwargs) -> None:
                '''  
                - type: ITEM_PURCHASED/ITEM_DESTROYED
                    - timestamp
                    - participantId
                    - itemId

                - type: WARD_PLACED(X)
                    - timestamp
                    - wardType
                    - creatorId
                
                - type: SKILL_LEVEL_UP
                    - timestamp
                    - participantId
                    - skillSlot
                    - levelUpType
                
                - type: CHAMPION_KILL
                    - timestamp
                    - position: dict{'x':0,'y':0}
                    - killerId
                    - victimId
                    - assistingParticipantIds: list
                '''
                for x in kwargs:
                    self.__dict__[x] = kwargs[x]

class GameDetailMatching():
    def __init__(self,detail: dict) -> None:
        '''### Transfrom to a mapping with participant ID and name'''
        self.gameId = detail['gameId']
        self.gameCreation = detail['gameCreation']
        self.gameDuration = detail['gameDuration']
        self.mapId = detail['mapId']
        self.seasonId = detail['seasonId']
        self.gameVersion = detail['gameVersion']
        self.gameMode = detail['gameMode']
        self.gameType = detail['gameType']
        self.teams = detail['teams']
        self.participants = detail['participants']
        self.participantIdentities = [self._ParticipantIdentities(**x) for x in detail['participantIdentities']]

    def matching_dict(self) -> dict:
        '''Return dict of participantId:(accountId,summonerName)'''
        ret = dict()
        for x in self.participantIdentities:
            ret[x.participantId] = (x.player.accountId,x.player.summonerName)
        return ret
    
    def matching_func(self) -> typing.Callable:
        '''Return mapping function of participantId:(accountId,summonerName)'''
        ret = dict()
        for x in self.participantIdentities:
            ret[x.participantId] = (x.player.accountId,x.player.summonerName)
        return lambda x: ret[x][1]
        
    class _ParticipantIdentities:
        def __init__(self,**kwargs) -> None:
            '''
            ### Attributes
            - participantId: the true mapping of id and time line
            - player: A player object
            '''
            self.participantId = kwargs['participantId']
            self.player = self.Player(**kwargs['player'])
        class Player:
            def __init__(self,**kwargs) -> None:
                '''
                ### Attribute:
                - "platformId",  
                - "accountId" ,  
                - "summonerName",  
                - "summonerId" ,  
                - "currentPlatformId",  
                - "currentAccountId",  
                - "matchHistoryUri",  
                - "profileIcon":   
                '''
                for x in kwargs:
                    self.__dict__[x] = kwargs[x]
        
def _tPlayerHistory():
    id = GetAccountID("alankingdom")
    history = GetPlayerHistory(id)
    HR = HistoryReader(history)
    print(HR.games.games[9].participants.championId)

def _tGetGameTimeline():
    timeline = GetGameTimeline(1940347176)
    detail = GetSingleGameDetail(1940347176)
    func = GameDetailMatching(detail).matching_func()
    TimeLineReader(timeline).display(func)

def _tELOTransfrom():
    print(ELOTransform(Tier,1537))

if __name__=="__main__":
    pass