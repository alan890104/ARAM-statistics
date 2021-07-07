from typing import Any
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

def CommandResp(event, line_bot_api: LineBotApi) -> Any:
    '''
    ### Receive event and response
    '''
    LineId = event.source.user_id
    Content = event.message.text.strip()
    Agent = DB.DBAgent()
    if not Agent.GetLOLNameByLineId(LineId):
        if isinstance(event.source, SourceUser):
            profile = line_bot_api.get_profile(event.source.user_id)
            LineName = profile.display_name
            Msg = "用戶{}尚未登錄資料庫, 請使用指令連動自己的LOL召喚師名稱。\
                   範例: @register alankingdom".format(LineName)
            return TextSendMessage(text=Msg)

    if Content[:9]=="@register":
        if len(Content.split(maxsplit=1))!=2:
            return TextSendMessage(text="格式錯誤。範例: @register alankingdom")
        if isinstance(event.source, SourceUser):
            profile = line_bot_api.get_profile(event.source.user_id)
            LineName = profile.display_name
            LOLName = Agent.GetLOLNameByLineId(LineId)
            if not LOLName:
                Agent._InsertLine([ LineId, Content[10:] ])
                LOLName = Agent.GetLOLNameByLineId(LineId)
                Msg = "{}註冊成功!你的召喚師名稱是:{}".format(LineName,LOLName)   
            else:
                Msg = "{}，你已經註冊過帳號了!你的召喚師名稱是:{}".format(LineName,LOLName)
            return TextSendMessage(text=Msg)
    
    if Content[:5]=="@echo":
        return FlexSendMessage(alt_text="您目前的裝置不支援圖像模組，請改為使用文字命令。命令介紹: \
                                         https://hackmd.io/@alankingdom/S1ZYT3i-w",
                               contents=WelcomeInterface())


def WelcomeInterface() -> FlexContainer:
    '''
    Will be called after user types "@echo"
    1. 個人強勢英雄
    2. 愛用道具
    3. 最佳紀錄保持者
    4. 浪費人生計算機
    '''
    pass