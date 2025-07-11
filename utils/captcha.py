"""
Date: 2023-11-13 19:55:22
LastEditors: Night-stars-1 nujj1042633805@gmail.com
LastEditTime: 2025-02-11 00:59:19
"""

import json
import time
from traceback import print_exc

from jsonpath_ng import parse
from jsonpath_ng.exceptions import JsonPathParserError

from .config import ConfigManager
from .data_model import GeetestResult
from .logger import log
from .request import request
from twocaptcha import TwoCaptcha

_conf = ConfigManager.data_obj


def find_key(data: dict, key: str):
    """递归查找字典中的key"""
    for dkey, dvalue in data.items():
        if dkey == key:
            return dvalue
        if isinstance(dvalue, dict):
            find_key(dvalue, key)
    return None


def get_validate_other(
    gt: str, challenge: str, result: str
) -> GeetestResult:  # pylint: disable=invalid-name
    """获取人机验证结果"""
    try:
        validate = ""
        if _conf.preference.get_geetest_url:
            params = _conf.preference.get_geetest_params.copy()
            params = json.loads(
                json.dumps(params)
                .replace("{gt}", gt)
                .replace("{challenge}", challenge)
                .replace("{result}", str(result))
            )
            data = _conf.preference.get_geetest_data.copy()
            data = json.loads(
                json.dumps(data)
                .replace("{gt}", gt)
                .replace("{challenge}", challenge)
                .replace("{result}", str(result))
            )
            for i in range(_conf.preference.get_geetest_try_count):
                log.info(f"第{i}次获取结果")
                response = request(
                    _conf.preference.get_geetest_method,
                    _conf.preference.get_geetest_url,
                    params=params,
                    json=data,
                )
                log.debug(response.text)
                result = response.json()
                geetest_validate_expr = parse(
                    _conf.preference.get_geetest_validate_path
                )
                geetest_validate_match = geetest_validate_expr.find(result)
                if len(geetest_validate_match) > 0:
                    validate = geetest_validate_match[0].value
                geetest_challenge_expr = parse(
                    _conf.preference.get_geetest_challenge_path
                )
                geetest_challenge_match = geetest_challenge_expr.find(result)
                if len(geetest_challenge_match) > 0:
                    challenge = geetest_challenge_match[0].value
                if validate and challenge:
                    return GeetestResult(challenge=challenge, validate=validate)
                time.sleep(1)
            return GeetestResult(challenge="", validate="")
        else:
            return GeetestResult(challenge="", validate="")
    except Exception:  # pylint: disable=broad-exception-caught
        log.exception("获取人机验证结果异常")
        return GeetestResult(challenge="", validate="")


def get_validate(
    gt: str, challenge: str
) -> GeetestResult:  # pylint: disable=invalid-name
    """创建人机验证并结果"""
    try:
        validate = ""
        result = ""
        if _conf.preference.geetest_url:
            params = _conf.preference.geetest_params.copy()
            params = json.loads(
                json.dumps(params).replace("{gt}", gt).replace("{challenge}", challenge)
            )
            data = _conf.preference.geetest_data.copy()
            data = json.loads(
                json.dumps(data).replace("{gt}", gt).replace("{challenge}", challenge)
            )
            response = request(
                _conf.preference.geetest_method,
                _conf.preference.geetest_url,
                params=params,
                json=data,
            )
            log.debug(response.text)
            result = response.json()
            try:
                geetest_validate_expr = parse(_conf.preference.geetest_validate_path)
                geetest_validate_match = geetest_validate_expr.find(result)
                if len(geetest_validate_match) > 0:
                    validate = geetest_validate_match[0].value
                geetest_challenge_expr = parse(_conf.preference.geetest_challenge_path)
                geetest_challenge_match = geetest_challenge_expr.find(result)
                if len(geetest_challenge_match) > 0:
                    challenge = geetest_challenge_match[0].value
                geetest_result_expr = parse(_conf.preference.geetest_result_path)
                geetest_result_match = geetest_result_expr.find(result)
                if len(geetest_result_match) > 0:
                    result = geetest_result_match[0].value
            except JsonPathParserError:
                print_exc()
            if validate and challenge:
                return GeetestResult(challenge=challenge, validate=validate)
            else:
                return get_validate_other(gt=gt, challenge=challenge, result=result)
        else:
            return GeetestResult(challenge="", validate="")
    except Exception:  # pylint: disable=broad-exception-caught
        log.exception("获取人机验证结果异常")
        return GeetestResult(challenge="", validate="")
    
def get_validate_by_2captcha(gt: str, challenge: str, websiteUrl: str) -> GeetestResult | None:  # pylint: disable=invalid-name
    """获取人机验证结果(2captcha)"""
    try:
        solver = TwoCaptcha(apiKey=_conf.preference.two_captcha_api_key)
        geetest_data = solver.geetest(gt=gt,challenge=challenge,url=websiteUrl,userAgent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/119.0.0.0 Safari/537.36 Edg/119.0.0.0")
        captchaId=geetest_data["captchaId"]
        geetest = json.loads(geetest_data["code"])
        challenge = geetest["geetest_challenge"]
        validate = geetest["geetest_validate"]
        return GeetestResult(challenge=challenge, validate=validate, taskId=captchaId)
    except Exception as e:  # pylint: disable=broad-exception-caught
        log.exception("2captcha接口调用异常")
        raise Exception("2captcha接口调用异常")
