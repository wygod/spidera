# -*- encoding：utf-8 -*-
import copy
import json
import math
import re
import random

import time

import requests
import requests_html
from lxml import etree
from urllib.parse import quote

import verifyCode


class AmazonCsmId:

    def __init__(self):
        pass

    @staticmethod
    def random_csm_id():
        o = ""
        q = 20
        h = "0123456789"

        for i in range(q):
            p = math.floor(random.random() * len(h))
            o = o + h[p]

        return o[0:3] + "-" + o[4:11] + "-" + o[11:18]


class AmazonHandleDetailPage:

    def __init__(self, init_other_value, init_csm_hit_dict):
        self.header = {
            'accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.9',
            'accept-encoding': 'gzip, deflate, br',
            'accept-language': 'zh-CN,zh;q=0.9',
            'user-agent': 'Mozilla/5.0 (Windows NT 10.0; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/86.0.4240.198 Safari/537.36',
            'sec-fetch-dest': 'document',
            'sec-fetch-mode': 'navigate',
            'cache-control': 'no-cache'
        }

        self.session = requests.session()

        self.init_other = init_other_value
        self.init_csm_hit = init_csm_hit_dict

    def amazon_atom_requests(self, url, header):
        data = self.session.get(url, headers=header, verify=False)
        temp_html = etree.HTML(data.text)
        return data, temp_html

    def amazon_atom_addr(self, url, ue_id):
        csm_hit = "csm-hit=tb:{}+s-{}|{}&t:{}&adb:adblk_no".format(self.init_csm_hit["first_login_page_id"],
                                                                   self.init_csm_hit["sub_product_id_first"],
                                                                   ue_id,
                                                                   str(int(time.time() * 1000)),
                                                                   str(int(time.time() * 1000)))

        self.header[
            "Cookie"] = 'csm-sid={}; x-amz-captcha-1={}; x-amz-captcha-2={}; session-id={}; session-id-time={}; i18n-prefs={}; lc-main={}; sp-cdn={}; skin={}; csm-hit={};ubid-main={};session-token={}'.format(
            self.init_other["csm-id"], self.init_other["x-amz-captcha-1"], self.init_other["x-amz-captcha-2"],
            self.init_other['session-id'], self.init_other['session-id-time'], self.init_other["i18n-perfs"],
            self.init_other["lc-main"], self.init_other["sp-cdn"], self.init_other["skin"], csm_hit,
            self.init_other["ubid-main"], self.init_other["session-token"]
        )

        self.header["referer"] = url
        data, temp_html = self.amazon_atom_requests(url, self.header)
        add_detail = temp_html.xpath('//div[@id="page-section-detail-seller-info"]//text()')

        return add_detail

    def amazon_atom_product(self, url, iter_one):
        csm_hit = "tb:{}+sa-{}-{}|{}&t:{}&adb:adblk_no".format(self.init_csm_hit["first_login_page_id"],
                                                               self.init_csm_hit["sub_product_id_first"],
                                                               iter_one[-1],
                                                               str(int(time.time() * 1000)),
                                                               str(int(time.time() * 1000))
                                                               )

        self.header[
            "Cookie"] = 'csm-sid={}; x-amz-captcha-1={}; x-amz-captcha-2={}; session-id={}; session-id-time={}; i18n-prefs={}; lc-main={}; sp-cdn={}; skin={}; csm-hit={};ubid-main={};session-token={}'.format(
            self.init_other["csm-id"], self.init_other["x-amz-captcha-1"], self.init_other["x-amz-captcha-2"],
            self.init_other['session-id'], self.init_other['session-id-time'], self.init_other["i18n-perfs"],
            self.init_other["lc-main"], self.init_other["sp-cdn"], self.init_other["skin"], csm_hit,
            self.init_other["ubid-main"], self.init_other["session-token"]
        )

        self.header["referer"] = url
        data, temp_html = self.amazon_atom_requests(url, self.header)

        sold_by = temp_html.xpath(
            '//*[@id="merchantInfoFeature_feature_div"]//div[@class="a-spacing-none"]/span/text()')
        addr = temp_html.xpath('//span[@class="a-size-small"]/a[@id="sellerProfileTriggerId"]/text()')
        add_url = temp_html.xpath('//span[@class="a-size-small"]/a[@id="sellerProfileTriggerId"]/@href')
        product_list = temp_html.xpath('//div[@class="prodDetails"]//text()')

        ue_id = data.headers["X-Amz-Rid"]

        add_detail = self.amazon_atom_addr(add_url, ue_id)


class AmazonMenuListPage:
    def __init__(self, csm_hit_dict, other_vale_dict, amazon_clear_data):

        self.header = {
            'accept': 'text/html,*/*',
            'accept-encoding': 'gzip, deflate, br',
            'accept-language': 'zh-CN,zh;q=0.9',
            # 'content-type': 'application/json',
            'user-agent': 'Mozilla/5.0 (Windows NT 10.0; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/86.0.4240.198 Safari/537.36',
            # 'sec-fetch-dest': 'empty',
            # 'sec-fetch-mode': 'cors'
        }

        self.csm_hit_value = csm_hit_dict

        self.other_vale_dict = other_vale_dict

        self.amazon_clear_data = amazon_clear_data

        self.csm_key_one = []
        self.iter_one = []

    def amazon_handle_list_page(self, content):
        page_content = content.split("&&&")

        for per_content in iter(page_content):

            per_temp_data = re.findall("\"html\" : (.*?)\n", per_content)[0].strip(":").strip(",")

            if per_temp_data:
                temp_html = etree.HTML(per_temp_data)

                title = temp_html.xpath('//div[@data-cy="title-recipe"]//span/text()')

                star = temp_html.xpath('//div[@class="a-row a-size-small"]//span[@class="a-icon-alt"]/text()')

                sum_count = temp_html.xpath('//div[@class="a-row a-size-small"]//span[2]//text()')

                sale_count = temp_html.xpath('//div[@class="a-row a-size-base"]/span/text()')

                price = temp_html.xpath('//span[@class="a-offscreen"]/text()')

                date_text = temp_html.xpath('//div[@data-cy="delivery-recipe"]//span/text()')

                product_url = temp_html.xpath('//div[@data-cy="title-recipe"]//a/@href')

                self.amazon_clear_data.amazon_atom_product(product_url, self.other_vale_dict, self.csm_hit_value)

    def amazon_request(self, url, header, json_form):

        data = requests.post(url, headers=header, data=json.dumps(json_form), verify=False)

        data_content = etree.HTML(data.content)

        return data, data_content

    def amazon_handle_list_content(self, url, start_page, next_page, csm_hit, key_meta=None):

        bbn = re.findall("bbn=(.*?)&", url)[0]

        n = re.findall('rh=i%3Aspecialty-aps%2C(.*)&ref', url)[0]
        # a = n[0].rsplit("A")[-1]

        first_page_url = "https://www.amazon.com/s/query?bbn={}&i=electronics-intl-ship&page={}&qid={}&ref=sr_pg_{}&rh={}".format(
            bbn, next_page, str(int(time.time() * 1000)), start_page, n)

        print(first_page_url)

        json_form = {"page-content-type": "atf", "prefetch-type": "rq", "customer-action": "pagination"}

        self.header[
            'cookie'] = 'csm-sid={}; x-amz-captcha-1={}; x-amz-captcha-2={}; session-id={}; session-id-time={}; i18n-prefs={}; lc-main={}; sp-cdn={}; skin={}; csm-hit={};ubid-main={};session-token={}'.format(
            self.other_vale_dict["csm-id"], self.other_vale_dict["x-amz-captcha-1"],
            self.other_vale_dict["x-amz-captcha-2"],
            self.other_vale_dict['session-id'], self.other_vale_dict['session-id-time'],
            self.other_vale_dict["i18n-perfs"],
            self.other_vale_dict["lc-main"], self.other_vale_dict["sp-cdn"], self.other_vale_dict["skin"], csm_hit,
            self.other_vale_dict["ubid-main"], self.other_vale_dict["session-token"]
        )

        self.header['origin'] = 'https://www.amazon.com'
        self.header['referer'] = url

        # header = {
        #     'accept': 'text/html,*/*',
        #     'accept-encoding': 'gzip, deflate, br',
        #     'accept-language': 'zh-CN,zh;q=0.9',
        #     'content-type': 'application/json',
        #     'device-memory': '8',
        #     'downlink': '1.5',
        #     'dpr': '1.25',
        #     'ect': '3g',
        #     'origin': 'https://www.amazon.com',
        #     'referer': url,
        #     'rtt': '300',
        #     'sec-fetch-dest': 'empty',
        #     'sec-fetch-mode': 'cors',
        #     'sec-fetch-site': 'same-origin',
        #     'user-agent': 'Mozilla/5.0 (Windows NT 10.0; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/86.0.4240.198 Safari/537.36',
        #     'x-amazon-s-fallback-url': '',
        #     'x-amazon-s-mismatch-behavior': 'ABANDON',
        #     'x-requested-with': 'XMLHttpRequest'
        # }

        print(self.header)

        data, data_content = self.amazon_request(first_page_url, self.header, json_form)

        print(data.text)
        print(data.headers)

        self.amazon_handle_list_page(data.content)

        last_page = data_content.xpath('//span[@class="s-pagination-item s-pagination-disabled"]/text()')[0]
        self.other_vale_dict["last_count_page"] = last_page

        if not key_meta:
            key_meta.append(data.headers["x-amz-rid"])

    def amazon_content_two_csm(self, url, csm_hit, start_page, next_page):

        bbn = re.findall("bbn=(.*?)&", url)[0]

        n = re.findall('rh=i%3Aspecialty-aps%2C(.*)&ref', url)[0]

        url = "https://www.amazon.com/s?i=electronics-intl-ship&bbn={}&rh={}&page={}&qid={}&ref=sr_pg_{}".format(
            bbn, n, next_page, str(int(time.time() * 1000)), start_page
        )
        self.header[
            'cookie'] = 'csm-sid={}; x-amz-captcha-1={}; x-amz-captcha-2={}; session-id={}; session-id-time={}; i18n-prefs={}; lc-main={}; sp-cdn={}; skin={}; csm-hit={};ubid-main={};session-token={}'.format(
            self.other_vale_dict["csm-id"], self.other_vale_dict["x-amz-captcha-1"],
            self.other_vale_dict["x-amz-captcha-2"],
            self.other_vale_dict['session-id'], self.other_vale_dict['session-id-time'],
            self.other_vale_dict["i18n-perfs"],
            self.other_vale_dict["lc-main"], self.other_vale_dict["sp-cdn"], self.other_vale_dict["skin"], csm_hit,
            self.other_vale_dict["ubid-main"], self.other_vale_dict["session-token"]
        )

        data = requests.get(url, headers=self.header, verify=False)

        self.csm_hit_value["sub_product_id_two"] = data.headers["x-amz-rid"]

    def amazon_content_first_csm(self, url, csm_hit):
        print(url)

        # header = copy.deepcopy(self.header)
        # header['cookie'] = 'csm-sid={}; x-amz-captcha-1={}; x-amz-captcha-2={}; session-id={}; session-id-time={}; i18n-prefs={}; lc-main={}; sp-cdn={}; skin={}; csm-hit={};ubid-main={};session-token={}'.format(
        #     self.other_vale_dict["csm-id"], self.other_vale_dict["x-amz-captcha-1"],
        #     self.other_vale_dict["x-amz-captcha-2"],
        #     self.other_vale_dict['session-id'], self.other_vale_dict['session-id-time'],
        #     self.other_vale_dict["i18n-perfs"],
        #     self.other_vale_dict["lc-main"], self.other_vale_dict["sp-cdn"], self.other_vale_dict["skin"], csm_hit,
        #     self.other_vale_dict["ubid-main"], self.other_vale_dict["session-token"]
        # )
        # header['device-memory']='8'
        # header['downlink'] = '1.75'
        # header['dpr'] = '1.25'
        # header['ect'] = '4g'
        # header['pragma'] = 'no-cache'
        # header['rtt'] = '250'
        # header['sec-fetch-dest'] = 'document'
        # header['sec-fetch-mode'] = 'navigate'
        # header['sec-fetch-site'] = 'same-origin'
        # header['upgrade-insecure-requests'] = '1'
        # header['viewport-width'] = '1229'
        # header["accept"] = "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.7"
        # header["Referer"] = "https://www.amazon.com/?&language=en_US&currency=USD"

        # print(self.header)
        # session = requests_html.HTMLSession()

        header = {
            'Downlink': '0.6'.format(random.randint(1,10)),
            'Dpr': '1',
            'Ect': '3g',
            'Sec-Ch-Viewport-Width': '1920',
            'Viewport-Width': '1920',
            'Rtt': '{}'.format(random.randint(1, 200)),

            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.7',
            'Accept-Encoding': 'gzip, deflate, br',
            'Accept-Language': 'zh-CN,zh;q=0.9',
            'Device-Memory': '8',
            'Referer': 'https://www.amazon.com/?&language=en_US&currency=USD',
            'Sec-Ch-Device-Memorvice-Memory': '8',
            'Sec-Ch-Dpr': '1',
            'Sec-Ch-Ua': '"Not.A/Brand";v="8", "Chromium";v="114", "Google Chrome";v="114"',
            'Sec-Ch-Ua-Mobile': '?0',
            'Sec-Ch-Ua-Platform': '"Windows"',
            'Sec-Ch-Ua-Platform-Version': '"10.0.0"',
            'Sec-Fetch-Dest': 'document',
            'Sec-Fetch-Mode': 'navigate',
            'Sec-Fetch-Site': 'same-origin',
            'Sec-Fetch-User': '?1',
            'Upgrade-Insecure-Requests': '1',
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/114.0.0.0 Safari/537.36',
            'Cookie': 'csm-sid={}; x-amz-captcha-1={}; x-amz-captcha-2={}; session-id={}; session-id-time={}; i18n-prefs={}; lc-main={}; sp-cdn={}; skin={}; ubid-main={}; session-token={}; csm-hit={}'.format(
                self.other_vale_dict["csm-id"], self.other_vale_dict["x-amz-captcha-1"],
                self.other_vale_dict["x-amz-captcha-2"],
                self.other_vale_dict['session-id'], self.other_vale_dict['session-id-time'],
                self.other_vale_dict["i18n-perfs"],
                self.other_vale_dict["lc-main"], self.other_vale_dict["sp-cdn"],
                self.other_vale_dict["skin"], self.other_vale_dict["ubid-main"],
                self.other_vale_dict["session-token"],
                csm_hit
            )
        }

        print(header)

        # session = requests_html.HTMLSession()

        data = requests.get(url, headers=header, verify=False)

        # data.html.render()
        print(data.headers)
        print(data.text)

        self.csm_hit_value["sub_product_id_first"] = data.headers["x-amz-rid"]

        # session.close()

    def amazon_init_data(self, url, start_page, next_page):
        if start_page == 1:
            init_time = int(time.time() * 1000)
            csm_hit_init_1 = "tb:{}+s-{}|{}&t:{}&adb:adblk_no".format(self.csm_hit_value["first_login_page_id"],
                                                                      self.csm_hit_value["first_login_page_id"],
                                                                      str(init_time),
                                                                      str(init_time))
            self.amazon_content_first_csm(url, csm_hit_init_1)

            init_time_value = int(time.time() * 1000)
            csm_hit_init = "tb:s-{}|{}&t:{}&adb:adblk_no".format(self.csm_hit_value["first_login_page_id"],
                                                                 str(init_time_value),
                                                                 init_time_value + random.randint(1, 200))
            # url, start_page, next_page, key_meta
            self.amazon_handle_list_content(url, start_page, next_page, csm_hit_init)

            csm_hit_init = "tb:{}+s-{}|{}&t:{}&adb:adblk_no".format(self.csm_hit_value["first_login_page_id"],
                                                                    self.csm_hit_value["sub_product_id_first"],
                                                                    init_time_value,
                                                                    init_time_value + random.randint(1, 200))
            self.amazon_content_two_csm(url, csm_hit_init, start_page, next_page)

        elif start_page == 2:
            init_time = int(time.time() * 1000)
            csm_hit_init = "tb:s-{}|{}&t:{}&adb:adblk_no".format(self.csm_hit_value["sub_product_id_two"],
                                                                 init_time, init_time + random.randint(1, 200))

            self.amazon_handle_list_content(url, start_page, next_page, csm_hit_init)

            csm_hit_init = "csm-hit=tb:{}+s-{}|{}&t:{}&adb:adblk_no".format(self.csm_hit_value["first_login_page_id"],
                                                                            self.csm_hit_value["sub_product_id_first"],
                                                                            init_time, init_time
                                                                            )
            self.csm_key_one.append(csm_hit_init)

            self.amazon_handle_list_content(url, start_page, next_page, csm_hit_init, self.iter_one)

        else:

            self.amazon_handle_list_content(url, start_page, next_page, self.csm_key_one[-1])

            csm_hit = "csm-hit=tb:{}+sa-{}-{}|&t:&adb:adblk_no".format(self.csm_hit_value["first_login_page_id"],
                                                                       self.csm_hit_value["sub_product_id_two"],
                                                                       self.iter_one[-1],
                                                                       str(int(time.time() * 1000)),
                                                                       str(int(time.time() * 1000)))
            self.csm_key_one.append(csm_hit)
            self.amazon_handle_list_content(url, start_page, next_page, csm_hit, self.iter_one)

    def amazon_session_token(self, url):
        verify_code_url = "https://www.amazon.com/hz/rhf?currentPageType=Gateway&currentSubPageType=desktop&excludeAsin=&fieldKeywords=&k=&keywords=&search=&auditEnabled=&previewCampaigns=&forceWidgets=&searchAlias=&isAUI=1&cardJSPresent=true&pageUrl=%2F"
        header = {
            'Accept': '*/*',
            'Accept-Encoding': 'gzip, deflate, br',
            'Accept-Language': 'zh-CN,zh;q=0.9',
            'Device-Memory': '8',
            'Downlink': '3.85',
            'Dpr': '1',
            'Ect': '4g',
            'Referer': url,
            'Rtt': '250',
            'Sec-Ch-Device-Memory': '8',
            'Sec-Ch-Dpr': '1',
            'Sec-Ch-Ua': '"Not.A/Brand";v="8 "Chromium";v="114 "Google Chrome";v="114"',
            'Sec-Ch-Ua-Mobile': '?0',
            'Sec-Ch-Ua-Platform': '"Windows',
            'Sec-Ch-Ua-Platform-Version': '10.0.0',
            'Sec-Ch-Viewport-Width': '1920',
            'Sec-Fetch-Dest': 'empty',
            'Sec-Fetch-Mode': 'cors',
            'Sec-Fetch-Site': 'same-origin',
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/114.0.0.0 Safari/537.36',
            'Viewport-Width': '1920',
            'X-Requested-With': 'XMLHttpRequest'
        }
        data = requests.get(verify_code_url, headers=header, verify=False)

        print(data.headers)

    def amazon_handle_data_start(self, url):

        init_start_page = 1
        init_next_page = 2

        last_page = 1000

        while init_next_page < last_page:

            self.amazon_init_data(url, init_start_page, init_next_page)

            init_start_page = init_next_page

            init_next_page = init_next_page + 1

            if init_next_page <= last_page:
                break


class AmazonInitData:

    def __init__(self, csm_id):
        self.header = {
            'accept': 'text/html,*/*',
            'accept-encoding': 'gzip, deflate, br',
            'accept-language': 'zh-CN,zh;q=0.9',
            'content-type': 'application/json',
            'user-agent': 'Mozilla/5.0 (Windows NT 10.0; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/86.0.4240.198 Safari/537.36'
        }

        self.base_url = 'https://www.amazon.com/?&language=en_US&currency=USD'

        self.verify_func = verifyCode.AmazonCode()

        self.other_init_value = {"csm-id": csm_id}

        self.csm_init_value = {}

    def amazon_random_time(self):
        return str(int(time.time() * 1000))

    def amazon_class_data(self, cusum_id):
        url = "https://www.amazon.com/nav/ajax/hamburgerMainContent?ajaxTemplate=hamburgerMainContent&pageType=Gateway&hmDataAjaxHint=1&navDeviceType=desktop&isSmile=0&isPrime=0&isBackup=false&hashCustomerAndSessionId={}&languageCode=en_US&environmentVFI=AmazonNavigationCards%2Fdevelopment-nov13patch%40B6166161938-AL2_x86_64&secondLayerTreeName=prm_digital_music_hawkfire%2Bkindle%2Bandroid_appstore%2Belectronics_exports%2Bcomputers_exports%2Bsbd_alexa_smart_home%2Barts_and_crafts_exports%2Bautomotive_exports%2Bbaby_exports%2Bbeauty_and_personal_care_exports%2Bwomens_fashion_exports%2Bmens_fashion_exports%2Bgirls_fashion_exports%2Bboys_fashion_exports%2Bhealth_and_household_exports%2Bhome_and_kitchen_exports%2Bindustrial_and_scientific_exports%2Bluggage_exports%2Bmovies_and_television_exports%2Bpet_supplies_exports%2Bsoftware_exports%2Bsports_and_outdoors_exports%2Btools_home_improvement_exports%2Btoys_games_exports%2Bvideo_games_exports%2Bgiftcards%2Bamazon_live%2BAmazon_Global&customerCountryCode=CN".format(cusum_id)

        menu_time = str(int(time.time() * 1000))

        csm_hit = "tb:s-{}|{}&t:{}&adb:adblk_no".format(self.csm_init_value["first_login_page_id"], menu_time,
                                                        menu_time)

        self.header['referer'] = self.base_url

        self.header[
            'cookie'] = 'csm-sid={}; x-amz-captcha-1={}; x-amz-captcha-2={}; session-id={}; session-id-time={}; i18n-prefs={}; lc-main={}; sp-cdn={}; skin={}; csm-hit={};ubid-main={};session-token={}'.format(
            self.other_init_value["csm-id"], self.other_init_value["x-amz-captcha-1"],
            self.other_init_value["x-amz-captcha-2"],
            self.other_init_value['session-id'], self.other_init_value['session-id-time'],
            self.other_init_value["i18n-perfs"],
            self.other_init_value["lc-main"], self.other_init_value["sp-cdn"], self.other_init_value["skin"], csm_hit,
            self.other_init_value["ubid-main"], self.other_init_value["session-token"]
        )

        data = requests.get(url, headers=self.header, verify=False)
        print(data.text)
        data_list_content = json.loads(data.text)["data"]
        print(data_list_content)

        want_get_url_list = []

        data_index = etree.HTML(data_list_content).xpath('//div[contains(@class, "hmenu-title")]/text()')

        electronics_index = data_index.index("electronics")

        toys_and_games = data_index.index("toys and games")

        want_get_url_list.extend(
            etree.HTML(data_list_content).xpath('//ul[@data-menu-id="{}"]//a/@href'.format(electronics_index))[1:])

        want_get_url_list.extend(
            etree.HTML(data_list_content).xpath('//ul[@data-menu-id="{}"]//a/@href'.format(toys_and_games))[1:])

        return want_get_url_list

    def amazon_session_token(self):
        # url = "https://www.amazon.com/portal-migration/hz/glow/get-rendered-toaster?pageType=Gateway&aisTransitionState=in&rancorLocationSource=REALM_DEFAULT&_={}".format(
        #     str(int(time.time() * 1000)))
        # url = "https://www.amazon.com/hz/rhf?currentPageType=Gateway&currentSubPageType=desktop&excludeAsin=&fieldKeywords=&k=&keywords=&search=&auditEnabled=&previewCampaigns=&forceWidgets=&searchAlias=&isAUI=1&cardJSPresent=true&pageUrl=%2F"

        url = "https://www.amazon.com/puff/content?data=%7B%22pageType%22%3A%22Gateway%22%2C%22subPageType%22%3A%22desktop%22%2C%22referrer%22%3A%22https%3A%2F%2Fwww.amazon.com%2F%3F%26language%3Den_US%26currency%3DUSD%22%2C%22hostName%22%3A%22www.amazon.com%22%2C%22path%22%3A%22%2F%22%2C%22queryString%22%3A%22%3F%26language%3Den_US%26currency%3DUSD%22%7D"

        csm_hit = "tb:s-{}|{}&t:{}&adb:adblk_no".format(self.csm_init_value["first_login_page_id"],
                                                        str(int(time.time() * 1000)),
                                                        str(int(time.time() * 1000) + random.randint(1, 300)))
        self.header[
            'cookie'] = 'csm-sid={}; x-amz-captcha-1={}; x-amz-captcha-2={}; session-id={}; session-id-time={}; i18n-prefs={}; lc-main={}; sp-cdn={}; skin={}; csm-hit={};ubid-main={}'.format(
            self.other_init_value["csm-id"], self.other_init_value["x-amz-captcha-1"],
            self.other_init_value["x-amz-captcha-2"],
            self.other_init_value['session-id'], self.other_init_value['session-id-time'],
            self.other_init_value["i18n-perfs"],
            self.other_init_value["lc-main"], self.other_init_value["sp-cdn"], self.other_init_value["skin"], csm_hit,
            self.other_init_value["ubid-main"]
        )

        data = requests.get(url, headers=self.header, verify=False)

        if data.status_code == 200:
            new_xid = data.headers["x-amz-rid"]

            header = data.headers["set-cookie"]

            session_token = re.findall("session-token=(.*?);", header)[0]

            self.other_init_value["session-token"] = session_token

    def amazon_bid_main(self, url):
        time_id = self.amazon_random_time()
        csm_hit = "tb:s-{}|{}&t:{}&adb:adblk_no".format(self.csm_init_value["first_login_page_id"],
                                                        time_id, time_id)

        self.header['origin'] = 'https://www.amazon.com'
        self.header['referer'] = self.base_url

        self.header[
            'cookie'] = 'csm-sid={}; x-amz-captcha-1={}; x-amz-captcha-2={}; session-id={}; session-id-time={}; i18n-prefs={}; lc-main={}; sp-cdn={}; skin={}; csm-hit={}'.format(
            self.other_init_value["csm-id"], self.other_init_value["x-amz-captcha-1"],
            self.other_init_value["x-amz-captcha-2"],
            self.other_init_value['session-id'], self.other_init_value['session-id-time'],
            self.other_init_value["i18n-perfs"],
            self.other_init_value["lc-main"], self.other_init_value["sp-cdn"], self.other_init_value["skin"], csm_hit
        )

        data = requests.get(url, headers=self.header, verify=False)

        header = data.headers["set-cookie"]

        ubid_main = re.findall("ubid-main=(.*?);", header)[0]

        self.other_init_value["ubid-main"] = ubid_main

    def amazon_again_login(self):

        self.header["cookie"] = 'csm-sid={}; x-amz-captcha-1={}; x-amz-captcha-2={}'.format(
            self.other_init_value["csm-id"],
            self.other_init_value["x-amz-captcha-1"],
            self.other_init_value["x-amz-captcha-2"]
        )

        self.header['referer'] = self.base_url

        data = requests.get(self.base_url, headers=self.header, verify=False)

        url_ajax = re.findall("GwInstrumentation.markH1Af\\(\\{ uri: \"(.*)\\}\\)", data.text)[0]

        print(data.text)

        customer_id = re.findall("hashCustomerAndSessionId','(.*)'\\);", data.text)[0]

        self.csm_init_value['first_login_page_id'] = data.headers['x-amz-rid']

        if "Set-Cookie" in data.headers.keys() or "set-sookie" in data.headers.keys():
            time.sleep(1)
            cookie_content = data.headers["Set-Cookie"] if "Set-Cookie" in data.headers.keys() else data.headers[
                "set-cookie"]

            self.other_init_value["skin"] = re.findall("skin=(.*?);", cookie_content)[0]

            self.other_init_value["i18n-perfs"] = re.findall("i18n-prefs=(.*?);", cookie_content)[0]

            self.other_init_value["lc-main"] = re.findall("lc-main=(.*?);", cookie_content)[0]

            self.other_init_value["sp-cdn"] = re.findall("sp-cdn=(.*?);", cookie_content)[0]

            self.other_init_value["session-id"] = re.findall("session-id=(.*?);", cookie_content)[0]

            self.other_init_value["session-id-time"] = re.findall("session-id-time=(.*?);", cookie_content)[0]

        self.other_init_value['ue_id'] = re.findall("ue_id=(.*?),", data.text)[0]

        self.amazon_bid_main("https://www.amazon.com" + url_ajax)

        return customer_id

    def amazon_login(self, verify_code, amazon_input_one, amazon_input_two):
        url = "https://www.amazon.com/errors/validateCaptcha?amzn={}&amzn-r={}&field-keywords={}".format(
            quote(amazon_input_one), quote(amazon_input_two).replace("/", "%2F"), verify_code)

        header = copy.deepcopy(self.header)

        header['cookie'] = "csm-id={}".format(self.other_init_value["csm-id"])
        header['referer'] = url
        print(header)

        response = requests.get(url, headers=header, verify=False, allow_redirects=False)

        if "set-cookie" in response.headers.keys() or "Set-Cookie" in response.headers.keys():
            temp_cookie = response.headers.get("set-cookie")

            x_amz_captcha_two = re.findall("x-amz-captcha-2=(.*?);", temp_cookie)[0]

            self.other_init_value["x-amz-captcha-2"] = x_amz_captcha_two

            x_amz_captcha_one = re.findall("x-amz-captcha-1=(.*?);", temp_cookie)[0]

            self.other_init_value["x-amz-captcha-1"] = x_amz_captcha_one

    def amazon_start(self):

        amazon_content = requests.get(self.base_url, headers=self.header, verify=False)

        html_content = etree.HTML(amazon_content.text)

        img_url = html_content.xpath("//form//img/@src")[0]

        amazon_input_one_value = html_content.xpath("//form/input[1]/@value")

        amazon_input_tow_value = html_content.xpath("//form/input[2]/@value")

        verify_value = self.verify_func.verify_code(img_url)

        self.amazon_login(verify_value, amazon_input_one_value[0], amazon_input_tow_value[0])

    def get(self):
        self.amazon_start()
        custom_id = self.amazon_again_login()
        self.amazon_session_token()
        return self.csm_init_value, self.other_init_value, self.amazon_class_data(custom_id)


if __name__ == "__main__":
    # clear_url, header_dict = start_app()
    # print(clear_url)
    # print(header_dict)

    # session = requests_html.HTMLSession()
    #
    # init_csm_hit_dict = {}
    #
    # init_other_value = {}
    #
    # img_url, amazon_value, amazon_val_tow = start_app()

    # data = {
    #     "data": "\n<ul class=\"hmenu hmenu-translateX-right\" data-menu-id=\"2\" data-parent-menu-id=\"1\">\n  <li><a href=\"/\" class=\"hmenu-item hmenu-back-button\" aria-label=\"Back to main menu\" data-ref-tag=\"nav_em_1_2_BT_0_main_menu\"><div style=\"align-items: center;\"><i class=\"nav-sprite hmenu-arrow-prev\"></i>main menu</div></a></li>\n  <li><div class=\"hmenu-item hmenu-title \">stream music</div></li><li><a href=\"https://music.amazon.com/unlimited?ref_=nav_em__dm_hf_0_2_2_2\" class=\"hmenu-item\">Amazon Music Unlimited</a></li><li><a href=\"/music/free?ref_=nav_em__dm_nav_nw_0_2_2_3\" class=\"hmenu-item\">Free Streaming Music</a></li><li><a href=\"/music/lp/podcasts?ref_=nav_em__dm_nav_rh_0_2_2_4\" class=\"hmenu-item\">Podcasts</a></li><li><a href=\"https://music.amazon.com?ref_=nav_em_dm_webplayer_0_2_2_5\" class=\"hmenu-item\">Open Web Player</a></li><li><a href=\"https://music.amazon.com?ref_=nav_em_dm_webplayer_0_2_2_6\" class=\"hmenu-item\">Open Web Player</a></li><li><a href=\"/gp/browse.html?node=23653176011&ref_=nav_em__dm_store_ms_0_2_2_7\" class=\"hmenu-item\">Download the app</a></li>\n  <li class=\"hmenu-separator\"></li>\n</ul>\n\n<ul class=\"hmenu hmenu-translateX-right\" data-menu-id=\"3\" data-parent-menu-id=\"1\">\n  <li><a href=\"/\" class=\"hmenu-item hmenu-back-button\" aria-label=\"Back to main menu\" data-ref-tag=\"nav_em_1_3_BT_0_main_menu\"><div style=\"align-items: center;\"><i class=\"nav-sprite hmenu-arrow-prev\"></i>main menu</div></a></li>\n  <li><div class=\"hmenu-item hmenu-title \">kindle e-readers</div></li><li><a href=\"/dp/B0BLJ6LJBM?ref_=nav_em__k_ods_eink_kke_0_2_3_2\" class=\"hmenu-item\">Kindle Kids</a></li><li><a href=\"/dp/B09SWW583J?ref_=nav_em__k_ods_eink_jr_0_2_3_3\" class=\"hmenu-item\">Kindle</a></li><li><a href=\"/dp/B0BL8S6ZPT?ref_=nav_em__k_ods_eink_mkke_0_2_3_4\" class=\"hmenu-item\">Kindle Paperwhite Kids</a></li><li><a href=\"/dp/B08KTZ8249?ref_=nav_em__k_ods_eink_sd_me_0_2_3_5\" class=\"hmenu-item\">Kindle Paperwhite</a></li><li><a href=\"/dp/B07F7TLZF4?ref_=nav_em__k_ods_eink_wy_0_2_3_6\" class=\"hmenu-item\">Kindle Oasis</a></li><li><a href=\"/dp/B09BS26B8B?ref_=nav_em__k_ods_eink_bo_0_2_3_7\" class=\"hmenu-item\">Kindle Scribe</a></li><li><a href=\"/gp/browse.html?node=370783011&ref_=nav_em__ods_eink_acc_0_2_3_8\" class=\"hmenu-item\">Accessories</a></li><li><a href=\"/gp/browse.html?node=6669702011&ref_=nav_em__ods_eink_catp_0_2_3_9\" class=\"hmenu-item\">See all Kindle E-Readers</a></li><li class=\"hmenu-separator\"></li><li><div class=\"hmenu-item hmenu-title \">kindle store</div></li><li><a href=\"/gp/browse.html?node=1286228011&ref_=nav_em__ods_eink_con_books_0_2_3_11\" class=\"hmenu-item\">Kindle Books</a></li><li><a href=\"/gp/kindle/ku/sign-up/ui/rw/about?ref_=nav_em__ods_eink_con_ku_0_2_3_12\" class=\"hmenu-item\">Kindle Unlimited</a></li><li><a href=\"/kindle-dbs/fd/prime-pr?ref_=nav_em__ods_eink_con_pr_0_2_3_13\" class=\"hmenu-item\">Prime Reading</a></li><li><a href=\"/kindle-vella?ref_=nav_em__vla_dt_gw_hm_keb_0_2_3_14\" class=\"hmenu-item\">Kindle Vella</a></li><li class=\"hmenu-separator\"></li><li><div class=\"hmenu-item hmenu-title \">apps & resources</div></li><li><a href=\"/kindle-dbs/fd/kcp?ref_=nav_em__ods_eink_con_karl_0_2_3_17_0_2_3_16\" class=\"hmenu-item\">Free Kindle Reading Apps</a></li><li><a href=\"https://read.amazon.com/?ref_=nav_em__ods_eink_con_kcr_0_2_3_17\" class=\"hmenu-item\">Kindle for Web</a></li><li><a href=\"/gp/digital/fiona/manage?ref_=nav_em__ods_eink_con_myk_0_2_3_18\" class=\"hmenu-item\">Manage Your Content and Devices</a></li><li><a href=\"/gp/browse.html?node=9187220011&ref_=nav_em__ods_ha_echo_tradein_0_2_3_19\" class=\"hmenu-item\">Trade-In</a></li>\n  <li class=\"hmenu-separator\"></li>\n</ul>\n\n<ul class=\"hmenu hmenu-translateX-right\" data-menu-id=\"4\" data-parent-menu-id=\"1\">\n  <li><a href=\"/\" class=\"hmenu-item hmenu-back-button\" aria-label=\"Back to main menu\" data-ref-tag=\"nav_em_1_4_BT_0_main_menu\"><div style=\"align-items: center;\"><i class=\"nav-sprite hmenu-arrow-prev\"></i>main menu</div></a></li>\n  <li><div class=\"hmenu-item hmenu-title \">amazon appstore</div></li><li><a href=\"/gp/browse.html?node=2350149011&ref_=nav_em__adr_app_0_2_4_2\" class=\"hmenu-item\">All Apps and Games </a></li><li><a href=\"/gp/browse.html?node=9209902011&ref_=nav_em__adr_gam_0_2_4_3\" class=\"hmenu-item\">Games</a></li><li><a href=\"/coins?ref_=nav_em__adr_coins_0_2_4_4\" class=\"hmenu-item\">Amazon Coins</a></li><li><a href=\"/gp/mas/get/android?ref_=nav_em__adr_dl_0_2_4_5\" class=\"hmenu-item\">Download Amazon Appstore</a></li><li><a href=\"/gp/feature.html?docId=1000645111&ref_=nav_em__adr_amz_0_2_4_6\" class=\"hmenu-item\">Amazon Apps</a></li><li><a href=\"/gp/mas/your-account/myapps?ref_=nav_em__adr_yad_0_2_4_7\" class=\"hmenu-item\">Your Apps and Subscriptions</a></li>\n  <li class=\"hmenu-separator\"></li>\n</ul>\n\n<ul class=\"hmenu hmenu-translateX-right\" data-menu-id=\"5\" data-parent-menu-id=\"1\">\n  <li><a href=\"/\" class=\"hmenu-item hmenu-back-button\" aria-label=\"Back to main menu\" data-ref-tag=\"nav_em_1_5_BT_0_main_menu\"><div style=\"align-items: center;\"><i class=\"nav-sprite hmenu-arrow-prev\"></i>main menu</div></a></li>\n  <li><div class=\"hmenu-item hmenu-title \">electronics</div></li><li><a href=\"/s?bbn=16225009011&rh=i%3Aspecialty-aps%2Cn%3A%2116225009011%2Cn%3A281407&ref_=nav_em__nav_desktop_sa_intl_accessories_and_supplies_0_2_5_2\" class=\"hmenu-item\">Accessories & Supplies</a></li><li><a href=\"/s?bbn=16225009011&rh=i%3Aspecialty-aps%2Cn%3A%2116225009011%2Cn%3A502394&ref_=nav_em__nav_desktop_sa_intl_camera_and_photo_0_2_5_3\" class=\"hmenu-item\">Camera & Photo</a></li><li><a href=\"/s?bbn=16225009011&rh=i%3Aspecialty-aps%2Cn%3A%2116225009011%2Cn%3A3248684011&ref_=nav_em__nav_desktop_sa_intl_car_and_vehicle_electronics_0_2_5_4\" class=\"hmenu-item\">Car & Vehicle Electronics</a></li><li><a href=\"/s?bbn=16225009011&rh=i%3Aspecialty-aps%2Cn%3A%2116225009011%2Cn%3A2811119011&ref_=nav_em__nav_desktop_sa_intl_cell_phones_and_accessories_0_2_5_5\" class=\"hmenu-item\">Cell Phones & Accessories</a></li><li><a href=\"/s?bbn=16225009011&rh=i%3Aspecialty-aps%2Cn%3A%2116225009011%2Cn%3A541966&ref_=nav_em__nav_desktop_sa_intl_computers_and_accessories_0_2_5_6\" class=\"hmenu-item\">Computers & Accessories</a></li><li><a href=\"/s?bbn=16225009011&rh=i%3Aspecialty-aps%2Cn%3A%2116225009011%2Cn%3A172526&ref_=nav_em__nav_desktop_sa_intl_gps_and_navigation_0_2_5_7\" class=\"hmenu-item\">GPS & Navigation</a></li><li><a href=\"/s?bbn=16225009011&rh=i%3Aspecialty-aps%2Cn%3A%2116225009011%2Cn%3A172541&ref_=nav_em__nav_desktop_sa_intl_headphones_0_2_5_8\" class=\"hmenu-item\">Headphones</a></li><li><a href=\"/s?bbn=16225009011&rh=i%3Aspecialty-aps%2Cn%3A%2116225009011%2Cn%3A667846011&ref_=nav_em__nav_desktop_sa_intl_home_audio_0_2_5_9\" class=\"hmenu-item\">Home Audio</a></li><li><a href=\"/s?bbn=16225009011&rh=i%3Aspecialty-aps%2Cn%3A%2116225009011%2Cn%3A172574&ref_=nav_em__nav_desktop_sa_intl_office_electronics_0_2_5_10\" class=\"hmenu-item\">Office Electronics</a></li><li><a href=\"/s?bbn=16225009011&rh=i%3Aspecialty-aps%2Cn%3A%2116225009011%2Cn%3A172623&ref_=nav_em__nav_desktop_sa_intl_portable_audio_and_video_0_2_5_11\" class=\"hmenu-item\">Portable Audio & Video</a></li><li><a href=\"/s?bbn=16225009011&rh=i%3Aspecialty-aps%2Cn%3A%2116225009011%2Cn%3A524136&ref_=nav_em__nav_desktop_sa_intl_security_and_surveillance_0_2_5_12\" class=\"hmenu-item\">Security & Surveillance</a></li><li><a href=\"/s?bbn=16225009011&rh=i%3Aspecialty-aps%2Cn%3A%2116225009011%2Cn%3A16285901&ref_=nav_em__nav_desktop_sa_intl_service_plans_0_2_5_13\" class=\"hmenu-item\">Service Plans</a></li><li><a href=\"/s?bbn=16225009011&rh=i%3Aspecialty-aps%2Cn%3A%2116225009011%2Cn%3A1266092011&ref_=nav_em__nav_desktop_sa_intl_television_and_video_0_2_5_14\" class=\"hmenu-item\">Television & Video</a></li><li><a href=\"/s?bbn=16225009011&rh=i%3Aspecialty-aps%2Cn%3A%2116225009011%2Cn%3A7926841011&ref_=nav_em__nav_desktop_sa_intl_video_game_consoles_and_accessories_0_2_5_15\" class=\"hmenu-item\">Video Game Consoles & Accessories</a></li><li><a href=\"/s?bbn=16225009011&rh=i%3Aspecialty-aps%2Cn%3A%2116225009011%2Cn%3A300334&ref_=nav_em__nav_desktop_sa_intl_video_projectors_0_2_5_16\" class=\"hmenu-item\">Video Projectors</a></li><li><a href=\"/s?bbn=16225009011&rh=i%3Aspecialty-aps%2Cn%3A%2116225009011%2Cn%3A10048700011&ref_=nav_em__nav_desktop_sa_intl_wearable_technology_0_2_5_17\" class=\"hmenu-item\">Wearable Technology</a></li><li><a href=\"/s?bbn=16225009011&rh=i%3Aspecialty-aps%2Cn%3A%2116225009011%2Cn%3A2642125011&ref_=nav_em__nav_desktop_sa_intl_ebook_readers_and_accessories_0_2_5_18\" class=\"hmenu-item\">eBook Readers & Accessories</a></li>\n  <li class=\"hmenu-separator\"></li>\n</ul>\n\n<ul class=\"hmenu hmenu-translateX-right\" data-menu-id=\"6\" data-parent-menu-id=\"1\">\n  <li><a href=\"/\" class=\"hmenu-item hmenu-back-button\" aria-label=\"Back to main menu\" data-ref-tag=\"nav_em_1_6_BT_0_main_menu\"><div style=\"align-items: center;\"><i class=\"nav-sprite hmenu-arrow-prev\"></i>main menu</div></a></li>\n  <li><div class=\"hmenu-item hmenu-title \">computers</div></li><li><a href=\"/s?bbn=16225007011&rh=i%3Aspecialty-aps%2Cn%3A16225007011%2Cn%3A172456&ref_=nav_em__nav_desktop_sa_intl_computer_accessories_and_peripherals_0_2_6_2\" class=\"hmenu-item\">Computer Accessories & Peripherals</a></li><li><a href=\"/s?bbn=16225007011&rh=i%3Aspecialty-aps%2Cn%3A16225007011%2Cn%3A193870011&ref_=nav_em__nav_desktop_sa_intl_computer_components_0_2_6_3\" class=\"hmenu-item\">Computer Components</a></li><li><a href=\"/s?bbn=16225007011&rh=i%3Aspecialty-aps%2Cn%3A16225007011%2Cn%3A13896617011&ref_=nav_em__nav_desktop_sa_intl_computers_tablets_0_2_6_4\" class=\"hmenu-item\">Computers & Tablets</a></li><li><a href=\"/s?bbn=16225007011&rh=i%3Aspecialty-aps%2Cn%3A16225007011%2Cn%3A1292110011&ref_=nav_em__nav_desktop_sa_intl_data_storage_0_2_6_5\" class=\"hmenu-item\">Data Storage</a></li><li><a href=\"/s?bbn=16225007011&rh=i%3Aspecialty-aps%2Cn%3A16225007011%2Cn%3A3012292011&ref_=nav_em__nav_desktop_sa_intl_external_components_0_2_6_6\" class=\"hmenu-item\">External Components</a></li><li><a href=\"/s?bbn=16225007011&rh=i%3Aspecialty-aps%2Cn%3A16225007011%2Cn%3A3011391011&ref_=nav_em__nav_desktop_sa_intl_laptop_accessories_0_2_6_7\" class=\"hmenu-item\">Laptop Accessories</a></li><li><a href=\"/s?bbn=16225007011&rh=i%3Aspecialty-aps%2Cn%3A16225007011%2Cn%3A1292115011&ref_=nav_em__nav_desktop_sa_intl_monitors_0_2_6_8\" class=\"hmenu-item\">Monitors</a></li><li><a href=\"/s?bbn=16225007011&rh=i%3Aspecialty-aps%2Cn%3A16225007011%2Cn%3A172504&ref_=nav_em__nav_desktop_sa_intl_networking_products_0_2_6_9\" class=\"hmenu-item\">Networking Products</a></li><li><a href=\"/s?bbn=16225007011&rh=i%3Aspecialty-aps%2Cn%3A16225007011%2Cn%3A17854127011&ref_=nav_em__nav_desktop_sa_intl_power_strips_and_surge_protectors_0_2_6_10\" class=\"hmenu-item\">Power Strips & Surge Protectors</a></li><li><a href=\"/s?bbn=16225007011&rh=i%3Aspecialty-aps%2Cn%3A16225007011%2Cn%3A172635&ref_=nav_em__nav_desktop_sa_intl_printers_0_2_6_11\" class=\"hmenu-item\">Printers</a></li><li><a href=\"/s?bbn=16225007011&rh=i%3Aspecialty-aps%2Cn%3A16225007011%2Cn%3A172584&ref_=nav_em__nav_desktop_sa_intl_scanners_0_2_6_12\" class=\"hmenu-item\">Scanners</a></li><li><a href=\"/s?bbn=16225007011&rh=i%3Aspecialty-aps%2Cn%3A16225007011%2Cn%3A11036071&ref_=nav_em__nav_desktop_sa_intl_servers_0_2_6_13\" class=\"hmenu-item\">Servers</a></li><li><a href=\"/s?bbn=16225007011&rh=i%3Aspecialty-aps%2Cn%3A16225007011%2Cn%3A2348628011&ref_=nav_em__nav_desktop_sa_intl_tablet_accessories_0_2_6_14\" class=\"hmenu-item\">Tablet Accessories</a></li><li><a href=\"/s?bbn=16225007011&rh=i%3Aspecialty-aps%2Cn%3A16225007011%2Cn%3A15524379011&ref_=nav_em__nav_desktop_sa_intl_tablet_replacement_parts_0_2_6_15\" class=\"hmenu-item\">Tablet Replacement Parts</a></li><li><a href=\"/s?bbn=16225007011&rh=i%3Aspecialty-aps%2Cn%3A16225007011%2Cn%3A16285851&ref_=nav_em__nav_desktop_sa_intl_warranties_and_services_0_2_6_16\" class=\"hmenu-item\">Warranties & Services</a></li>\n  <li class=\"hmenu-separator\"></li>\n</ul>\n\n<ul class=\"hmenu hmenu-translateX-right\" data-menu-id=\"7\" data-parent-menu-id=\"1\">\n  <li><a href=\"/\" class=\"hmenu-item hmenu-back-button\" aria-label=\"Back to main menu\" data-ref-tag=\"nav_em_1_7_BT_0_main_menu\"><div style=\"align-items: center;\"><i class=\"nav-sprite hmenu-arrow-prev\"></i>main menu</div></a></li>\n  <li><div class=\"hmenu-item hmenu-title \">smart home</div></li><li><a href=\"/gp/browse.html?node=6563140011&ref_=nav_em_amazon_smart_home_0_2_7_2\" class=\"hmenu-item\">Amazon Smart Home</a></li><li><a href=\"/gp/browse.html?node=73846268011&ref_=nav_em__ods_ha_vicc_ee_0_2_7_3\" class=\"hmenu-item\">Works with Alexa Devices</a></li><li><a href=\"/gp/browse.html?node=21217035011&ref_=nav_em_sh_lighting_0_2_7_4\" class=\"hmenu-item\">Smart Home Lighting</a></li><li><a href=\"/gp/browse.html?node=21216824011&ref_=nav_em_sh_locks-entry_0_2_7_5\" class=\"hmenu-item\">Smart Locks and Entry</a></li><li><a href=\"/gp/browse.html?node=21217033011&ref_=nav_em_sh_security-cameras-systems_0_2_7_6\" class=\"hmenu-item\">Security Cameras and Systems</a></li><li><a href=\"/gp/browse.html?node=21217037011&ref_=nav_em_sh_plugs-outlets_0_2_7_7\" class=\"hmenu-item\">Plugs and Outlets</a></li><li><a href=\"/gp/browse.html?node=19185106011&ref_=nav_em_sh_new-devices_0_2_7_8\" class=\"hmenu-item\">New Smart Devices</a></li><li><a href=\"/gp/browse.html?node=21217041011&ref_=nav_em_sh_heating-cooling_0_2_7_9\" class=\"hmenu-item\">Heating and Cooling</a></li><li><a href=\"/gp/browse.html?node=21217048011&ref_=nav_em_sh_detectors-sensors_0_2_7_10\" class=\"hmenu-item\">Detectors and Sensors</a></li><li><a href=\"/gp/browse.html?node=21216826011&ref_=nav_em_sh_home-entertainment_0_2_7_11\" class=\"hmenu-item\">Home Entertainment</a></li><li><a href=\"/gp/browse.html?node=21221447011&ref_=nav_em_sh_pet_0_2_7_12\" class=\"hmenu-item\">Pet</a></li><li><a href=\"/gp/browse.html?node=21216812011&ref_=nav_em_sh_voice-assistants-hubs_0_2_7_13\" class=\"hmenu-item\">Voice Assistants and Hubs</a></li><li><a href=\"/gp/browse.html?node=21217039011&ref_=nav_em_sh_kitchen_0_2_7_14\" class=\"hmenu-item\">Kitchen</a></li><li><a href=\"/gp/browse.html?node=21217038011&ref_=nav_em_sh_vacuums-mops_0_2_7_15\" class=\"hmenu-item\">Vacuums and Mops</a></li><li><a href=\"/gp/browse.html?node=21217056011&ref_=nav_em_sh_lawn-garden_0_2_7_16\" class=\"hmenu-item\">Lawn and Garden</a></li><li><a href=\"/gp/browse.html?node=21217028011&ref_=nav_em_sh_wifi-networking_0_2_7_17\" class=\"hmenu-item\">WIFI and Networking</a></li><li><a href=\"/gp/browse.html?node=21217060011&ref_=nav_em_sh_other_0_2_7_18\" class=\"hmenu-item\">Other Solutions</a></li>\n  <li class=\"hmenu-separator\"></li>\n</ul>\n\n<ul class=\"hmenu hmenu-translateX-right\" data-menu-id=\"8\" data-parent-menu-id=\"1\">\n  <li><a href=\"/\" class=\"hmenu-item hmenu-back-button\" aria-label=\"Back to main menu\" data-ref-tag=\"nav_em_1_8_BT_0_main_menu\"><div style=\"align-items: center;\"><i class=\"nav-sprite hmenu-arrow-prev\"></i>main menu</div></a></li>\n  <li><div class=\"hmenu-item hmenu-title \">arts & crafts</div></li><li><a href=\"/s?bbn=4954955011&rh=i%3Aspecialty-aps%2Cn%3A4954955011%2Cn%3A%212617942011%2Cn%3A2747968011&ref_=nav_em__nav_desktop_sa_intl_painting_drawing_supplies_0_2_8_2\" class=\"hmenu-item\">Painting, Drawing & Art Supplies</a></li><li><a href=\"/s?bbn=4954955011&rh=i%3Aspecialty-aps%2Cn%3A4954955011%2Cn%3A%212617942011%2Cn%3A12896081&ref_=nav_em__nav_desktop_sa_intl__beading_jewelry_making_0_2_8_3\" class=\"hmenu-item\">Beading & Jewelry Making</a></li><li><a href=\"/s?bbn=4954955011&rh=i%3Aspecialty-aps%2Cn%3A4954955011%2Cn%3A%212617942011%2Cn%3A378733011&ref_=nav_em__nav_desktop_sa_intl_crafting_0_2_8_4\" class=\"hmenu-item\">Crafting</a></li><li><a href=\"/s?bbn=4954955011&rh=i%3Aspecialty-aps%2Cn%3A4954955011%2Cn%3A%212617942011%2Cn%3A12899121&ref_=nav_em__nav_desktop_sa_intl_fabric_0_2_8_5\" class=\"hmenu-item\">Fabric</a></li><li><a href=\"/s?bbn=4954955011&rh=i%3Aspecialty-aps%2Cn%3A4954955011%2Cn%3A%212617942011%2Cn%3A12896841&ref_=nav_em__nav_desktop_sa_intl_fabric_decorating_0_2_8_6\" class=\"hmenu-item\">Fabric Decorating</a></li><li><a href=\"/s?bbn=4954955011&rh=i%3Aspecialty-aps%2Cn%3A4954955011%2Cn%3A%212617942011%2Cn%3A12897221&ref_=nav_em__nav_desktop_sa_intl_knitting_crochet_0_2_8_7\" class=\"hmenu-item\">Knitting & Crochet</a></li><li><a href=\"/s?bbn=4954955011&rh=i%3Aspecialty-aps%2Cn%3A4954955011%2Cn%3A%212617942011%2Cn%3A2237329011&ref_=nav_em__nav_desktop_sa_intl_needlework_0_2_8_8\" class=\"hmenu-item\">Needlework</a></li><li><a href=\"/s?bbn=4954955011&rh=i%3Aspecialty-aps%2Cn%3A4954955011%2Cn%3A%212617942011%2Cn%3A2237594011&ref_=nav_em__nav_desktop_sa_intl_organization_storage_transport_0_2_8_9\" class=\"hmenu-item\">Organization, Storage & Transport</a></li><li><a href=\"/s?bbn=4954955011&rh=i%3Aspecialty-aps%2Cn%3A4954955011%2Cn%3A%212617942011%2Cn%3A12898451&ref_=nav_em__nav_desktop_sa_intl_printmaking_0_2_8_10\" class=\"hmenu-item\">Printmaking</a></li><li><a href=\"/s?bbn=4954955011&rh=i%3Aspecialty-aps%2Cn%3A4954955011%2Cn%3A%212617942011%2Cn%3A12898821&ref_=nav_em__nav_desktop_sa_intl_scrapbookig_stamping_0_2_8_11\" class=\"hmenu-item\">Scrapbooking & Stamping</a></li><li><a href=\"/s?bbn=4954955011&rh=i%3Aspecialty-aps%2Cn%3A4954955011%2Cn%3A%212617942011%2Cn%3A12899091&ref_=nav_em__nav_desktop_sa_intl_sewing_0_2_8_12\" class=\"hmenu-item\">Sewing</a></li><li><a href=\"/s?bbn=4954955011&rh=i%3Aspecialty-aps%2Cn%3A4954955011%2Cn%3A%212617942011%2Cn%3A723469011&ref_=nav_em__nav_desktop_sa_intl_party_decorations_supplies_0_2_8_13\" class=\"hmenu-item\">Party Decorations & Supplies</a></li><li><a href=\"/s?bbn=4954955011&rh=i%3Aspecialty-aps%2Cn%3A4954955011%2Cn%3A%212617942011%2Cn%3A723452011&ref_=nav_em__nav_desktop_sa_intl_gift_wrapping_supplies_0_2_8_14\" class=\"hmenu-item\">Gift Wrapping Supplies</a></li>\n  <li class=\"hmenu-separator\"></li>\n</ul>\n\n<ul class=\"hmenu hmenu-translateX-right\" data-menu-id=\"9\" data-parent-menu-id=\"1\">\n  <li><a href=\"/\" class=\"hmenu-item hmenu-back-button\" aria-label=\"Back to main menu\" data-ref-tag=\"nav_em_1_9_BT_0_main_menu\"><div style=\"align-items: center;\"><i class=\"nav-sprite hmenu-arrow-prev\"></i>main menu</div></a></li>\n  <li><div class=\"hmenu-item hmenu-title \">automotive</div></li><li><a href=\"/s?bbn=2562090011&rh=i%3Aspecialty-aps%2Cn%3A2562090011%2Cn%3A%2115690151%2Cn%3A15718271&ref_=nav_em__nav_desktop_sa_intl_car_care_0_2_9_2\" class=\"hmenu-item\">Car Care</a></li><li><a href=\"/s?bbn=2562090011&rh=i%3Aspecialty-aps%2Cn%3A2562090011%2Cn%3A%2115690151%2Cn%3A2230642011&ref_=nav_em__nav_desktop_sa_intl_car_electronics_accessories_0_2_9_3\" class=\"hmenu-item\">Car Electronics & Accessories</a></li><li><a href=\"/s?bbn=2562090011&rh=i%3Aspecialty-aps%2Cn%3A2562090011%2Cn%3A%2115690151%2Cn%3A15857511&ref_=nav_em__nav_desktop_sa_intl_exterior_accessories__0_2_9_4\" class=\"hmenu-item\">Exterior Accessories</a></li><li><a href=\"/s?bbn=2562090011&rh=i%3Aspecialty-aps%2Cn%3A2562090011%2Cn%3A%2115690151%2Cn%3A15857501&ref_=nav_em__nav_desktop_sa_intl_interior_accessories_0_2_9_5\" class=\"hmenu-item\">Interior Accessories</a></li><li><a href=\"/s?bbn=2562090011&rh=i%3Aspecialty-aps%2Cn%3A2562090011%2Cn%3A%2115690151%2Cn%3A15736321&ref_=nav_em__nav_desktop_sa_intl_lights_lighting_accessories_0_2_9_6\" class=\"hmenu-item\">Lights & Lighting Accessories</a></li><li><a href=\"/s?bbn=2562090011&rh=i%3Aspecialty-aps%2Cn%3A2562090011%2Cn%3A%2115690151%2Cn%3A346333011&ref_=nav_em__nav_desktop_sa_intl_motorcycle_powersports_0_2_9_7\" class=\"hmenu-item\">Motorcycle & Powersports</a></li><li><a href=\"/s?bbn=2562090011&rh=i%3Aspecialty-aps%2Cn%3A2562090011%2Cn%3A%2115690151%2Cn%3A15718791&ref_=nav_em__nav_desktop_sa_intl_oils_fluid_0_2_9_8\" class=\"hmenu-item\">Oils & Fluids</a></li><li><a href=\"/s?bbn=2562090011&rh=i%3Aspecialty-aps%2Cn%3A2562090011%2Cn%3A%2115690151%2Cn%3A13591416011&ref_=nav_em__nav_desktop_sa_intl_paint_paint_supplies_0_2_9_9\" class=\"hmenu-item\">Paint & Paint Supplies</a></li><li><a href=\"/s?bbn=2562090011&rh=i%3Aspecialty-aps%2Cn%3A2562090011%2Cn%3A%2115690151%2Cn%3A15710351&ref_=nav_em__nav_desktop_sa_intl_performance_parts_accessories_0_2_9_10\" class=\"hmenu-item\">Performance Parts & Accessories</a></li><li><a href=\"/s?bbn=2562090011&rh=i%3Aspecialty-aps%2Cn%3A2562090011%2Cn%3A%2115690151%2Cn%3A15719731&ref_=nav_em__nav_desktop_sa_intl_replacement_parts_0_2_9_11\" class=\"hmenu-item\">Replacement Parts</a></li><li><a href=\"/s?bbn=2562090011&rh=i%3Aspecialty-aps%2Cn%3A2562090011%2Cn%3A%2115690151%2Cn%3A2258019011&ref_=nav_em__nav_desktop_sa_intl_rv_parts_accessories_0_2_9_12\" class=\"hmenu-item\">RV Parts & Accessories</a></li><li><a href=\"/s?bbn=2562090011&rh=i%3Aspecialty-aps%2Cn%3A2562090011%2Cn%3A%2115690151%2Cn%3A15706571&ref_=nav_em__nav_desktop_sa_intl_tires_wheels_0_2_9_13\" class=\"hmenu-item\">Tires & Wheels</a></li><li><a href=\"/s?bbn=2562090011&rh=i%3Aspecialty-aps%2Cn%3A2562090011%2Cn%3A%2115690151%2Cn%3A15706941&ref_=nav_em__nav_desktop_sa_intl_tools_equipment_0_2_9_14\" class=\"hmenu-item\">Tools & Equipment</a></li><li><a href=\"/s?bbn=2562090011&rh=i%3Aspecialty-aps%2Cn%3A2562090011%2Cn%3A%2115690151%2Cn%3A2204830011&ref_=nav_em__nav_desktop_sa_intl_automotive_enthusiast_merchandise_0_2_9_15\" class=\"hmenu-item\">Automotive Enthusiast Merchandise</a></li><li><a href=\"/s?bbn=2562090011&rh=i%3Aspecialty-aps%2Cn%3A2562090011%2Cn%3A%2115690151%2Cn%3A15682003011&ref_=nav_em__nav_desktop_sa_intl_heavyduty_commercial_0_2_9_16\" class=\"hmenu-item\">Heavy Duty & Commercial Vehicle Equipment</a></li>\n  <li class=\"hmenu-separator\"></li>\n</ul>\n\n<ul class=\"hmenu hmenu-translateX-right\" data-menu-id=\"10\" data-parent-menu-id=\"1\">\n  <li><a href=\"/\" class=\"hmenu-item hmenu-back-button\" aria-label=\"Back to main menu\" data-ref-tag=\"nav_em_1_10_BT_0_main_menu\"><div style=\"align-items: center;\"><i class=\"nav-sprite hmenu-arrow-prev\"></i>main menu</div></a></li>\n  <li><div class=\"hmenu-item hmenu-title \">baby</div></li><li><a href=\"/s?bbn=16225005011&rh=i%3Aspecialty-aps%2Cn%3A%2116225005011%2Cn%3A239225011&ref_=nav_em__nav_desktop_sa_intl_activity_entertainment_0_2_10_2\" class=\"hmenu-item\">Activity & Entertainment</a></li><li><a href=\"/s?bbn=16225005011&rh=i%3Aspecialty-aps%2Cn%3A%2116225005011%2Cn%3A7147444011&ref_=nav_em__nav_desktop_sa_intl_apparel_accessories_0_2_10_3\" class=\"hmenu-item\">Apparel & Accessories</a></li><li><a href=\"/s?bbn=16225005011&rh=i%3Aspecialty-aps%2Cn%3A%2116225005011%2Cn%3A196601011&ref_=nav_em__nav_desktop_sa_intl_baby_toddler_toys_0_2_10_4\" class=\"hmenu-item\">Baby & Toddler Toys</a></li><li><a href=\"/s?bbn=16225005011&rh=i%3Aspecialty-aps%2Cn%3A%2116225005011%2Cn%3A17720255011&ref_=nav_em__nav_desktop_sa_intl_baby_care_0_2_10_5\" class=\"hmenu-item\">Baby Care</a></li><li><a href=\"/s?bbn=16225005011&rh=i%3Aspecialty-aps%2Cn%3A%2116225005011%2Cn%3A405369011&ref_=nav_em__nav_desktop_sa_intl_baby_stationary_0_2_10_6\" class=\"hmenu-item\">Baby Stationery</a></li><li><a href=\"/s?bbn=16225005011&rh=i%3Aspecialty-aps%2Cn%3A%2116225005011%2Cn%3A166835011&ref_=nav_em__nav_desktop_sa_intl_car_seats_accessories_0_2_10_7\" class=\"hmenu-item\">Car Seats & Accessories</a></li><li><a href=\"/s?bbn=16225005011&rh=i%3Aspecialty-aps%2Cn%3A%2116225005011%2Cn%3A166764011&ref_=nav_em__nav_desktop_sa_intl_diapering_0_2_10_8\" class=\"hmenu-item\">Diapering</a></li><li><a href=\"/s?bbn=16225005011&rh=i%3Aspecialty-aps%2Cn%3A%2116225005011%2Cn%3A166777011&ref_=nav_em__nav_desktop_sa_intl_feeding_0_2_10_9\" class=\"hmenu-item\">Feeding</a></li><li><a href=\"/s?bbn=16225005011&rh=i%3Aspecialty-aps%2Cn%3A%2116225005011%2Cn%3A239226011&ref_=nav_em__nav_desktop_sa_intl_gifts_0_2_10_10\" class=\"hmenu-item\">Gifts</a></li><li><a href=\"/s?bbn=16225005011&rh=i%3Aspecialty-aps%2Cn%3A%2116225005011%2Cn%3A695338011&ref_=nav_em__nav_desktop_sa_intl_nursery_0_2_10_11\" class=\"hmenu-item\">Nursery</a></li><li><a href=\"/s?bbn=16225005011&rh=i%3Aspecialty-aps%2Cn%3A%2116225005011%2Cn%3A166887011&ref_=nav_em__nav_desktop_sa_intl_potty_training_0_2_10_12\" class=\"hmenu-item\">Potty Training</a></li><li><a href=\"/s?bbn=16225005011&rh=i%3Aspecialty-aps%2Cn%3A%2116225005011%2Cn%3A166804011&ref_=nav_em__nav_desktop_sa_intl_pregnancy_and_maternity_0_2_10_13\" class=\"hmenu-item\">Pregnancy & Maternity</a></li><li><a href=\"/s?bbn=16225005011&rh=i%3Aspecialty-aps%2Cn%3A%2116225005011%2Cn%3A166863011&ref_=nav_em__nav_desktop_sa_intl_safety_0_2_10_14\" class=\"hmenu-item\">Safety</a></li><li><a href=\"/s?bbn=16225005011&rh=i%3Aspecialty-aps%2Cn%3A%2116225005011%2Cn%3A8446318011&ref_=nav_em__nav_desktop_sa_intl_strollers_and_accessories_0_2_10_15\" class=\"hmenu-item\">Strollers & Accessories</a></li><li><a href=\"/s?bbn=16225005011&rh=i%3Aspecialty-aps%2Cn%3A%2116225005011%2Cn%3A17726796011&ref_=nav_em__nav_desktop_sa_intl_travel_gear_0_2_10_16\" class=\"hmenu-item\">Travel Gear</a></li>\n  <li class=\"hmenu-separator\"></li>\n</ul>\n\n<ul class=\"hmenu hmenu-translateX-right\" data-menu-id=\"11\" data-parent-menu-id=\"1\">\n  <li><a href=\"/\" class=\"hmenu-item hmenu-back-button\" aria-label=\"Back to main menu\" data-ref-tag=\"nav_em_1_11_BT_0_main_menu\"><div style=\"align-items: center;\"><i class=\"nav-sprite hmenu-arrow-prev\"></i>main menu</div></a></li>\n  <li><div class=\"hmenu-item hmenu-title \">beauty and personal care</div></li><li><a href=\"/s?bbn=16225006011&rh=i%3Aspecialty-aps%2Cn%3A%2116225006011%2Cn%3A11058281&ref_=nav_em__nav_desktop_sa_intl_makeup_0_2_11_2\" class=\"hmenu-item\">Makeup</a></li><li><a href=\"/s?bbn=16225006011&rh=i%3Aspecialty-aps%2Cn%3A%2116225006011%2Cn%3A11060451&ref_=nav_em__nav_desktop_sa_intl_skin_care_0_2_11_3\" class=\"hmenu-item\">Skin Care</a></li><li><a href=\"/s?bbn=16225006011&rh=i%3Aspecialty-aps%2Cn%3A%2116225006011%2Cn%3A11057241&ref_=nav_em__nav_desktop_sa_intl__0_2_11_4\" class=\"hmenu-item\">Hair Care</a></li><li><a href=\"/s?bbn=16225006011&rh=i%3Aspecialty-aps%2Cn%3A%2116225006011%2Cn%3A11056591&ref_=nav_em__nav_desktop_sa_intl_fragrance_0_2_11_5\" class=\"hmenu-item\">Fragrance</a></li><li><a href=\"/s?bbn=16225006011&rh=i%3Aspecialty-aps%2Cn%3A%2116225006011%2Cn%3A17242866011&ref_=nav_em__nav_desktop_sa_intl_foot_hand_and_nail_care_0_2_11_6\" class=\"hmenu-item\">Foot, Hand & Nail Care</a></li><li><a href=\"/s?bbn=16225006011&rh=i%3Aspecialty-aps%2Cn%3A%2116225006011%2Cn%3A11062741&ref_=nav_em__nav_desktop_sa_intl_tools_and_accessories_0_2_11_7\" class=\"hmenu-item\">Tools & Accessories</a></li><li><a href=\"/s?bbn=16225006011&rh=i%3Aspecialty-aps%2Cn%3A%2116225006011%2Cn%3A3778591&ref_=nav_em__nav_desktop_sa_intl_shave_and_hair_removal_0_2_11_8\" class=\"hmenu-item\">Shave & Hair Removal</a></li><li><a href=\"/s?bbn=16225006011&rh=i%3Aspecialty-aps%2Cn%3A%2116225006011%2Cn%3A3777891&ref_=nav_em__nav_desktop_sa_intl_personal_care_0_2_11_9\" class=\"hmenu-item\">Personal Care</a></li><li><a href=\"/s?bbn=16225006011&rh=i%3Aspecialty-aps%2Cn%3A%2116225006011%2Cn%3A10079992011&ref_=nav_em__nav_desktop_sa_intl_oral_care_0_2_11_10\" class=\"hmenu-item\">Oral Care</a></li>\n  <li class=\"hmenu-separator\"></li>\n</ul>\n\n<ul class=\"hmenu hmenu-translateX-right\" data-menu-id=\"12\" data-parent-menu-id=\"1\">\n  <li><a href=\"/\" class=\"hmenu-item hmenu-back-button\" aria-label=\"Back to main menu\" data-ref-tag=\"nav_em_1_12_BT_0_main_menu\"><div style=\"align-items: center;\"><i class=\"nav-sprite hmenu-arrow-prev\"></i>main menu</div></a></li>\n  <li><div class=\"hmenu-item hmenu-title \">women's fashion</div></li><li><a href=\"/s?bbn=16225018011&rh=i%3Aspecialty-aps%2Cn%3A7141123011%2Cn%3A16225018011%2Cn%3A1040660&ref_=nav_em__nav_desktop_sa_intl_clothing_0_2_12_2\" class=\"hmenu-item\">Clothing</a></li><li><a href=\"/s?bbn=16225018011&rh=i%3Aspecialty-aps%2Cn%3A7141123011%2Cn%3A16225018011%2Cn%3A679337011&ref_=nav_em__nav_desktop_sa_intl_shoes_0_2_12_3\" class=\"hmenu-item\">Shoes</a></li><li><a href=\"/s?bbn=16225018011&rh=i%3Aspecialty-aps%2Cn%3A7141123011%2Cn%3A16225018011%2Cn%3A7192394011&ref_=nav_em__nav_desktop_sa_intl_jewelry_0_2_12_4\" class=\"hmenu-item\">Jewelry</a></li><li><a href=\"/s?bbn=16225018011&rh=i%3Aspecialty-aps%2Cn%3A7141123011%2Cn%3A16225018011%2Cn%3A6358543011&ref_=nav_em__nav_desktop_sa_intl_watches_0_2_12_5\" class=\"hmenu-item\">Watches</a></li><li><a href=\"/s?bbn=16225018011&rh=i%3Aspecialty-aps%2Cn%3A7141123011%2Cn%3A16225018011%2Cn%3A15743631&ref_=nav_em__nav_desktop_sa_intl_handbags_0_2_12_6\" class=\"hmenu-item\">Handbags</a></li><li><a href=\"/s?bbn=16225018011&rh=i%3Aspecialty-aps%2Cn%3A7141123011%2Cn%3A16225018011%2Cn%3A2474936011&ref_=nav_em__nav_desktop_sa_intl_accessories_0_2_12_7\" class=\"hmenu-item\">Accessories</a></li><li><a href=\"/gp/browse.html?node=16225019011&ref_=nav_em__nav_desktop_sa_intl_mens_fashion_0_2_12_8\" class=\"hmenu-item\">Men's Fashion</a></li><li><a href=\"/gp/browse.html?node=16225020011&ref_=nav_em__nav_desktop_sa_intl_girls_fashion_0_2_12_9\" class=\"hmenu-item\">Girls' Fashion</a></li><li><a href=\"/gp/browse.html?node=16225019011&ref_=nav_em__nav_desktop_sa_intl_boys_fashion_0_2_12_10\" class=\"hmenu-item\">Boys' Fashion</a></li>\n  <li class=\"hmenu-separator\"></li>\n</ul>\n\n<ul class=\"hmenu hmenu-translateX-right\" data-menu-id=\"13\" data-parent-menu-id=\"1\">\n  <li><a href=\"/\" class=\"hmenu-item hmenu-back-button\" aria-label=\"Back to main menu\" data-ref-tag=\"nav_em_1_13_BT_0_main_menu\"><div style=\"align-items: center;\"><i class=\"nav-sprite hmenu-arrow-prev\"></i>main menu</div></a></li>\n  <li><div class=\"hmenu-item hmenu-title \">men's fashion</div></li><li><a href=\"/s?bbn=16225019011&rh=i%3Aspecialty-aps%2Cn%3A7141123011%2Cn%3A16225019011%2Cn%3A1040658&ref_=nav_em__nav_desktop_sa_intl_clothing_0_2_13_2\" class=\"hmenu-item\">Clothing</a></li><li><a href=\"/s?bbn=16225019011&rh=i%3Aspecialty-aps%2Cn%3A7141123011%2Cn%3A16225019011%2Cn%3A679255011&ref_=nav_em__nav_desktop_sa_intl_shoes_0_2_13_3\" class=\"hmenu-item\">Shoes</a></li><li><a href=\"/s?bbn=16225019011&rh=i%3Aspecialty-aps%2Cn%3A7141123011%2Cn%3A16225019011%2Cn%3A6358539011&ref_=nav_em__nav_desktop_sa_intl_watches_0_2_13_4\" class=\"hmenu-item\">Watches</a></li><li><a href=\"/s?bbn=16225019011&rh=i%3Aspecialty-aps%2Cn%3A7141123011%2Cn%3A16225019011%2Cn%3A2474937011&ref_=nav_em__nav_desktop_sa_intl_accessories_0_2_13_5\" class=\"hmenu-item\">Accessories</a></li><li><a href=\"/gp/browse.html?node=16225018011&ref_=nav_em__nav_desktop_sa_intl_womens_fashion_0_2_13_6\" class=\"hmenu-item\">Women's Fashion</a></li><li><a href=\"/gp/browse.html?node=16225020011&ref_=nav_em__nav_desktop_sa_intl_girls_fashion_0_2_13_7\" class=\"hmenu-item\">Girls' Fashion</a></li><li><a href=\"/gp/browse.html?node=16225021011&ref_=nav_em__nav_desktop_sa_intl_boys_fashion_0_2_13_8\" class=\"hmenu-item\">Boys' Fashion</a></li>\n  <li class=\"hmenu-separator\"></li>\n</ul>\n\n<ul class=\"hmenu hmenu-translateX-right\" data-menu-id=\"14\" data-parent-menu-id=\"1\">\n  <li><a href=\"/\" class=\"hmenu-item hmenu-back-button\" aria-label=\"Back to main menu\" data-ref-tag=\"nav_em_1_14_BT_0_main_menu\"><div style=\"align-items: center;\"><i class=\"nav-sprite hmenu-arrow-prev\"></i>main menu</div></a></li>\n  <li><div class=\"hmenu-item hmenu-title \">girls' fashion</div></li><li><a href=\"/s?bbn=16225020011&rh=i%3Aspecialty-aps%2Cn%3A7141123011%2Cn%3A16225020011%2Cn%3A1040664&ref_=nav_em__nav_desktop_sa_intl_clothing_0_2_14_2\" class=\"hmenu-item\">Clothing</a></li><li><a href=\"/s?bbn=16225020011&rh=i%3Aspecialty-aps%2Cn%3A7141123011%2Cn%3A16225020011%2Cn%3A679217011&ref_=nav_em__nav_desktop_sa_intl_shoes_0_2_14_3\" class=\"hmenu-item\">Shoes</a></li><li><a href=\"/s?bbn=16225020011&rh=i%3Aspecialty-aps%2Cn%3A7141123011%2Cn%3A16225020011%2Cn%3A3880961&ref_=nav_em__nav_desktop_sa_intl_jewelry_0_2_14_4\" class=\"hmenu-item\">Jewelry</a></li><li><a href=\"/s?bbn=16225020011&rh=i%3Aspecialty-aps%2Cn%3A7141123011%2Cn%3A16225020011%2Cn%3A6358547011&ref_=nav_em__nav_desktop_sa_intl_watches_0_2_14_5\" class=\"hmenu-item\">Watches</a></li><li><a href=\"/s?bbn=16225020011&rh=i%3Aspecialty-aps%2Cn%3A7141123011%2Cn%3A16225020011%2Cn%3A2474938011&ref_=nav_em__nav_desktop_sa_intl_accessories_0_2_14_6\" class=\"hmenu-item\">Accessories</a></li><li><a href=\"/s?bbn=16225020011&rh=i%3Aspecialty-aps%2Cn%3A7141123011%2Cn%3A7147442011%2Cn%3A7581687011&ref_=nav_em__nav_desktop_sa_intl_school_uniforms_0_2_14_7\" class=\"hmenu-item\">School Uniforms</a></li><li><a href=\"/gp/browse.html?node=16225018011&ref_=nav_em__nav_desktop_sa_intl_womens_fashion_0_2_14_8\" class=\"hmenu-item\">Women's Fashion</a></li><li><a href=\"/gp/browse.html?node=16225019011&ref_=nav_em__nav_desktop_sa_intl_mens_fashion_0_2_14_9\" class=\"hmenu-item\">Men's Fashion</a></li><li><a href=\"/gp/browse.html?node=16225021011&ref_=nav_em__nav_desktop_sa_intl_boys_fashion_0_2_14_10\" class=\"hmenu-item\">Boys' Fashion</a></li>\n  <li class=\"hmenu-separator\"></li>\n</ul>\n\n<ul class=\"hmenu hmenu-translateX-right\" data-menu-id=\"15\" data-parent-menu-id=\"1\">\n  <li><a href=\"/\" class=\"hmenu-item hmenu-back-button\" aria-label=\"Back to main menu\" data-ref-tag=\"nav_em_1_15_BT_0_main_menu\"><div style=\"align-items: center;\"><i class=\"nav-sprite hmenu-arrow-prev\"></i>main menu</div></a></li>\n  <li><div class=\"hmenu-item hmenu-title \">boys' fashion</div></li><li><a href=\"/s?bbn=16225021011&rh=i%3Aspecialty-aps%2Cn%3A7141123011%2Cn%3A16225021011%2Cn%3A1040666&ref_=nav_em__nav_desktop_sa_intl_clothing_0_2_15_2\" class=\"hmenu-item\">Clothing</a></li><li><a href=\"/s?bbn=16225021011&rh=i%3Aspecialty-aps%2Cn%3A7141123011%2Cn%3A16225021011%2Cn%3A679182011&ref_=nav_em__nav_desktop_sa_intl_shoes_0_2_15_3\" class=\"hmenu-item\">Shoes</a></li><li><a href=\"/s?bbn=16225021011&rh=i%3Aspecialty-aps%2Cn%3A7141123011%2Cn%3A16225021011%2Cn%3A3880611&ref_=nav_em__nav_desktop_sa_intl_jewelry_0_2_15_4\" class=\"hmenu-item\">Jewelry</a></li><li><a href=\"/s?bbn=16225021011&rh=i%3Aspecialty-aps%2Cn%3A7141123011%2Cn%3A16225021011%2Cn%3A6358551011&ref_=nav_em__nav_desktop_sa_intl_watches_0_2_15_5\" class=\"hmenu-item\">Watches</a></li><li><a href=\"/s?bbn=16225021011&rh=i%3Aspecialty-aps%2Cn%3A7141123011%2Cn%3A16225021011%2Cn%3A2474939011&ref_=nav_em__nav_desktop_sa_intl_accessories_0_2_15_6\" class=\"hmenu-item\">Accessories</a></li><li><a href=\"/s?bbn=7581691011&rh=i%3Aspecialty-aps%2Cn%3A7141123011%2Cn%3A7147443011%2Cn%3A7581691011&ref_=nav_em__nav_desktop_sa_intl_school_uniforms_0_2_15_7\" class=\"hmenu-item\">School Uniforms</a></li><li><a href=\"/gp/browse.html?node=16225018011&ref_=nav_em__nav_desktop_sa_intl_womens_fashion_0_2_15_8\" class=\"hmenu-item\">Women's Fashion</a></li><li><a href=\"/gp/browse.html?node=16225019011&ref_=nav_em__nav_desktop_sa_intl_mens_fashion_0_2_15_9\" class=\"hmenu-item\">Men's Fashion</a></li><li><a href=\"/gp/browse.html?node=16225020011&ref_=nav_em__nav_desktop_sa_intl_girls_fashion_0_2_15_10\" class=\"hmenu-item\">Girls' Fashion</a></li>\n  <li class=\"hmenu-separator\"></li>\n</ul>\n\n<ul class=\"hmenu hmenu-translateX-right\" data-menu-id=\"16\" data-parent-menu-id=\"1\">\n  <li><a href=\"/\" class=\"hmenu-item hmenu-back-button\" aria-label=\"Back to main menu\" data-ref-tag=\"nav_em_1_16_BT_0_main_menu\"><div style=\"align-items: center;\"><i class=\"nav-sprite hmenu-arrow-prev\"></i>main menu</div></a></li>\n  <li><div class=\"hmenu-item hmenu-title \">health and household</div></li><li><a href=\"/s?bbn=16225010011&rh=i%3Aspecialty-aps%2Cn%3A%2116225010011%2Cn%3A10787321&ref_=nav_em__nav_desktop_sa_intl_baby_and_child_care_0_2_16_2\" class=\"hmenu-item\">Baby & Child Care</a></li><li><a href=\"/s?bbn=16225010011&rh=i%3Aspecialty-aps%2Cn%3A%2116225010011%2Cn%3A3760941&ref_=nav_em__nav_desktop_sa_intl_health_care_0_2_16_3\" class=\"hmenu-item\">Health Care</a></li><li><a href=\"/s?bbn=16225010011&rh=i%3Aspecialty-aps%2Cn%3A%2116225010011%2Cn%3A15342811&ref_=nav_em__nav_desktop_sa_intl_household_supplies_0_2_16_4\" class=\"hmenu-item\">Household Supplies</a></li><li><a href=\"/s?bbn=16225010011&rh=i%3Aspecialty-aps%2Cn%3A%2116225010011%2Cn%3A3775161&ref_=nav_em__nav_desktop_sa_intl_medical_supplies_and_equipment_0_2_16_5\" class=\"hmenu-item\">Medical Supplies & Equipment</a></li><li><a href=\"/s?bbn=16225010011&rh=i%3Aspecialty-aps%2Cn%3A%2116225010011%2Cn%3A10079992011&ref_=nav_em__nav_desktop_sa_intl_oral_care_0_2_16_6\" class=\"hmenu-item\">Oral Care</a></li><li><a href=\"/s?bbn=16225010011&rh=i%3Aspecialty-aps%2Cn%3A%2116225010011%2Cn%3A3777891&ref_=nav_em__nav_desktop_sa_intl_personal_care_0_2_16_7\" class=\"hmenu-item\">Personal Care</a></li><li><a href=\"/s?bbn=16225010011&rh=i%3Aspecialty-aps%2Cn%3A%2116225010011%2Cn%3A3777371&ref_=nav_em__nav_desktop_sa_intl_sexual_wellness_0_2_16_8\" class=\"hmenu-item\">Sexual Wellness</a></li><li><a href=\"/s?bbn=16225010011&rh=i%3Aspecialty-aps%2Cn%3A%2116225010011%2Cn%3A6973663011&ref_=nav_em__nav_desktop_sa_intl_sports_nutrition_0_2_16_9\" class=\"hmenu-item\">Sports Nutrition</a></li><li><a href=\"/s?bbn=16225010011&rh=i%3Aspecialty-aps%2Cn%3A%2116225010011%2Cn%3A723418011&ref_=nav_em__nav_desktop_sa_intl_stationery_and_gift_wrapping_supplies_0_2_16_10\" class=\"hmenu-item\">Stationery & Gift Wrapping Supplies</a></li><li><a href=\"/s?bbn=16225010011&rh=i%3Aspecialty-aps%2Cn%3A%2116225010011%2Cn%3A10079994011&ref_=nav_em__nav_desktop_sa_intl_vision_care_0_2_16_11\" class=\"hmenu-item\">Vision Care</a></li><li><a href=\"/s?bbn=16225010011&rh=i%3Aspecialty-aps%2Cn%3A%2116225010011%2Cn%3A3764441&ref_=nav_em__nav_desktop_sa_intl_vitamins_and_dietary_supplements_0_2_16_12\" class=\"hmenu-item\">Vitamins & Dietary Supplements</a></li><li><a href=\"/s?bbn=16225010011&rh=i%3Aspecialty-aps%2Cn%3A%2116225010011%2Cn%3A10079996011&ref_=nav_em__nav_desktop_sa_intl_wellness_and_relaxation_0_2_16_13\" class=\"hmenu-item\">Wellness & Relaxation</a></li>\n  <li class=\"hmenu-separator\"></li>\n</ul>\n\n<ul class=\"hmenu hmenu-translateX-right\" data-menu-id=\"17\" data-parent-menu-id=\"1\">\n  <li><a href=\"/\" class=\"hmenu-item hmenu-back-button\" aria-label=\"Back to main menu\" data-ref-tag=\"nav_em_1_17_BT_0_main_menu\"><div style=\"align-items: center;\"><i class=\"nav-sprite hmenu-arrow-prev\"></i>main menu</div></a></li>\n  <li><div class=\"hmenu-item hmenu-title \">home and kitchen</div></li><li><a href=\"/s?bbn=16225011011&rh=i%3Aspecialty-aps%2Cn%3A%2116225011011%2Cn%3A3206325011&ref_=nav_em__nav_desktop_sa_intl_kids_home_store_0_2_17_2\" class=\"hmenu-item\">Kids' Home Store</a></li><li><a href=\"/s?bbn=16225011011&rh=i%3Aspecialty-aps%2Cn%3A%2116225011011%2Cn%3A284507&ref_=nav_em__nav_desktop_sa_intl_kitchen_and_dining_0_2_17_3\" class=\"hmenu-item\">Kitchen & Dining</a></li><li><a href=\"/s?bbn=16225011011&rh=i%3Aspecialty-aps%2Cn%3A%2116225011011%2Cn%3A1063252&ref_=nav_em__nav_desktop_sa_intl_bedding_0_2_17_4\" class=\"hmenu-item\">Bedding</a></li><li><a href=\"/s?bbn=16225011011&rh=i%3Aspecialty-aps%2Cn%3A%2116225011011%2Cn%3A1063236&ref_=nav_em__nav_desktop_sa_intl_bath_0_2_17_5\" class=\"hmenu-item\">Bath</a></li><li><a href=\"/s?bbn=16225011011&rh=i%3Aspecialty-aps%2Cn%3A%2116225011011%2Cn%3A1063306&ref_=nav_em__nav_desktop_sa_intl_furniture_0_2_17_6\" class=\"hmenu-item\">Furniture</a></li><li><a href=\"/s?bbn=16225011011&rh=i%3Aspecialty-aps%2Cn%3A%2116225011011%2Cn%3A1063278&ref_=nav_em__nav_desktop_sa_intl_home_decor_0_2_17_7\" class=\"hmenu-item\">Home Décor</a></li><li><a href=\"/s?bbn=16225011011&rh=i%3Aspecialty-aps%2Cn%3A%2116225011011%2Cn%3A3736081&ref_=nav_em__nav_desktop_sa_intl_wall_art_0_2_17_8\" class=\"hmenu-item\">Wall Art</a></li><li><a href=\"/s?bbn=16225011011&rh=i%3Aspecialty-aps%2Cn%3A%2116225011011%2Cn%3A16510975011&ref_=nav_em__nav_desktop_sa_intl_lighting_and_ceiling_fans_0_2_17_9\" class=\"hmenu-item\">Lighting & Ceiling Fans</a></li><li><a href=\"/s?bbn=16225011011&rh=i%3Aspecialty-aps%2Cn%3A%2116225011011%2Cn%3A13679381&ref_=nav_em__nav_desktop_sa_intl_seasonal_decor_0_2_17_10\" class=\"hmenu-item\">Seasonal Décor</a></li><li><a href=\"/s?bbn=16225011011&rh=i%3Aspecialty-aps%2Cn%3A%2116225011011%2Cn%3A901590&ref_=nav_em__nav_desktop_sa_intl_event_and_party_supplies_0_2_17_11\" class=\"hmenu-item\">Event & Party Supplies</a></li><li><a href=\"/s?bbn=16225011011&rh=i%3Aspecialty-aps%2Cn%3A%2116225011011%2Cn%3A3206324011&ref_=nav_em__nav_desktop_sa_intl_heating_cooling_and_air_quality_0_2_17_12\" class=\"hmenu-item\">Heating, Cooling & Air Quality</a></li><li><a href=\"/s?bbn=16225011011&rh=i%3Aspecialty-aps%2Cn%3A%2116225011011%2Cn%3A510240&ref_=nav_em__nav_desktop_sa_intl_heating_cooling_and_air_quality_0_2_17_13\" class=\"hmenu-item\">Irons & Steamers</a></li><li><a href=\"/s?bbn=16225011011&rh=i%3Aspecialty-aps%2Cn%3A%2116225011011%2Cn%3A510106&ref_=nav_em__nav_desktop_sa_intl_vacuums_and_floor_care_0_2_17_14\" class=\"hmenu-item\">Vacuums & Floor Care</a></li><li><a href=\"/s?bbn=16225011011&rh=i%3Aspecialty-aps%2Cn%3A%2116225011011%2Cn%3A3610841&ref_=nav_em__nav_desktop_sa_intl_storage_and_organization_0_2_17_15\" class=\"hmenu-item\">Storage & Organization</a></li><li><a href=\"/s?bbn=16225011011&rh=i%3Aspecialty-aps%2Cn%3A%2116225011011%2Cn%3A10802561&ref_=nav_em__nav_desktop_sa_intl_cleaning_supplies_0_2_17_16\" class=\"hmenu-item\">Cleaning Supplies</a></li>\n  <li class=\"hmenu-separator\"></li>\n</ul>\n\n<ul class=\"hmenu hmenu-translateX-right\" data-menu-id=\"18\" data-parent-menu-id=\"1\">\n  <li><a href=\"/\" class=\"hmenu-item hmenu-back-button\" aria-label=\"Back to main menu\" data-ref-tag=\"nav_em_1_18_BT_0_main_menu\"><div style=\"align-items: center;\"><i class=\"nav-sprite hmenu-arrow-prev\"></i>main menu</div></a></li>\n  <li><div class=\"hmenu-item hmenu-title \">industrial and scientific</div></li><li><a href=\"/s?bbn=16225012011&rh=i%3Aspecialty-aps%2Cn%3A%2116225012011%2Cn%3A256167011&ref_=nav_em__nav_desktop_sa_intl_abrasive_and_finishing_products_0_2_18_2\" class=\"hmenu-item\">Abrasive & Finishing Products</a></li><li><a href=\"/s?bbn=16225012011&rh=i%3Aspecialty-aps%2Cn%3A%2116225012011%2Cn%3A6066126011&ref_=nav_em__nav_desktop_sa_intl_additive_manufacturing_products_0_2_18_3\" class=\"hmenu-item\">Additive Manufacturing Products</a></li><li><a href=\"/s?bbn=16225012011&rh=i%3Aspecialty-aps%2Cn%3A%2116225012011%2Cn%3A10773802011&ref_=nav_em__nav_desktop_sa_intl_commercial_door_products_0_2_18_4\" class=\"hmenu-item\">Commercial Door Products</a></li><li><a href=\"/s?bbn=16225012011&rh=i%3Aspecialty-aps%2Cn%3A%2116225012011%2Cn%3A383598011&ref_=nav_em__nav_desktop_sa_intl_cutting_tools_0_2_18_5\" class=\"hmenu-item\">Cutting Tools</a></li><li><a href=\"/s?bbn=16225012011&rh=i%3Aspecialty-aps%2Cn%3A%2116225012011%2Cn%3A383599011&ref_=nav_em__nav_desktop_sa_intl_fasteners_0_2_18_6\" class=\"hmenu-item\">Fasteners</a></li><li><a href=\"/s?bbn=16225012011&rh=i%3Aspecialty-aps%2Cn%3A%2116225012011%2Cn%3A3061625011&ref_=nav_em__nav_desktop_sa_intl_filtration_0_2_18_7\" class=\"hmenu-item\">Filtration</a></li><li><a href=\"/s?bbn=16225012011&rh=i%3Aspecialty-aps%2Cn%3A%2116225012011%2Cn%3A6054382011&ref_=nav_em__nav_desktop_sa_intl_food_service_equipment_and_supplies_0_2_18_8\" class=\"hmenu-item\">Food Service Equipment & Supplies</a></li><li><a href=\"/s?bbn=16225012011&rh=i%3Aspecialty-aps%2Cn%3A%2116225012011%2Cn%3A3021479011&ref_=nav_em__nav_desktop_sa_intl_hydraulics_pneumatics_and_plumbing_0_2_18_9\" class=\"hmenu-item\">Hydraulics, Pneumatics & Plumbing</a></li><li><a href=\"/s?bbn=16225012011&rh=i%3Aspecialty-aps%2Cn%3A%2116225012011%2Cn%3A306506011&ref_=nav_em__nav_desktop_sa_intl_industrial_electrical_0_2_18_10\" class=\"hmenu-item\">Industrial Electrical</a></li><li><a href=\"/s?bbn=16225012011&rh=i%3Aspecialty-aps%2Cn%3A%2116225012011%2Cn%3A16412251&ref_=nav_em__nav_desktop_sa_intl_industrial_hardware_0_2_18_11\" class=\"hmenu-item\">Industrial Hardware</a></li><li><a href=\"/s?bbn=16225012011&rh=i%3Aspecialty-aps%2Cn%3A%2116225012011%2Cn%3A3021459011&ref_=nav_em__nav_desktop_sa_intl_industrial_power_and_hand_tools_0_2_18_12\" class=\"hmenu-item\">Industrial Power & Hand Tools</a></li><li><a href=\"/s?bbn=16225012011&rh=i%3Aspecialty-aps%2Cn%3A%2116225012011%2Cn%3A317971011&ref_=nav_em__nav_desktop_sa_intl_janitorial_and_sanitation_supplies_0_2_18_13\" class=\"hmenu-item\">Janitorial & Sanitation Supplies</a></li><li><a href=\"/s?bbn=16225012011&rh=i%3Aspecialty-aps%2Cn%3A%2116225012011%2Cn%3A317970011&ref_=nav_em__nav_desktop_sa_intl_lab_and_scientific_products_0_2_18_14\" class=\"hmenu-item\">Lab & Scientific Products</a></li><li><a href=\"/s?bbn=16225012011&rh=i%3Aspecialty-aps%2Cn%3A%2116225012011%2Cn%3A256346011&ref_=nav_em__nav_desktop_sa_intl_material_handling_products_0_2_18_15\" class=\"hmenu-item\">Material Handling Products</a></li><li><a href=\"/s?bbn=16225012011&rh=i%3Aspecialty-aps%2Cn%3A%2116225012011%2Cn%3A318135011&ref_=nav_em__nav_desktop_sa_intl_occupational_health_and_safety_products_0_2_18_16\" class=\"hmenu-item\">Occupational Health & Safety Products</a></li><li><a href=\"/s?bbn=16225012011&rh=i%3Aspecialty-aps%2Cn%3A%2116225012011%2Cn%3A8553197011&ref_=nav_em__nav_desktop_sa_intl_packaging_and_shipping_supplies_0_2_18_17\" class=\"hmenu-item\">Packaging & Shipping Supplies</a></li><li><a href=\"/s?bbn=16225012011&rh=i%3Aspecialty-aps%2Cn%3A%2116225012011%2Cn%3A16310181&ref_=nav_em__nav_desktop_sa_intl_power_transmission_products_0_2_18_18\" class=\"hmenu-item\">Power Transmission Products</a></li><li><a href=\"/s?bbn=16225012011&rh=i%3Aspecialty-aps%2Cn%3A%2116225012011%2Cn%3A8297371011&ref_=nav_em__nav_desktop_sa_intl_professional_dental_supplies_0_2_18_19\" class=\"hmenu-item\">Professional Dental Supplies</a></li><li><a href=\"/s?bbn=16225012011&rh=i%3Aspecialty-aps%2Cn%3A%2116225012011%2Cn%3A8297370011&ref_=nav_em__nav_desktop_sa_intl_professional_medical_supplies_0_2_18_20\" class=\"hmenu-item\">Professional Medical Supplies</a></li><li><a href=\"/s?bbn=16225012011&rh=i%3Aspecialty-aps%2Cn%3A%2116225012011%2Cn%3A16310191&ref_=nav_em__nav_desktop_sa_intl_raw_materials_0_2_18_21\" class=\"hmenu-item\">Raw Materials</a></li><li><a href=\"/s?bbn=16225012011&rh=i%3Aspecialty-aps%2Cn%3A%2116225012011%2Cn%3A8615538011&ref_=nav_em__nav_desktop_sa_intl_retail_store_fixtures_and_equipment_0_2_18_22\" class=\"hmenu-item\">Retail Store Fixtures & Equipment</a></li><li><a href=\"/s?bbn=16225012011&rh=i%3Aspecialty-aps%2Cn%3A%2116225012011%2Cn%3A8498884011&ref_=nav_em__nav_desktop_sa_intl_robotics_0_2_18_23\" class=\"hmenu-item\">Robotics</a></li><li><a href=\"/s?bbn=16225012011&rh=i%3Aspecialty-aps%2Cn%3A%2116225012011%2Cn%3A393459011&ref_=nav_em__nav_desktop_sa_intl_science_education_0_2_18_24\" class=\"hmenu-item\">Science Education</a></li><li><a href=\"/s?bbn=16225012011&rh=i%3Aspecialty-aps%2Cn%3A%2116225012011%2Cn%3A256225011&ref_=nav_em__nav_desktop_sa_intl_tapes_adhesives_and_sealants_0_2_18_25\" class=\"hmenu-item\">Tapes, Adhesives & Sealants</a></li><li><a href=\"/s?bbn=16225012011&rh=i%3Aspecialty-aps%2Cn%3A%2116225012011%2Cn%3A256409011&ref_=nav_em__nav_desktop_sa_intl_test_measure_and_inspect_0_2_18_26\" class=\"hmenu-item\">Test, Measure & Inspect</a></li>\n  <li class=\"hmenu-separator\"></li>\n</ul>\n\n<ul class=\"hmenu hmenu-translateX-right\" data-menu-id=\"19\" data-parent-menu-id=\"1\">\n  <li><a href=\"/\" class=\"hmenu-item hmenu-back-button\" aria-label=\"Back to main menu\" data-ref-tag=\"nav_em_1_19_BT_0_main_menu\"><div style=\"align-items: center;\"><i class=\"nav-sprite hmenu-arrow-prev\"></i>main menu</div></a></li>\n  <li><div class=\"hmenu-item hmenu-title \">luggage</div></li><li><a href=\"/s?bbn=16225017011&rh=i%3Afashion-luggage%2Cn%3A7141123011%2Cn%3A16225017011%2Cn%3A15743251%2Cn%3A15743261&ref_=nav_em__nav_desktop_sa_intl_carry_ons_0_2_19_2\" class=\"hmenu-item\">Carry-ons</a></li><li><a href=\"/s?bbn=16225017011&rh=i%3Afashion-luggage%2Cn%3A7141123011%2Cn%3A16225017011%2Cn%3A360832011&ref_=nav_em__nav_desktop_sa_intl_backpacks_0_2_19_3\" class=\"hmenu-item\">Backpacks</a></li><li><a href=\"/s?bbn=16225017011&rh=i%3Afashion-luggage%2Cn%3A7141123011%2Cn%3A16225017011%2Cn%3A15743251%2Cn%3A15743271&ref_=nav_em__nav_desktop_sa_intl_garment_bags_0_2_19_4\" class=\"hmenu-item\">Garment bags</a></li><li><a href=\"/s?bbn=16225017011&rh=i%3Afashion-luggage%2Cn%3A7141123011%2Cn%3A16225017011%2Cn%3A15743241&ref_=nav_em__nav_desktop_sa_intl_travel_totes_0_2_19_5\" class=\"hmenu-item\">Travel Totes</a></li><li><a href=\"/s?bbn=16225017011&rh=i%3Afashion-luggage%2Cn%3A7141123011%2Cn%3A16225017011%2Cn%3A15743251%2Cn%3A15743291&ref_=nav_em__nav_desktop_sa_intl_luggage_sets_0_2_19_6\" class=\"hmenu-item\">Luggage Sets</a></li><li><a href=\"/s?bbn=16225017011&rh=i%3Afashion-luggage%2Cn%3A7141123011%2Cn%3A16225017011%2Cn%3A9971584011&ref_=nav_em__nav_desktop_sa_intl_laptop_bags_0_2_19_7\" class=\"hmenu-item\">Laptop Bags</a></li><li><a href=\"/s?bbn=16225017011&rh=i%3Afashion-luggage%2Cn%3A7141123011%2Cn%3A16225017011%2Cn%3A15743251%2Cn%3A2477388011&ref_=nav_em__nav_desktop_sa_intl_suitcases_0_2_19_8\" class=\"hmenu-item\">Suitcases</a></li><li><a href=\"/s?bbn=16225017011&rh=i%3Afashion-luggage%2Cn%3A7141123011%2Cn%3A16225017011%2Cn%3A15743251%2Cn%3A2477386011&ref_=nav_em__nav_desktop_sa_intl_kids_luggage_0_2_19_9\" class=\"hmenu-item\">Kids Luggage</a></li><li><a href=\"/s?bbn=16225017011&rh=i%3Afashion-luggage%2Cn%3A7141123011%2Cn%3A16225017011%2Cn%3A15743231&ref_=nav_em__nav_desktop_sa_intl_messenger_bags_0_2_19_10\" class=\"hmenu-item\">Messenger Bags</a></li><li><a href=\"/s?bbn=16225017011&rh=i%3Afashion-luggage%2Cn%3A7141123011%2Cn%3A16225017011%2Cn%3A15744111&ref_=nav_em__nav_desktop_sa_intl_umbrellas_0_2_19_11\" class=\"hmenu-item\">Umbrellas</a></li><li><a href=\"/s?bbn=16225017011&rh=i%3Afashion-luggage%2Cn%3A7141123011%2Cn%3A16225017011%2Cn%3A15743211&ref_=nav_em__nav_desktop_sa_intl_duffles_0_2_19_12\" class=\"hmenu-item\">Duffles</a></li><li><a href=\"/s?bbn=16225017011&rh=i%3Afashion-luggage%2Cn%3A7141123011%2Cn%3A16225017011%2Cn%3A15743971&ref_=nav_em__nav_desktop_sa_intl_travel_accessories_0_2_19_13\" class=\"hmenu-item\">Travel Accessories</a></li>\n  <li class=\"hmenu-separator\"></li>\n</ul>\n\n<ul class=\"hmenu hmenu-translateX-right\" data-menu-id=\"20\" data-parent-menu-id=\"1\">\n  <li><a href=\"/\" class=\"hmenu-item hmenu-back-button\" aria-label=\"Back to main menu\" data-ref-tag=\"nav_em_1_20_BT_0_main_menu\"><div style=\"align-items: center;\"><i class=\"nav-sprite hmenu-arrow-prev\"></i>main menu</div></a></li>\n  <li><div class=\"hmenu-item hmenu-title \">movies & television</div></li><li><a href=\"/gp/browse.html?node=2649512011&ref_=nav_em__nav_desktop_sa_intl_movies_0_2_20_2\" class=\"hmenu-item\">Movies</a></li><li><a href=\"/gp/browse.html?node=2649513011&ref_=nav_em__nav_desktop_sa_intl_tv_shows_0_2_20_3\" class=\"hmenu-item\">TV Shows</a></li><li><a href=\"/gp/browse.html?node=2901953011&ref_=nav_em__nav_desktop_sa_intl_blu_ray_0_2_20_4\" class=\"hmenu-item\">Blu-ray</a></li><li><a href=\"/gp/browse.html?node=11598814011&ref_=nav_em__nav_desktop_sa_intl_4k_ultra_hd_0_2_20_5\" class=\"hmenu-item\">4K Ultra HD</a></li><li><a href=\"/best-sellers-movies-TV-DVD-Blu-ray/zgbs/movies-tv/?ref_=nav_em_MoviesHP_H1_BestSellers_0_2_20_6\" class=\"hmenu-item\">Best Sellers</a></li><li><a href=\"/gp/browse.html?node=2921749011&ref_=nav_em__nav_desktop_sa_intl_todays_deals_0_2_20_7\" class=\"hmenu-item\">Today's Deals</a></li><li><a href=\"/gp/browse.html?node=2921748011&ref_=nav_em__nav_desktop_sa_intl_new_releases_0_2_20_8\" class=\"hmenu-item\">New Releases</a></li><li><a href=\"/gp/browse.html?node=7353051011&ref_=nav_em__nav_desktop_sa_intl_pre_orders_0_2_20_9\" class=\"hmenu-item\">Pre-orders</a></li><li><a href=\"/gp/browse.html?node=2650365011&ref_=nav_em__nav_desktop_sa_intl_kids_and_family_0_2_20_10\" class=\"hmenu-item\">Kids & Family</a></li><li><a href=\"/gp/browse.html?node=2858778011&ref_=nav_em__nav_desktop_sa_intl_prime_video_0_2_20_11\" class=\"hmenu-item\">Prime Video</a></li>\n  <li class=\"hmenu-separator\"></li>\n</ul>\n\n<ul class=\"hmenu hmenu-translateX-right\" data-menu-id=\"21\" data-parent-menu-id=\"1\">\n  <li><a href=\"/\" class=\"hmenu-item hmenu-back-button\" aria-label=\"Back to main menu\" data-ref-tag=\"nav_em_1_21_BT_0_main_menu\"><div style=\"align-items: center;\"><i class=\"nav-sprite hmenu-arrow-prev\"></i>main menu</div></a></li>\n  <li><div class=\"hmenu-item hmenu-title \">pet supplies</div></li><li><a href=\"/s?bbn=16225013011&rh=i%3Aspecialty-aps%2Cn%3A%2116225013011%2Cn%3A2975312011&ref_=nav_em__nav_desktop_sa_intl_dogs_0_2_21_2\" class=\"hmenu-item\">Dogs</a></li><li><a href=\"/s?bbn=16225013011&rh=i%3Aspecialty-aps%2Cn%3A%2116225013011%2Cn%3A2975241011&ref_=nav_em__nav_desktop_sa_intl_cats_0_2_21_3\" class=\"hmenu-item\">Cats</a></li><li><a href=\"/s?bbn=16225013011&rh=i%3Aspecialty-aps%2Cn%3A%2116225013011%2Cn%3A2975446011&ref_=nav_em__nav_desktop_sa_intl_fish_and_acquatic_pets_0_2_21_4\" class=\"hmenu-item\">Fish & Aquatic Pets</a></li><li><a href=\"/s?bbn=16225013011&rh=i%3Aspecialty-aps%2Cn%3A%2116225013011%2Cn%3A2975221011&ref_=nav_em__nav_desktop_sa_intl_birds_0_2_21_5\" class=\"hmenu-item\">Birds</a></li><li><a href=\"/s?bbn=16225013011&rh=i%3Aspecialty-aps%2Cn%3A%2116225013011%2Cn%3A2975481011&ref_=nav_em__nav_desktop_sa_intl_horses_0_2_21_6\" class=\"hmenu-item\">Horses</a></li><li><a href=\"/s?bbn=16225013011&rh=i%3Aspecialty-aps%2Cn%3A%2116225013011%2Cn%3A2975504011&ref_=nav_em__nav_desktop_sa_intl_reptiles_and_amphibians_0_2_21_7\" class=\"hmenu-item\">Reptiles & Amphibians</a></li><li><a href=\"/s?bbn=16225013011&rh=i%3Aspecialty-aps%2Cn%3A%2116225013011%2Cn%3A2975520011&ref_=nav_em__nav_desktop_sa_intl_small_animals_0_2_21_8\" class=\"hmenu-item\">Small Animals</a></li>\n  <li class=\"hmenu-separator\"></li>\n</ul>\n\n<ul class=\"hmenu hmenu-translateX-right\" data-menu-id=\"22\" data-parent-menu-id=\"1\">\n  <li><a href=\"/\" class=\"hmenu-item hmenu-back-button\" aria-label=\"Back to main menu\" data-ref-tag=\"nav_em_1_22_BT_0_main_menu\"><div style=\"align-items: center;\"><i class=\"nav-sprite hmenu-arrow-prev\"></i>main menu</div></a></li>\n  <li><div class=\"hmenu-item hmenu-title \">software</div></li><li><a href=\"/s?bbn=16225008011&rh=i%3Aspecialty-aps%2Cn%3A%2116225008011%2Cn%3A5223260011&ref_=nav_em__nav_desktop_sa_intl_accounting_and_finance_0_2_22_2\" class=\"hmenu-item\">Accounting & Finance</a></li><li><a href=\"/s?bbn=16225008011&rh=i%3Aspecialty-aps%2Cn%3A%2116225008011%2Cn%3A229677&ref_=nav_em__nav_desktop_sa_intl_antivirus_security_0_2_22_3\" class=\"hmenu-item\">Antivirus & Security</a></li><li><a href=\"/s?bbn=16225008011&rh=i%3Aspecialty-aps%2Cn%3A%2116225008011%2Cn%3A229535&ref_=nav_em__nav_desktop_sa_intl_business_office_0_2_22_4\" class=\"hmenu-item\">Business & Office</a></li><li><a href=\"/s?bbn=16225008011&rh=i%3Aspecialty-aps%2Cn%3A%2116225008011%2Cn%3A229548&ref_=nav_em__nav_desktop_sa_intl_childrens_0_2_22_5\" class=\"hmenu-item\">Children's</a></li><li><a href=\"/s?bbn=16225008011&rh=i%3Aspecialty-aps%2Cn%3A%2116225008011%2Cn%3A229614&ref_=nav_em__nav_desktop_sa_intl_design_illustration_0_2_22_6\" class=\"hmenu-item\">Design & Illustration</a></li><li><a href=\"/s?bbn=16225008011&rh=i%3Aspecialty-aps%2Cn%3A%2116225008011%2Cn%3A1233514011&ref_=nav_em__nav_desktop_sa_intl_digital_software_0_2_22_7\" class=\"hmenu-item\">Digital Software</a></li><li><a href=\"/s?bbn=16225008011&rh=i%3Aspecialty-aps%2Cn%3A%2116225008011%2Cn%3A229563&ref_=nav_em__nav_desktop_sa_intl_education_reference_0_2_22_8\" class=\"hmenu-item\">Education & Reference</a></li><li><a href=\"/s?bbn=16225008011&rh=i%3Aspecialty-aps%2Cn%3A%2116225008011%2Cn%3A1294826011&ref_=nav_em__nav_desktop_sa_intl_games_0_2_22_9\" class=\"hmenu-item\">Games</a></li><li><a href=\"/s?bbn=16225008011&rh=i%3Aspecialty-aps%2Cn%3A%2116225008011%2Cn%3A229624&ref_=nav_em__nav_desktop_sa_intl_lifestyle_hobbies_0_2_22_10\" class=\"hmenu-item\">Lifestyle & Hobbies</a></li><li><a href=\"/s?bbn=16225008011&rh=i%3Aspecialty-aps%2Cn%3A%2116225008011%2Cn%3A497022&ref_=nav_em__nav_desktop_sa_intl_music_0_2_22_11\" class=\"hmenu-item\">Music</a></li><li><a href=\"/s?bbn=16225008011&rh=i%3Aspecialty-aps%2Cn%3A%2116225008011%2Cn%3A229637&ref_=nav_em__nav_desktop_sa_intl_networking_services_0_2_22_12\" class=\"hmenu-item\">Networking & Servers</a></li><li><a href=\"/s?bbn=16225008011&rh=i%3Aspecialty-aps%2Cn%3A%2116225008011%2Cn%3A229653&ref_=nav_em__nav_desktop_sa_intl_operating_systems_0_2_22_13\" class=\"hmenu-item\">Operating Systems</a></li><li><a href=\"/s?bbn=16225008011&rh=i%3Aspecialty-aps%2Cn%3A%2116225008011%2Cn%3A229621&ref_=nav_em__nav_desktop_sa_intl_photography_0_2_22_14\" class=\"hmenu-item\">Photography</a></li><li><a href=\"/s?bbn=16225008011&rh=i%3Aspecialty-aps%2Cn%3A%2116225008011%2Cn%3A5223262011&ref_=nav_em__nav_desktop_sa_intl_programming_web_development_0_2_22_15\" class=\"hmenu-item\">Programming & Web Development</a></li><li><a href=\"/s?bbn=16225008011&rh=i%3Aspecialty-aps%2Cn%3A%2116225008011%2Cn%3A229545&ref_=nav_em__nav_desktop_sa_intl_tax_preparation_0_2_22_16\" class=\"hmenu-item\">Tax Preparation</a></li><li><a href=\"/s?bbn=16225008011&rh=i%3Aspecialty-aps%2Cn%3A%2116225008011%2Cn%3A229672&ref_=nav_em__nav_desktop_sa_intl_utilities_0_2_22_17\" class=\"hmenu-item\">Utilities</a></li><li><a href=\"/s?bbn=16225008011&rh=i%3Aspecialty-aps%2Cn%3A%2116225008011%2Cn%3A290542&ref_=nav_em__nav_desktop_sa_intl_video_0_2_22_18\" class=\"hmenu-item\">Video</a></li>\n  <li class=\"hmenu-separator\"></li>\n</ul>\n\n<ul class=\"hmenu hmenu-translateX-right\" data-menu-id=\"23\" data-parent-menu-id=\"1\">\n  <li><a href=\"/\" class=\"hmenu-item hmenu-back-button\" aria-label=\"Back to main menu\" data-ref-tag=\"nav_em_1_23_BT_0_main_menu\"><div style=\"align-items: center;\"><i class=\"nav-sprite hmenu-arrow-prev\"></i>main menu</div></a></li>\n  <li><div class=\"hmenu-item hmenu-title \">sports and outdoors</div></li><li><a href=\"/gp/browse.html?node=16225014011&ref_=nav_em__nav_desktop_sa_intl_sports_and_outdoors_0_2_23_2\" class=\"hmenu-item\">Sports and Outdoors</a></li><li><a href=\"/s?bbn=16225014011&rh=i%3Aspecialty-aps%2Cn%3A%2116225014011%2Cn%3A706814011&ref_=nav_em__nav_desktop_sa_intl_outdoor_recreations_0_2_23_3\" class=\"hmenu-item\">Outdoor Recreation</a></li><li><a href=\"/s?bbn=16225014011&rh=i%3Aspecialty-aps%2Cn%3A%2116225014011%2Cn%3A10971181011&ref_=nav_em__nav_desktop_sa_intl_sports_fitness_0_2_23_4\" class=\"hmenu-item\">Sports & Fitness</a></li>\n  <li class=\"hmenu-separator\"></li>\n</ul>\n\n<ul class=\"hmenu hmenu-translateX-right\" data-menu-id=\"24\" data-parent-menu-id=\"1\">\n  <li><a href=\"/\" class=\"hmenu-item hmenu-back-button\" aria-label=\"Back to main menu\" data-ref-tag=\"nav_em_1_24_BT_0_main_menu\"><div style=\"align-items: center;\"><i class=\"nav-sprite hmenu-arrow-prev\"></i>main menu</div></a></li>\n  <li><div class=\"hmenu-item hmenu-title \">tools & home improvement</div></li><li><a href=\"/gp/browse.html?node=256643011&ref_=nav_em__nav_desktop_sa_intl_tools_and_home_improvement_0_2_24_2\" class=\"hmenu-item\">Tools & Home Improvement</a></li><li><a href=\"/s?bbn=256643011&rh=i%3Aspecialty-aps%2Cn%3A256643011%2Cn%3A%21468240%2Cn%3A13397451&ref_=nav_em__nav_desktop_sa_intl_appliances_0_2_24_3\" class=\"hmenu-item\">Appliances</a></li><li><a href=\"/s?bbn=256643011&rh=i%3Aspecialty-aps%2Cn%3A256643011%2Cn%3A%21468240%2Cn%3A551240&ref_=nav_em__nav_desktop_sa_intl_building_supplies_0_2_24_4\" class=\"hmenu-item\">Building Supplies</a></li><li><a href=\"/s?bbn=256643011&rh=i%3Aspecialty-aps%2Cn%3A256643011%2Cn%3A%21468240%2Cn%3A495266&ref_=nav_em__nav_desktop_sa_intl_electrical_0_2_24_5\" class=\"hmenu-item\">Electrical</a></li><li><a href=\"/s?bbn=256643011&rh=i%3Aspecialty-aps%2Cn%3A256643011%2Cn%3A%21468240%2Cn%3A511228&ref_=nav_em__nav_desktop_sa_intl_hardware_0_2_24_6\" class=\"hmenu-item\">Hardware</a></li><li><a href=\"/s?bbn=256643011&rh=i%3Aspecialty-aps%2Cn%3A256643011%2Cn%3A%21468240%2Cn%3A3754161&ref_=nav_em__nav_desktop_sa_intl_kitchen_bath_fixtures_0_2_24_7\" class=\"hmenu-item\">Kitchen & Bath Fixtures</a></li><li><a href=\"/s?bbn=256643011&rh=i%3Aspecialty-aps%2Cn%3A256643011%2Cn%3A%21468240%2Cn%3A322525011&ref_=nav_em__nav_desktop_sa_intl_light_bulbs_0_2_24_8\" class=\"hmenu-item\">Light Bulbs</a></li><li><a href=\"/s?bbn=256643011&rh=i%3Aspecialty-aps%2Cn%3A256643011%2Cn%3A%21468240%2Cn%3A495224&ref_=nav_em__nav_desktop_sa_intl_lighting_ceilling_fans_0_2_24_9\" class=\"hmenu-item\">Lighting & Ceiling Fans</a></li><li><a href=\"/s?bbn=256643011&rh=i%3Aspecialty-aps%2Cn%3A256643011%2Cn%3A%21468240%2Cn%3A553244&ref_=nav_em__nav_desktop_sa_intl_measuring_layout_tools_0_2_24_10\" class=\"hmenu-item\">Measuring & Layout Tools</a></li><li><a href=\"/s?bbn=256643011&rh=i%3Aspecialty-aps%2Cn%3A256643011%2Cn%3A%21468240%2Cn%3A228899&ref_=nav_em__nav_desktop_sa_intl_painting_supplies_wall_treatment_0_2_24_11\" class=\"hmenu-item\">Painting Supplies & Wall Treatments</a></li><li><a href=\"/s?bbn=256643011&rh=i%3Aspecialty-aps%2Cn%3A256643011%2Cn%3A%21468240%2Cn%3A328182011&ref_=nav_em__nav_desktop_sa_intl_power_hand_tools_0_2_24_12\" class=\"hmenu-item\">Power & Hand Tools</a></li><li><a href=\"/s?bbn=256643011&rh=i%3Aspecialty-aps%2Cn%3A256643011%2Cn%3A%21468240%2Cn%3A13749581&ref_=nav_em__nav_desktop_sa_intl_rough_plumbing_0_2_24_13\" class=\"hmenu-item\">Rough Plumbing</a></li><li><a href=\"/s?bbn=256643011&rh=i%3Aspecialty-aps%2Cn%3A256643011%2Cn%3A%21468240%2Cn%3A3180231&ref_=nav_em__nav_desktop_sa_intl_safety_security_0_2_24_14\" class=\"hmenu-item\">Safety & Security</a></li><li><a href=\"/s?bbn=256643011&rh=i%3Aspecialty-aps%2Cn%3A256643011%2Cn%3A%21468240%2Cn%3A13400631&ref_=nav_em__nav_desktop_sa_intl_storage_home_organization_0_2_24_15\" class=\"hmenu-item\">Storage & Home Organization</a></li><li><a href=\"/s?bbn=256643011&rh=i%3Aspecialty-aps%2Cn%3A256643011%2Cn%3A%21468240%2Cn%3A8106310011&ref_=nav_em__nav_desktop_sa_intl_welding_soldering_0_2_24_16\" class=\"hmenu-item\">Welding & Soldering</a></li>\n  <li class=\"hmenu-separator\"></li>\n</ul>\n\n<ul class=\"hmenu hmenu-translateX-right\" data-menu-id=\"25\" data-parent-menu-id=\"1\">\n  <li><a href=\"/\" class=\"hmenu-item hmenu-back-button\" aria-label=\"Back to main menu\" data-ref-tag=\"nav_em_1_25_BT_0_main_menu\"><div style=\"align-items: center;\"><i class=\"nav-sprite hmenu-arrow-prev\"></i>main menu</div></a></li>\n  <li><div class=\"hmenu-item hmenu-title \">toys and games</div></li><li><a href=\"/s?bbn=16225015011&rh=i%3Aspecialty-aps%2Cn%3A%2116225015011%2Cn%3A165993011&ref_=nav_em__nav_desktop_sa_intl_action_figures_statues_0_2_25_2\" class=\"hmenu-item\">Action Figures & Statues</a></li><li><a href=\"/s?bbn=16225015011&rh=i%3Aspecialty-aps%2Cn%3A%2116225015011%2Cn%3A166057011&ref_=nav_em__nav_desktop_sa_intl_arts_craft_0_2_25_3\" class=\"hmenu-item\">Arts & Crafts</a></li><li><a href=\"/s?bbn=16225015011&rh=i%3Aspecialty-aps%2Cn%3A%2116225015011%2Cn%3A196601011&ref_=nav_em__nav_desktop_sa_intl_baby_toddler_toys_0_2_25_4\" class=\"hmenu-item\">Baby & Toddler Toys</a></li><li><a href=\"/s?bbn=16225015011&rh=i%3Aspecialty-aps%2Cn%3A%2116225015011%2Cn%3A166092011&ref_=nav_em__nav_desktop_sa_intl_building_toys_0_2_25_5\" class=\"hmenu-item\">Building Toys</a></li><li><a href=\"/s?bbn=16225015011&rh=i%3Aspecialty-aps%2Cn%3A%2116225015011%2Cn%3A166118011&ref_=nav_em__nav_desktop_sa_intl_dolls_accessories_0_2_25_6\" class=\"hmenu-item\">Dolls & Accessories</a></li><li><a href=\"/s?bbn=16225015011&rh=i%3Aspecialty-aps%2Cn%3A%2116225015011%2Cn%3A166316011&ref_=nav_em__nav_desktop_sa_intl_dress_up_pretend_play_0_2_25_7\" class=\"hmenu-item\">Dress Up & Pretend Play</a></li><li><a href=\"/s?bbn=16225015011&rh=i%3Aspecialty-aps%2Cn%3A%2116225015011%2Cn%3A166164011&ref_=nav_em__nav_desktop_sa_intl_kids_electronics_0_2_25_8\" class=\"hmenu-item\">Kids' Electronics</a></li><li><a href=\"/s?bbn=16225015011&rh=i%3Aspecialty-aps%2Cn%3A%2116225015011%2Cn%3A166220011&ref_=nav_em__nav_desktop_sa_intl_games_0_2_25_9\" class=\"hmenu-item\">Games</a></li><li><a href=\"/s?bbn=16225015011&rh=i%3Aspecialty-aps%2Cn%3A%2116225015011%2Cn%3A3226142011&ref_=nav_em__nav_desktop_sa_intl_grown_up_toys_0_2_25_10\" class=\"hmenu-item\">Grown-Up Toys</a></li><li><a href=\"/s?bbn=16225015011&rh=i%3Aspecialty-aps%2Cn%3A%2116225015011%2Cn%3A276729011&ref_=nav_em__nav_desktop_sa_intl_hobbies_0_2_25_11\" class=\"hmenu-item\">Hobbies</a></li><li><a href=\"/s?bbn=16225015011&rh=i%3Aspecialty-aps%2Cn%3A%2116225015011%2Cn%3A166210011&ref_=nav_em__nav_desktop_sa_intl_kids_furniture_decor_storage_0_2_25_12\" class=\"hmenu-item\">Kids' Furniture, Décor & Storage</a></li><li><a href=\"/s?bbn=16225015011&rh=i%3Aspecialty-aps%2Cn%3A%2116225015011%2Cn%3A166269011&ref_=nav_em__nav_desktop_sa_intl_learning_education_0_2_25_13\" class=\"hmenu-item\">Learning & Education</a></li><li><a href=\"/s?bbn=16225015011&rh=i%3Aspecialty-aps%2Cn%3A%2116225015011%2Cn%3A166027011&ref_=nav_em__nav_desktop_sa_intl_novelty_gag_toys_0_2_25_14\" class=\"hmenu-item\">Novelty & Gag Toys</a></li><li><a href=\"/s?bbn=16225015011&rh=i%3Aspecialty-aps%2Cn%3A%2116225015011%2Cn%3A1266203011&ref_=nav_em__nav_desktop_sa_intl_party_supplies_0_2_25_15\" class=\"hmenu-item\">Party Supplies</a></li><li><a href=\"/s?bbn=16225015011&rh=i%3Aspecialty-aps%2Cn%3A%2116225015011%2Cn%3A166333011&ref_=nav_em__nav_desktop_sa_intl_novelty_gag_toys_0_2_25_16\" class=\"hmenu-item\">Puppets</a></li><li><a href=\"/s?bbn=16225015011&rh=i%3Aspecialty-aps%2Cn%3A%2116225015011%2Cn%3A166359011&ref_=nav_em__nav_desktop_sa_intl_puzzles_0_2_25_17\" class=\"hmenu-item\">Puzzles</a></li><li><a href=\"/s?bbn=16225015011&rh=i%3Aspecialty-aps%2Cn%3A%2116225015011%2Cn%3A166420011&ref_=nav_em__nav_desktop_sa_intl_sports_outdoor_play_0_2_25_18\" class=\"hmenu-item\">Sports & Outdoor Play</a></li><li><a href=\"/s?bbn=16225015011&rh=i%3Aspecialty-aps%2Cn%3A%2116225015011%2Cn%3A166461011&ref_=nav_em__nav_desktop_sa_intl_stuffed_animals_plush_toys_0_2_25_19\" class=\"hmenu-item\">Stuffed Animals & Plush Toys</a></li><li><a href=\"/s?bbn=16225015011&rh=i%3Aspecialty-aps%2Cn%3A%2116225015011%2Cn%3A166508011&ref_=nav_em__nav_desktop_sa_intl_toy_remote_control_play_vehicles_0_2_25_20\" class=\"hmenu-item\">Toy Remote Control & Play Vehicles</a></li><li><a href=\"/s?bbn=16225015011&rh=i%3Aspecialty-aps%2Cn%3A%2116225015011%2Cn%3A256994011&ref_=nav_em__nav_desktop_sa_intl_tricycles_scooters_wagons_0_2_25_21\" class=\"hmenu-item\">Tricycles, Scooters & Wagons</a></li><li><a href=\"/s?bbn=16225015011&rh=i%3Aspecialty-aps%2Cn%3A%2116225015011%2Cn%3A8794716011&ref_=nav_em__nav_desktop_sa_intl_video_games_0_2_25_22\" class=\"hmenu-item\">Video Games</a></li>\n  <li class=\"hmenu-separator\"></li>\n</ul>\n\n<ul class=\"hmenu hmenu-translateX-right\" data-menu-id=\"26\" data-parent-menu-id=\"1\">\n  <li><a href=\"/\" class=\"hmenu-item hmenu-back-button\" aria-label=\"Back to main menu\" data-ref-tag=\"nav_em_1_26_BT_0_main_menu\"><div style=\"align-items: center;\"><i class=\"nav-sprite hmenu-arrow-prev\"></i>main menu</div></a></li>\n  <li><div class=\"hmenu-item hmenu-title \">video games</div></li><li><a href=\"/gp/browse.html?node=16225016011&ref_=nav_em__nav_desktop_sa_intl_video_games_0_2_26_2\" class=\"hmenu-item\">Video Games</a></li><li><a href=\"/s?bbn=16225016011&rh=i%3Aspecialty-aps%2Cn%3A%2116225016011%2Cn%3A6427814011&ref_=nav_em__nav_desktop_sa_intl_playstation4_0_2_26_3\" class=\"hmenu-item\">PlayStation 4</a></li><li><a href=\"/s?bbn=16225016011&rh=i%3Aspecialty-aps%2Cn%3A%2116225016011%2Cn%3A14210751&ref_=nav_em__nav_desktop_sa_intl_playstation3_0_2_26_4\" class=\"hmenu-item\">PlayStation 3</a></li><li><a href=\"/s?bbn=16225016011&rh=i%3Aspecialty-aps%2Cn%3A%2116225016011%2Cn%3A6469269011&ref_=nav_em__nav_desktop_sa_intl_xbox_one_0_2_26_5\" class=\"hmenu-item\">Xbox One</a></li><li><a href=\"/s?bbn=16225016011&rh=i%3Aspecialty-aps%2Cn%3A%2116225016011%2Cn%3A14220161&ref_=nav_em__nav_desktop_sa_intl_xbox_360_0_2_26_6\" class=\"hmenu-item\">Xbox 360</a></li><li><a href=\"/s?bbn=16225016011&rh=i%3Aspecialty-aps%2Cn%3A%2116225016011%2Cn%3A16227128011&ref_=nav_em__nav_desktop_sa_intl_nintendo_switch_0_2_26_7\" class=\"hmenu-item\">Nintendo Switch</a></li><li><a href=\"/s?bbn=16225016011&rh=i%3Aspecialty-aps%2Cn%3A%2116225016011%2Cn%3A3075112011&ref_=nav_em__nav_desktop_sa_intl_wii_u_0_2_26_8\" class=\"hmenu-item\">Wii U</a></li><li><a href=\"/s?bbn=16225016011&rh=i%3Aspecialty-aps%2Cn%3A%2116225016011%2Cn%3A14218901&ref_=nav_em__nav_desktop_sa_intl_wii_0_2_26_9\" class=\"hmenu-item\">Wii</a></li><li><a href=\"/s?bbn=16225016011&rh=i%3Aspecialty-aps%2Cn%3A%2116225016011%2Cn%3A229575&ref_=nav_em__nav_desktop_sa_intl_pc_0_2_26_10\" class=\"hmenu-item\">PC</a></li><li><a href=\"/s?bbn=16225016011&rh=i%3Aspecialty-aps%2Cn%3A%2116225016011%2Cn%3A229647&ref_=nav_em__nav_desktop_sa_intl_mac_0_2_26_11\" class=\"hmenu-item\">Mac</a></li><li><a href=\"/s?bbn=16225016011&rh=i%3Aspecialty-aps%2Cn%3A%2116225016011%2Cn%3A2622269011&ref_=nav_em__nav_desktop_sa_intl_nintendo_3ds_2ds_0_2_26_12\" class=\"hmenu-item\">Nintendo 3DS & 2DS</a></li><li><a href=\"/s?bbn=16225016011&rh=i%3Aspecialty-aps%2Cn%3A%2116225016011%2Cn%3A11075831&ref_=nav_em__nav_desktop_sa_intl_nintendo_ds_0_2_26_13\" class=\"hmenu-item\">Nintendo DS</a></li><li><a href=\"/s?bbn=16225016011&rh=i%3Aspecialty-aps%2Cn%3A%2116225016011%2Cn%3A3010556011&ref_=nav_em__nav_desktop_sa_intl_playstation_vita_0_2_26_14\" class=\"hmenu-item\">PlayStation Vita</a></li><li><a href=\"/s?bbn=16225016011&rh=i%3Aspecialty-aps%2Cn%3A%2116225016011%2Cn%3A11075221&ref_=nav_em__nav_desktop_sa_intl_sony_psp_0_2_26_15\" class=\"hmenu-item\">Sony PSP</a></li><li><a href=\"/s?bbn=16225016011&rh=i%3Aspecialty-aps%2Cn%3A%2116225016011%2Cn%3A294940&ref_=nav_em__nav_desktop_sa_intl_retro_gaming_microconsoles_0_2_26_16\" class=\"hmenu-item\">Retro Gaming & Microconsoles</a></li><li><a href=\"/s?bbn=16225016011&rh=i%3Aspecialty-aps%2Cn%3A%2116225016011%2Cn%3A471304&ref_=nav_em__nav_desktop_sa_intl_accessories_0_2_26_17\" class=\"hmenu-item\">Accessories</a></li><li><a href=\"/s?bbn=16225016011&rh=i%3Aspecialty-aps%2Cn%3A%2116225016011%2Cn%3A979455011&ref_=nav_em__nav_desktop_sa_intl_digital_games_0_2_26_18\" class=\"hmenu-item\">Digital Games</a></li><li><a href=\"/s?bbn=16225016011&rh=i%3Aspecialty-aps%2Cn%3A%2116225016011%2Cn%3A8400376011&ref_=nav_em__nav_desktop_sa_intl_kids_family_0_2_26_19\" class=\"hmenu-item\">Kids & Family</a></li>\n  <li class=\"hmenu-separator\"></li>\n</ul>\n\n<ul class=\"hmenu hmenu-translateX-right\" data-menu-id=\"27\" data-parent-menu-id=\"1\">\n  <li><a href=\"/\" class=\"hmenu-item hmenu-back-button\" aria-label=\"Back to main menu\" data-ref-tag=\"nav_em_1_27_BT_0_main_menu\"><div style=\"align-items: center;\"><i class=\"nav-sprite hmenu-arrow-prev\"></i>main menu</div></a></li>\n  <li><div class=\"hmenu-item hmenu-title \">give a gift card</div></li><li><a href=\"/gp/browse.html?node=2238192011&ref_=nav_em_hmc_gc_allgc_0_2_27_2\" class=\"hmenu-item\">All gift cards</a></li><li><a href=\"/s?bbn=2238192011&page=1&rh=n%3A2238192011%2Cp_n_format_browse-bin%3A2740964011%2Cp_89%3AAmazon&ref_=nav_em_hmc_gc_egc_0_2_27_3\" class=\"hmenu-item\">eGift cards</a></li><li><a href=\"/s?bbn=2238192011&page=1&rh=n%3A2238192011%2Cp_89%3AAmazon%2Cp_n_format_browse-bin%3A2740967011&ref_=nav_em_hmc_gc_pgc_C_0_2_27_4\" class=\"hmenu-item\">Gift cards by mail</a></li><li><a href=\"/gp/browse.html?node=2864196011&ref_=nav_em_hmc_gc_bgc_0_2_27_5\" class=\"hmenu-item\">Specialty gift cards</a></li><li><a href=\"/gp/browse.html?node=14583169011&ref_=nav_em_hmc_gc_amazoncash_0_2_27_6\" class=\"hmenu-item\">Amazon Cash</a></li><li><a href=\"/gp/browse.html?node=15243182011&ref_=nav_em_hmc_gc_incentives_0_2_27_7\" class=\"hmenu-item\">For Businesses</a></li><li class=\"hmenu-separator\"></li><li><div class=\"hmenu-item hmenu-title \">manage your gift card</div></li><li><a href=\"/gc/redeem?ref_=nav_em_hmc_gc_redeem_0_2_27_9\" class=\"hmenu-item\">Redeem a gift card</a></li><li><a href=\"/gp/css/gc/balance?ref_=nav_em_hmc_gc_viewbalance_0_2_27_10\" class=\"hmenu-item\">View Your Balance</a></li><li><a href=\"/asv/reload/order?ref_=nav_em_hmc_gc_asv_0_2_27_11\" class=\"hmenu-item\">Reload Your Balance</a></li>\n  <li class=\"hmenu-separator\"></li>\n</ul>\n\n<ul class=\"hmenu hmenu-translateX-right\" data-menu-id=\"28\" data-parent-menu-id=\"1\">\n  <li><a href=\"/\" class=\"hmenu-item hmenu-back-button\" aria-label=\"Back to main menu\" data-ref-tag=\"nav_em_1_28_BT_0_main_menu\"><div style=\"align-items: center;\"><i class=\"nav-sprite hmenu-arrow-prev\"></i>main menu</div></a></li>\n  <li><div class=\"hmenu-item hmenu-title \">amazon live</div></li><li><a href=\"/live?ref_=nav_em_sd_al_dest_0_2_28_2\" class=\"hmenu-item\">Live</a></li><li><a href=\"/live?ref_=nav_em_sd_al_dest#recently_0_2_28_3\" class=\"hmenu-item\">Recently Live</a></li>\n  <li class=\"hmenu-separator\"></li>\n</ul>\n\n<ul class=\"hmenu hmenu-translateX-right\" data-menu-id=\"29\" data-parent-menu-id=\"1\">\n  <li><a href=\"/\" class=\"hmenu-item hmenu-back-button\" aria-label=\"Back to main menu\" data-ref-tag=\"nav_em_1_29_BT_0_main_menu\"><div style=\"align-items: center;\"><i class=\"nav-sprite hmenu-arrow-prev\"></i>main menu</div></a></li>\n  <li><div class=\"hmenu-item hmenu-title \">international shopping</div></li><li><a href=\"/gp/help/customer/display.html?nodeId=201910800&ref_=nav_em_full_store_dir_AG_shipping_0_2_29_2\" class=\"hmenu-item\">Where we ship</a></li><li><a href=\"/gp/browse.html?node=17416544011&ref_=nav_em_full_store_dir_VisitAg_help_0_2_29_3\" class=\"hmenu-item\">Visit Amazon Global</a></li>\n  <li class=\"hmenu-separator\"></li>\n</ul>\n"}
    #
    # print(etree.HTML(data["data"]).xpath('//div[contains(@class, "hmenu-title")]/text()'))
    # https://www.amazon.com/s/query?bbn=16225009011&i=electronics-intl-ship&page=5&qid=1702970244&ref=sr_pg_4&rh=n%3A16225009011%2Cn%3A281407
    # url = "/s?bbn=16225015011&rh=i%3Aspecialty-aps%2Cn%3A%2116225015011%2Cn%3A165993011&ref_=nav_em__nav_desktop_sa_intl_action_figures_statues_0_2_25_2"

    # print(re.findall('rh=i%3Aspecialty-aps%2C(.*)&ref', url))

    # https://www.amazon.com/s?bbn=16225009011&rh=i%3Aspecialty-aps%2Cn%3A%2116225009011%2Cn%3A281407&ref_=nav_em__nav_desktop_sa_intl_accessories_and_supplies_0_2_5_2
    # https://www.amazon.com/s?bbn=16225009011&rh=i%3Aspecialty-aps%2Cn%3A%2116225009011%2Cn%3A281407&ref_=nav_em__nav_desktop_sa_intl_accessories_and_supplies_0_2_5_2

    amazon_csm_id = AmazonCsmId
    amazon_csm_id_value = amazon_csm_id.random_csm_id()
    amazon_init_data = AmazonInitData(amazon_csm_id_value)
    csm_init_value, other_init_value, data = amazon_init_data.get()
    amazon_handle_detail_page = AmazonHandleDetailPage(csm_init_value, other_init_value)
    amazon_menu_list_page = AmazonMenuListPage(csm_init_value, other_init_value, amazon_handle_detail_page)
    for i in data:
        amazon_menu_list_page.amazon_handle_data_start("https://www.amazon.com" + i)
