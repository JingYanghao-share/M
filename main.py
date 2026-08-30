import os
import time
import random
from typing import Tuple, Optional
from enum import Enum, auto

import push
import login
import tools
import config
import mihoyobbs
import cloudgames
import gamecheckin
import hoyo_checkin
import web_activity
import os_cloudgames
from loghelper import log
from error import CookieError, StokenError


class StatusCode(Enum):
    SUCCESS = 0
    FAILURE = 1
    PARTIAL_FAILURE = 2
    CAPTCHA_TRIGGERED = 3


def is_github_actions() -> bool:
    """检测是否在 GitHub Actions 环境"""
    return os.getenv('GITHUB_ACTIONS') == 'true'


def check_github_actions() -> None:
    """检测并允许 GitHub Actions 运行（不再退出）"""
    if is_github_actions():
        log.warning("检测到 GitHub Actions 环境运行，已允许执行")


def initialize_config() -> Tuple[bool, Optional[str]]:
    config.load_config()
    if not config.config["enable"]:
        log.warning("Config 未启用！")
        return False, "Config 未启用！"
    return True, None


def handle_login() -> None:
    """
    处理登录逻辑
    - GitHub Actions 环境下，若缺少 cookie/stoken/stuid/mid 则直接抛出异常提示设置 Secrets
    - 本地环境则进行交互式登录
    """
    account_cfg = config.config["account"]
    # 检查必要字段是否为空
    if any([
        account_cfg["stuid"] == "",
        account_cfg["stoken"] == "",
        account_cfg["mid"] == ""
    ]):
        if is_github_actions():
            raise CookieError(
                "GitHub Actions 环境：缺少账号 Secrets！请设置 COOKIE, STOKEN, STUID, MID"
            )
        else:
            # 本地环境，尝试交互式登录
            if config.config["mihoyobbs"]["enable"]:
                login.login()
                time.sleep(random.randint(3, 8))
    account_cfg["cookie"] = tools.tidy_cookie(account_cfg["cookie"])


def run_mihoyobbs() -> Tuple[str, bool]:
    return_data = ""
    raise_stoken = False
    if config.config["mihoyobbs"]["enable"]:
        if config.config["account"]["stoken"] == "StokenError":
            return_data = "米游社：\n账号 Stoken 异常"
            raise_stoken = True
        else:
            try:
                bbs = mihoyobbs.Mihoyobbs()
                return_data = bbs.run_task()
            except StokenError:
                raise_stoken = True
    return return_data, raise_stoken


def run_cn_tasks() -> str:
    result = []
    if config.config["games"]['cn']["enable"]:
        result.append(gamecheckin.run_task())
    if config.config["cloud_games"]['cn']["enable"]:
        log.info("正在进行云游戏签到")
        result.append(cloudgames.run_task())
    return "\n\n".join(filter(None, result))


def run_os_tasks() -> str:
    result = []
    if config.config["games"]['os']["enable"]:
        log.info("海外版：")
        os_result = hoyo_checkin.run_task()
        if os_result:
            result.append(f"海外版：{os_result}")
    if config.config["cloud_games"]['os']["enable"]:
        log.info("正在进行云游戏国际版签到")
        result.append(os_cloudgames.run_task())
    return "\n\n".join(filter(None, result))


def run_web_activity() -> None:
    if config.config["web_activity"]['enable']:
        log.info("正在进行米游社网页活动任务")
        web_activity.run_task()


def main() -> Tuple[int, str]:
    check_github_actions()

    success, msg = initialize_config()
    if not success:
        return StatusCode.FAILURE.value, msg

    handle_login()

    if config.config["account"]["cookie"] == "CookieError":
        raise CookieError('Cookie expires')

    return_data = []
    status_code = StatusCode.SUCCESS.value

    mihoyo_result, raise_stoken = run_mihoyobbs()
    return_data.append(mihoyo_result)

    return_data.append(run_cn_tasks())
    return_data.append(run_os_tasks())

    run_web_activity()

    if raise_stoken:
        raise StokenError("Stoken 异常")

    result_msg = "\n".join(filter(None, return_data))
    if "触发验证码" in result_msg:
        status_code = StatusCode.CAPTCHA_TRIGGERED.value

    return status_code, result_msg


def task_run() -> None:
    """任务运行入口，统一捕获异常并推送"""
    push_message = ""   # 初始化默认值，避免 UnboundLocalError
    status_code = StatusCode.FAILURE.value

    try:
        status_code, message = main()
        push_message = message
    except CookieError as e:
        status_code = StatusCode.FAILURE.value
        push_message = f"账号 Cookie 出错！\n{str(e)}"
        log.error(f"账号 Cookie 有问题：{str(e)}")
    except StokenError as e:
        status_code = StatusCode.FAILURE.value
        push_message = f"账号 Stoken 出错！\n{str(e)}"
        log.error(f"账号 Stoken 有问题：{str(e)}")
    except Exception as e:
        status_code = StatusCode.FAILURE.value
        push_message = f"运行出错！\n{str(e)}"
        log.error(f"运行出错：{str(e)}")
    finally:
        push.push(status_code, push_message)


if __name__ == "__main__":
    task_run()
