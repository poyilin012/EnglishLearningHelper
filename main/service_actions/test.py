from urllib.parse import parse_qsl, parse_qs
import datetime, random, json
from line_chatbot_api import *
import re, sqlite3

answer = []
con = sqlite3.connect('Line_Bot.db',check_same_thread=False)
cur = con.cursor()
result0 = list(cur.execute('SELECT * FROM vocabulary_level_1 ORDER BY number'))
result1 = list(cur.execute('SELECT * FROM vocabulary_level_2 ORDER BY number'))
result2 = list(cur.execute('SELECT * FROM vocabulary_level_3 ORDER BY number'))
result3 = list(cur.execute('SELECT * FROM vocabulary_level_4 ORDER BY number'))
result4 = list(cur.execute('SELECT * FROM vocabulary_level_5 ORDER BY number'))
result5 = list(cur.execute('SELECT * FROM vocabulary_level_6 ORDER BY number'))
result = [result0,result1,result2,result3,result4,result5]
database = result0

def choose_level2(event):
    message = TemplateSendMessage(
        alt_text='選取難度',
        template=CarouselTemplate(
            columns=[
                CarouselColumn(
                    title='請選擇難度',
                    text='1~3級',
                    actions=[
                        PostbackAction(
                            label='1級',
                            display_text='1級',
                            data='action=難度&item=0'
                        ),
                        PostbackAction(
                            label='2級',
                            display_text='2級',
                            data='action=難度&item=1'
                        ),
                        PostbackAction(
                            label='3級',
                            display_text='3級',
                            data='action=難度&item=2'
                        )
                    ]
                ),
                CarouselColumn(
                    title='請選擇難度',
                    text='4~6級',
                    actions=[
                        PostbackAction(
                            label='4級',
                            display_text='4級',
                            data='action=難度&item=3'
                        ),
                        PostbackAction(
                            label='5級',
                            display_text='5級',
                            data='action=難度&item=4'
                        ),
                        PostbackAction(
                            label='6級',
                            display_text='5級',
                            data='action=難度&item=5'
                        )
                    ]
                ),
                CarouselColumn(
                    title='複習',
                    text='複習曾經答錯的單字',
                    actions=[
                        PostbackAction(
                            label='錯字重考',
                            display_text='錯字重考',
                            data='action=錯字重考'
                        ),
                        PostbackAction(
                            label='功能開發中',
                            display_text=' ',
                            data='action='
                        ),
                        PostbackAction(
                            label='功能開發中',
                            display_text=' ',
                            data='action='
                        )
                    ]
                )
            ]
        )
    )
    line_bot_api.reply_message(event.reply_token, message)

def test_type(event,level):
    global database
    database = result[level]
    message = TemplateSendMessage(
        alt_text='Buttons template',
        template=ButtonsTemplate(
            # thumbnail_image_url=url_for('static', filename='images/brown_1024.jpg', _external=True),
            title='請選擇測驗題數',
            text='請在下方點選您需要的服務項目',
            actions=[
                #options a,b,c,d
                PostbackAction(
                    label='做 10 題就好',
                    display_text='做 10 題就好',
                    # if correct and answer
                    data='action=題數&item=10'
                ),
                PostbackAction(
                    label='30 題剛剛好',
                    display_text='30 題剛剛好',
                    data='action=題數&item=30'
                ),
                PostbackAction(
                    label='我要挑戰 100 題',
                    display_text='我要挑戰 100 題',
                    data='action=題數&item=100'
                ),
            ]
        )
    )
    line_bot_api.reply_message(event.reply_token, message)

def vocabulary_test(event,n_test,level):
    database = result[level]
    ifcorrect = []
    options = random.sample(range(0,len(database)-1),4)
    question = random.choice(options)
    for ans in options:
        ifcorrect.append(question == ans)
    message = TemplateSendMessage(
        alt_text='Buttons template',
        template=ButtonsTemplate(
            # thumbnail_image_url=url_for('static', filename='images/brown_1024.jpg', _external=True),
            title=f'{n_test}. ' + database[question][1],
            text='4選1',
            actions=[
                #options a,b,c,d
                PostbackAction(
                    label='(A)'+ database[options[0]][2]+'.' + database[options[0]][3],
                    display_text='(A)',
                    data=f'action={ifcorrect[0]}&item={database[question][0]}&state=new'
                ),
                PostbackAction(
                    label='(B)'+ database[options[1]][2]+'.' + database[options[1]][3],
                    display_text='(B)',
                    data=f'action={ifcorrect[1]}&item={database[question][0]}&state=new'
                ),
                PostbackAction(
                    label='(C)'+ database[options[2]][2]+'.' + database[options[2]][3],
                    display_text='(C)',
                    data=f'action={ifcorrect[2]}&item={database[question][0]}&state=new'
                ),
                PostbackAction(
                    label='(D)'+ database[options[3]][2]+'.' + database[options[3]][3],
                    display_text='(D)',
                    data=f'action={ifcorrect[3]}&item={database[question][0]}&state=new'
                )
            ]
        )
    )
    line_bot_api.reply_message(event.reply_token, message)


def choose_level(event):
    message = TemplateSendMessage(
        alt_text='Buttons template',
        template=ButtonsTemplate(
            title='請選擇測驗單字等級',
            text='請在下方點選您需要的服務項目',
            actions=[
                PostbackAction(
                    label='3級',
                    display_text='3',
                    data='action=難度&item=2'
                ),
                PostbackAction(
                    label='4級',
                    display_text='4',
                    data='action=難度&item=3'
                ),
                PostbackAction(
                    label='5級',
                    display_text='5',
                    data='action=難度&item=4'
                ),
                PostbackAction(
                    label='6級',
                    display_text='6',
                    data='action=難度&item=5'
                )
            ]
        )
    )
    line_bot_api.reply_message(event.reply_token, message)

def wrong_word_test(event,ID,n_test):
    words = list(cur.execute(f'SELECT * FROM user_wronganswer WHERE (`userID`)=("{ID}")'))
    question_number = random.choice(words)
    level = question_number[1]
    database = result[level]
    cur.execute(f"UPDATE user SET chosenlevel='{level}' WHERE `userID`='{ID}'")
    con.commit()
    question = question_number[2]
    others = random.sample(range(0,len(database)-1),3)
    questions = [question,others[0],others[1],others[2]]
    dice = random.sample(range(0,4),4)
    options = []
    ifcorrect = []
    for i in dice:
        options.append(questions[i])
    for ans in options:
        ifcorrect.append(question == ans)
    print(ifcorrect)
    message = TemplateSendMessage(
        alt_text='Buttons template',
        template=ButtonsTemplate(
            title=f'{n_test}. ' + database[question-1][1],
            text='4選1',
            actions=[
                #options a,b,c,d
                PostbackAction(
                    label='(A)'+ database[options[0]-1][2]+'.' + database[options[0]-1][3],
                    display_text='(A)',
                    data=f'action={ifcorrect[0]}&item={database[question-1][0]}&level={level}&state=old'
                ),
                PostbackAction(
                    label='(B)'+ database[options[1]-1][2]+'.' + database[options[1]-1][3],
                    display_text='(B)',
                    data=f'action={ifcorrect[1]}&item={database[question-1][0]}&level={level}&state=old'
                ),
                PostbackAction(
                    label='(C)'+ database[options[2]-1][2]+'.' + database[options[2]-1][3],
                    display_text='(C)',
                    data=f'action={ifcorrect[2]}&item={database[question-1][0]}&level={level}&state=old'
                ),
                PostbackAction(
                    label='(D)'+ database[options[3]-1][2]+'.' + database[options[3]-1][3],
                    display_text='(D)',
                    data=f'action={ifcorrect[3]}&item={database[question-1][0]}&level={level}&state=old'
                )
            ]
        )
    )
    line_bot_api.reply_message(event.reply_token, message)

def vocabulary_database(event):
    message = TemplateSendMessage(
        alt_text='Buttons template',
        template=ButtonsTemplate(
            title='查閱單字庫',
            text='請在下方點選想要查閱的單字庫',
            actions=[
                PostbackAction(
                    label='考試錯過的單字',
                    display_text='錯誤單字',
                    data='action=錯誤單字'
                ),
                PostbackAction(
                    label='高中英文單字庫',
                    display_text='高中英文單字',
                    data='action=高中單字庫'
                )
            ]
        )
    )
    line_bot_api.reply_message(event.reply_token, message)
    
    
def find_word(level,number):
    data = list(cur.execute(f'SELECT * FROM vocabulary_level_{level+1} WHERE `number`="{number}"'))
    wrong_word = data[0][1:4]
    return wrong_word

def find_wrongword(ID,test_time):
    wrong_words = []
    words = list(cur.execute(f'SELECT * FROM user_wronganswer WHERE (`userID`,`test_time`)=("{ID}","{test_time}")'))
    for word in words:
        wrong_words.append(find_word(word[1],word[2]))
    return wrong_words

def find_all_wrongword(ID):
    wrong_words = []
    words = list(cur.execute(f'SELECT * FROM user_wronganswer WHERE (`userID`)=("{ID}")'))
    for word in words:
        wrong_words.append(find_word(word[1],word[2]))
    return wrong_words
