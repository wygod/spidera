#
# def product_page(session, url, init_other_value, init_csm_hit_dict, ue_id):
#     csm_hit = " csm-hit=tb:{}+s-{}|{}&t:{}&adb:adblk_no".format(init_csm_hit_dict["first_login_page_id"],
#                                                                 init_csm_hit_dict["sub_product_id_first"],
#                                                                 ue_id,
#                                                                 str(int(time.time() * 1000)),
#                                                                 str(int(time.time() * 1000)))
#     header = {
#         'accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.9',
#         'accept-encoding': 'gzip, deflate, br',
#         'accept-language': 'zh-CN,zh;q=0.9',
#         'cache-control': 'no-cache',
#         'device-memory': '8',
#         'downlink': '1.75',
#         'dpr': '1.25',
#         'ect': '4g',
#         'pragma': 'no-cache',
#         'rtt': '250',
#         'sec-fetch-dest': 'document',
#         'sec-fetch-mode': 'navigate',
#         'sec-fetch-site': 'same-origin',
#         'upgrade-insecure-requests': '1',
#         'user-agent': 'Mozilla/5.0 (Windows NT 10.0; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/86.0.4240.198 Safari/537.36',
#         'viewport-width': '1229',
#         'referer': url,
#         "cookie": 'csm-sid={}; x-amz-captcha-1={}; x-amz-captcha-2={}; session-id={}; session-id-time={}; i18n-prefs={}; lc-main={}; sp-cdn={}; skin={}; csm-hit={};ubid-main={};session-token={}'.format(
#             init_other_value["csm-id"], init_other_value["x-amz-captcha-1"], init_other_value["x-amz-captcha-2"],
#             init_other_value['session-id'], init_other_value['session-id-time'], init_other_value["i18n-perfs"],
#             init_other_value["lc-main"], init_other_value["sp-cdn"], init_other_value["skin"], csm_hit,
#             init_other_value["ubid-main"], init_other_value["session-token"]
#         )
#     }
#     data = session.get(url, headers=header, verify=False)
#     temp_html = etree.HTML(data.text)
#     add_detail = temp_html.xpath('//div[@id="page-section-detail-seller-info"]//text()')
#
#     return add_detail
#
#
# def clear_product(session, url, init_other_value, init_csm_hit_dict, iter_one):
#     csm_hit = "tb:{}+sa-{}-{}|{}&t:{}&adb:adblk_no".format(init_csm_hit_dict["first_login_page_id"],
#                                                            init_csm_hit_dict["sub_product_id_first"],
#                                                            iter_one[-1],
#                                                            str(int(time.time() * 1000)),
#                                                            str(int(time.time() * 1000))
#                                                            )
#     header = {
#         'accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.9',
#         'accept-encoding': 'gzip, deflate, br',
#         'accept-language': 'zh-CN,zh;q=0.9',
#         'cache-control': 'no-cache',
#         'device-memory': '8',
#         'downlink': '1.75',
#         'dpr': '1.25',
#         'ect': '4g',
#         'pragma': 'no-cache',
#         'rtt': '250',
#         'sec-fetch-dest': 'document',
#         'sec-fetch-mode': 'navigate',
#         'sec-fetch-site': 'same-origin',
#         'upgrade-insecure-requests': '1',
#         'user-agent': 'Mozilla/5.0 (Windows NT 10.0; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/86.0.4240.198 Safari/537.36',
#         'viewport-width': '1229',
#         'referer': url,
#         "cookie": 'csm-sid={}; x-amz-captcha-1={}; x-amz-captcha-2={}; session-id={}; session-id-time={}; i18n-prefs={}; lc-main={}; sp-cdn={}; skin={}; csm-hit={};ubid-main={};session-token={}'.format(
#             init_other_value["csm-id"], init_other_value["x-amz-captcha-1"], init_other_value["x-amz-captcha-2"],
#             init_other_value['session-id'], init_other_value['session-id-time'], init_other_value["i18n-perfs"],
#             init_other_value["lc-main"], init_other_value["sp-cdn"], init_other_value["skin"], csm_hit,
#             init_other_value["ubid-main"], init_other_value["session-token"]
#         )
#     }
#     data = session.get(url, headers=header)
#     temp_html = etree.HTML(data.text)
#     sold_by = temp_html.xpath('//*[@id="merchantInfoFeature_feature_div"]//div[@class="a-spacing-none"]/span/text()')
#     addr = temp_html.xpath('//span[@class="a-size-small"]/a[@id="sellerProfileTriggerId"]/text()')
#     add_url = temp_html.xpath('//span[@class="a-size-small"]/a[@id="sellerProfileTriggerId"]/@href')
#     product_list = temp_html.xpath('//div[@class="prodDetails"]//text()')
#
#     ue_id = data.headers["X-Amz-Rid"]
#
#     add_detail = product_page(session, init_other_value, init_csm_hit_dict, ue_id)
#
#     return [sold_by, addr, add_url, product_list, add_detail]
#
#
# def clear_data(session, data, init_other_value, init_csm_hit_dict):
#     result = data.split("&&&")
#     for i in result:
#
#         temp_data = re.findall("\"html\" : (.*?)\n", i)[0].strip(":").strip(",")
#         if temp_data:
#             temp_html = etree.HTML(temp_data)
#
#             title = temp_html.xpath('//div[@data-cy="title-recipe"]//span/text()')
#
#             star = temp_html.xpath('//div[@class="a-row a-size-small"]//span[@class="a-icon-alt"]/text()')
#
#             sum_count = temp_html.xpath('//div[@class="a-row a-size-small"]//span[2]//text()')
#
#             sale_count = temp_html.xpath('//div[@class="a-row a-size-base"]/span/text()')
#
#             price = temp_html.xpath('//span[@class="a-offscreen"]/text()')
#
#             date_text = temp_html.xpath('//div[@data-cy="delivery-recipe"]//span/text()')
#
#             product_url = temp_html.xpath('//div[@data-cy="title-recipe"]//a/@href')
#
#             clear_product(session, product_url, init_other_value, init_csm_hit_dict)
#
#
# def start_detail_page(url, init_other_value, init_csm_hit_dict, start_init_page, next_init_page, csm_hit,
#                       key_meta=None):
#     bbn = re.findall("bbn=(.*?)&", url)
#
#     n = re.findall("rh=.2C(.*?)&", url)
#
#     a = n[0].rsplit("A")[-1]
#
#     first_page_url = "https://www.amazon.com/s/query?bbn={}&i=electronics-intl-ship&page={}&qid={}&ref=sr_pg_{}&rh={}".format(
#         bbn, next_init_page, str(int(time.time() * 1000)), start_init_page, n)
#
#     json_form = {"page-content-type": "atf", "prefetch-type": "rq", "customer-action": "pagination"}
#
#     header = {
#         'accept': 'text/html,*/*',
#         'accept-encoding': 'gzip, deflate, br',
#         'accept-language': 'zh-CN,zh;q=0.9',
#         # 'content-length': '79',
#         'content-type': 'application/json',
#         'cookie': 'csm-sid={}; x-amz-captcha-1={}; x-amz-captcha-2={}; session-id={}; session-id-time={}; i18n-prefs={}; lc-main={}; sp-cdn={}; skin={}; csm-hit={};ubid-main={};session-token={}'.format(
#             init_other_value["csm-id"], init_other_value["x-amz-captcha-1"], init_other_value["x-amz-captcha-2"],
#             init_other_value['session-id'], init_other_value['session-id-time'], init_other_value["i18n-perfs"],
#             init_other_value["lc-main"], init_other_value["sp-cdn"], init_other_value["skin"], csm_hit,
#             init_other_value["ubid-main"], init_other_value["session-token"]
#         ),
#         'device-memory': '8',
#         'downlink': '1.5',
#         'dpr': '1.25',
#         'ect': '3g',
#         'origin': 'https://www.amazon.com',
#         'referer': url,
#         'rtt': '300',
#         'sec-fetch-dest': 'empty',
#         'sec-fetch-mode': 'cors',
#         'sec-fetch-site': 'same-origin',
#         'user-agent': 'Mozilla/5.0 (Windows NT 10.0; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/86.0.4240.198 Safari/537.36',
#         'x-amazon-s-fallback-url': '',
#         'x-amazon-s-mismatch-behavior': 'ABANDON',
#         'x-requested-with': 'XMLHttpRequest'
#     }
#
#     data = requests.post(first_page_url, headers=header, data=json.dumps(json_form), verify=False)
#
#     data_content = etree.HTML(data.content)
#
#     clear_data(data.content)
#
#     last_page = data_content.xpath('//span[@class="s-pagination-item s-pagination-disabled"]/text()')[0]
#     init_other_value["last_count_page"] = last_page
#
#     if not key_meta:
#         key_meta.append(data.headers["x-amz-rid"])
#     # 增加相应数据获取
#
#
# def init_detail_product_two(url, init_other_value, csm_hit, start_init_page, next_init_page):
#     bbn = re.findall("bbn=(.*?)&", url)
#
#     n = re.findall("rh=.2C(.*?)&", url)
#
#     url = "https://www.amazon.com/s?i=electronics-intl-ship&bbn={}&rh={}&page={}&qid={}&ref=sr_pg_{}".format(
#         bbn, n, next_init_page, str(int(time.time() * 1000)), start_init_page
#     )
#     header = {
#         "accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.9",
#         "accept-encoding": "gzip, deflate, br",
#         "accept-language": "zh-CN,zh;q=0.9",
#         "device-memory": "8",
#         "downlink": "1.35",
#         "dpr": "1.25",
#         "ect": "3g",
#         "referer": url,
#         "rtt": "300",
#         "sec-fetch-dest": "document",
#         "sec-fetch-mode": "navigate",
#         "sec-fetch-site": "same-origin",
#         "sec-fetch-user": "?1",
#         "upgrade-insecure-requests": "1",
#         "user-agent": "Mozilla/5.0 (Windows NT 10.0; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/86.0.4240.198 Safari/537.36",
#         "viewport-width": "1229",
#         'cookie': 'csm-sid={}; x-amz-captcha-1={}; x-amz-captcha-2={}; session-id={}; session-id-time={}; i18n-prefs={}; lc-main={}; sp-cdn={}; skin={};ubid-main={};ubid-main csm-hit={};session-token={}'.format(
#             init_other_value["csm-id"], init_other_value["x-amz-captcha-1"], init_other_value["x-amz-captcha-2"],
#             init_other_value['session-id'], init_other_value['session-id-time'], init_other_value["i18n-perfs"],
#             init_other_value["lc-main"], init_other_value["sp-cdn"], init_other_value["skin"], csm_hit,
#             init_other_value["ubid-main"], init_other_value["session-token"])
#     }
#
#     data = requests.get(url, headers=header, verify=False)
#
#     init_csm_hit_dict["sub_product_id_two"] = data.headers["x-amz-rid"]
#
#
# def init_detail_product(session, url, init_other_value, init_csm_hit_dict, csm_hit):
#     header = {
#         "accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.9",
#         "accept-encoding": "gzip, deflate, br",
#         "accept-language": "zh-CN,zh;q=0.9",
#         "device-memory": "8",
#         "downlink": "1.35",
#         "dpr": "1.25",
#         "ect": "3g",
#         "referer": url,
#         "rtt": "300",
#         "sec-fetch-dest": "document",
#         "sec-fetch-mode": "navigate",
#         "sec-fetch-site": "same-origin",
#         "sec-fetch-user": "?1",
#         "upgrade-insecure-requests": "1",
#         "user-agent": "Mozilla/5.0 (Windows NT 10.0; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/86.0.4240.198 Safari/537.36",
#         "viewport-width": "1229",
#         'cookie': 'csm-sid={}; x-amz-captcha-1={}; x-amz-captcha-2={}; session-id={}; session-id-time={}; i18n-prefs={}; lc-main={}; sp-cdn={}; skin={};ubid-main={};ubid-main csm-hit={};session-token={}'.format(
#             init_other_value["csm-id"], init_other_value["x-amz-captcha-1"], init_other_value["x-amz-captcha-2"],
#             init_other_value['session-id'], init_other_value['session-id-time'], init_other_value["i18n-perfs"],
#             init_other_value["lc-main"], init_other_value["sp-cdn"], init_other_value["skin"], csm_hit,
#             init_other_value["ubid-main"], init_other_value["session-token"])
#
#     }
#
#     data = requests.get(url, headers=header, verify=False)
#
#     init_csm_hit_dict["sub_product_id_first"] = data.headers["x-amz-rid"]
#
#
# def map_init_data(session, url, init_other_value, init_csm_hit_dict, init_start_page, iter_one, csm_key_one):
#     if init_start_page == 1:
#         init_time = str(int(time.time() * 1000))
#         csm_hit_init_1 = "tb:{}+s-{}|{}&t:{}&adb:adblk_no".format(init_csm_hit_dict["first_login_page_id"],
#                                                                   init_csm_hit_dict["first_login_page_id"],
#                                                                   init_time, init_time + random.randint(1, 200))
#         init_detail_product(session, url, init_other_value, init_csm_hit_dict, csm_hit_init_1)
#
#         init_time_value = str(int(time.time() * 1000))
#         csm_hit_init = "tb:s-{}|{}&t:{}&adb:adblk_no".format(init_csm_hit_dict["first_login_page_id"],
#                                                              init_time_value, init_time_value + random.randint(1, 200))
#         start_detail_page(session, url, init_other_value, init_csm_hit_dict, csm_hit_init)
#
#         csm_hit_init = "tb:{}+s-{}|{}&t:{}&adb:adblk_no".format(init_csm_hit_dict["first_login_page_id"],
#                                                                 init_csm_hit_dict["sub_product_id_first"],
#                                                                 init_time_value,
#                                                                 init_time_value + random.randint(1, 200))
#         init_detail_product_two(session, url, init_other_value, init_csm_hit_dict, csm_hit_init)
#
#     elif init_start_page == 2:
#         init_time = str(int(time.time() * 1000))
#         csm_hit_init = "tb:s-{}|{}&t:{}&adb:adblk_no".format(init_csm_hit_dict["sub_product_id_two"],
#                                                              init_time, init_time + random.randint(1, 200))
#
#         start_detail_page(session, url, init_other_value, init_csm_hit_dict, csm_hit_init)
#
#         csm_hit_init = "csm-hit=tb:{}+s-{}|{}&t:{}&adb:adblk_no".format(init_csm_hit_dict["first_login_page_id"],
#                                                                         init_csm_hit_dict["sub_product_id_first"],
#                                                                         init_time, init_time
#                                                                         )
#         csm_key_one.append(csm_hit_init)
#
#         start_detail_page(session, url, init_other_value, init_csm_hit_dict, csm_hit_init, iter_one)
#
#     else:
#
#         start_detail_page(session, url, init_other_value, init_csm_hit_dict, csm_key_one[-1])
#
#         # tb:0F05R11CSE55229B7AY8+sa-3KW5BCZ3DZ4FPFQ0H2H5-3YJY25RYW6T743EMX7ER|1702970244858&t:1702970244859&adb:adblk_no
#         csm_hit = "csm-hit=tb:{}+sa-{}-{}|&t:&adb:adblk_no".format(init_csm_hit_dict["first_login_page_id"],
#                                                                    init_csm_hit_dict["sub_product_id_two"],
#                                                                    iter_one[-1],
#                                                                    str(int(time.time() * 1000)),
#                                                                    str(int(time.time() * 1000)))
#         csm_key_one.append(csm_hit)
#         start_detail_page(session, url, init_other_value, init_csm_hit_dict, csm_hit, iter_one)
#
#
# def iter_get_page(url, init_other_value, init_csm_hit_dict):
#     # 检查session-token page  csm-hit x-amz-rid
#     iter_one = []
#     csm_key_one = []
#
#     init_start_page = 1
#     init_next_page = 2
#
#     last_page = 1000
#
#     while init_next_page < last_page:
#
#         map_init_data(session, url, init_other_value, init_csm_hit_dict, init_start_page,
#                       init_next_page, iter_one, csm_key_one)
#
#         init_start_page = init_next_page
#
#         init_next_page = init_next_page + 1
#
#         if init_next_page <= last_page:
#             break
#
#
# def get_menu_list(session, init_other_value, init_csm_hit_dict):
#     url = "https://www.amazon.com/nav/ajax/hamburgerMainContent?ajaxTemplate=hamburgerMainContent&pageType=Gateway&hmDataAjaxHint=1&navDeviceType=desktop&isSmile=0&isPrime=0&isBackup=false&hashCustomerAndSessionId=f54202771684942bc313dd84536b946a91be8da4&languageCode=en_US&environmentVFI=AmazonNavigationCards%2Fdevelopment-nov13patch%40B6166161938-AL2_x86_64&secondLayerTreeName=prm_digital_music_hawkfire%2Bkindle%2Bandroid_appstore%2Belectronics_exports%2Bcomputers_exports%2Bsbd_alexa_smart_home%2Barts_and_crafts_exports%2Bautomotive_exports%2Bbaby_exports%2Bbeauty_and_personal_care_exports%2Bwomens_fashion_exports%2Bmens_fashion_exports%2Bgirls_fashion_exports%2Bboys_fashion_exports%2Bhealth_and_household_exports%2Bhome_and_kitchen_exports%2Bindustrial_and_scientific_exports%2Bluggage_exports%2Bmovies_and_television_exports%2Bpet_supplies_exports%2Bsoftware_exports%2Bsports_and_outdoors_exports%2Btools_home_improvement_exports%2Btoys_games_exports%2Bvideo_games_exports%2Bgiftcards%2Bamazon_live%2BAmazon_Global&customerCountryCode=CN"
#
#     menu_time = str(int(time.time() * 1000))
#
#     csm_hit = "tb:s-{}|{}&t:{}&adb:adblk_no".format(init_csm_hit_dict["first_login_page_id"], menu_time, menu_time)
#
#     header = {
#         'accept': 'text/html, */*',
#         'accept-encoding': 'gzip, deflate, br',
#         'accept-language': 'zh-CN,zh;q=0.9',
#         "cache-control": "no-cache",
#         "device-memory": "8",
#         "downlink": "10",
#         "dpr": "1.25",
#         "ect": "4g",
#         "pragma": "no-cache",
#         "rtt": '150',
#         "sec-fetch-dest": "empty",
#         "sec-fetch-mode": "cors",
#         "sec-fetch-site": "same-origin",
#         'referer': 'https://www.amazon.com/?&language=en_US&currency=USD',
#         'sec-fetch-user': '?1',
#         'upgrade-insecure-requests': '1',
#         "viewport-width": '648',
#         "x-requested-with": "XMLHttpRequest",
#         'user-agent': 'Mozilla/5.0 (Windows NT 10.0; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/86.0.4240.198 Safari/537.36',
#         'cookie': 'csm-sid={}; x-amz-captcha-1={}; x-amz-captcha-2={};session-id={};session-id-time={};i18n-perfs={};lc-main={};sp-cdn={};skin={};csm-hit={};ubid-main={};session-token={}'.format(
#             init_other_value["csm-id"], init_other_value["x-amz-captcha-1"], init_other_value["x-amz-captcha-2"],
#             init_other_value['session-id'], init_other_value['session-id-time'], init_other_value["i18n-perfs"],
#             init_other_value["lc-main"], init_other_value["sp-cdn"], init_other_value["skin"], csm_hit,
#             init_other_value["ubid-main"], init_other_value["session-token"]
#         )
#     }
#
#     data = session.get(url, headers=header, verify=False)
#
#     data_list_content = data.text["data"].split("</ul>")
#     want_get_url_list = []
#     for per_ul in data_list_content:
#         if "toys and games" in per_ul or "electronics" in per_ul:
#             want_get_url_list.extend(etree.HTML(per_ul + "</ul>").xpath("//a/@href"))
#
#     return want_get_url_list
#
#
# def get_session_token(session, init_other_value, init_csm_hit_dict):
#     url = "https://www.amazon.com/portal-migration/hz/glow/get-rendered-toaster?pageType=Gateway&aisTransitionState=in&rancorLocationSource=REALM_DEFAULT&_={}".format(
#         str(int(time.time() * 1000)))
#
#     csm_hit = "tb:s-{}|{}&t:{}&adb:adblk_no".format(init_csm_hit_dict["first_login_page_id"],
#                                                     str(int(time.time() * 1000)),
#                                                     str(int(time.time() * 1000) + random.randint(1, 300)))
#
#     header = {
#         'accept': 'text/html, */*',
#         'accept-encoding': 'gzip, deflate, br',
#         'accept-language': 'zh-CN,zh;q=0.9',
#         "cache-control": "no-cache",
#         "device-memory": "8",
#         "downlink": "10",
#         "dpr": "1.25",
#         "ect": "4g",
#         "pragma": "no-cache",
#         "rtt": "150",
#         "sec-fetch-dest": "empty",
#         "sec-fetch-mode": "cors",
#         "sec-fetch-site": "same-origin",
#         'referer': 'https://www.amazon.com/?&language=en_US&currency=USD',
#         'sec-fetch-user': '?1',
#         'upgrade-insecure-requests': '1',
#         "viewport-width": "648",
#         "x-requested-with": "XMLHttpRequest",
#         'user-agent': 'Mozilla/5.0 (Windows NT 10.0; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/86.0.4240.198 Safari/537.36',
#         'cookie': 'csm-sid={}; x-amz-captcha-1={}; x-amz-captcha-2={};session-id={};session-id-time={};i18n-perfs={};lc-main={};sp-cdn={};skin={};csm-hit={};ubid-main={}'.format(
#             init_other_value["csm-id"], init_other_value["x-amz-captcha-1"], init_other_value["x-amz-captcha-2"],
#             init_other_value['session-id'], init_other_value['session-id-time'], init_other_value["i18n-perfs"],
#             init_other_value["lc-main"], init_other_value["sp-cdn"], init_other_value["skin"], csm_hit,
#             init_other_value["ubid-main"]
#         )}
#
#     data = requests.get(url, headers=header, verify=False)
#
#     new_xid = data.headers["x-amz-rid"]
#
#     header = data.headers["set-cookie"]
#
#     session_token = re.findall("session-token=(.*?);", header)[0]
#
#     init_other_value["session-token"] = session_token
#
#
# def get_u_bid_main(session, url, init_other_value, init_csm_hit_dict):
#     csm_hit = "tb:s-{}|{}&t:{}&adb:adblk_no".format(init_csm_hit_dict["first_login_page_id"],
#                                                     str(int(time.time() * 1000)))
#
#     header = {
#         'accept': ' */*',
#         'accept-encoding': ' gzip, deflate, br',
#         'accept-language': ' zh-CN,zh;q=0.9',
#         'content-length': ' 0',
#         'device-memory': ' 8',
#         'downlink': ' 9.8',
#         'dpr': ' 1.25',
#         'ect': ' 4g',
#         'origin': ' https://www.amazon.com',
#         'referer': ' https://www.amazon.com/?&language=en_US&currency=USD',
#         'rtt': ' 50',
#         'sec-fetch-dest': ' empty',
#         'sec-fetch-mode': ' cors',
#         'sec-fetch-site': ' same-origin',
#         'user-agent': ' Mozilla/5.0 (Windows NT 10.0; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/86.0.4240.198 Safari/537.36',
#         'viewport-width': ' 530',
#         'x-requested-with': ' XMLHttpRequest',
#         "Cookie": 'csm-sid={}; x-amz-captcha-1={}; x-amz-captcha-2={}; session-id={}; session-id-time={}; i18n-prefs={}; lc-main={}; sp-cdn={}; skin={}; csm-hit={}'.format(
#             init_other_value["csm-id"], init_other_value["x-amz-captcha-1"], init_other_value["x-amz-captcha-2"],
#             init_other_value['session-id'], init_other_value['session-id-time'], init_other_value["i18n-perfs"],
#             init_other_value["lc-main"], init_other_value["sp-cdn"], init_other_value["skin"], csm_hit
#         )
#     }
#     data = requests.get(url, headers=header, verify=False)
#
#     # new_xid = data.headers["x-amz-rid"]
#
#     header = data.headers["set-cookie"]
#
#     ubid_main = re.findall("ubid-main=(.*?);", header)[0]
#
#     init_other_value["ubid-main"] = ubid_main
#
#
# def redict_login(session, init_other_value, init_csm_hit_dict):
#     url = "https://www.amazon.com/?&language=en_US&currency=USD"
#
#     header = {
#         'accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.9',
#         'accept-encoding': 'gzip, deflate, br',
#         'accept-language': 'zh-CN,zh;q=0.9',
#         'cookie': 'csm-sid={}; x-amz-captcha-1={}; x-amz-captcha-2={}'.format(init_other_value["csm_id"],
#                                                                               init_other_value["x-amz-captcha-1"],
#                                                                               init_other_value["x-amz-captcha-2"]),
#         'referer': 'https://www.amazon.com/?&language=en_US&currency=USD',
#         'sec-fetch-dest': 'document',
#         'sec-fetch-mode': 'navigate',
#         'sec-fetch-site': 'same-origin',
#         'sec-fetch-user': '?1',
#         'upgrade-insecure-requests': '1',
#         'user-agent': 'Mozilla/5.0 (Windows NT 10.0; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/86.0.4240.198 Safari/537.36'
#     }
#
#     data = requests.get(url, headers=header, verify=False)
#
#     url_ajax = re.findall("GwInstrumentation.markH1Af\\(\\{ uri: \"(.*)\\}\\)", data.text)[0]
#
#     init_csm_hit_dict['first_login_page_id'] = data.headers['x-amz-rid']
#
#     if "Set-Cookie" in data.headers.keys() or "set-sookie" in data.headers.keys():
#         time.sleep(1)
#         cookie_content = data.headers["Set-Cookie"] if "Set-Cookie" in data.headers.keys() else data.headers[
#             "set-cookie"]
#
#         init_other_value["skin"] = re.findall("skin=(.*?);", cookie_content)[0]
#
#         init_other_value["i18n-perfs"] = re.findall("i18n-prefs=(.*?);", cookie_content)[0]
#
#         init_other_value["lc-main"] = re.findall("lc-main=(.*?);", cookie_content)[0]
#
#         init_other_value["sp-cdn"] = re.findall("sp-cdn=(.*?);", cookie_content)[0]
#
#         init_other_value["session-id"] = re.findall("session-id=(.*?);", cookie_content)[0]
#
#         init_other_value["session-id-time"] = re.findall("session-id-time=(.*?);", cookie_content)[0]
#
#     init_other_value['ue_id'] = re.findall("ue_id=(.*?),", data.text)[0]
#
#     return url_ajax
#
#
# def login_again(session, verify_code, amazon_value, amazon_val_tow, init_other_value):
#     url = "https://www.amazon.com/errors/validateCaptcha?amzn={}&amzn-r={}&field-keywords={}".format(
#         quote(amazon_value), quote(amazon_val_tow).replace("/", "%2F"), verify_code)
#     print(url)
#
#     header = {
#         'accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.9',
#         'accept-encoding': 'gzip, deflate, br',
#         'accept-language': 'zh-CN,zh;q=0.9',
#         'cookie': "csm-id={}".format(init_other_value["csm-id"]),
#         'referer': url,
#         'sec-fetch-dest': 'document',
#         'sec-fetch-mode': 'navigate',
#         'sec-fetch-site': 'same-origin',
#         'sec-fetch-user': '?1',
#         'upgrade-insecure-requests': '1',
#         'user-agent': 'Mozilla/5.0 (Windows NT 10.0; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/86.0.4240.198 Safari/537.36'
#     }
#
#     response = requests.get(url, headers=header, verify=False, allow_redirects=False)
#
#     print(response.status_code)
#
#     if "set-cookie" in response.headers.keys() or "Set-Cookie" in response.headers.keys():
#         temp_cookie = response.headers.get("set-cookie")
#
#         x_amz_captcha_two = re.findall("x-amz-captcha-2=(.*?);", temp_cookie)[0]
#
#         init_other_value["x-amz-captcha-2"] = x_amz_captcha_two
#
#         x_amz_captcha_one = re.findall("x-amz-captcha-1=(.*?);", temp_cookie)[0]
#
#         init_other_value["x-amz-captcha-1"] = x_amz_captcha_one
#
#     return init_other_value
#
#
# def start_app(init_other_value, init_csm_hit_dict):
#     # session = requests_html.HTMLSession()
#
#     url = "https://www.amazon.com/?&language=en_US&currency=USD"
#
#     header = {
#         'Accept': 'text/html, */*; q=0.01',
#         'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/86.0.4240.198 Safari/537.36',
#         'accept': 'text/html,*/*',
#         'accept-encoding': 'gzip, deflate, br',
#         'accept-language': 'zh-CN,zh;q=0.9'
#     }
#
#     csm_sid = random_csm_id()
#
#     amazon_content = requests.get(url, headers=header, verify=False)
#
#     html_content = etree.HTML(amazon_content.text)
#
#     img_url = html_content.xpath("//form//img/@src")[0]
#
#     amazon_value = html_content.xpath("//form/input[1]/@value")
#
#     amazon_val_tow = html_content.xpath("//form/input[2]/@value")
#
#     verify_code(session, img_url, "verify.jpg")
#
#     ve_value = easy_code_value("verify.jpg")
#
#     init_other_value['csm-id'] = csm_sid
#
#     cookie, result = login_again(session, ve_value, amazon_value[0], amazon_val_tow[0], init_other_value,
#                                  init_csm_hit_dict)
#
#     return img_url, amazon_value, amazon_val_tow
#