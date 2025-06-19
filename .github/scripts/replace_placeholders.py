import os
import re
import json
import argparse
import sys
from pathlib import Path

def replace_placeholders(content, env_vars):
    """替换所有 ${{ VARIABLE_NAME }} 格式的占位符"""
    pattern = re.compile(r'\$\{\{\s*([A-Za-z0-9_]+)\s*\}\}')
    
    def replace_match(match):
        var_name = match.group(1)
        # 如果变量存在则替换，否则保留原占位符
        return env_vars.get(var_name, match.group(0))
    
    return pattern.sub(replace_match, content)

def main():
    parser = argparse.ArgumentParser(description='替换配置文件中的占位符')
    parser.add_argument('--input', required=True, help='输入文件路径')
    parser.add_argument('--output', required=True, help='输出文件路径')
    parser.add_argument('--env-json', required=True, help='环境变量JSON字符串')
    
    args = parser.parse_args()
    
    try:
        # 解析环境变量JSON
        env_vars = json.loads(args.env_json)
        
        # 读取输入文件
        with open(args.input, 'r', encoding='utf-8') as f:
            content = f.read()
        
        # 替换占位符
        new_content = replace_placeholders(content, env_vars)
        
        # 确保输出目录存在
        output_dir = os.path.dirname(args.output)
        if output_dir:
            Path(output_dir).mkdir(parents=True, exist_ok=True)
        
        # 写入输出文件
        with open(args.output, 'w', encoding='utf-8') as f:
            f.write(new_content)
        
        print(f"成功处理: {args.input} -> {args.output}")
        sys.exit(0)
    
    except Exception as e:
        print(f"处理文件 {args.input} 时出错: {str(e)}")
        sys.exit(1)

if __name__ == '__main__':
    main()
