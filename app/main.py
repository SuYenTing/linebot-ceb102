#!/usr/bin/env python
# coding: utf-8

# 載入相關套件
import datetime
import json
import mysql.connector
from flask import Flask, request, abort    
from flask_apscheduler import APScheduler                          # 任務排程
from apscheduler.schedulers.background import BackgroundScheduler  # 調整APScheduler時區使用
from linebot import LineBotApi, WebhookHandler
from linebot.exceptions import InvalidSignatureError
from linebot.models import MessageEvent, TextMessage, TextSendMessage, ImageMessage, TextSendMessage


# 排程任務
class Config(object):
    JOBS = [{'id':'morning', 'func':'__main__:RemindClass', 'args':('上午',), 'trigger':'cron', 'hour':8, 'minute':50},
            {'id':'afternoon', 'func':'__main__:RemindClass', 'args':('下午',), 'trigger':'cron', 'hour':13, 'minute':20},
            {'id':'night', 'func':'__main__:RemindClass', 'args':('夜間',), 'trigger':'cron', 'hour':18, 'minute':20},
            {'id':'tmrClass', 'func':'__main__:RemindTmrClass', 'trigger':'cron', 'hour':21, 'minute':30}]
    SCHEDULER_TIMEZONE = 'Asia/Taipei'


# 課前提醒任務
def RemindClass(status):
    
    # 讀取今日行程資訊
    conn = mysql.connector.connect(host=secretFile['host'], 
                                   user=secretFile['user'], 
                                   password=secretFile['password'],
                                   port=secretFile['port'], 
                                   database=secretFile['dbName'])
    cursor = conn.cursor()
    query = "select * from linebot.curriculum where dates = '" + str(datetime.datetime.now().strftime('%Y-%m-%d')) + "';"
    cursor.execute(query)
    result = cursor.fetchall()
    conn.close()

    # 判斷今日是否有行程 若沒有則不做任何動作
    if result:

        # 若有行程 則進行判斷是否要推播
        for row in result:

                # 行程資訊
                period = row[1]
                className = row[2]
                principal = row[3]

                # 判斷行程期間是否與當前期間一致 若一致則進行對應操作
                if status == period:

                    if period == '上午':

                        if principal:
                            msg = '早安! 今早的課程是「' + className + '」\n大家請記得要打卡唷!\n教室日誌要麻煩 ' + principal[-2::] + ' 填寫唷!'
                        else:
                            msg = '早安! 今早的課程是「' + className + '」\n大家請記得要打卡唷!'
                        line_bot_api.push_message(lineGroupID, TextSendMessage(text=msg))

                    elif period == '下午':

                        if principal:
                            msg = '午安! 下午的課程是「' + className + '」\n大家請記得要打卡唷!\n教室日誌要麻煩 ' + principal[-2::] + ' 填寫唷!'
                        else:
                            msg = '午安! 下午的課程是「' + className + '」\n大家請記得要打卡唷!'
                        line_bot_api.push_message(lineGroupID, TextSendMessage(text=msg))

                    elif period == '夜間':

                        if principal:
                            msg = '晚上好! 晚上的課程是「' + className + '」\n大家請記得要打卡唷!\n教室日誌要麻煩 ' + principal[-2::] + ' 填寫唷!'
                        else:
                            msg = '晚上好! 晚上的課程是「' + className + '」\n大家請記得要打卡唷!'
                        line_bot_api.push_message(lineGroupID, TextSendMessage(text=msg))


# 提醒明日課程任務
def RemindTmrClass():
    
    # 讀取明日行程資訊
    conn = mysql.connector.connect(host=secretFile['host'], 
                                       user=secretFile['user'], 
                                       password=secretFile['password'],
                                       port=secretFile['port'], 
                                       database=secretFile['dbName'])
    cursor = conn.cursor()
    query = "select * from linebot.curriculum where dates = '" + str((datetime.datetime.now() + datetime.timedelta(days=1)).strftime('%Y-%m-%d')) + "';"
    cursor.execute(query)
    result = cursor.fetchall()
    conn.close()

    # 判斷明日是否有行程 若沒有則不做任何動作
    if result:
        msg = '提醒大家 明日有上課唷!\n課程資訊如下: \n'
        for row in result:
            period = row[1]
            className = row[2]
            msg = msg + period + ' ' + className + '\n'
        msg = msg + '記得要來唷!'
        line_bot_api.push_message(lineGroupID, TextSendMessage(text=msg))


# 判斷使用者輸入'小幫手'訊息是否有關鍵字詞 若有做對應訊息處理
def FindKeyWordInText(text, userId):
    
    # 比對關鍵字詞 若有則輸出對應訊息
    for key in keywordInfoData:
        if key[1] in text:
            return(key[2])
        
    # 若比對不到關鍵字 則紀錄使用者輸入訊息 並回傳提示關鍵字訊息
    # 使用者輸入找不到的訊息可做為之後開發參考
    conn = mysql.connector.connect(host=secretFile['host'], 
                                       user=secretFile['user'], 
                                       password=secretFile['password'],
                                       port=secretFile['port'], 
                                       database=secretFile['dbName'])
    cursor = conn.cursor()
    query = 'INSERT INTO linebot.msg (user_id, time, msg) VALUES (%s, %s, %s)'
    value = (userId, datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S"), text)
    cursor.execute(query, value)
    conn.commit()
    conn.close()
    
    return(remindKeyMsg)


# 讀取linebot和mysql連線資訊
secretFile = json.load(open('secretFile.json', 'r'))

# 讀取LineBot驗證資訊
line_bot_api = LineBotApi(secretFile['channelAccessToken'])
handler = WebhookHandler(secretFile['channelSecret'])

# 推播群組的ID
lineGroupID = secretFile['lineGroupID']

# 讀取資料庫關鍵字對應訊息
conn = mysql.connector.connect(host=secretFile['host'], 
                               user=secretFile['user'], 
                               password=secretFile['password'],
                               port=secretFile['port'], 
                               database=secretFile['dbName'])
cursor = conn.cursor()
query = "select * from linebot.keyword;"
cursor.execute(query)
keywordInfoData = cursor.fetchall()
conn.close()

# 關鍵字列表
keys = set()
for key in keywordInfoData:
    keys.add(key[0])
    
# 提醒使用者可輸入關鍵字訊息(將所有關鍵字列出來)
remindKeyMsg = '糟糕! 我聽不懂您在說什麼? \n我目前可以輸入的關鍵字有：\n\n'
for key in keys:
    remindKeyMsg = remindKeyMsg + ' > ' + key + '\n'
remindKeyMsg = remindKeyMsg + '\n您可以嘗試輸入看看唷!\n例如：「小幫手 筆記」'

# 建立Flask
app = Flask(__name__)

# 建立任務
app.config.from_object(Config())

# linebot接收訊息
@app.route("/", methods=['POST'])
def callback():
    # get X-Line-Signature header value: 驗證訊息來源
    signature = request.headers['X-Line-Signature']

    # get request body as text: 讀取訊息內容
    body = request.get_data(as_text=True)
    app.logger.info("Request body: " + body)

    # handle webhook body
    try:
        handler.handle(body, signature)
    except InvalidSignatureError:
        print("Invalid signature. Please check your channel access token/channel secret.")
        abort(400)

    return 'OK'

# linebot處理文字訊息
@handler.add(MessageEvent, message=TextMessage)
def handle_message(event):

    # linebot關鍵字回傳訊息
    if '小幫手' in event.message.text:
        replyMsg = FindKeyWordInText(text=event.message.text, userId=event.source.user_id)
        line_bot_api.reply_message(event.reply_token, TextSendMessage(text=replyMsg))

# 開始運作Flask
if __name__ == "__main__":
    scheduler = APScheduler(BackgroundScheduler(timezone="Asia/Taipei"))  # 例項化APScheduler
    scheduler.init_app(app)  # 把任務列表放進flask
    scheduler.start()        # 啟動任務列表
    app.run(host='0.0.0.0')
