# import flask related
from ast import JoinedStr
from multiprocessing import JoinableQueue
from ntpath import join
import re, sqlite3
from flask import Flask, request, abort
from urllib.parse import parse_qsl
import os

# import linebot related
from linebot import (
    LineBotApi, WebhookHandler
)
from linebot.exceptions import (
    InvalidSignatureError
)
from linebot.models import (
    MessageEvent, TextMessage, TextSendMessage,
    LocationSendMessage, ImageSendMessage, StickerSendMessage,
    VideoSendMessage, TemplateSendMessage, ButtonsTemplate, PostbackAction, MessageAction, URIAction,
    PostbackEvent, ConfirmTemplate, CarouselTemplate, CarouselColumn,FollowEvent,UnfollowEvent,
    ImageCarouselTemplate, ImageCarouselColumn, FlexSendMessage,AudioSendMessage
)
import json

from pyparsing import FollowedBy
from service_actions.translate import *
from service_actions.test import *
from service_actions.speechrecognition import *
from service_actions.audioanalysis import *
from service_actions.correct_pron import *
from translator import *
from txt2videoUrl import *

#  可使用指令:  單字庫、考試、正音、翻譯、功能介紹


# create flask server
app = Flask(__name__)
line_bot_api = LineBotApi('3BvVYSR5j98k7wgN08DljS4e3/KEVGl/rR3ch82H4/PL0rGJHQ07HC7mX7z11QZxJpd8+jJQ2bnk6p9L5su/8p1NWgOLTEVjQDmuHX2DcHCAh2bx3wsrEfsjJ5bV74V3UA484qv6q3BZ67QAGque4wdB04t89/1O/w1cDnyilFU=')
handler = WebhookHandler('3d88d7099067823f5171425421c8a2f1')


@app.route("/callback", methods=['POST'])
def callback():
    # get X-Line-Signature header value
    signature = request.headers['X-Line-Signature']

    # get request body as text
    body = request.get_data(as_text=True)
    app.logger.info("Request body: " + body)

    # handle webhook body
    try:
        print('receive msg')
        handler.handle(body, signature)
    except InvalidSignatureError:
        print("Invalid signature. Please check your channel access token/channel secret.")
        abort(400)
    return 'OK'

@handler.add(FollowEvent)
def handle_follow(event):
    con = sqlite3.connect('Line_Bot.db')
    cur = con.cursor()
    user_id = event.source.user_id
    cur.execute(f"INSERT INTO user (`userID`) VALUES ('{user_id}')")
    con.commit()
    con.close()

@handler.add(UnfollowEvent)
def handle_follow(event):
    con = sqlite3.connect('Line_Bot.db')
    cur = con.cursor()
    user_id = event.source.user_id
    cur.execute(f"DELETE FROM user WHERE `userID`='{user_id}'")
    cur.execute(f"DELETE FROM user_wronganswer WHERE `userID`='{user_id}'")
    con.commit()
    con.close()

@handler.add(PostbackEvent)
def handle_postback(event):
    
    con = sqlite3.connect('Line_Bot.db')
    cur = con.cursor()
    user_id = event.source.user_id
    userdata = list(cur.execute(f'SELECT * FROM user WHERE `userID`="{user_id}"'))
    con.commit()
    n_test = userdata[0][2]
    n_test_total = userdata[0][3]
    level = userdata[0][4]
    test_time = userdata[0][5]

    postback_data = dict(parse_qsl(event.postback.data))

    if postback_data.get('action')=='英翻中':
        cur.execute(f"UPDATE user SET en_zh_lookup='1' WHERE `userID`='{user_id}'")
        con.commit()
        line_bot_api.reply_message(event.reply_token, TextSendMessage(text='請輸入想翻譯的英文'))
    elif postback_data.get('action')=='中翻英':
        cur.execute(f"UPDATE user SET zh_en_lookup='1' WHERE `userID`='{user_id}'")
        con.commit()
        line_bot_api.reply_message(event.reply_token, TextSendMessage(text = '請輸入想翻譯的中文'))

### 答對 ###
    elif postback_data.get('action')=='True':
        number = int(postback_data.get('item'))
        ifexist = list(cur.execute(f"SELECT * FROM user_wronganswer WHERE (`userID`,`level`,`number`) = ('{user_id}','{level}','{number}')"))
        if len(ifexist) != 0:
            cur.execute(f"UPDATE user_wronganswer SET `remaining`='{ifexist[0][4]-1}' WHERE (`userID`,`level`,`number`) = ('{user_id}','{level}','{number}')")
            con.commit()
            cur.execute(f"DELETE FROM user_wronganswer WHERE (`userID`,`remaining`) = ('{user_id}','0')")
            con.commit()
        if n_test <= n_test_total:
            n_test += 1
            if n_test != n_test_total + 1:
                cur.execute(f"UPDATE user SET n_test='{n_test}' WHERE `userID`='{user_id}'")
                con.commit()
                if postback_data.get('state')=='new':
                    vocabulary_test(event,n_test,level)
                else:
                    wrong_word_test(event,user_id,n_test)
            else:
                answer = find_wrongword(user_id,test_time)
                score = f'測驗結束\n總共答對: {n_test_total-len(answer)}/{n_test_total} 題\n答錯題目: \n'
                for ans in answer:
                    score += ans[0]+' '+ans[1]+'.'+ans[2]+'\n'
                cur.execute(f"UPDATE user SET (`n_test`,`n_test_total`)=('1','0') WHERE `userID`='{user_id}'")
                con.commit()
                line_bot_api.reply_message(event.reply_token, TextSendMessage(text = score))
        else:
            cur.execute(f"UPDATE user SET (`n_test`,`n_test_total`)=('1','0') WHERE `userID`='{user_id}'")
            con.commit()
            line_bot_api.reply_message(event.reply_token, TextSendMessage(text = '測驗結束'))

### 答錯 ###
    elif postback_data.get('action')=='False':
        number = int(postback_data.get('item'))
        ifexist = cur.execute(f"SELECT * FROM user_wronganswer WHERE (`userID`,`level`,`number`) = ('{user_id}','{level}','{number}')")
        if len(list(ifexist)) == 0:
            cur.execute(f"INSERT INTO user_wronganswer (`userID`,`level`,`number`,`test_time`) VALUES ('{user_id}','{level}','{number}','{test_time}')")
            con.commit()
        else:
            cur.execute(f"UPDATE user_wronganswer SET (`test_time`,`remaining`)=('{test_time}','3') WHERE (`userID`,`level`,`number`) = ('{user_id}','{level}','{number}')")
            con.commit()
        if n_test <= n_test_total:
            n_test += 1
            if n_test != n_test_total + 1:
                cur.execute(f"UPDATE user SET n_test='{n_test}' WHERE `userID`='{user_id}'")
                con.commit()
                if postback_data.get('state')=='new':
                    vocabulary_test(event,n_test,level)
                else:
                    wrong_word_test(event,user_id,n_test)
            else:
                answer = find_wrongword(user_id,test_time)
                score = f'測驗結束\n總共答對: {n_test_total-len(answer)}題\n答錯題目: \n'
                for ans in answer:
                    score += ans[0]+' '+ans[1]+'.'+ans[2]+'\n'
                cur.execute(f"UPDATE user SET (`n_test`,`n_test_total`)=('1','0') WHERE `userID`='{user_id}'")
                con.commit()
                line_bot_api.reply_message(event.reply_token, TextSendMessage(text = score))
        else:
            line_bot_api.reply_message(event.reply_token, TextSendMessage(text = '測驗結束'))

### 選擇題數 ###
    elif postback_data.get('action')=='題數':
        n_test_total = int(postback_data.get('item'))
        cur.execute(f"UPDATE user SET (`n_test`,`n_test_total`,`test_time`)=('1','{n_test_total}','{test_time+1}') WHERE `userID`='{user_id}'")
        userdata = list(cur.execute(f'SELECT * FROM user WHERE `userID`="{user_id}"'))
        con.commit()
        level = userdata[0][4]
        vocabulary_test(event,1,level)

### 選擇難度 ###
    elif postback_data.get('action')=='難度':
        cur.execute(f"UPDATE user SET chosenlevel='{int(postback_data.get('item'))}' WHERE `userID`='{user_id}'")
        con.commit()
        test_type(event,int(postback_data.get('item')))
### 錯字重考 ###
    elif postback_data.get('action')=='錯字重考':
        words = list(cur.execute(f'SELECT * FROM user_wronganswer WHERE (`userID`)=("{user_id}")'))
        cur.execute(f"UPDATE user SET (`n_test`,`n_test_total`,`test_time`)=('1','{len(words)}','{test_time+1}') WHERE `userID`='{user_id}'")
        con.commit()
        wrong_word_test(event,user_id,1)
### 正音分數 ###    
    elif postback_data.get('action')=='正音分數':
        messages=[]
        messages.append(TextSendMessage(text='錄製短時英文語音即可隨時開始'))
        line_bot_api.reply_message(event.reply_token, messages)

    elif postback_data.get('action')=='聽發音':
        cur.execute(f"UPDATE user SET check_pron='1' WHERE `userID`='{user_id}'")
        con.commit()
        messages=[]
        messages.append(TextSendMessage(text='請輸入想聽的英文單字(第一個字母請使用小寫)'))
        line_bot_api.reply_message(event.reply_token, messages)
    elif postback_data.get('action')=='高中單字庫':
        messages=[]
        messages.append(TextSendMessage(text='https://douze.pixnet.net/blog/post/398218087?fbclid=IwAR13BuahWHzS8cv_q_YlObksq1BH7zIh-8eaMpdo73gjE9FptpZMNfBwwKY'))
        line_bot_api.reply_message(event.reply_token, messages)
    elif postback_data.get('action')=='錯誤單字':
        message = ''
        wrong_words = find_all_wrongword(user_id)
        for word in wrong_words:
            message += word[0]+' '+word[1]+'.'+word[2]+'\n'
        message += f'共 {len(wrong_words)} 個單字' 
        line_bot_api.reply_message(event.reply_token, TextSendMessage(text = message))

    con.close()

# handle msg
@handler.add(MessageEvent)
def handle_message(event):
    user_id = event.source.user_id
    con = sqlite3.connect('Line_Bot.db')
    cur = con.cursor()
    userdata = list(cur.execute(f'SELECT * FROM user WHERE `userID`="{user_id}"'))
    en_zh_lookup = userdata[0][6]
    zh_en_lookup = userdata[0][7]
    check_pron = userdata[0][8]

    if event.message.type=='text':
        msg = event.message.text
    ### 英翻中 ###
        if en_zh_lookup:
            cur.execute(f"UPDATE user SET en_zh_lookup='0' WHERE `userID`='{user_id}'")
            con.commit()
            translatedmsg = translate_en_zh(msg)
            line_bot_api.reply_message(event.reply_token, TextSendMessage(text = translatedmsg))
    ### 中翻英 ###
        elif zh_en_lookup:
            cur.execute(f"UPDATE user SET zh_en_lookup='0' WHERE `userID`='{user_id}'")
            con.commit()
            translatedmsg = translate_zh_en(msg)
            line_bot_api.reply_message(event.reply_token, TextSendMessage(text = translatedmsg))
        elif check_pron:
            cur.execute(f"UPDATE user SET check_pron='0' WHERE `userID`='{user_id}'")
            con.commit()
            video_url = init_video_urls()
            message = []
            try:
                message.append(TextSendMessage(video_url[f'{msg}']))
            except KeyError:
                message.append(TextSendMessage(text = '查無此單字'))
            return line_bot_api.reply_message(event.reply_token, message)
            
        elif '翻譯' in msg:
            translate_type(event)
        elif '考試' in msg:
            choose_level2(event)
        elif '單字庫' in msg:
            vocabulary_database(event)
        elif '正音' in msg:
            correct_pron_type(event)
        elif '功能介紹' in msg:
            message = '功能介紹:\n'
            message += '---翻譯--- \n幫您中翻英、英翻中!\n'
            message += '---考試--- \n指定難度、題數，就可以幫您做高中單字的小測驗，還能複習錯過的單字!\n'
            message += '---正音--- \n查詢高中單字的正確發音，也可以幫您的發音打分數!\n'
            message += '---單字庫--- \n看看高中單字都有些甚麼，還能看看之前測驗錯了哪些字!\n'
            #message += '\n官網請見: https://www.youtube.com/watch?v=dQw4w9WgXcQ'
            line_bot_api.reply_message(event.reply_token, TextSendMessage(text = message))

### 正音 ###
    elif event.message.type=='audio':
        filename_wav='temp_audio.wav'
        filename_mp3='temp_audio.mp3'
        message_content = line_bot_api.get_message_content(event.message.id)
        with open(filename_mp3, 'wb') as fd:
            for chunk in message_content.iter_content():
                fd.write(chunk)
        os.system(f'ffmpeg -y -i {filename_mp3} {filename_wav} -loglevel quiet')
        text = speechtotext()
        texttospeech(text)
        nums = [SimilarityAnalysis1(),SimilarityAnalysis2(),SimilarityAnalysis3()]
        text1 = '{:.2%}'.format(1-min(nums)/1300)
        messages=[]
        messages.append(TextSendMessage(text))
        if text != 'No speech could be recognized':
            messages.append(TextSendMessage(text=f'相似度為{text1}'))     
        line_bot_api.reply_message(event.reply_token, messages)
    
    con.close()


# run app
if __name__ == "__main__":
    app.run(host='127.0.0.1', port=5566)