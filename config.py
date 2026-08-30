import collections
import os
import yaml
from copy import deepcopy

from loghelper import log

serverless = False
# 提示需要更新config版本
update_config_need = False

# 检测是否在 GitHub Actions 环境
def is_github_actions() -> bool:
    return os.getenv('GITHUB_ACTIONS') == 'true'

# 从环境变量获取敏感信息
def get_secret_from_env(key: str, default: str = "") -> str:
    """从环境变量获取敏感信息，支持多种命名格式"""
    # 尝试不同的环境变量命名格式
    env_vars = [
        key.upper(),  # COOKIE
        key.lower(),  # cookie
        f"AUTO_{key.upper()}",  # AUTO_COOKIE
        f"AUTOMIHOYOBBS_{key.upper()}",  # AUTOMIHOYOBBS_COOKIE
    ]
    
    for env_var in env_vars:
        value = os.getenv(env_var)
        if value:
            return value
    
    # 特殊处理：如果 key 是 cookie，尝试从 ACCOUNT_COOKIE 获取
    if key == "cookie":
        return os.getenv("ACCOUNT_COOKIE", default)
    elif key == "stoken":
        return os.getenv("ACCOUNT_STOKEN", default)
    elif key == "stuid":
        return os.getenv("ACCOUNT_STUID", default)
    elif key == "mid":
        return os.getenv("ACCOUNT_MID", default)
    
    return default

config = {
    'enable': True, 'version': 15, "push": "",
    'account': {'cookie': '', 'stuid': '', 'stoken': '', 'mid': ''},
    'device': {'name': 'Xiaomi MI 6', 'model': 'Mi 6', 'id': '', 'fp': ''},
    'mihoyobbs': {
        'enable': True, 'checkin': True, 'checkin_list': [5, 2],
        'read': True, 'like': True, 'cancel_like': True, 'share': True
    },
    'games': {
        'cn': {
            'enable': True,
            'useragent': 'Mozilla/5.0 (Linux; Android 12; Unspecified Device) AppleWebKit/537.36 (KHTML, like Gecko) '
                         'Version/4.0 Chrome/103.0.5060.129 Mobile Safari/537.36',
            'retries': 3,
            'genshin': {'checkin': True, 'black_list': []},
            'honkai2': {'checkin': False, 'black_list': []},
            'honkai3rd': {'checkin': False, 'black_list': []},
            'tears_of_themis': {'checkin': False, 'black_list': []},
            'honkai_sr': {'checkin': False, 'black_list': []},
            'zzz': {'checkin': False, 'black_list': []}
        },
        'os': {
            'enable': False, 'cookie': '', 'lang': 'zh-cn',
            'genshin': {'checkin': False, 'black_list': []},
            'honkai3rd': {'checkin': False, 'black_list': []},
            'tears_of_themis': {'checkin': False, 'black_list': []},
            'honkai_sr': {'checkin': False, 'black_list': []},
            'zzz': {'checkin': False, 'black_list': []}
        }
    },
    'cloud_games': {
        "cn": {
            "enable": False,
            "genshin": {'enable': False, 'token': ""},
            "zzz": {'enable': False, 'token': ""}
        },
        "os": {
            "enable": False, 'lang': 'zh-cn',
            "genshin": {'enable': False, 'token': ""}
        }
    },
    'competition': {
        'enable': False,
        'genius_invokation': {'enable': False, 'account': [], 'checkin': False, 'weekly': False}
    },
    'web_activity': {'enable': False, 'activities': []}
}
config_raw = deepcopy(config)

path = os.path.dirname(os.path.realpath(__file__)) + "/config"
if os.getenv("AutoMihoyoBBS_config_path") is not None:
    path = os.getenv("AutoMihoyoBBS_config_path")
config_prefix = os.getenv("AutoMihoyoBBS_config_prefix")
if config_prefix is None:
    config_prefix = ""
config_Path = f"{path}/{config_prefix}config.yaml"


def copy_config():
    return deepcopy(config_raw)


def config_v11_update(data: dict):
    global update_config_need
    update_config_need = True
    data['version'] = 13
    new_config = {}
    for key in data:
        if key == "account":
            new_config["push"] = ""
        if key == "cloud_games":
            new_config['cloud_games'] = deepcopy(config_raw['cloud_games'])
            continue
        new_config[key] = deepcopy(data[key])
    new_config['cloud_games']['cn']['enable'] = data['cloud_games']['genshin']['enable']
    new_config['cloud_games']['cn']['genshin']['enable'] = data['cloud_games']['genshin']['enable']
    new_config['cloud_games']['cn']['genshin']['token'] = data['cloud_games']['genshin']['token']
    log.info("config 已升级到：13")
    return new_config


def config_v12_update(data: dict):
    global update_config_need
    update_config_need = True
    data['version'] = 13
    data['cloud_games']['cn']['zzz'] = {'enable': False, 'token': ""}
    log.info("config 已升级到: 13")
    return data


def config_v13_update(data: dict):
    global update_config_need
    update_config_need = True
    new_config = deepcopy(data)

    # 确保版本号更新为14
    new_config['version'] = 14
    new_config['device']['fp'] = config['device'].get('fp', '')

    log.info("config 已升级到：14")
    return new_config


def update_v14_update(data: dict):
    global update_config_need
    update_config_need = True
    new_config = deepcopy(data)
    new_config['version'] = 15
    new_config['web_activity'] = {'enable': False, 'activities': []}
    log.info("config 已升级到：15")
    return new_config


def load_config(p_path=None):
    global config
    
    # 如果在 GitHub Actions 环境，优先从环境变量加载
    if is_github_actions():
        log.info("检测到 GitHub Actions 环境，从环境变量加载配置")
        return load_config_from_env()
    
    if not p_path:
        p_path = config_Path
    
    # 检查配置文件是否存在
    if not os.path.exists(p_path):
        log.warning(f"配置文件不存在: {p_path}，尝试从环境变量加载")
        env_config = load_config_from_env()
        if env_config:
            return env_config
        log.warning("使用默认配置")
        return config
    
    try:
        with open(p_path, "r", encoding='utf-8') as f:
            data = yaml.load(f, Loader=yaml.FullLoader)
    except Exception as e:
        log.error(f"读取配置文件失败: {e}")
        return load_config_from_env()
    
    if data['version'] != config_raw['version']:
        if data['version'] == 11:
            data = config_v11_update(data)
        if data['version'] == 12:
            data = config_v12_update(data)
        if data['version'] == 13:
            data = config_v13_update(data)
        if data['version'] == 14:
            data = update_v14_update(data)
        save_config(p_config=data)
    
    # 去除cookie最末尾的空格
    data["account"]["cookie"] = str(data["account"]["cookie"]).rstrip(' ')
    
    # 从环境变量覆盖敏感信息（如果存在）
    data = override_from_env(data)
    
    config = data
    log.info("Config 加载完毕")
    return data


def load_config_from_env():
    """从环境变量加载配置"""
    log.info("从环境变量加载配置")
    
    # 创建配置副本
    env_config = deepcopy(config_raw)
    
    # 加载账号信息
    env_config['account']['cookie'] = get_secret_from_env('cookie')
    env_config['account']['stoken'] = get_secret_from_env('stoken')
    env_config['account']['stuid'] = get_secret_from_env('stuid')
    env_config['account']['mid'] = get_secret_from_env('mid')
    
    # 加载云游戏 Token
    env_config['cloud_games']['cn']['genshin']['token'] = get_secret_from_env('CLOUD_GAME_GENSHIN_TOKEN')
    env_config['cloud_games']['cn']['zzz']['token'] = get_secret_from_env('CLOUD_GAME_ZZZ_TOKEN')
    env_config['cloud_games']['os']['genshin']['token'] = get_secret_from_env('CLOUD_GAME_GENSHIN_OS_TOKEN')
    
    # 加载国际服 Cookie
    env_config['games']['os']['cookie'] = get_secret_from_env('GAME_OS_COOKIE')
    
    # 检查是否启用（通过环境变量控制）
    if os.getenv('ENABLE_ALL') == 'true':
        env_config['enable'] = True
        env_config['mihoyobbs']['enable'] = True
        env_config['games']['cn']['enable'] = True
        env_config['games']['os']['enable'] = True
    
    # 加载各项功能的启用状态
    env_config['mihoyobbs']['enable'] = os.getenv('ENABLE_MIHOYOBBS', 'true').lower() == 'true'
    env_config['games']['cn']['enable'] = os.getenv('ENABLE_GAME_CN', 'true').lower() == 'true'
    env_config['games']['os']['enable'] = os.getenv('ENABLE_GAME_OS', 'false').lower() == 'true'
    env_config['cloud_games']['cn']['enable'] = os.getenv('ENABLE_CLOUD_GAME_CN', 'false').lower() == 'true'
    env_config['cloud_games']['os']['enable'] = os.getenv('ENABLE_CLOUD_GAME_OS', 'false').lower() == 'true'
    env_config['web_activity']['enable'] = os.getenv('ENABLE_WEB_ACTIVITY', 'false').lower() == 'true'
    
    # 加载云游戏启用状态
    env_config['cloud_games']['cn']['genshin']['enable'] = os.getenv('ENABLE_CLOUD_GAME_GENSHIN', 'false').lower() == 'true'
    env_config['cloud_games']['cn']['zzz']['enable'] = os.getenv('ENABLE_CLOUD_GAME_ZZZ', 'false').lower() == 'true'
    env_config['cloud_games']['os']['genshin']['enable'] = os.getenv('ENABLE_CLOUD_GAME_GENSHIN_OS', 'false').lower() == 'true'
    
    # 加载游戏签到启用状态
    games = ['genshin', 'honkai2', 'honkai3rd', 'tears_of_themis', 'honkai_sr', 'zzz']
    for game in games:
        env_key = f'ENABLE_GAME_{game.upper()}'
        if os.getenv(env_key):
            env_config['games']['cn'][game]['checkin'] = os.getenv(env_key).lower() == 'true'
        
        # 国际服
        env_key_os = f'ENABLE_GAME_OS_{game.upper()}'
        if os.getenv(env_key_os):
            env_config['games']['os'][game]['checkin'] = os.getenv(env_key_os).lower() == 'true'
    
    log.info("从环境变量加载配置完成")
    return env_config


def override_from_env(data: dict):
    """用环境变量覆盖配置中的敏感信息"""
    if is_github_actions():
        # 覆盖账号信息
        cookie = get_secret_from_env('cookie')
        if cookie:
            data['account']['cookie'] = cookie
        
        stoken = get_secret_from_env('stoken')
        if stoken:
            data['account']['stoken'] = stoken
        
        stuid = get_secret_from_env('stuid')
        if stuid:
            data['account']['stuid'] = stuid
        
        mid = get_secret_from_env('mid')
        if mid:
            data['account']['mid'] = mid
        
        # 覆盖云游戏 Token
        token = get_secret_from_env('CLOUD_GAME_GENSHIN_TOKEN')
        if token:
            data['cloud_games']['cn']['genshin']['token'] = token
        
        token_zzz = get_secret_from_env('CLOUD_GAME_ZZZ_TOKEN')
        if token_zzz:
            data['cloud_games']['cn']['zzz']['token'] = token_zzz
        
        token_os = get_secret_from_env('CLOUD_GAME_GENSHIN_OS_TOKEN')
        if token_os:
            data['cloud_games']['os']['genshin']['token'] = token_os
        
        # 覆盖国际服 Cookie
        os_cookie = get_secret_from_env('GAME_OS_COOKIE')
        if os_cookie:
            data['games']['os']['cookie'] = os_cookie
    
    return data


def save_config(p_path=None, p_config=None):
    global serverless
    if serverless:
        log.info("云函数执行，无法保存")
        return None
    
    # 在 GitHub Actions 环境不保存配置文件
    if is_github_actions():
        log.info("GitHub Actions 环境，跳过保存配置文件")
        return None
    
    if not p_path:
        p_path = config_Path
    if not p_config:
        p_config = config
    
    # 创建配置目录
    os.makedirs(os.path.dirname(p_path), exist_ok=True)
    
    try:
        with open(p_path, "w+", encoding='utf-8') as f:
            f.seek(0)
            f.truncate()
            # 在保存前移除敏感信息（如果是从环境变量加载的）
            if is_github_actions():
                # 创建副本，移除敏感信息
                safe_config = deepcopy(p_config)
                safe_config['account']['cookie'] = ''
                safe_config['account']['stoken'] = ''
                safe_config['account']['stuid'] = ''
                safe_config['account']['mid'] = ''
                safe_config['cloud_games']['cn']['genshin']['token'] = ''
                safe_config['cloud_games']['cn']['zzz']['token'] = ''
                safe_config['cloud_games']['os']['genshin']['token'] = ''
                safe_config['games']['os']['cookie'] = ''
                f.write(yaml.dump(safe_config, Dumper=yaml.Dumper, sort_keys=False))
            else:
                f.write(yaml.dump(p_config, Dumper=yaml.Dumper, sort_keys=False))
            f.flush()
    except OSError:
        serverless = True
        log.info("Cookie 保存失败")
    else:
        log.info("Config 保存完毕")


def clear_stoken():
    global config
    if serverless:
        log.info("云函数执行，无法保存")
        return None
    if is_github_actions():
        log.info("GitHub Actions 环境，无需清除 Stoken")
        return None
    config["account"]["mid"] = ""
    config["account"]["stuid"] = ""
    config["account"]["stoken"] = "StokenError"
    log.info("Stoken 已删除")
    save_config()


def clear_cookie():
    global config
    if serverless:
        log.info("云函数执行，无法保存")
        return None
    if is_github_actions():
        log.info("GitHub Actions 环境，无需清除 Cookie")
        return None
    config["account"]["cookie"] = "CookieError"
    log.info(f"Cookie 已删除")
    save_config()


def disable_games(region: str = "cn"):
    global config
    if serverless:
        log.info("云函数执行，无法保存")
        return None
    if is_github_actions():
        log.info("GitHub Actions 环境，跳过禁用游戏签到")
        return None
    config['games'][region]['enable'] = False
    log.info(f"游戏签到（{region}）已关闭")
    save_config()


def clear_cookie_cloudgame_genshin():
    global config
    if serverless:
        log.info("云函数执行，无法保存")
        return None
    if is_github_actions():
        log.info("GitHub Actions 环境，无需清除云游戏 Cookie")
        return None
    config['cloud_games']['cn']['genshin']["enable"] = False
    config['cloud_games']['cn']['genshin']['token'] = ""
    log.info("国服云原神 Cookie 删除完毕")
    save_config()


def clear_cookie_cloudgame_genshin_os():
    global config
    if serverless:
        log.info("云函数执行，无法保存")
        return None
    if is_github_actions():
        log.info("GitHub Actions 环境，无需清除云游戏 Cookie")
        return None
    config['cloud_games']['os']['genshin']["enable"] = False
    config['cloud_games']['os']['genshin']['token'] = ""
    log.info("国际服云原神 Cookie 删除完毕")
    save_config()


def clear_cookie_cloudgame_zzz():
    global config
    if serverless:
        log.info("云函数执行，无法保存")
        return None
    if is_github_actions():
        log.info("GitHub Actions 环境，无需清除云游戏 Cookie")
        return None
    config['cloud_games']['cn']['zzz']["enable"] = False
    config['cloud_games']['cn']['zzz']['token'] = ""
    log.info("国服云绝区零 Cookie 删除完毕")
    save_config()


if __name__ == "__main__":
    # 初始化配置文件
    passzz
        
        token_os = get_secret_from_env('CLOUD_GAME_GENSHIN_OS_TOKEN')
        if token_os:
            data['cloud_games']['os']['genshin']['token'] = token_os
        
        # 覆盖国际服 Cookie
        os_cookie = get_secret_from_env('GAME_OS_COOKIE')
        if os_cookie:
            data['games']['os']['cookie'] = os_cookie
    
    return data


def save_config(p_path=None, p_config=None):
    global serverless
    if serverless:
        log.info("云函数执行，无法保存")
        return None
    
    # 在 GitHub Actions 环境不保存配置文件
    if is_github_actions():
        log.info("GitHub Actions 环境，跳过保存配置文件")
        return None
    
    if not p_path:
        p_path = config_Path
    if not p_config:
        p_config = config
    
    # 创建配置目录
    os.makedirs(os.path.dirname(p_path), exist_ok=True)
    
    try:
        with open(p_path, "w+", encoding='utf-8') as f:
            f.seek(0)
            f.truncate()
            # 在保存前移除敏感信息（如果是从环境变量加载的）
            if is_github_actions():
                # 创建副本，移除敏感信息
                safe_config = deepcopy(p_config)
                safe_config['account']['cookie'] = ''
                safe_config['account']['stoken'] = ''
                safe_config['account']['stuid'] = ''
                safe_config['account']['mid'] = ''
                safe_config['cloud_games']['cn']['genshin']['token'] = ''
                safe_config['cloud_games']['cn']['zzz']['token'] = ''
                safe_config['cloud_games']['os']['genshin']['token'] = ''
                safe_config['games']['os']['cookie'] = ''
                f.write(yaml.dump(safe_config, Dumper=yaml.Dumper, sort_keys=False))
            else:
                f.write(yaml.dump(p_config, Dumper=yaml.Dumper, sort_keys=False))
            f.flush()
    except OSError:
        serverless = True
        log.info("Cookie 保存失败")
    else:
        log.info("Config 保存完毕")


def clear_stoken():
    global config
    if serverless:
        log.info("云函数执行，无法保存")
        return None
    if is_github_actions():
        log.info("GitHub Actions 环境，无需清除 Stoken")
        return None
    config["account"]["mid"] = ""
    config["account"]["stuid"] = ""
    config["account"]["stoken"] = "StokenError"
    log.info("Stoken 已删除")
    save_config()


def clear_cookie():
    global config
    if serverless:
        log.info("云函数执行，无法保存")
        return None
    if is_github_actions():
        log.info("GitHub Actions 环境，无需清除 Cookie")
        return None
    config["account"]["cookie"] = "CookieError"
    log.info(f"Cookie 已删除")
    save_config()


def disable_games(region: str = "cn"):
    global config
    if serverless:
        log.info("云函数执行，无法保存")
        return None
    if is_github_actions():
        log.info("GitHub Actions 环境，跳过禁用游戏签到")
        return None
    config['games'][region]['enable'] = False
    log.info(f"游戏签到（{region}）已关闭")
    save_config()


def clear_cookie_cloudgame_genshin():
    global config
    if serverless:
        log.info("云函数执行，无法保存")
        return None
    if is_github_actions():
        log.info("GitHub Actions 环境，无需清除云游戏 Cookie")
        return None
    config['cloud_games']['cn']['genshin']["enable"] = False
    config['cloud_games']['cn']['genshin']['token'] = ""
    log.info("国服云原神 Cookie 删除完毕")
    save_config()


def clear_cookie_cloudgame_genshin_os():
    global config
    if serverless:
        log.info("云函数执行，无法保存")
        return None
    if is_github_actions():
        log.info("GitHub Actions 环境，无需清除云游戏 Cookie")
        return None
    config['cloud_games']['os']['genshin']["enable"] = False
    config['cloud_games']['os']['genshin']['token'] = ""
    log.info("国际服云原神 Cookie 删除完毕")
    save_config()


def clear_cookie_cloudgame_zzz():
    global config
    if serverless:
        log.info("云函数执行，无法保存")
        return None
    if is_github_actions():
        log.info("GitHub Actions 环境，无需清除云游戏 Cookie")
        return None
    config['cloud_games']['cn']['zzz']["enable"] = False
    config['cloud_games']['cn']['zzz']['token'] = ""
    log.info("国服云绝区零 Cookie 删除完毕")
    save_config()


if __name__ == "__main__":
    # 初始化配置文件
    passzz
        
        token_os = get_secret_from_env('CLOUD_GAME_GENSHIN_OS_TOKEN')
        if token_os:
            data['cloud_games']['os']['genshin']['token'] = token_os
        
        # 覆盖国际服 Cookie
        os_cookie = get_secret_from_env('GAME_OS_COOKIE')
        if os_cookie:
            data['games']['os']['cookie'] = os_cookie
    
    return data


def save_config(p_path=None, p_config=None):
    global serverless
    if serverless:
        log.info("云函数执行，无法保存")
        return None
    
    # 在 GitHub Actions 环境不保存配置文件
    if is_github_actions():
        log.info("GitHub Actions 环境，跳过保存配置文件")
        return None
    
    if not p_path:
        p_path = config_Path
    if not p_config:
        p_config = config
    
    # 创建配置目录
    os.makedirs(os.path.dirname(p_path), exist_ok=True)
    
    try:
        with open(p_path, "w+", encoding='utf-8') as f:
            f.seek(0)
            f.truncate()
            # 在保存前移除敏感信息（如果是从环境变量加载的）
            if is_github_actions():
                # 创建副本，移除敏感信息
                safe_config = deepcopy(p_config)
                safe_config['account']['cookie'] = ''
                safe_config['account']['stoken'] = ''
                safe_config['account']['stuid'] = ''
                safe_config['account']['mid'] = ''
                safe_config['cloud_games']['cn']['genshin']['token'] = ''
                safe_config['cloud_games']['cn']['zzz']['token'] = ''
                safe_config['cloud_games']['os']['genshin']['token'] = ''
                safe_config['games']['os']['cookie'] = ''
                f.write(yaml.dump(safe_config, Dumper=yaml.Dumper, sort_keys=False))
            else:
                f.write(yaml.dump(p_config, Dumper=yaml.Dumper, sort_keys=False))
            f.flush()
    except OSError:
        serverless = True
        log.info("Cookie 保存失败")
    else:
        log.info("Config 保存完毕")


def clear_stoken():
    global config
    if serverless:
        log.info("云函数执行，无法保存")
        return None
    if is_github_actions():
        log.info("GitHub Actions 环境，无需清除 Stoken")
        return None
    config["account"]["mid"] = ""
    config["account"]["stuid"] = ""
    config["account"]["stoken"] = "StokenError"
    log.info("Stoken 已删除")
    save_config()


def clear_cookie():
    global config
    if serverless:
        log.info("云函数执行，无法保存")
        return None
    if is_github_actions():
        log.info("GitHub Actions 环境，无需清除 Cookie")
        return None
    config["account"]["cookie"] = "CookieError"
    log.info(f"Cookie 已删除")
    save_config()


def disable_games(region: str = "cn"):
    global config
    if serverless:
        log.info("云函数执行，无法保存")
        return None
    if is_github_actions():
        log.info("GitHub Actions 环境，跳过禁用游戏签到")
        return None
    config['games'][region]['enable'] = False
    log.info(f"游戏签到（{region}）已关闭")
    save_config()


def clear_cookie_cloudgame_genshin():
    global config
    if serverless:
        log.info("云函数执行，无法保存")
        return None
    if is_github_actions():
        log.info("GitHub Actions 环境，无需清除云游戏 Cookie")
        return None
    config['cloud_games']['cn']['genshin']["enable"] = False
    config['cloud_games']['cn']['genshin']['token'] = ""
    log.info("国服云原神 Cookie 删除完毕")
    save_config()


def clear_cookie_cloudgame_genshin_os():
    global config
    if serverless:
        log.info("云函数执行，无法保存")
        return None
    if is_github_actions():
        log.info("GitHub Actions 环境，无需清除云游戏 Cookie")
        return None
    config['cloud_games']['os']['genshin']["enable"] = False
    config['cloud_games']['os']['genshin']['token'] = ""
    log.info("国际服云原神 Cookie 删除完毕")
    save_config()


def clear_cookie_cloudgame_zzz():
    global config
    if serverless:
        log.info("云函数执行，无法保存")
        return None
    if is_github_actions():
        log.info("GitHub Actions 环境，无需清除云游戏 Cookie")
        return None
    config['cloud_games']['cn']['zzz']["enable"] = False
    config['cloud_games']['cn']['zzz']['token'] = ""
    log.info("国服云绝区零 Cookie 删除完毕")
    save_config()


if __name__ == "__main__":
    # 初始化配置文件
    pass
