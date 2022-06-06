from transformers import MarianTokenizer, MarianMTModel
from opencc import OpenCC
'''
# 初始化
tokenizer = MarianTokenizer.from_pretrained("./opus-mt-en-zh")
model = MarianMTModel.from_pretrained("./opus-mt-en-zh")
tokenizer_ch = MarianTokenizer.from_pretrained("./opus-mt-en-zh")
model_ch = MarianMTModel.from_pretrained("./opus-mt-en-zh")
cc = OpenCC('s2t')

# 英翻簡中
def translate_en_zh(entext):
    text = entext
    batch = tokenizer([text], return_tensors="pt")

    generated_ids = model.generate(**batch)
    result = tokenizer.batch_decode(generated_ids, skip_special_tokens=True)[0]

# 簡中轉繁中
    chtext = cc.convert(result)
    return chtext

def translate_zh_en(chtext):
    text = chtext
    batch = tokenizer_ch([text], return_tensors="pt")

    generated_ids = model_ch.generate(**batch)
    result = tokenizer_ch.batch_decode(generated_ids, skip_special_tokens=True)[0]

# 簡中轉繁中
    entext = cc.convert(result)
    return entext
'''


# 初始化 (英翻中)
tokenizer_en2zh = MarianTokenizer.from_pretrained("./opus-mt-en-zh")
model_en2zh = MarianMTModel.from_pretrained("./opus-mt-en-zh")
cc_en2zh = OpenCC('s2t')

def translate_en_zh(text):
# 英 翻 簡中 翻繁中
    batch = tokenizer_en2zh([text], return_tensors="pt")
    generated_ids = model_en2zh.generate(**batch)
    result = tokenizer_en2zh.batch_decode(generated_ids, skip_special_tokens=True)[0]
    return cc_en2zh.convert(result)


# 初始化 (中翻英)
tokenizer_zh2en = MarianTokenizer.from_pretrained("./opus-mt-zh-en")
model_zh2en = MarianMTModel.from_pretrained("./opus-mt-zh-en")
cc_zh2en = OpenCC('t2s')

# 繁中 翻 簡中 翻英
def translate_zh_en(text):
    text = cc_en2zh.convert(text)
    batch = tokenizer_zh2en([text], return_tensors="pt")
    generated_ids = model_zh2en.generate(**batch)
    result = tokenizer_zh2en.batch_decode(generated_ids, skip_special_tokens=True)[0]
    return result

