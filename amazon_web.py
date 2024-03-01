# -*-  encoding:utf-8 -*-
import json
import math
import random
import re
import time
from urllib.parse import quote

import httpx
import requests_html
from easyocr import easyocr
from lxml import etree

header = {
    'Host': 'www.amazon.com',
    'Connection': 'keep-alive',
    'sec-ch-ua': '"Not.A/Brand";v="8", "Chromium";v="114", "Google Chrome";v="114"',
    'sec-ch-ua-mobile': '?0',
    'sec-ch-ua-platform': '"Windows"',
    'Upgrade-Insecure-Requests': '1',
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/114.0.0.0 Safari/537.36',
    'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.7',
    'Sec-Fetch-Site': 'none',
    'Sec-Fetch-Mode': 'navigate',
    'Sec-Fetch-User': '?1',
    'Sec-Fetch-Dest': 'document',
    'Accept-Encoding': 'gzip, deflate, br',
    'Accept-Language': 'zh-CN,zh;q=0.9'
}

session = httpx.Client(http2=True, verify=False)# httpx#requests_html.HTMLSession()

url_1 = 'https://www.amazon.com/?&language=en_US&currency=USD'

data = session.get(url_1, headers=header)

print(data.text)

img_url = etree.HTML(data.text).xpath("//form//img/@src")[0]

amazon_input_one_value = etree.HTML(data.text).xpath("//form/input[1]/@value")[0]

amazon_input_tow_value = etree.HTML(data.text).xpath("//form/input[2]/@value")[0]


def random_csm_id():
    o = ""
    q = 20
    h = "0123456789"

    for i in range(q):
        p = math.floor(random.random() * len(h))
        o = o + h[p]

    return o[0:3] + "-" + o[4:11] + "-" + o[11:18]


random_id = random_csm_id()

headers = {
            'Accept': 'text/html, */*; q=0.01',
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/86.0.4240.198 Safari/537.36',
            'accept': 'text/html,*/*',
            'accept-encoding': 'gzip, deflate, br',
            'accept-language': 'zh-CN,zh;q=0.9'
        }

img_data = session.get(img_url, headers=headers)

with open('verify.jpg', "wb") as f:
    f.write(img_data.content)
    f.flush()

f.close()

reader = easyocr.Reader(['en'])
result = reader.readtext('verify.jpg')
data_text = result[0][1]

url_2 = "https://www.amazon.com/errors/validateCaptcha?amzn={}&amzn-r={}&field-keywords={}".format(
    quote(amazon_input_one_value), quote(amazon_input_tow_value).replace("/", "%2F"), data_text)

header_2 = {
    'Host': 'www.amazon.com',
    'Connection': 'keep-alive',
    'sec-ch-ua': '"Not.A/Brand";v="8", "Chromium";v="114", "Google Chrome";v="114"',
    'sec-ch-ua-mobile': '?0',
    'sec-ch-ua-platform': '"Windows"',
    'Upgrade-Insecure-Requests': '1',
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/114.0.0.0 Safari/537.36',
    'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.7',
    'Sec-Fetch-Site': 'same-origin',
    'Sec-Fetch-Mode': 'navigate',
    'Sec-Fetch-User': '?1',
    'Sec-Fetch-Dest': 'document',
    'Referer': 'https://www.amazon.com/?&language=en_US&currency=USD',
    'Accept-Encoding': 'gzip, deflate, br',
    'Accept-Language': 'zh-CN,zh;q=0.9',
    'Cookie': 'csm-sid={}'.format(random_id)
}

# header['cookie'] = "csm-id={}".format(random_id)
# header['referer'] = url


response = session.get(url_2, headers=header_2, follow_redirects=False)
print(response.headers)
x_amz_captcha_two = ''
x_amz_captcha_one = ''
if "set-cookie" in response.headers.keys() or "Set-Cookie" in response.headers.keys():
    temp_cookie = response.headers.get("set-cookie")
    x_amz_captcha_two = re.findall("x-amz-captcha-2=(.*?);", temp_cookie)[0]
    x_amz_captcha_one = re.findall("x-amz-captcha-1=(.*?);", temp_cookie)[0]

url_3 = 'https://www.amazon.com/?&language=en_US&currency=USD'

header_3 = {
    'Host': 'www.amazon.com',
    'Connection': 'keep-alive',
    'Upgrade-Insecure-Requests': '1',
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/114.0.0.0 Safari/537.36',
    'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.7',
    'Sec-Fetch-Site': 'same-origin',
    'Sec-Fetch-Mode': 'navigate',
    'Sec-Fetch-User': '?1',
    'Sec-Fetch-Dest': 'document',
    'sec-ch-ua': '"Not.A/Brand";v="8", "Chromium";v="114", "Google Chrome";v="114"',
    'sec-ch-ua-mobile': '?0',
    'sec-ch-ua-platform': '"Windows"',
    'Referer': 'https://www.amazon.com/?&language=en_US&currency=USD',
    'Accept-Encoding': 'gzip, deflate, br',
    'Accept-Language': 'zh-CN,zh;q=0.9',
    'Cookie': 'csm-sid={}; x-amz-captcha-1={}; x-amz-captcha-2={}'.format(random_id, x_amz_captcha_one,
                                                                          x_amz_captcha_two)
}

response_1 = session.get(url_3, headers=header_3)

# response_1.html.render()

url_ajax = re.findall("GwInstrumentation.markH1Af\\(\\{ uri: \"(.*)\\}\\)", response_1.text)[0]

print(response_1.text)

customer_id = re.findall("hashCustomerAndSessionId','(.*)'\\);", response_1.text)[0]

first_login_page_id = response_1.headers['x-amz-rid']

skin = ''
i18n_perfs = ''
lc_main = ''
sp_cdn = ''
session_id = ''
session_id_time = ''

if "Set-Cookie" in response_1.headers.keys() or "set-sookie" in response_1.headers.keys():
    time.sleep(1)
    cookie_content = response_1.headers["Set-Cookie"] if "Set-Cookie" in response_1.headers.keys() else \
    response_1.headers[
        "set-cookie"]

    skin = re.findall("skin=(.*?);", cookie_content)[0]
    i18n_perfs = re.findall("i18n-prefs=(.*?);", cookie_content)[0]
    lc_main = re.findall("lc-main=(.*?);", cookie_content)[0]
    sp_cdn = re.findall("sp-cdn=(.*?);", cookie_content)[0]
    session_id = re.findall("session-id=(.*?);", cookie_content)[0]
    session_id_time = re.findall("session-id-time=(.*?);", cookie_content)[0]
ue_id = re.findall("ue_id=(.*?),", response_1.text)[0]

print("------------------login a")

print(response_1.headers)


url_4 = "https://www.amazon.com" + url_ajax

menu_time = str(int(time.time() * 1000))
csm_hit_4 = "tb:s-{}|{}&t:{}&adb:adblk_no".format(first_login_page_id, menu_time, menu_time)

header_4 = {
    'Host': 'www.amazon.com',
    'Connection': 'keep-alive',
    'Content-Length': '0',
    'sec-ch-ua': '"Not.A/Brand";v="8", "Chromium";v="114", "Google Chrome";v="114"',
    'sec-ch-device-memory': '8',
    'sec-ch-viewport-width': '1012',
    'sec-ch-ua-platform-version': '"10.0.0"',
    'X-Requested-With': 'XMLHttpRequest',
    'dpr': '1',
    'downlink': '1.25',
    'sec-ch-ua-platform': '"Windows"',
    'device-memory': '8',
    'rtt': '500',
    'sec-ch-ua-mobile': '?0',
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/114.0.0.0 Safari/537.36',
    'viewport-width': '1012',
    'Accept': '*/*',
    'sec-ch-dpr': '1',
    'ect': '3g',
    'Origin': 'https://www.amazon.com',
    'Sec-Fetch-Site': 'same-origin',
    'Sec-Fetch-Mode': 'cors',
    'Sec-Fetch-Dest': 'empty',
    'Referer': 'https://www.amazon.com/?&language=en_US&currency=USD',
    'Accept-Encoding': 'gzip, deflate, br',
    'Accept-Language': 'zh-CN,zh;q=0.9',
    "Cookie": 'csm-sid={}; x-amz-captcha-1={}; x-amz-captcha-2={}; session-id={}; session-id-time={}; i18n-prefs=USD; lc-main=en_US; sp-cdn="L5Z9:CN"; skin=noskin; csm-hit={}'.format(
        random_id, x_amz_captcha_one, x_amz_captcha_two, session_id, session_id_time, csm_hit_4
    )
}

data_4 = session.get(url_4, headers=header_4)

header_4 = data_4.headers["set-cookie"]

ubid_main_4 = re.findall("ubid-main=(.*?);", header_4)[0]

menu_time_5 = str(int(time.time() * 1000))
url_5 = url = "https://www.amazon.com/portal-migration/hz/glow/get-rendered-toaster?pageType=Gateway&aisTransitionState=in&rancorLocationSource=REALM_DEFAULT&_={}".format(
    menu_time_5)
# url_5 = "https://www.amazon.com/puff/content?data=%7B%22pageType%22%3A%22Gateway%22%2C%22subPageType%22%3A%22desktop%22%2C%22referrer%22%3A%22https%3A%2F%2Fwww.amazon.com%2F%3F%26language%3Den_US%26currency%3DUSD%22%2C%22hostName%22%3A%22www.amazon.com%22%2C%22path%22%3A%22%2F%22%2C%22queryString%22%3A%22%3F%26language%3Den_US%26currency%3DUSD%22%7D"

csm_hit_5 = "tb:s-{}|{}&t:{}&adb:adblk_no".format(first_login_page_id, menu_time_5, menu_time_5)

header_5 = {
    'Host': 'www.amazon.com',
    'Connection': 'keep-alive',
    'sec-ch-ua': '"Not.A/Brand";v="8", "Chromium";v="114", "Google Chrome";v="114"',
    'sec-ch-device-memory': '8',
    'sec-ch-viewport-width': '1012',
    'sec-ch-ua-platform-version': '"10.0.0"',
    'X-Requested-With': 'XMLHttpRequest',
    'dpr': '1',
    'downlink': '1.25',
    'sec-ch-ua-platform': '"Windows"',
    'device-memory': '8',
    'rtt': '500',
    'sec-ch-ua-mobile': '?0',
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/114.0.0.0 Safari/537.36',
    'viewport-width': '1012',
    'Accept': 'text/html,*/*',
    'sec-ch-dpr': '1',
    'ect': '3g',
    'Sec-Fetch-Site': 'same-origin',
    'Sec-Fetch-Mode': 'cors',
    'Sec-Fetch-Dest': 'empty',
    'Referer': 'https://www.amazon.com/?&language=en_US&currency=USD',
    'Accept-Encoding': 'gzip, deflate, br',
    'Accept-Language': 'zh-CN,zh;q=0.9',
    'Cookie': 'csm-sid={}; x-amz-captcha-1={}; x-amz-captcha-2={}; session-id={}; session-id-time={}; i18n-prefs=USD; lc-main=en_US; sp-cdn="L5Z9:CN"; skin=noskin; csm-hit={}; ubid-main={}'.format(
        random_id, x_amz_captcha_one, x_amz_captcha_two, session_id, session_id_time, csm_hit_5, ubid_main_4
    )

}

data_5 = session.get(url_5, headers=header_5)

# new_xid = data.headers["x-amz-rid"]

header_5_c = data_5.headers["set-cookie"]

session_token = re.findall("session-token=(.*?);", header_5_c)[0]


url_6 = "https://www.amazon.com/nav/ajax/hamburgerMainContent?ajaxTemplate=hamburgerMainContent&pageType=Gateway&hmDataAjaxHint=1&navDeviceType=desktop&isSmile=0&isPrime=0&isBackup=false&hashCustomerAndSessionId={}&languageCode=en_US&environmentVFI=AmazonNavigationCards%2Fdevelopment-nov13patch%40B6166161938-AL2_x86_64&secondLayerTreeName=prm_digital_music_hawkfire%2Bkindle%2Bandroid_appstore%2Belectronics_exports%2Bcomputers_exports%2Bsbd_alexa_smart_home%2Barts_and_crafts_exports%2Bautomotive_exports%2Bbaby_exports%2Bbeauty_and_personal_care_exports%2Bwomens_fashion_exports%2Bmens_fashion_exports%2Bgirls_fashion_exports%2Bboys_fashion_exports%2Bhealth_and_household_exports%2Bhome_and_kitchen_exports%2Bindustrial_and_scientific_exports%2Bluggage_exports%2Bmovies_and_television_exports%2Bpet_supplies_exports%2Bsoftware_exports%2Bsports_and_outdoors_exports%2Btools_home_improvement_exports%2Btoys_games_exports%2Bvideo_games_exports%2Bgiftcards%2Bamazon_live%2BAmazon_Global&customerCountryCode=CN".format(
    customer_id)

menu_time_6 = str(int(time.time() * 1000))

csm_hit_6 = "tb:s-{}|{}&t:{}&adb:adblk_no".format(first_login_page_id, menu_time_6, menu_time_6)

header_6 = {
    'Host': 'www.amazon.com',
    'Connection': 'keep-alive',
    'sec-ch-ua': '"Not.A/Brand";v="8", "Chromium";v="114", "Google Chrome";v="114"',
    'sec-ch-device-memory': '8',
    'sec-ch-viewport-width': '1012',
    'sec-ch-ua-platform-version': '"10.0.0"',
    'X-Requested-With': 'XMLHttpRequest',
    'dpr': '1',
    'downlink': '8.4',
    'sec-ch-ua-platform': '"Windows"',
    'device-memory': '8',
    'rtt': '250',
    'sec-ch-ua-mobile': '?0',
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/114.0.0.0 Safari/537.36',
    'viewport-width': '1012',
    'Accept': 'text/html, */*; q=0.01',
    'sec-ch-dpr': '1',
    'ect': '4g',
    'Sec-Fetch-Site': 'same-origin',
    'Sec-Fetch-Mode': 'cors',
    'Sec-Fetch-Dest': 'empty',
    'Referer': 'https://www.amazon.com/?&language=en_US&currency=USD',
    'Accept-Encoding': 'gzip, deflate, br',
    'Accept-Language': 'zh-CN,zh;q=0.9',
    'Cookie': 'csm-sid={}; x-amz-captcha-1={}; x-amz-captcha-2={}; session-id={}; session-id-time={}; i18n-prefs=USD; lc-main=en_US; sp-cdn="L5Z9:CN"; skin=noskin; csm-hit={}; ubid-main={}; session-token={}'.format(
        random_id, x_amz_captcha_one, x_amz_captcha_two, session_id, session_id_time, csm_hit_6, ubid_main_4,
        session_token
    )
}

data_6 = session.get(url_6, headers=header_6)
print(header_6)
print("------------------------")
print(data.html.html)

print("----------------------")

data_list_content = json.loads(data_6.text)["data"]
print(data_list_content)

want_get_url_list = []

data_index = etree.HTML(data_list_content).xpath('//div[contains(@class, "hmenu-title")]/text()')

electronics_index = data_index.index("electronics")

toys_and_games = data_index.index("toys and games")
print(data_list_content)

want_get_url_list.extend(
    etree.HTML(data_list_content).xpath('//ul[@data-menu-id="{}"]//a/@href'.format(electronics_index))[1:])

want_get_url_list.extend(
    etree.HTML(data_list_content).xpath('//ul[@data-menu-id="{}"]//a/@href'.format(toys_and_games))[1:])


url_7 = "https://www.amazon.com" + want_get_url_list[0]
print(url_7)
init_time = int(time.time() * 1000)

csm_hit_init_1 = "tb:{}+s-{}|{}&t:{}&adb:adblk_no".format(first_login_page_id, first_login_page_id, str(init_time),
                                                          str(init_time))
print(csm_hit_init_1)
header_7 = {
    'Host': 'www.amazon.com',
    # 'Connection': 'keep-alive',
    'device-memory': '8',
    'sec-ch-device-memory': '8',
    'dpr': '1',
    'sec-ch-dpr': '1',
    # 'viewport-width': '1012',
    # 'sec-ch-viewport-width': '1012',
    'rtt': '{}'.format(random.randint(1, 200)),
    'downlink': '{}'.format(random.randint(1, 10) + round(random.random(), 1)),
    'ect': '4g',
    'sec-ch-ua': '"Not.A/Brand";v="8", "Chromium";v="114", "Google Chrome";v="114"',
    'sec-ch-ua-mobile': '?0',
    'sec-ch-ua-platform': '"Windows"',
    'sec-ch-ua-platform-version': '"10.0.0"',
    'Upgrade-Insecure-Requests': '1',
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/114.0.0.0 Safari/537.36',
    'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.7',
    'Sec-Fetch-Site': 'same-origin',
    'Sec-Fetch-Mode': 'navigate',
    'Sec-Fetch-User': '?1',
    'Sec-Fetch-Dest': 'document',
    'Referer': url_7,#'https://www.amazon.com/?&language=en_US&currency=USD',#
    'Accept-Encoding': 'gzip, deflate, br',
    'Accept-Language': 'zh-CN,zh;q=0.9',
    'Cookie': 'csm-sid={}; x-amz-captcha-1={}; x-amz-captcha-2={}; session-id={}; session-id-time={}; i18n-prefs=USD; lc-main=en_US; sp-cdn="L5Z9:CN"; skin=noskin; csm-hit={}; ubid-main={}; session-token={}'.format(
        random_id, x_amz_captcha_one, x_amz_captcha_two, session_id, session_id_time, csm_hit_init_1, ubid_main_4,
        session_token)
}
print(header_7)
data = session.get(url_7, headers=header_7)
# data.html.render()
print(data.status_code)
print(data.headers)
print(data.text)

#
# sub_product_id_first = data.headers["x-amz-rid"]
# init_time_value = int(time.time() * 1000)
# csm_hit_init_8 = "tb:s-{}|{}&t:{}&adb:adblk_no".format(first_login_page_id, str(init_time_value), str(init_time_value))
#
# bbn = re.findall("bbn=(.*?)&", url_7)[0]
# n = re.findall('rh=i%3Aspecialty-aps%2C(.*)&ref', url_7)[0]
#
# headers_8 = {
# 'Host':'www.amazon.com',
# 'Connection':'keep-alive',
# 'Content-Length':'79',
# 'sec-ch-ua':'"Not.A/Brand";v="8", "Chromium";v="114", "Google Chrome";v="114"',
# 'X-Amazon-s-swrs-version':'B4603C4CBB20C4CEDF46269B5AC4B17D,D41D8CD98F00B204E9800998ECF8427E',
# 'X-Amazon-s-fallback-url':'',
# 'sec-ch-device-memory':'8',
# 'sec-ch-viewport-width':'1012',
# 'sec-ch-ua-platform-version':'"10.0.0"',
# 'X-Requested-With':'XMLHttpRequest',
# 'dpr':'1',
# 'downlink':'5.65',
# 'sec-ch-ua-platform':'"Windows"',
# 'device-memory':'8',
# 'X-Amazon-s-mismatch-behavior':'ABANDON',
# 'rtt':'200',
# 'sec-ch-ua-mobile':'?0',
# 'x-amazon-rush-fingerprints':'AmazonRushAssetLoader:F944FEBFA09E474A9B4245B38AF57444DD7D4B73|AmazonRushFramework:223D2FE826CF365B8EC92694FD32972FD9D790C6|AmazonRushRouter:9D7FF98D3D960BF3526D89F77378BC31D8DFDB7E'#,
# # 'User-Agent':'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/114.0.0.0 Safari/537.36',
# # 'viewport-width':'1012',
# # 'Content-Type':'application/json',
# # 'Accept':'text/html,*/*',
# # 'sec-ch-dpr':'1',
# # 'ect':'4g',
# # 'Origin':'https://www.amazon.com',
# # 'Sec-Fetch-Site':'same-origin',
# # 'Sec-Fetch-Mode':'cors',
# # 'Sec-Fetch-Dest':'empty',
# # 'Referer':'https://www.amazon.com/s?i=electronics-intl-ship&bbn=16225009011&rh=n%3A16225009011%2Cn%3A281407&page=2&qid=1703293611&ref=sr_pg_2',
# # 'Accept-Encoding':'gzip, deflate, br',
# # 'Accept-Language':'zh-CN,zh;q=0.9',
# }
#
# start_page = 1
# next_page = 2
#
# first_page_url = "https://www.amazon.com/s/query?bbn={}&i=electronics-intl-ship&page={}&qid={}&ref=sr_pg_{}&rh={}".format(
#             bbn, next_page, str(int(time.time() * 1000)), start_page, n)
#
# json_form = {"page-content-type": "atf", "prefetch-type": "rq", "customer-action": "pagination"}
#
# data = session.post(url, headers=header, data=json.dumps(json_form), verify=False)
#
# print(data.status_code)
# print(data.text)
# print(data.headers)

