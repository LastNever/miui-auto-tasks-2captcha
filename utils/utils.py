"""工具类"""

import base64
import random
import string
import time
from io import BytesIO
from typing import Type, Union
from urllib.parse import parse_qsl, urlparse

from Crypto.Cipher import AES, PKCS1_v1_5
from Crypto.PublicKey import RSA
from Crypto.Util.Padding import pad
from qrcode import QRCode, constants
from tenacity import RetryError, Retrying, stop_after_attempt
from twocaptcha import TwoCaptcha

from .captcha import get_validate,get_validate_by_2captcha
from .data_model import TokenResultHandler
from .logger import log
from .request import post
from .config import ConfigManager
_conf = ConfigManager.data_obj


PUBLIC_KEY_PEM = """-----BEGIN PUBLIC KEY-----
MIIBIjANBgkqhkiG9w0BAQEFAAOCAQ8AMIIBCgKCAQEArxfNLkuAQ/BYHzkzVwtu
g+0abmYRBVCEScSzGxJIOsfxVzcuqaKO87H2o2wBcacD3bRHhMjTkhSEqxPjQ/FE
XuJ1cdbmr3+b3EQR6wf/cYcMx2468/QyVoQ7BADLSPecQhtgGOllkC+cLYN6Md34
Uii6U+VJf0p0q/saxUTZvhR2ka9fqJ4+6C6cOghIecjMYQNHIaNW+eSKunfFsXVU
+QfMD0q2EM9wo20aLnos24yDzRjh9HJc6xfr37jRlv1/boG/EABMG9FnTm35xWrV
R0nw3cpYF7GZg13QicS/ZwEsSd4HyboAruMxJBPvK3Jdr4ZS23bpN0cavWOJsBqZ
VwIDAQAB
-----END PUBLIC KEY-----"""

headers = {
    "Accept": "*/*",
    "Accept-Language": "zh-CN,zh;q=0.9,en;q=0.8,en-GB;q=0.7,en-US;q=0.6",
    "Cache-Control": "no-cache",
    "Connection": "keep-alive",
    "Content-type": "application/x-www-form-urlencoded",
    "Origin": "https://web.vip.miui.com",
    "Pragma": "no-cache",
    "Referer": "https://web.vip.miui.com/",
    "Sec-Fetch-Dest": "empty",
    "Sec-Fetch-Mode": "cors",
    "Sec-Fetch-Site": "cross-site",
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/119.0.0.0 Safari/537.36 Edg/119.0.0.0",
    "sec-ch-ua": '"Microsoft Edge";v="119", "Chromium";v="119", "Not?A_Brand";v="24"',
    "sec-ch-ua-mobile": "?0",
    "sec-ch-ua-platform": '"Windows"',
}


def get_random_chars_as_string(
    length, characters: str = string.ascii_letters + string.digits + string.punctuation
):
    """获取随机字符串"""
    return "".join(random.choice(characters) for _ in range(length))


def aes_encrypt(key: str, data: str):
    """AES 加密"""
    iv = "0102030405060708".encode("utf-8")
    cipher = AES.new(key.encode("utf-8"), AES.MODE_CBC, iv)
    padded_data = pad(data.encode("utf-8"), AES.block_size, style="pkcs7")
    ciphertext = cipher.encrypt(padded_data)
    return base64.b64encode(ciphertext).decode("utf-8")


def rsa_encrypt(key: str, data: str):
    """RSA 加密"""
    public_key = RSA.import_key(key)
    cipher = PKCS1_v1_5.new(public_key)
    ciphertext = cipher.encrypt(base64.b64encode(data.encode("utf-8")))
    return base64.b64encode(ciphertext).decode("utf-8")


IncorrectReturn = (KeyError, TypeError, AttributeError, IndexError)
"""API返回数据无效会触发的异常组合"""


def is_incorrect_return(
    exception: Exception, *addition_exceptions: Type[Exception]
) -> bool:
    """
    判断是否是API返回数据无效的异常
    :param exception: 异常对象
    :param addition_exceptions: 额外的异常类型，用于触发判断
    """
    exceptions = IncorrectReturn + addition_exceptions
    return isinstance(exception, exceptions) or isinstance(
        exception.__cause__, exceptions
    )


def get_token_by_captcha(url: str) -> Union[str, bool]:
    """通过人机验证码获取TOKEN"""
    try:
        parsed_url = urlparse(url)
        query_params = dict(parse_qsl(parsed_url.query))  # 解析URL参数
        gt = query_params.get("c", "")
        challenge = query_params.get("l", "")
        if _conf.preference.two_captcha_api_key:
            solver = TwoCaptcha(apiKey=_conf.preference.two_captcha_api_key)
            geetest_data = get_validate_by_2captcha(gt, challenge ,url)
        else:
            geetest_data = get_validate(gt, challenge)
        params = {
            "k": "3dc42a135a8d45118034d1ab68213073",
            "locale": "zh_CN",
            "_t": round(time.time() * 1000),
        }

        data = {
            "e": query_params.get("e"),  # 人机验证的e参数，来自URL
            "challenge": geetest_data.challenge,
            "seccode": f"{geetest_data.validate}|jordan",
        }

        response = post(
            "https://verify.sec.xiaomi.com/captcha/v2/gt/dk/verify",
            params=params,
            headers=headers,
            data=data,
        )
        log.debug(response.text)
        result = response.json()
        api_data = TokenResultHandler(result)
        if api_data.success:
            solver.report(geetest_data.taskId,True)
            return api_data.token
        elif not api_data.data.get("result"):
            solver.report(geetest_data.taskId,False)
            log.error("遇到人机验证码，无法获取TOKEN")
            return False
        else:
            solver.report(geetest_data.taskId,False)
            log.error("遇到未知错误，无法获取TOKEN")
            return False
    except Exception:  # pylint: disable=broad-exception-caught
        log.exception("获取TOKEN异常")
        return False


# pylint: disable=trailing-whitespace
def get_token(uid: str) -> str | bool:
    """获取TOKEN"""
    try:
        for attempt in Retrying(stop=stop_after_attempt(3)):
            with attempt:
                data = {
                    "type": 0,
                    "startTs": round(time.time() * 1000),
                    "endTs": round(time.time() * 1000),
                    "env": {
                        "p1": "",
                        "p2": "",
                        "p3": "",
                        "p4": "",
                        "p5": "",
                        "p6": "",
                        "p7": "",
                        "p8": "",
                        "p9": "",
                        "p10": "",
                        "p11": "",
                        "p12": "",
                        "p13": "",
                        "p14": "",
                        "p15": "",
                        "p16": "",
                        "p17": "",
                        "p18": "",
                        "p19": "",
                        "p20": "",
                        "p21": "",
                        "p22": "",
                        "p23": "",
                        "p24": "",
                        "p25": "",
                        "p26": "",
                        "p28": "",
                        "p29": "",
                        "p30": "",
                        "p31": "",
                        "p32": "",
                        "p33": [],
                        "p34": "",
                    },
                    "action": {
                        "a1": [],
                        "a2": [],
                        "a3": [],
                        "a4": [],
                        "a5": [],
                        "a6": [],
                        "a7": [],
                        "a8": [],
                        "a9": [],
                        "a10": [],
                        "a11": [],
                        "a12": [],
                        "a13": [],
                        "a14": [],
                    },
                    "force": False,
                    "talkBack": False,
                    "uid": uid,
                    "nonce": {"t": round(time.time()), "r": round(time.time())},
                    "version": "2.0",
                    "scene": "GROW_UP_CHECKIN",
                }

                key = get_random_chars_as_string(16)

                params = {
                    "k": "3dc42a135a8d45118034d1ab68213073",
                    "locale": "zh_CN",
                    "_t": round(time.time() * 1000),
                }

                data = {
                    "s": rsa_encrypt(PUBLIC_KEY_PEM, key),
                    "d": aes_encrypt(key, str(data)),
                    "a": "GROW_UP_CHECKIN",
                }
                response = post(
                    "https://verify.sec.xiaomi.com/captcha/v2/data",
                    params=params,
                    headers=headers,
                    data=data,
                )
                log.debug(response.text)
                result = response.json()
                api_data = TokenResultHandler(result)
                if api_data.success:
                    return api_data.token
                elif api_data.need_verify:
                    log.error("遇到人机验证码, 尝试调用解决方案")
                    url = api_data.data.get("url", "")
                    if token := get_token_by_captcha(url):
                        return token
                    else:
                        raise ValueError("人机验证失败")
                else:
                    log.error("遇到未知错误，无法获取TOKEN")
                    return False
    except RetryError as error:
        if is_incorrect_return(error):
            log.exception(f"TOKEN - 服务器没有正确返回 {response.text}")
        else:
            log.exception("获取TOKEN异常")
        return False


def generate_qrcode(url):
    """生成二维码"""
    qr = QRCode(
        version=1,
        error_correction=constants.ERROR_CORRECT_L,
        box_size=10,
        border=4,
    )
    qr.add_data(url)
    qr.make(fit=True)
    img = qr.make_image(fill_color="black", back_color="white")
    bio = BytesIO()
    img.save(bio)
    # 获取二维码的模块 (module) 列表
    qr_modules = qr.get_matrix()
    chaes = ["  ", "██"]
    # 在控制台中打印二维码
    for row in qr_modules:
        line = "".join(chaes[pixel] for pixel in row)
        print(line)
        log.debug(line)
