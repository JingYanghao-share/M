import os
import yaml
from copy import deepcopy

from loghelper import log

serverless = False
update_config_need = False


def is_github_actions() -> bool:
    return os.getenv('GITHUB_ACTIONS') == 'true'


def get_secret_from_env(key: str, default: str = "", verbose: bool = True) -> str:
    """
    从环境变量获取敏感信息
    优先使用全大写名称，如 COOKIE, STOKEN, STUID, MID
    """
    # 标准大写名称（与 GitHub Secrets 名称一致）
    env_names = [
        key.upper(),                     # COOKIE
        f"ACCOUNT_{key.upper()}",        # ACCOUNT_COOKIE
        f"AUTO_{key.upper()}",           # AUTO_COOKIE
    ]
    
    for name in env_names:
        value = os.getenv(name)
        if value:
            if verbose:
                # 不打印完整值，只显示长度和状态
                log.info(f"✅ 已读取环境变量: {name} (长度: {len(value)} 字符)")
            return value
    
    if verbose:
        log.warning(f"❌ 未找到环境变量: {', '.join(env_names)}")
    return default


# ========== 配置定义 ==========
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
config_raw = deepcopy(config)  # 必须在函数定义之前定义

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


def load_config_from_env():
    """从环境变量加载所有配置，并显示详细的状态信息"""
    log.info("=" * 60)
    log.info("开始从环境变量加载配置...")
    log.info("=" * 60)
    
    env_config = deepcopy(config_raw)  # 现在 config_raw 已经定义了
    
    # ========== 账号信息（必须） ==========
    log.info("\n📋 [必需] 账号信息:")
    
    cookie = get_secret_from_env('cookie')
    if cookie:
        env_config['account']['cookie'] = cookie
        log.info(f"   COOKIE: ✅ 已设置 (长度: {len(cookie)} 字符)")
    else:
        log.warning("   COOKIE: ❌ 未设置！请添加 Secrets: COOKIE")
    
    stoken = get_secret_from_env('stoken')
    if stoken:
        env_config['account']['stoken'] = stoken
        log.info(f"   STOKEN: ✅ 已设置 (长度: {len(stoken)} 字符)")
    else:
        log.warning("   STOKEN: ❌ 未设置！请添加 Secrets: STOKEN")
    
    stuid = get_secret_from_env('stuid')
    if stuid:
        env_config['account']['stuid'] = stuid
        log.info(f"   STUID: ✅ 已设置 (长度: {len(stuid)} 字符)")
    else:
        log.warning("   STUID: ❌ 未设置！请添加 Secrets: STUID")
    
    mid = get_secret_from_env('mid')
    if mid:
        env_config['account']['mid'] = mid
        log.info(f"   MID: ✅ 已设置 (长度: {len(mid)} 字符)")
    else:
        log.warning("   MID: ❌ 未设置！请添加 Secrets: MID")
    
    # ========== 云游戏 Token（可选） ==========
    log.info("\n📋 [可选] 云游戏 Token:")
    
    token = get_secret_from_env('CLOUD_GAME_GENSHIN_TOKEN')
    if token:
        env_config['cloud_games']['cn']['genshin']['token'] = token
        log.info("   CLOUD_GAME_GENSHIN_TOKEN: ✅ 已设置")
    else:
        log.info("   CLOUD_GAME_GENSHIN_TOKEN: ⏭️ 未设置（如不使用云原神可忽略）")
    
    token_zzz = get_secret_from_env('CLOUD_GAME_ZZZ_TOKEN')
    if token_zzz:
        env_config['cloud_games']['cn']['zzz']['token'] = token_zzz
        log.info("   CLOUD_GAME_ZZZ_TOKEN: ✅ 已设置")
    else:
        log.info("   CLOUD_GAME_ZZZ_TOKEN: ⏭️ 未设置（如不使用云绝区零可忽略）")
    
    token_os = get_secret_from_env('CLOUD_GAME_GENSHIN_OS_TOKEN')
    if token_os:
        env_config['cloud_games']['os']['genshin']['token'] = token_os
        log.info("   CLOUD_GAME_GENSHIN_OS_TOKEN: ✅ 已设置")
    else:
        log.info("   CLOUD_GAME_GENSHIN_OS_TOKEN: ⏭️ 未设置（如不使用国际服云原神可忽略）")
    
    # ========== 国际服 Cookie（可选） ==========
    log.info("\n📋 [可选] 国际服配置:")
    
    os_cookie = get_secret_from_env('GAME_OS_COOKIE')
    if os_cookie:
        env_config['games']['os']['cookie'] = os_cookie
        log.info("   GAME_OS_COOKIE: ✅ 已设置")
    else:
        log.info("   GAME_OS_COOKIE: ⏭️ 未设置（如不使用国际服可忽略）")
    
    # ========== 功能开关 ==========
    log.info("\n📋 [配置] 功能开关（可通过环境变量覆盖）:")
    
    if os.getenv('ENABLE_ALL') == 'true':
        env_config['enable'] = True
        env_config['mihoyobbs']['enable'] = True
        env_config['games']['cn']['enable'] = True
        env_config['games']['os']['enable'] = True
        log.info("   ENABLE_ALL: true (已启用所有功能)")
    
    env_config['mihoyobbs']['enable'] = os.getenv('ENABLE_MIHOYOBBS', 'true').lower() == 'true'
    log.info(f"   ENABLE_MIHOYOBBS: {env_config['mihoyobbs']['enable']}")
    
    env_config['games']['cn']['enable'] = os.getenv('ENABLE_GAME_CN', 'true').lower() == 'true'
    log.info(f"   ENABLE_GAME_CN: {env_config['games']['cn']['enable']}")
    
    env_config['games']['os']['enable'] = os.getenv('ENABLE_GAME_OS', 'false').lower() == 'true'
    log.info(f"   ENABLE_GAME_OS: {env_config['games']['os']['enable']}")
    
    env_config['cloud_games']['cn']['enable'] = os.getenv('ENABLE_CLOUD_GAME_CN', 'false').lower() == 'true'
    log.info(f"   ENABLE_CLOUD_GAME_CN: {env_config['cloud_games']['cn']['enable']}")
    
    env_config['cloud_games']['os']['enable'] = os.getenv('ENABLE_CLOUD_GAME_OS', 'false').lower() == 'true'
    log.info(f"   ENABLE_CLOUD_GAME_OS: {env_config['cloud_games']['os']['enable']}")
    
    env_config['web_activity']['enable'] = os.getenv('ENABLE_WEB_ACTIVITY', 'false').lower() == 'true'
    log.info(f"   ENABLE_WEB_ACTIVITY: {env_config['web_activity']['enable']}")
    
    # 云游戏子功能
    env_config['cloud_games']['cn']['genshin']['enable'] = os.getenv('ENABLE_CLOUD_GAME_GENSHIN', 'false').lower() == 'true'
    env_config['cloud_games']['cn']['zzz']['enable'] = os.getenv('ENABLE_CLOUD_GAME_ZZZ', 'false').lower() == 'true'
    env_config['cloud_games']['os']['genshin']['enable'] = os.getenv('ENABLE_CLOUD_GAME_GENSHIN_OS', 'false').lower() == 'true'
    
    # 游戏签到子功能
    games = ['genshin', 'honkai2', 'honkai3rd', 'tears_of_themis', 'honkai_sr', 'zzz']
    for game in games:
        env_key = f'ENABLE_GAME_{game.upper()}'
        if os.getenv(env_key):
            env_config['games']['cn'][game]['checkin'] = os.getenv(env_key).lower() == 'true'
        env_key_os = f'ENABLE_GAME_OS_{game.upper()}'
        if os.getenv(env_key_os):
            env_config['games']['os'][game]['checkin'] = os.getenv(env_key_os).lower() == 'true'
    
    # ========== 最终状态汇总 ==========
    log.info("\n" + "=" * 60)
    log.info("📊 加载状态汇总:")
    log.info("=" * 60)
    
    # 检查必需项
    missing_required = []
    if not env_config['account']['cookie']:
        missing_required.append("COOKIE")
    if not env_config['account']['stoken']:
        missing_required.append("STOKEN")
    if not env_config['account']['stuid']:
        missing_required.append("STUID")
    if not env_config['account']['mid']:
        missing_required.append("MID")
    
    if missing_required:
        log.error(f"❌ 缺少必需的 Secrets: {', '.join(missing_required)}")
        log.error("请前往 Settings → Secrets and variables → Actions 添加以下 Secrets:")
        for secret in missing_required:
            log.error(f"   - {secret}")
    else:
        log.info("✅ 所有必需的 Secrets 已配置")
    
    log.info("=" * 60 + "\n")
    
    return env_config


def load_config(p_path=None):
    global config
    # GitHub Actions 环境优先从环境变量加载
    if is_github_actions():
        log.info("检测到 GitHub Actions 环境，从环境变量加载配置")
        config = load_config_from_env()
        return config

    if not p_path:
        p_path = config_Path

    if not os.path.exists(p_path):
        log.warning(f"配置文件不存在: {p_path}，尝试从环境变量加载")
        config = load_config_from_env()
        return config

    try:
        with open(p_path, "r", encoding='utf-8') as f:
            data = yaml.load(f, Loader=yaml.FullLoader)
    except Exception as e:
        log.error(f"读取配置文件失败: {e}")
        config = load_config_from_env()
        return config

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

    data["account"]["cookie"] = str(data["account"]["cookie"]).rstrip(' ')
    data = override_from_env(data)
    config = data
    log.info("Config 加载完毕")
    return data


def override_from_env(data: dict):
    """用环境变量覆盖配置中的敏感信息（主要用于混合模式）"""
    if is_github_actions():
        cookie = get_secret_from_env('cookie', verbose=False)
        if cookie:
            data['account']['cookie'] = cookie
        
        stoken = get_secret_from_env('stoken', verbose=False)
        if stoken:
            data['account']['stoken'] = stoken
        
        stuid = get_secret_from_env('stuid', verbose=False)
        if stuid:
            data['account']['stuid'] = stuid
        
        mid = get_secret_from_env('mid', verbose=False)
        if mid:
            data['account']['mid'] = mid

        token = get_secret_from_env('CLOUD_GAME_GENSHIN_TOKEN', verbose=False)
        if token:
            data['cloud_games']['cn']['genshin']['token'] = token
        
        token_zzz = get_secret_from_env('CLOUD_GAME_ZZZ_TOKEN', verbose=False)
        if token_zzz:
            data['cloud_games']['cn']['zzz']['token'] = token_zzz
        
        token_os = get_secret_from_env('CLOUD_GAME_GENSHIN_OS_TOKEN', verbose=False)
        if token_os:
            data['cloud_games']['os']['genshin']['token'] = token_os

        os_cookie = get_secret_from_env('GAME_OS_COOKIE', verbose=False)
        if os_cookie:
            data['games']['os']['cookie'] = os_cookie

    return data


def save_config(p_path=None, p_config=None):
    global serverless
    if serverless:
        log.info("云函数执行，无法保存")
        return None
    if is_github_actions():
        log.info("GitHub Actions 环境，跳过保存配置文件")
        return None
    if not p_path:
        p_path = config_Path
    if not p_config:
        p_config = config
    os.makedirs(os.path.dirname(p_path), exist_ok=True)
    try:
        with open(p_path, "w+", encoding='utf-8') as f:
            f.seek(0)
            f.truncate()
            if is_github_actions():
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
    log.info("Cookie 已删除")
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
    pass
