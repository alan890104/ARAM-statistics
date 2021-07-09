from flask import Flask, request, abort
from linebot import LineBotApi, WebhookHandler
from linebot.exceptions import InvalidSignatureError
from linebot.models import (
    MessageEvent, TextMessage, ImageMessage, FileMessage
)
from linebot.models.events import PostbackEvent
import AccessGameData as AGD
import Database as DB
import EventHandler as EH

# Origin Route = https://lol-winrate.herokuapp.com/callback

app = Flask(__name__)
Secrets = AGD.JsonRead("secret/token.json")
line_bot_api = LineBotApi(Secrets["ChannelAccessToken"])
handler = WebhookHandler(Secrets["ChanelSecret"])

@app.route("/",methods=["GET","POST"])
def index():
    return "OK"

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
    Reply = EH.CommandResp(event,line_bot_api)
    if Reply!=None:
        line_bot_api.reply_message(Token,Reply)

@handler.add(PostbackEvent)
def HandlePostBack(event):
    Token = event.reply_token
    Reply = EH.PostBackResp(event,line_bot_api)
    line_bot_api.reply_message(Token,Reply)

@handler.add(MessageEvent, message=ImageMessage)
def HandleImageMessage(event):
    Token = event.reply_token
    Reply = EH.ImageResp(event,line_bot_api)
    if Reply!=None:
        line_bot_api.reply_message(Token,Reply)

@handler.add(MessageEvent, message=FileMessage)
def HandleFileMessage(event):
    Token = event.reply_token
    Reply = EH.FileResp(event,line_bot_api)
    if Reply!=None:
        line_bot_api.reply_message(Token,Reply)


if __name__ == "__main__":
    app.run(host="0.0.0.0",port=5000,debug=True)
    # app.run(host="0.0.0.0",port=5000,ssl_context=('secret/cert.pem', 'secret/key.pem'))