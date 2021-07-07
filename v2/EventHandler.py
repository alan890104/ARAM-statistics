import os
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
                Agent._InsertLine([ LineId, Content[10:] ])
                LOLName = Agent.GetLOLNameByLineId(LineId)
                Msg = "{}註冊成功!你的召喚師名稱是:{}".format(LineName,LOLName)   
            else:
                Msg = "{}，你已經註冊過帳號了!你的召喚師名稱是:{}".format(LineName,LOLName)
            return TextSendMessage(text=Msg),LastCmd
    
    if Content[:5]=="@echo":
        '''
        1. 個人強勢英雄 @specialize
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
        return FlexSendMessage(alt_text="請使用智慧型裝置瀏覽強勢英雄",
                               contents=contents),LastCmd
    elif PBData=="@item":
        contents = ItemFlexGenerator(LineId,LOLName,Agent)
        return FlexSendMessage(alt_text="請使用智慧型裝置瀏覽最愛道具",
                               contents=contents),LastCmd
    elif PBData=="@best":
        LastCmd[LineId] = PBData
        # label : gameDuration,gameMode,teamId,championId,KDA
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
            pass
            del LastCmd[LineId]
        elif LastCmd[LineId]=="@best":
            del LastCmd[LineId]

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




