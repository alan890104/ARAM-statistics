import os
from copy import deepcopy
from datetime import datetime, timedelta
from sqlite3.dbapi2 import paramstyle
from typing import Any, Text
import AccessGameData as AGD
import Database as DB
from linebot import LineBotApi
from linebot.models import (
    MessageEvent, TextMessage, TextSendMessage,
    SourceUser, SourceGroup, SourceRoom,
    TemplateSendMessage, ConfirmTemplate, MessageAction,
    ButtonsTemplate, ImageCarouselTemplate, ImageCarouselColumn, URIAction,
    PostbackAction, DatetimePickerAction,
    CameraAction, CameraRollAction, LocationAction,
    CarouselTemplate, CarouselColumn, PostbackEvent,
    StickerMessage, StickerSendMessage, LocationMessage, LocationSendMessage,
    ImageMessage, VideoMessage, AudioMessage, FileMessage,
    UnfollowEvent, FollowEvent, JoinEvent, LeaveEvent, BeaconEvent,
    MemberJoinedEvent, MemberLeftEvent,FlexContainer,
    FlexSendMessage, BubbleContainer, ImageComponent, BoxComponent,
    TextComponent, IconComponent, ButtonComponent,
    SeparatorComponent, QuickReply, QuickReplyButton,
    ImageSendMessage)

def GetDirSize(Location: os.PathLike) -> int:
    total_size = 0
    for dirpath, dirnames, filenames in os.walk(Location):
        for f in filenames:
            fp = os.path.join(dirpath, f)
            # skip if it is symbolic link
            if not os.path.islink(fp):
                total_size += os.path.getsize(fp)
    return total_size

def CommandResp(event, line_bot_api: LineBotApi) -> Any:
    '''
    ### Receive text event and response
    '''
    LineId = event.source.user_id
    Content = event.message.text.strip()
    Agent=DB.DBAgent()

    if Content[:9]=="@register":
        if len(Content.split(maxsplit=1))!=2:
            return TextSendMessage(text="格式錯誤，請輸入你的召喚師名稱。範例: @register alankingdom")
        try:
            profile = line_bot_api.get_profile(LineId)
            LineName = profile.display_name
            print(LineId,LineName)
        except:
            return TextSendMessage(text="請將你的Line更新至最新版本，並加我為好友")
        LOLName = Agent.GetLOLNameByLineId(LineId)
        if not LOLName:
            if Agent.CheckLOLNameExistInLine(LOLName):
                Msg = "請勿輸入他人的召喚師名稱。"
                return TextSendMessage(text=Msg)
            else:
                Agent._InsertLine([ LineId, Content[10:].strip() ])
                LOLName = Agent.GetLOLNameByLineId(LineId)
                Msg = "用戶{}註冊成功!你的召喚師名稱是:{}。接著，你可以試著輸入@echo來呼叫使用者介面。".format(LineName,LOLName)   
                return TextSendMessage(text=Msg)
        else:
            Msg = "{}，你已經註冊過帳號了!你的召喚師名稱是:{}".format(LineName,LOLName)
            return TextSendMessage(text=Msg)

    elif not Agent.GetLOLNameByLineId(LineId):
        # if isinstance(event.source, SourceUser):
        try:
            profile = line_bot_api.get_profile(LineId)
            LineName = profile.display_name
            print(LineId,LineName)
        except:
            return TextSendMessage(text="請將你的Line更新至最新版本，並加我為好友。隨後請輸入任意文字，我將提供協助。")
        Msg = "由於用戶{}尚未登錄資料庫, 請使用指令連動自己的LOL召喚師名稱。範例: @register alankingdom".format(LineName)
        return TextSendMessage(text=Msg)
    
    if Content[:5]=="@echo":
        '''
        1. 個人優勢 @specialize
        2. 愛用道具 @item
        3. 最佳紀錄保持者 @best
        4. 浪費人生計算機 @time
        '''
        contents = AGD.JsonRead("layout\WelcomeInterface.json")
        return FlexSendMessage(alt_text="請使用智慧型裝置瀏覽此訊息",
                               contents=contents)
    elif Content[:5]=="@help":
        Title = Content[6:].strip()
        if Title=="玩家近況":
            LOLName = Agent.GetLOLNameByLineId(LineId)
            items = [QuickReplyButton(action=MessageAction(label="我的近況", text="玩家近況 {}".format(LOLName)))]
            return TextSendMessage(text="輸入: 玩家近況  <召喚師名稱>，就可以查詢了!會對你最近20場超過15分鐘的NG場進行分析，也可以查詢不在此群組的人喔!",quick_reply=QuickReply(items=items))
    elif Content[:4]=="玩家近況":
        LOLName = Content[5:].strip()
        if not Agent.GetAccountIdByName(LOLName):
            accountId = AGD.GetAccountID(LOLName)
            if not accountId:
                items = [QuickReplyButton(action=MessageAction(label="查看說明", text="@help 玩家近況".format(LOLName)))]
                return TextSendMessage(text="名稱{}不存在，請檢查是否輸入錯誤。".format(LOLName),quick_reply=QuickReply(items=items))
            history = AGD.GetPlayerHistory(accountId)
            result = AGD.HistoryReader(history).Analyze_Recent_x_Games()
            ChampName = AGD.JsonRead("static\champion.json")
            LaneName = AGD.JsonRead("static\laneTrans.json")
            result["championId"] = ChampName[str(result["championId"])][1]
            result["lane"] = LaneName[result["lane"]]
            param = [LOLName]
            param.extend(list(result.values()))
            s = "玩家{}分析:\n場均KDA: {}\n場均視野分: {}\n場均勝率: {}\n首殺率: {}\n常用英雄: {} \n最愛路線: {}".format(*param)
            return [TextSendMessage(text="由於此玩家未在資料庫，因此近20場數據未經過濾(包含各種模式、提早投降)，此分析較為粗略。")
                    ,TextSendMessage(text=s)]
        else:
            accountId = Agent.GetAccountIdByName(LOLName)
            result = Agent.Analyze_Recent_x_Games(accountId)
            if len(result)==0:
                return TextSendMessage(text="玩家{}數據不足。(需求條件為最近20場15分鐘以上的NG)")
            ChampName = AGD.JsonRead("static\champion.json")
            LaneName = AGD.JsonRead("static\laneTrans.json")
            result["championId"] = ChampName[str(result["championId"])][1]
            result["lane"] = LaneName[result["lane"]]
            param = [LOLName]
            param.extend(list(result.values()))
            s = "玩家{}分析:\n場均KDA: {}\n場均擊殺參與率: {}\n場均拆塔率: {}\n場均視野分: {}\n場均勝率: {}\n首殺率: {}\n常用英雄: {}\n最愛路線: {}".format(*param)
            items = [QuickReplyButton(action=MessageAction(label="回到主選單", text="@echo".format(LOLName)))]
            return TextSendMessage(text=s,quick_reply=QuickReply(items=items))
    return None

def PostBackResp(event, line_bot_api: LineBotApi) -> Any:
    '''
    ### Receive postback event and response
    '''
    Agent=DB.DBAgent()
    LineId = event.source.user_id
    PBData = event.postback.data
    LOLName = Agent.GetLOLNameByLineId(LineId)
    if not LOLName:
        try:
            profile = line_bot_api.get_profile(LineId)
            LineName = profile.display_name
            print(LineId,LineName)
        except:
            return TextSendMessage(text="請將你的Line更新至最新版本，並加我為好友")
        Msg = "用戶{}尚未登錄資料庫, 請先加入此帳號好友並使用指令連動自己的LOL召喚師名稱。範例: @register alankingdom".format(LineName)
        return TextSendMessage(text=Msg)
    if PBData=="@elo":
        contents = ELOFlexGenerator(LineId,LOLName,Agent)
        if len(contents)==0:
            return TextSendMessage(text="目前您的場數不足，因此無法顯示隱分紀錄。")
        return [FlexSendMessage(alt_text="請使用智慧型裝置瀏覽隱藏積分",
                               contents=contents),QuickReplyGenerator()]
    elif PBData=="@specialize":
        # label : gameDuration,gameMode,teamId,championId
        contents = AGD.JsonRead("layout\Specialize.json")
        return FlexSendMessage(alt_text="請使用智慧型裝置瀏覽個人優勢",
                               contents=contents)
    elif PBData=="@item":
        contents = ItemFlexGenerator(LineId,LOLName,Agent)
        return [FlexSendMessage(alt_text="請使用智慧型裝置瀏覽最愛道具",
                               contents=contents),QuickReplyGenerator()]
    elif PBData=="@best":
        # label : gameDuration,totalDamageDealt,kda,visionScore,totalDamageTaken,totalMinionsKilled,goldEarned,damageDealtToObjectives,timeCCingOthers
        contents = AGD.JsonRead("layout\Best.json")
        return FlexSendMessage(alt_text="請使用智慧型裝置瀏覽最佳紀錄",
                               contents=contents)
    elif PBData=="@time":
        contents = TimeFlexGenerator(LineId,LOLName,Agent)
        return [FlexSendMessage(alt_text="請使用智慧型裝置瀏覽花費時間",
                               contents=contents),QuickReplyGenerator()]
    elif PBData[:11]=="@specialize":
        contents = SpecializeOptionFlexGenerator(LineId,LOLName,PBData[12:],Agent)
        return [FlexSendMessage(alt_text="請使用智慧型裝置瀏覽個人優勢",
                            contents=contents),QuickReplyGenerator(backto="@specialize")]
    elif PBData[:5]=="@best":
        contents = BestOptionFlexGenerator(PBData[6:],Agent)
        return [FlexSendMessage(alt_text="請使用智慧型裝置瀏覽最佳紀錄",
                            contents=contents),QuickReplyGenerator(backto="@best")]
            
def FileResp(event, line_bot_api: LineBotApi) -> Any:
    LineId = event.source.user_id
    if LineId=="Uea3f780dd528bcb2ff99fcaa1287d3f5": # my line id
        MsgContent = line_bot_api.get_message_content(event.message.id)
        FileName = event.message.file_name
        with open("Upload/{}".format(FileName),'wb') as F:
            for chunk in MsgContent.iter_content():
                F.write(chunk)
        return TextSendMessage(text="已儲存檔案:{}".format(FileName))

def ImageResp(event, line_bot_api: LineBotApi) -> Any:
    LineId = event.source.user_id
    if LineId=="Uea3f780dd528bcb2ff99fcaa1287d3f5": # my line id
        MsgContent = line_bot_api.get_message_content(event.message.id)
        Now = int((datetime.now()).timestamp()*1000)
        FileName = "{}.jpg".format(Now)
        with open("Image/{}".format(FileName),'wb') as F:
            for chunk in MsgContent.iter_content():
                F.write(chunk)
        return TextSendMessage(text="已儲存檔案:{}".format(FileName))

def QuickReplyGenerator(backto: str=None) ->  TextSendMessage:
    '''
    send post action if you're in @specialize... or @best...
    '''
    items = [QuickReplyButton(action=MessageAction(label="不用了", text="不用了謝謝"))]
    if backto=="@specialize":
        items.append( QuickReplyButton(action=PostbackAction(label="個人優勢", text="人家想繼續看個人優勢:)",data="@specialize")) )
    if backto=="@best":
        items.append( QuickReplyButton(action=PostbackAction(label="最佳紀錄", text="人家想繼續看最佳紀錄:)",data="@best")) )
    if backto==None:
        items.append(QuickReplyButton(action=MessageAction(label="好啊", text="@echo")))
    else:
        items.append(QuickReplyButton(action=MessageAction(label="回主選單", text="@echo")))
    QuickReplyObj = QuickReply(items=items)
    return TextSendMessage(
                    text="你是否要繼續查看其他內容呢?",
                    quick_reply=QuickReplyObj)

def ELOFlexGenerator(LineId: str,LOLName: str,Agent: DB.DBAgent) -> dict:
    '''
    If record not find in database, return an empty dict {}
    '''
    contents = AGD.JsonRead("layout\ELO.json")
    accountId = Agent.GetAccountByLindId(LineId)
    ELO = Agent.GetLatestELOByAccount(accountId)
    if len(ELO)==0: return dict()
    contents["contents"][0]["body"]["contents"][0]["contents"][0]["text"] = LOLName
    ELO_element_template = AGD.JsonRead("layout\ELO_element.json")
    RankImg = AGD.JsonRead("static\TierUri.json")
    for title in ELO:
        ELO_element = deepcopy(ELO_element_template)
        ELO_element["body"]["contents"][0]["contents"][0]["text"] = title
        ELO_element["body"]["contents"][1]["contents"][0]["text"] = "({})".format(ELO[title])
        Tier_name = AGD.ELOTransform(AGD.Tier,ELO[title])
        ELO_element["body"]["contents"][2]["contents"][0]["text"] = Tier_name
        ELO_element["hero"]["url"] = RankImg[Tier_name]
        contents["contents"].append(ELO_element)
    return contents

    

def ItemFlexGenerator(LineId: str,LOLName: str,Agent: DB.DBAgent) -> dict:
    contents = AGD.JsonRead("layout\Item.json")
    ItemName = AGD.JsonRead("static\item.json")
    version = AGD.GetVersion()
    accountId = Agent.GetAccountByLindId(LineId)
    items = Agent.GetFavoriteItem(accountId,version)
    items_key = list(items.keys())
    items_value = list(items.values())
    contents["body"]["contents"][0]["contents"][0]["text"] = "{}最愛道具".format(LOLName)
    contents["body"]["contents"][1]["contents"][0]["contents"][0]["url"] = AGD.DPREFIX+"cdn/{}/img/item/{}.png".format(version,items_key[0])
    contents["body"]["contents"][1]["contents"][1]["contents"][1]["contents"][0]["text"] = ItemName[str(items_key[0])]
    contents["body"]["contents"][1]["contents"][1]["contents"][2]["contents"][0]["text"] = "{}次".format(items_value[0])

    contents["body"]["contents"][3]["contents"][0]["contents"][0]["url"] = AGD.DPREFIX+"cdn/{}/img/item/{}.png".format(version,items_key[1])
    contents["body"]["contents"][3]["contents"][1]["contents"][1]["contents"][0]["text"] = ItemName[str(items_key[1])]
    contents["body"]["contents"][3]["contents"][1]["contents"][2]["contents"][0]["text"] = "{}次".format(items_value[1])

    contents["body"]["contents"][4]["contents"][0]["contents"][0]["url"] = AGD.DPREFIX+"cdn/{}/img/item/{}.png".format(version,items_key[2])
    contents["body"]["contents"][4]["contents"][1]["contents"][1]["contents"][0]["text"] = ItemName[str(items_key[2])]
    contents["body"]["contents"][4]["contents"][1]["contents"][2]["contents"][0]["text"] = "{}次".format(items_value[2])
    return contents

def TimeFlexGenerator(LineId: str,LOLName: str,Agent: DB.DBAgent) -> dict:
    contents = AGD.JsonRead("layout\Time.json")
    accountId = Agent.GetAccountByLindId(LineId)
    times = Agent.GetTotalPlayingTime(accountId)
    hours, remainder = divmod(times.seconds, 3600)
    minutes, seconds = divmod(remainder, 60)
    contents["body"]["contents"][1]["contents"][0]["text"] = LOLName+" "+contents["body"]["contents"][1]["contents"][0]["text"]
    contents["body"]["contents"][0]["text"] = "{}天{}小時{}分鐘{}秒".format(times.days,hours,minutes,seconds)
    return contents

def SpecializeOptionFlexGenerator(LineId: str, LOLName:str, PBData: str, Agent: DB.DBAgent) -> dict:
    '''
    * PBData: gameDuration,gameMode,teamId,championId,lane
    '''
    contents = AGD.JsonRead("layout\Specialize_Options.json")
    title = "{}勝率".format(LOLName)
    accountId = Agent.GetAccountByLindId(LineId)
    if PBData=="gameDuration":
        result = Agent.GetUserWinRateByCond(accountId,gameDuration=15*60)
        description = "{}%".format(round(result["ratio"]*100,2))
        detail = "{}場15分鐘內勝利".format(result["total"])
    elif PBData=="gameMode":
        result = Agent.GetUserWinRateByCond(accountId,category=True,sort="ratio")
        gameMode = list(result.keys())[0]
        ratio,total = result[gameMode]["ratio"],result[gameMode]["total"]
        translate = AGD.JsonRead("static\gameModeTrans.json")
        description = "{}%".format(round(ratio*100,2))
        detail = "在{}場{}內".format(total,translate[gameMode])
    elif PBData=="teamId":
        blue = Agent.GetUserWinRateByCond(accountId,teamId=100)
        red = Agent.GetUserWinRateByCond(accountId,teamId=200)
        if red["ratio"]>blue["ratio"]:
            result = red
            detail = "比藍方高{}%".format(round((red["ratio"]-blue["ratio"])*100,2))
            description = "紅方{}%".format(round(result["ratio"]*100,2))
        else:
            result = blue
            detail = "比紅方高{}%".format(round((blue["ratio"]-red["ratio"])*100,2))
            description = "藍方{}%".format(round(result["ratio"]*100,2))
    elif PBData=="championId":
        year_ago = int((datetime.now()-timedelta(days=365)).timestamp()*1000)
        result = Agent._Query("SELECT championId,COUNT(*) as total,ROUND((CAST(SUM(win) AS FLOAT)/CAST(COUNT(win) AS FLOAT)),4) as ratio FROM game\
                WHERE accountId=? AND gameCreation>? GROUP BY championId HAVING total>10 ORDER BY ratio DESC",[accountId,year_ago])
        if len(result)!=0: 
            result = result[0]
            Champion = AGD.JsonRead("static\champion.json")
            description = "{}%".format(round(result["ratio"]*100,2))
            detail = "共{}場{}(一年內)".format(result["total"],Champion[str(result["championId"])][1])
        else:
            description = "數據不足10筆"
            detail = "..."
    elif PBData=="lane":
        year_ago = int((datetime.now()-timedelta(days=365)).timestamp()*1000)
        result = Agent._Query("SELECT lane,COUNT(*) as total,ROUND((CAST(SUM(win) AS FLOAT)/CAST(COUNT(win) AS FLOAT)),4) as ratio FROM game\
                WHERE accountId=? AND lane!='NONE' AND gameMode='CLASSIC' AND gameCreation>? GROUP BY lane HAVING total>15 ORDER BY ratio DESC",[accountId,year_ago])
        if len(result)!=0: 
            result = result[0]
            description = "{}%".format(round(result["ratio"]*100,2))
            LanTrans = AGD.JsonRead("static\laneTrans.json")
            detail = "共{}場{}(一年內)".format(result["total"],LanTrans[result["lane"]])
        else:
            description = "數據不足15筆"
            detail = "..."

    contents["contents"][0]["body"]["contents"][0]["text"] = title
    contents["contents"][0]["body"]["contents"][1]["contents"][0]["text"] = description
    contents["contents"][0]["body"]["contents"][1]["contents"][1]["text"] = detail

    return contents


def BestOptionFlexGenerator(PBData: str,Agent: DB.DBAgent) -> dict:
    '''
    * PBData: gameDuration,totalDamageDealt,kda,visionScore,totalDamageTaken,totalMinionsKilled,goldEarned,damageDealtToObjectives,timeCCingOthers
    '''
    contents = AGD.JsonRead("layout\Best_Options.json")
    Champion = AGD.JsonRead("static\champion.json")
    if PBData=="kda":
        result = Agent.GetMAXAttribute("CAST( (kills+assists) AS FLOAT) /  (CASE WHEN deaths==0 THEN 1 ELSE deaths END)")
        description = "KDA {}".format(round(result["record"]))
    else:
        result = Agent.GetMAXAttribute(PBData)
        if PBData=="gameDuration":
            description = "{}遊戲時間".format(result["record"])
        elif PBData=="totalDamageDealt":
            description = "{}輸出傷害".format(result["record"])
        elif PBData=="visionScore":
            description = "{}視野分數".format(result["record"])
        elif PBData=="totalDamageTaken":
            description = "{}承受傷害".format(result["record"])
        elif PBData=="totalMinionsKilled":
            description = "{}吃兵數".format(result["record"])
        elif PBData=="goldEarned":
            description = "{}金幣".format(result["record"])
        elif PBData=="damageDealtToObjectives":
            description = "{}對建築傷害".format(result["record"])
        elif PBData=="timeCCingOthers":
            description = "{}控場分數".format(result["record"])
    history = AGD.GetPlayerHistory(result["accountId"],0,1)
    summonerId = AGD.HistoryReader(history).playerinfo()["summonerId"]
    ChampName = Champion[str(result["championId"])][1]
    version = AGD.GetVersion()
    pic_url = AGD.DPREFIX+"cdn/{}/img/champion/{}.png".format(version,Champion[str(result["championId"])][0])
    game_url = "https://lol.moa.tw/match/show/{}/{}".format(result["gameId"],summonerId)

    contents["contents"][0]["hero"]["url"] = pic_url
    contents["contents"][0]["body"]["contents"][0]["text"] = "{}的{}".format(result["LOLName"],ChampName)
    contents["contents"][0]["body"]["contents"][1]["contents"][0]["text"] = description
    contents["contents"][0]["footer"]["contents"][0]["action"]["uri"] = game_url

    return contents