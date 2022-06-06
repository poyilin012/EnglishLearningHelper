from urllib.parse import parse_qsl, parse_qs
import datetime, random, json
from line_chatbot_api import *
import re, sqlite3


def correct_pron_type(event):
    message = TemplateSendMessage(
        alt_text='Buttons template',
        template=ButtonsTemplate(
            title='請選擇需要的服務項目',
            text='請在下方點選您需要的服務項目',
            actions=[
                PostbackAction(
                    label='幫我打分數',
                    display_text='幫我打分數',
                    data='action=正音分數'
                ),
                PostbackAction(
                    label='查詢高中英文單字發音',
                    display_text='查詢高中英文單字發音',
                    data='action=聽發音'
                ),
            ]
        )
    )
    line_bot_api.reply_message(event.reply_token, message)

