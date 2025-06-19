import os
import sys
import main
import time
import push
import config
import random
import setting
from loghelper import log
from error import CookieError, StokenError

# 搜索配置文件
def find_config_files(search_path: str) -> list:
    """查找所有配置文件，支持递归查找"""
    config_files = []
    
    # 如果路径是文件，直接返回
    if os.path.isfile(search_path):
        return [search_path]
    
    # 如果路径是目录，递归查找所有.yml文件
    if os.path.isdir(search_path):
        for root, _, files in os.walk(search_path):
            for file in files:
                if file.lower().endswith(('.yml', '.yaml')):
                    config_files.append(os.path.join(root, file))
        return config_files
    
    # 默认行为：在config目录下查找
    config_path = config.path if hasattr(config, 'path') else 'config'
    if os.path.exists(config_path) and os.path.isdir(config_path):
        return find_config_files(config_path)
    
    log.warning(f"配置路径不存在: {search_path}")
    return []

# 获取配置文件列表
def get_config_list() -> list:
    # 获取配置搜索路径
    config_path = os.getenv("AUTOMIHOYOBBS_CONFIG_PATH", "config")
    log.info(f"搜索配置文件路径: {config_path}")
    
    # 查找所有配置文件
    config_files = find_config_files(config_path)
    
    # 过滤配置文件
    config_prefix = getattr(config, 'config_prefix', '')
    if config_prefix:
        config_files = [f for f in config_files 
                        if os.path.basename(f).startswith(config_prefix)]
    
    # 检查是否在青龙面板环境中
    if os.getenv("AutoMihoyoBBS_config_multi") == '1' and os.getenv("QL_DIR"):
        config_files = [f for f in config_files 
                        if os.path.basename(f).startswith('mhy_')]
    
    if not config_files:
        log.warning(f"未在 {config_path} 中找到任何配置文件")
        exit(1)
    
    log.info(f"找到 {len(config_files)} 个配置文件")
    return sorted(config_files)

def main_multi(autorun: bool):
    log.info("AutoMihoyoBBS 多用户模式启动")
    
    # 获取配置文件列表
    config_files = get_config_list()
    
    # 自动运行模式检测
    if os.getenv("GITHUB_ACTIONS") == "true" or autorun:
        log.info(f"自动运行模式，找到 {len(config_files)} 个配置文件")
    else:
        log.info(f"找到 {len(config_files)} 个配置文件:\n" + "\n".join(config_files))
        try:
            input("按回车开始执行，或 Ctrl+C 退出")
        except KeyboardInterrupt:
            exit(0)
    
    # 初始化结果跟踪
    results = {
        "success": [],
        "skipped": [],
        "failed": [],
        "captcha": [],
        "errors": []
    }
    
    # 处理每个配置文件
    for config_file in config_files:
        file_name = os.path.basename(config_file)
        log.info(f"开始处理: {file_name}")
        
        # 保存原始配置路径
        original_config_path = getattr(config, 'config_Path', None)
        
        try:
            # 设置当前配置文件
            config.config_Path = config_file
            
            # 执行主任务
            start_time = time.time()
            return_code, message = main.main()
            elapsed = time.time() - start_time
            
            # 记录结果
            if return_code == 0:
                results["success"].append(file_name)
                log.info(f"{file_name} 执行成功 ({elapsed:.1f}s)")
            elif return_code == 3:
                results["captcha"].append(file_name)
                log.warning(f"{file_name} 需要验证码 ({elapsed:.1f}s)")
            elif return_code == 1:
                results["skipped"].append(file_name)
                log.info(f"{file_name} 未执行 ({elapsed:.1f}s)")
            else:
                results["failed"].append(file_name)
                log.error(f"{file_name} 执行失败 ({elapsed:.1f}s)")
                
        except CookieError as e:
            results["errors"].append(f"{file_name}: Cookie错误")
            log.error(f"{file_name} Cookie错误: {str(e)}")
        except StokenError as e:
            results["errors"].append(f"{file_name}: Stoken错误")
            log.error(f"{file_name} Stoken错误: {str(e)}")
        except Exception as e:
            results["errors"].append(f"{file_name}: 未知错误")
            log.exception(f"{file_name} 处理时发生未知错误")
        finally:
            # 恢复原始配置路径
            if original_config_path:
                config.config_Path = original_config_path
            
            # 随机延迟
            delay = random.randint(3, 10)
            log.info(f"等待 {delay} 秒后继续...")
            time.sleep(delay)
    
    # 生成结果报告
    success_count = len(results["success"])
    skipped_count = len(results["skipped"])
    failed_count = len(results["failed"])
    captcha_count = len(results["captcha"])
    error_count = len(results["errors"])
    
    push_message = (
        f"🏁 任务执行完成\n"
        f"📋 配置文件总数: {len(config_files)}\n"
        f"✅ 成功: {success_count}\n"
        f"⚠️ 跳过: {skipped_count}\n"
        f"❌ 失败: {failed_count}\n"
        f"🔒 需要验证码: {captcha_count}\n"
        f"❗ 错误: {error_count}\n"
    )
    
    if results["success"]:
        push_message += f"\n✅ 成功列表: {', '.join(results['success'])}\n"
    if results["skipped"]:
        push_message += f"\n⚠️ 跳过列表: {', '.join(results['skipped'])}\n"
    if results["failed"]:
        push_message += f"\n❌ 失败列表: {', '.join(results['failed'])}\n"
    if results["captcha"]:
        push_message += f"\n🔒 验证码列表: {', '.join(results['captcha'])}\n"
    if results["errors"]:
        push_message += f"\n❗ 错误列表:\n - " + "\n - ".join(results['errors'])
    
    log.info(push_message)
    
    # 确定推送状态
    status = 0
    if error_count > 0 or failed_count > 0:
        status = 1
    elif captcha_count > 0:
        status = 2
    
    return status, push_message

if __name__ == "__main__":
    # 自动运行模式检测
    autorun = (
        len(sys.argv) > 1 and sys.argv[1] == "autorun" or
        os.getenv("AutoMihoyoBBS_autorun") == "1" or
        os.getenv("GITHUB_ACTIONS") == "true"
    )
    
    # 执行多用户任务
    status, message = main_multi(autorun)
    
    # 推送结果
    push.push(status, message)
    
    # 退出状态码
    exit(0 if status == 0 else 1)
