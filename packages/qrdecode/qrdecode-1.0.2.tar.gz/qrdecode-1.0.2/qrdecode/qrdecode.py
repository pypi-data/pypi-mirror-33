import requests
import json
import base64
import os


def decode(filename=''):
    url = 'https://www.yuanfudao.com/tutor-ybc-course-api-v2/api/qrcode'
    filepath = os.path.abspath(filename)
    files = {'file': open(filepath, 'rb')}
    r = requests.post(url, files=files)
    if r.status_code == 200:
        return r.text
    else:
        return '没有识别出二维码'

def main():
    print(decode('123.jpg'))
if __name__ == '__main__':
    main()
