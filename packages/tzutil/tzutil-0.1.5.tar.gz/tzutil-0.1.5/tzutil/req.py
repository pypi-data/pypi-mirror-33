import re
import requests
from functools import wraps
import traceback
from time import sleep
import logging
# def parse_curl_str(s):
#     """convert chrome curl string to url, headers dict and data"""
#     pat = re.compile("'(.*?)'")
#     str_list = [i.strip() for i in re.split(pat, s)]   # 拆分curl请求字符串

#     url = ''
#     headers = {}
#     data = ''

#     for i in range(0, len(str_list)-1, 2):
#         arg = str_list[i]
#         string = str_list[i+1]

#         if arg.startswith('curl'):
#             url = string

#         elif arg.startswith('-H'):
#             header_key = string.split(':', 1)[0].strip()
#             header_val = string.split(':', 1)[1].strip()
#             headers[header_key] = header_val

#         elif arg.startswith('--data'):
#             data = string

#     return url, headers, data


def retry(retries=3):
    def _retry(func):
        @wraps(func)
        def _wrapper(*args, **kwargs):
            index = 0
            while index < retries:
                index += 1
                try:
                    response = func(*args, **kwargs)
                    status_code = response.status_code
                    if status_code == 200:
                        break
                    else:
                        is_404 = status_code == 404
                        if is_404:
                            _logger = logging.warning
                        else:
                            _logger = logging.error
                        _logger('RESPONSE STATUS CODE : %s' % status_code)

                        if is_404:
                            break
                        else:
                            sleep(1)
                            continue
                except Exception as e:
                    traceback.print_exc()
                    response = None
            return response
        return _wrapper
    return _retry


_get = requests.get
_post = requests.post


def _method(get):
    @retry(5)
    def _(*args, **kwds):
        if 'timeout' not in kwds:
            kwds['timeout'] = 30
        if 'headers' not in kwds:
            kwds['headers'] = {}
        if 'User-Agent' not in kwds['headers']:
            kwds['headers'][
                'User-Agent'] = 'Mozilla/5.0 (compatible; Googlebot/2.1; +http://www.google.com/bot.html)'
        r = get(*args, **kwds)
        sleep(1)
        return r
    return _


get = _method(_get)
post = _method(_post)

requests.get = get
requests.post = post
