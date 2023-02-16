# send requests
import requests
#explain html
from lxml import etree
import os
from time import sleep

#To cheat server
headers = {'User-Agent':'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/109.0.0.0 Safari/537.36'}

hero_list_url = 'https://pvp.qq.com/web201605/js/herolist.json'
hero_list_resp = requests.get(hero_list_url, headers= headers)

#hero_list_resp.json() contains the no, figure name and skin name of the hero.
for h in hero_list_resp.json():
    ename = h.get('ename')
    cname = h.get('cname')
    skin_name = h.get('skin_name')

    #output the name of the figure and the skin
    print(f'{cname}:{skin_name}')

    if not (skin_name):
        continue
    
    if skin_name.find('|') != -1:
        skin_name = skin_name.split('|')
    else:
        skin_name = [skin_name]
    print(skin_name)
    directory = 'Image'  #The name of directory to store the skin.
    if not os.path.exists(f'{directory}/{cname}'):
        os.makedirs(f'{directory}/{cname}')
    
    #Another way to visit hero to know how many skin of heros.
    # hero_info_url = f'https://pvp.qq.com/web201605/herodetail/{ename}.shtml'
    # hero_info_resp = requests.get(hero_info_url, headers= headers)
    # hero_info_resp.encoding = 'gbk'
    # e = etree.HTML(hero_info_resp.text)
    # names = e.xpath('//ul[@class="pic-pf-list pic-pf-list3"]/@data-imgname')[0]
    # names =  [name[0:name.index('&')] for name in names.split('|')]

    for i in range(len(skin_name)):
        if  os.path.exists(f'{directory}/{cname}/{skin_name[i]}.jpg'):
            continue
        resp = requests.get(f'https://game.gtimg.cn/images/yxzj/img201606/skin/hero-info/{ename}/{ename}-bigskin-{i + 1}.jpg',\
            headers = headers )
        with open(f'{directory}/{cname}/{skin_name[i]}.jpg', 'wb') as f:
            f.write(resp.content) 
        print(f'Download {cname}:{skin_name[i]}')  
        sleep(1)  #prevent the sever finds the abnormal situation.
 
    #Comment: Using another way to get how many skin of heros will get more skins than json.

