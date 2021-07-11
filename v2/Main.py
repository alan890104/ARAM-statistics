import os
from flask import Flask, request, abort,send_from_directory
from linebot import LineBotApi, WebhookHandler
from linebot.exceptions import InvalidSignatureError
from linebot.models import (
    MessageEvent, TextMessage, ImageMessage, FileMessage,TextSendMessage
)
from linebot.models.events import PostbackEvent
from apscheduler.schedulers.background import BackgroundScheduler
import AccessGameData as AGD
import Builder as BLD
import Database as DB
import EventHandler as EH

# Origin Route = https://lol-winrate.herokuapp.com/callback

app = Flask(__name__)
Secrets = AGD.JsonRead("secret/token.json")
line_bot_api = LineBotApi(Secrets["ChannelAccessToken"])
handler = WebhookHandler(Secrets["ChanelSecret"])
scheduler = BackgroundScheduler()
UPDATE_SIGNAL = False

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
    global UPDATE_SIGNAL
    if UPDATE_SIGNAL: return
    if event.source.user_id == "Udeadbeefdeadbeefdeadbeefdeadbeef": return
    Token = event.reply_token
    Reply = EH.CommandResp(event,line_bot_api)
    if Reply!=None:
        line_bot_api.reply_message(Token,Reply)

@handler.add(PostbackEvent)
def HandlePostBack(event):
    global UPDATE_SIGNAL
    if UPDATE_SIGNAL: return
    Token = event.reply_token
    Reply = EH.PostBackResp(event,line_bot_api)
    line_bot_api.reply_message(Token,Reply)

@handler.add(MessageEvent, message=ImageMessage)
def HandleImageMessage(event):
    global UPDATE_SIGNAL
    if UPDATE_SIGNAL: return
    Token = event.reply_token
    Reply = EH.ImageResp(event,line_bot_api)
    if Reply!=None:
        line_bot_api.reply_message(Token,Reply)

@handler.add(MessageEvent, message=FileMessage)
def HandleFileMessage(event):
    global UPDATE_SIGNAL
    if UPDATE_SIGNAL: return
    Token = event.reply_token
    Reply = EH.FileResp(event,line_bot_api)
    if Reply!=None:
        line_bot_api.reply_message(Token,Reply)

@scheduler.scheduled_job("cron",hour='1,13')
def Update_Version_Game_Team_EVERY_DAY() -> None:
    '''
    Lock the bot while updating version and DB
    (1:00 and 13:00 are times to update)
    '''
    global UPDATE_SIGNAL
    UPDATE_SIGNAL = True
    BLD.UpdateVersion()
    BLD.UpdateGameTeamTable()
    UPDATE_SIGNAL = False

@scheduler.scheduled_job("cron",day_of_week="sun",hour=9)
def Update_ELO_EVERY_SUN() -> None:
    global UPDATE_SIGNAL
    UPDATE_SIGNAL = True
    BLD.UpdateELO()
    UPDATE_SIGNAL = False

@scheduler.scheduled_job("interval",days=5)
def BackUpDatabase_EVERY_FIVE_DAYS() -> None:
    '''
    Copy database to tmp folder every 5 days
    '''
    Agent = DB.DBAgent()
    Agent._Backup()

# @app.route('/rankimg/<path:filename>', methods=['GET', 'POST'])
# def PictureProvider(filename):
#     uploads = os.path.join(app.root_path,"static\Rank")
#     return send_from_directory(directory=uploads, filename=filename)

if __name__ == "__main__":
    # scheduler.start()
    app.run(host="0.0.0.0",port=5000,debug=True)
    # app.run(host="0.0.0.0",port=5000,ssl_context=('secret/cert.pem', 'secret/key.pem'))