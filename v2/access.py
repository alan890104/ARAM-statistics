# reference:
'''
https://github.com/nxhdev2002/checkLOLMatchHistory/blob/9a005e76791acf13ce71017f71ffaa0cff364413/lolmatchhistory.js
'''
import os
import json
import typing
import requests

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

def JsonWrite(data: dict, filename: os.PathLike) -> None:
    with open(filename,'w',encoding='utf-8') as F:
        json.dump(data,F,ensure_ascii=False,indent=4)

def JsonRead(filename: os.PathLike) -> dict:
    with open(filename,'r',encoding='utf-8') as F:
        data = json.load(F)
    return data

class HistoryReader():
    def __init__(self,r) -> None:
        '''Parse the result from GetPlayerHistory() function '''
        self.platformId = r['platformId']
        self.accountId = r['accountId']
        self.games = self._Games(**r['games'])
        self.shownQueues = r['shownQueues']
    def format(self) -> dict:
        '''format important attribute'''
        pass
    def versions(self) -> list:
        '''Get the version list of all games'''
        interval = self.games.gameIndexEnd-self.games.gameIndexBegin
        return list(set([self.games.games[x].gameVersion for x in range(interval)]))
    def totalGames(self) -> int:
        return self.games.gameCount
    def index(self) -> tuple:
        '''Return tuple (Start index, End index)'''
        return (self.games.gameIndexBegin,self.games.gameIndexEnd)
    def totalPlayingTime(self) -> int:
        '''Return total playing time in second'''
        interval = self.games.gameIndexEnd-self.games.gameIndexBegin
        return sum([self.games.games[x].gameDuration for x in range(interval)])
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
                self.gameId = kwargs['gameId']
                self.platformId = kwargs['platformId']
                self.gameCreation = kwargs['gameCreation']
                self.gameDuration = kwargs['gameDuration']
                self.queueId = kwargs['queueId']
                self.mapId = kwargs['mapId']
                self.seasonId = kwargs['seasonId']
                self.gameVersion = kwargs['gameVersion']
                self.gameMode = kwargs['gameMode']
                self.gameType = kwargs['gameType']
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

class GameDetailReader():
    pass

class TimeLineReader():
    def __init__(self,frame: dict) -> None:
        '''
        ### Read Time line data and display.
        '''
        self.frame_interval = frame['frameInterval']
        self.frame = [self.OneFrameReader(x) for x in frame['frames']]
    def display(self):
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
                    print("\tPlayer{} purchased item id-{} at {}s".format(e.participantId,e.itemId,timestamp))
                elif e.type=='ITEM_DESTROYED':
                    print("\tPlayer{} destroted item id-{} at {}s".format(e.participantId,e.itemId,timestamp))
                elif e.type=='CHAMPION_KILL':
                    print("\tPlayer{} killed player{} in ({},{}) at {}s".format(e.killerId,e.victimId,e.position['x'],e.position['y'],timestamp))
            print()
            for ptf in x.ptframe:
                try:
                    print("\tPlayer{} at ({},{}):".format(ptf.participantId,ptf.position['x'],ptf.position['y']))
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
    
if __name__=="__main__":
    # id = GetAccountID("alankingdom")
    # r = GetPlayerHistory(id,Begin=140,End=160)
    # JsonWrite(r,'data.json')
    r = JsonRead('data.json')
    HR = HistoryReader(r)
    print(HR.totalGames(),HR.versions())