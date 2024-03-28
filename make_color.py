# 启动前需要在collectibles目录下放所有的道具png，在trinkets下放饰品png
# 解包后的文件名即可，要求文件名包含正则[0-9]{3}作为ID
from pathlib import Path
import re
import cv2
import numpy as np
import colour
import mwclient
import json

col = Path("collectibles")
tri = Path("trinkets")


allcolors = set()

def str2colorimg(color):
    r = np.array([[[int(color[0:2], 16), int(color[2:4], 16), int(color[4:6], 16)]]],dtype='float32')/255
    return r
def str2rgb(color):
    return np.array([int(color[0:2], 16), int(color[2:4], 16), int(color[4:6], 16)])/255
def str2lab(color):
    return np.array(cv2.cvtColor(str2colorimg(color), cv2.COLOR_RGB2LAB)[0,0],dtype='float32')

def distance(colorA, colorB):
    colora = cv2.cvtColor(str2colorimg(colorA), cv2.COLOR_RGB2LAB)
    colorb = cv2.cvtColor(str2colorimg(colorB), cv2.COLOR_RGB2LAB)
    return colour.delta_E(colora,colorb)[0,0]

page_to_colors:dict[str, set[str]] = dict()

for file in col.glob("*.png"):
    id = re.match(".*([0-9]{3}).*",file.name)[1]
    page = "c" + id.lstrip("0")
    mycolors:set[str] = set()
    mat = cv2.imread(str(file), cv2.IMREAD_UNCHANGED)
    for i in range(mat.shape[0]):
        for j in range(mat.shape[1]):
            if mat[i,j,3] > 0:
                color = "%02x%02x%02x" % (mat[i,j,2], mat[i,j,1], mat[i,j,0])
                mycolors.add(color)
                allcolors.add(color)
    page_to_colors[page] = mycolors

for file in tri.glob("*.png"):
    id = re.match(".*([0-9]{3}).*",file.name)[1]
    page = "t" + id.lstrip("0")
    mycolors:set[str] = set()
    mat = cv2.imread(str(file), cv2.IMREAD_UNCHANGED)
    for i in range(mat.shape[0]):
        for j in range(mat.shape[1]):
            if mat[i,j,3] > 0:
                color = "%02x%02x%02x" % (mat[i,j,2], mat[i,j,1], mat[i,j,0])
                mycolors.add(color)
                allcolors.add(color)
    page_to_colors[page] = mycolors

preset_colors = "000000,c00000,00c000,0000c0,c0c000,c000c0,00c0c0,c0c0c0".split(',')

def to_nearest_color(color):
    distances = [distance(x, color) for x in preset_colors]
    near_dist = min(distances)
    ret = ""
    for i in range(len(distances)):
        if distances[i] - near_dist < 2:
            ret += (str(i)) + ","
    return ret

def get_item_nearest_color(page):
    colors = page_to_colors[page]
    ncolors = set()
    for color in colors:
        ncolors.add(to_nearest_color(color))
    ret_list = list(ncolors)
    ret_list.sort()
    return ';'.join(ret_list)

# for page in page_to_colors:
#     print(get_item_nearest_color(page))
#     break


site = mwclient.Site("isaac.huijiwiki.com",clients_useragent="Frto027/make_index.py")
with open("D:/pswd.txt", "r") as f:
    site.login("Frto027", f.read())

keywordPage = site.Pages["Data:ItemKeywords.tabx"]
keywordPageJson = json.loads(keywordPage.text())
for item in keywordPageJson["data"]:
    page = item[0]
    if not page in page_to_colors:
        continue
    item[3] = get_item_nearest_color(page)

keywordPage.save(json.dumps(keywordPageJson), summary="自动更新颜色")
# all_color_list = list(allcolors)

# with open("colors.m","w") as f:
#     rgbcolor = "rgb=["

#     f.write('color=[')
#     for c in all_color_list:
#         f.write(','.join([str(x) for x in str2lab(c)]))
#         f.write(';')
#         rgbcolor += ','.join([str(x) for x in str2rgb(c) ]) + ';'
#     rgbcolor += '];'

#     f.write('];\n')
#     f.write(rgbcolor)

#print(all_color_list)