# -*- encoding：utf-8 -*-
import requests
import easyocr


class AmazonCode:
    def __init__(self):

        self.path = "verify.jpg"

    def verify_code(self, url):
        header = {
            'Accept': 'text/html, */*; q=0.01',
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/86.0.4240.198 Safari/537.36',
            'accept': 'text/html,*/*',
            'accept-encoding': 'gzip, deflate, br',
            'accept-language': 'zh-CN,zh;q=0.9'
        }

        data = requests.get(url, headers=header, verify=False)

        with open(self.path, "wb") as f:
            f.write(data.content)
            f.flush()

        f.close()

        return self.easy_code_value()

    def easy_code_value(self):
        reader = easyocr.Reader(['en'])
        result = reader.readtext(self.path)
        print(result)
        return result[0][1]