import requests
import time


def health_Checks():
    payload = {'appname': 'gdgl', 'serviceport': '10009', 'min': '200', 'max': '400'}
    r = requests.post("http://127.0.0.1:5000/api/v1.0/autoextend", data=payload)
    print(r.text)



def auto_Extend():
    r = requests.post("http://127.0.0.1:5000/api/v1.0/flowmonitoring")
    print(r.text)
    pass



if __name__ =='__main__':
    while True:
        #health_Checks()
        auto_Extend()
        # 5秒调动一次
        time.sleep(5)
