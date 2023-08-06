
from tzutil.req import requests

def url_short(url):
    api ="http://api.t.sina.com.cn/short_url/shorten.json?source=3271760578&url_long=%s"%url.replace("&","%26")
    return requests.get(api).json()[0]['url_short']

if __name__ == "__main__":
    print(url_short(
        "http://mp.weixin.qq.com/s?__biz=MjM5OTUwNjM0Mg==&mid=2650392927&idx=3&sn=c25bb0cbddf0b139819f11c389854e2b&chksm=bf37119688409880e98651e237e0d5753e0d180cdbba5d52ecc3701579f6a3c78fc2269d99f6&mpshare=1&scene=1&srcid=0712YlwjRC76EfKBDCCPRn99#rd"
    ))
