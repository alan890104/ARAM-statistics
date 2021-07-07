from flask import Flask, request, abort
from linebot import LineBotApi, WebhookHandler
from linebot.exceptions import InvalidSignatureError
from linebot.models import (
    MessageEvent, TextMessage, TextSendMessage, ImageMessage
)
from linebot.models.events import PostbackEvent
import AccessGameData as AGD
import Database as DB
import EventHandler as EH

app = Flask(__name__)
Secrets = AGD.JsonRead("secret/token.json")
line_bot_api = LineBotApi(Secrets["ChannelAccessToken"])
handler = WebhookHandler(Secrets["ChanelSecret"])

@app.route("/callback", methods=['POST'])
def callback():
    '''
    ### Recieve Message From Line Server, and assign to corresponding handler
    '''
    # get X-Line-Signature header value
    signature = request.headers['X-Line-Signature']
    # get request body as text
    body = request.get_data(as_text=True)
    # handle webhook body
    try:
        handler.handle(body, signature)
    except InvalidSignatureError:
        print("Invalid signature. Please check your channel access token/channel secret.")
        abort(400)
    return 'OK'

@handler.add(MessageEvent, message=TextMessage)
def HandleTextMessage(event):
    '''
    ### Handle text message from line except "deadbeef"
    '''
    if event.source.user_id == "Udeadbeefdeadbeefdeadbeefdeadbeef": return
    Token = event.reply_token
    Reply= EH.CommandResp(event,line_bot_api)
    line_bot_api.reply_message(Token,Reply)

@handler.add(MessageEvent, message=ImageMessage)
def HandleImageMessage(event):
    pass

@handler.add(PostbackEvent)
def HandleImageMessage(event):
    pass


if __name__ == "__main__":
    pass
    # app.run()