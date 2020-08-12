from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
import smtplib
from replay import player_datail
from app import lineNotifyMessage


lineNotifyMessage(player_datail('X嘻哈酷老頭兒'))
