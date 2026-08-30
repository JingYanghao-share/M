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


def load_config_from_env():
    """从环境变量加载所有配置，并显示详细的状态信息"""
    log.info("=" * 60)
    log.info("开始从环境变量加载配置...")
    log.info("=" * 60)
    
    env_config = deepcopy(config_raw)
    
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
        log.error(f"请前往 Settings → Secrets and variables → Actions 添加以下 Secrets:")
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


# ... 保留其他函数不变 (config_v11_update, config_v12_update, config_v13_update, update_v14_update, save_config, clear_stoken, clear_cookie, disable_games, clear_cookie_cloudgame_genshin, clear_cookie_cloudgame_genshin_os, clear_cookie_cloudgame_zzz)
# 注意：这些函数和之前保持一致，此处省略以节省空间，但实际使用时需要保留完整代码
