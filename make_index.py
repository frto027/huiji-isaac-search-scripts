# pinyin dict from https://www.mdbg.net/chinese/dictionary ---> cedict_ts.u8

# input -> item.tabx (Page, NameZH, NameList), itemkeywords.tabx(Page, NameAlias)
# output -> itemkeywords.tabx (PinyinIndex)

import re
import mwclient
import json

pinyins = dict()

regex = re.compile(r"^[^ ]+ ([^ ]+) \[([A-Za-z0-9 ]+)\] .*$")

with open('cedict_ts.u8', 'r', encoding='utf8') as f:
    for line in f.readlines():
        group = regex.match(line)
        if not group:
            continue
        name = group[1]
        pinyin = group[2].replace("1","").replace("2","").replace("3","").replace("4","").replace("5","").replace(" ","")
        if not name in pinyins:
            pinyins[name] = str.lower(pinyin)

pinyins['？'] = ""
pinyins["("] = ""
pinyins[")"] = ""
# pinyins["？ 卡"]="wenhaoka"
# pinyins['卡'] = "ka"
pinyins['！'] =''
pinyins[' '] = ''
pinyins['绿'] = "lv"
pinyins['魔法'] = "m"

def get_pinyin(word):
    if word in pinyins:
        return pinyins[word]
    ret = ""

    i = 0
    while i < len(word):
        if re.match("[a-zA-Z0-9]", word[i]):
            ret += word[i]
            i += 1
            continue
        j = len(word)
        found = False
        while j > i:
            if word[i:j] in pinyins:
                ret += pinyins[word[i:j]]
                i = j
                found = True
                break
            j -= 1
        if found:
            continue
        ret += word[i]
        i += 1
    return ret

site = mwclient.Site("isaac.huijiwiki.com",clients_useragent="Frto027/make_index.py")
with open("D:/pswd.txt", "r") as f:
    site.login("Frto027", f.read())

itemPage = site.Pages["Data:Item.tabx"]
keywordPage = site.Pages["Data:ItemKeywords.tabx"]

items = dict()

itemPageJson = json.loads(itemPage.text())

def add_pinyin(page, word):
    pinyin = get_pinyin(word)
    if pinyin == word:
        return
    if pinyin == '':
        return
    if not page in items:
        items[page] = set()
    # print(f"{word}=>{pinyin}")
    items[page].add(pinyin)

for item in itemPageJson["data"]:
    page = item[0]
    namezh = item[1]
    namelist = item[5]
    add_pinyin(page, namezh)
    for n in namelist.split(";"):
        add_pinyin(page, n)
keywordPageJson = json.loads(keywordPage.text())
for item in keywordPageJson["data"]:
    page = item[0]
    namealias = item[1]
    if namealias == None:
        continue
    for n in namealias.split(";"):
        add_pinyin(page, n)

for item in keywordPageJson["data"]:
    page = item[0]
    if not page in items:
        continue
    item[2] = ';'.join(items[page])

# add data to keywordPage
# print(keywordPageJson)
keywordPage.save(json.dumps(keywordPageJson), summary="优化拼音算法")