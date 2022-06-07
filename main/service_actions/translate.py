from urllib.parse import parse_qsl, parse_qs
import datetime
from line_chatbot_api import *
import re, sqlite3

def translate_type(event):
    message = TemplateSendMessage(
        alt_text='Buttons template',
        template=ButtonsTemplate(
            title='請問需要如何翻譯呢?',
            text='請在下方點選您需要的服務項目',
            actions=[
                PostbackAction(
                    label='中翻英',
                    display_text='中翻英',
                    data='action=中翻英&item=apple'
                ),
                PostbackAction(
                    label='英翻中',
                    display_text='英翻中',
                    data='action=英翻中&item=apple'
                )
            ]
        )
    )
    line_bot_api.reply_message(event.reply_token, message)
