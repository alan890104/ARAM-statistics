import os
from datetime import datetime, timedelta
from typing import Any
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

def CommandResp(event, LastCmd: dict, line_bot_api: LineBotApi, Agent: DB.DBAgent) -> Any:
    '''
    ### Receive text event and response
    '''
    LineId = event.source.user_id
    Content = event.message.text.strip()
    if not Agent.GetLOLNameByLineId(LineId):
        if isinstance(event.source, SourceUser):
            profile = line_bot_api.get_profile(LineId)
            LineName = profile.display_name
            Msg = "用戶{}尚未登錄資料庫, 請使用指令連動自己的LOL召喚師名稱。\
                   範例: @register alankingdom".format(LineName)
            return TextSendMessage(text=Msg),LastCmd

    if Content[:9]=="@register":
        if len(Content.split(maxsplit=1))!=2:
            return TextSendMessage(text="格式錯誤。範例: @register alankingdom"),LastCmd
        if isinstance(event.source, SourceUser):
            profile = line_bot_api.get_profile(LineId)
            LineName = profile.display_name
            LOLName = Agent.GetLOLNameByLineId(LineId)
            if not LOLName:
                if Agent.CheckLOLNameExist():
                    Msg = "請勿輸入他人的召喚師名稱。"
                else:
                    Agent._InsertLine([ LineId, Content[10:] ])
                    LOLName = Agent.GetLOLNameByLineId(LineId)
                    Msg = "{}註冊成功!你的召喚師名稱是:{}".format(LineName,LOLName)   
            else:
                Msg = "{}，你已經註冊過帳號了!你的召喚師名稱是:{}".format(LineName,LOLName)
            return TextSendMessage(text=Msg),LastCmd
    
    if Content[:5]=="@echo":
        '''
        1. 個人優勢 @specialize
        2. 愛用道具 @item
        3. 最佳紀錄保持者 @best
        4. 浪費人生計算機 @time
        '''
        contents = AGD.JsonRead("layout\WelcomeInterface.json")
        return FlexSendMessage(alt_text="請使用智慧型裝置瀏覽此訊息",
                               contents=contents),LastCmd


def PostBackResp(event, LastCmd: dict ,line_bot_api: LineBotApi, Agent: DB.DBAgent) -> Any:
    '''
    ### Receive postback event and response
    '''
    LineId = event.source.user_id
    PBData = event.postback.data
    LOLName = Agent.GetLOLNameByLineId(LineId)
    if PBData=="@specialize":
        LastCmd[LineId] = PBData
        # label : gameDuration,gameMode,teamId,championId
        contents = AGD.JsonRead("layout\Specialize.json")
        return FlexSendMessage(alt_text="請使用智慧型裝置瀏覽個人優勢",
                               contents=contents),LastCmd
    elif PBData=="@item":
        contents = ItemFlexGenerator(LineId,LOLName,Agent)
        return FlexSendMessage(alt_text="請使用智慧型裝置瀏覽最愛道具",
                               contents=contents),LastCmd
    elif PBData=="@best":
        LastCmd[LineId] = PBData
        # label : gameDuration,totalDamageDealt,kda,visionScore,totalDamageTaken,totalMinionsKilled,goldEarned,damageDealtToObjectives,timeCCingOthers
        contents = AGD.JsonRead("layout\Best.json")
        return FlexSendMessage(alt_text="請使用智慧型裝置瀏覽最佳紀錄",
                               contents=contents),LastCmd
    elif PBData=="@time":
        contents = TimeFlexGenerator(LineId,Agent)
        return FlexSendMessage(alt_text="請使用智慧型裝置瀏覽花費時間",
                               contents=contents),LastCmd
    else:
        if LineId not in LastCmd:
            return TextSendMessage(text="錯誤: 指令發起與執行者不同。"),LastCmd
        if LastCmd[LineId]=="@specialize":
            contents = SpecializeOptionFlexGenerator(LineId,LOLName,PBData,Agent)
            del LastCmd[LineId]
            return FlexSendMessage(alt_text="請使用智慧型裝置瀏覽最佳紀錄",
                               contents=contents),LastCmd
        elif LastCmd[LineId]=="@best":
            contents = BestOptionFlexGenerator(PBData,Agent)
            del LastCmd[LineId]
            return FlexSendMessage(alt_text="請使用智慧型裝置瀏覽最佳紀錄",
                               contents=contents),LastCmd
            

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

    contents["body"]["contents"][3]["contents"][0]["url"] = AGD.DPREFIX+"cdn/{}/img/item/{}.png".format(version,items_key[1])
    contents["body"]["contents"][3]["contents"][1]["contents"][1]["contents"][0]["text"] = ItemName[str(items_key[1])]
    contents["body"]["contents"][3]["contents"][1]["contents"][2]["contents"][0]["text"] = "{}次".format(items_value[1])

    contents["body"]["contents"][4]["contents"][0]["url"] = AGD.DPREFIX+"cdn/{}/img/item/{}.png".format(version,items_key[2])
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
        else:
            result = blue
            detail = "比紅方高{}%".format(round((blue["ratio"]-red["ratio"])*100,2))
        description = "{}%".format(round(result["ratio"]*100,2))
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
    