import requests
from urllib import parse
import os

auth_proxy = 'http://localhost:8891'
kmodel = 'http://klab-public-service-1310418007.cn-north-1.elb.amazonaws.com.cn/production/kmodel'

def download(key, filepath=None):
    # filepath is key in current directory by default
    if filepath is None:
        filepath = key
    # use local proxy to auth requests
    proxies = {
        'http': auth_proxy,
    }
    r = requests.get(kmodel+'/model/get/apply/'+key, proxies=proxies)
    if r.status_code/100 != 2:
        print("unexpected status code:", r.status_code, "response:", r.text)
        return
    url = r.json()['url']
    r = requests.get(url, stream=True)
    with open(filepath, 'wb') as f:
        for chunk in r.iter_content(chunk_size=1024):
            if chunk:
                f.write(chunk)
    print("{0} download success!".format(filepath))

def upload(filepath, key=None, overwrite=False):
    # key is filepath basename by default
    if key is None:
        key = os.path.basename(filepath)
    # use local proxy to auth requests
    proxies = {
        'http': auth_proxy,
    }
    # get pre-signed url
    r = requests.get(kmodel+'/model/put/apply/' + key, proxies=proxies)
    if r.status_code/100 != 2:
        print("unexpected status code:", r.status_code, "response:", r.text)
        return
    url = r.json()['url']
    r = requests.put(url, data=open(filepath, 'rb').read())
    if r.status_code/100 != 2:
        print("unexpected status code:", r.status_code, "response:", r.text)
        return
    else:
        print("{0} upload success!".format(filepath))
        return
