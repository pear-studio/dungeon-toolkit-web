"""
HTML 预处理脚本

将 Word 转换的复杂 HTML 转换为纯文本格式，方便后续处理。
支持批量处理文件夹，输出 UTF-8 编码的 .txt 文件，与源 HTML 一一对应。

用法:
    python html_to_txt.py <源文件夹路径> [--output <输出文件夹路径>]
    python html_to_txt.py rules_source/DND5e_chm/玩家手册/职业 --output rules_source/DND5e_chm/玩家手册/职业/txt
"""

import os
import re
import sys
from pathlib import Path


def extract_text_from_html(html_content: str) -> str:
    """从 HTML 中提取纯文本，保留基本结构"""
    text = html_content

    text = re.sub(r'<head[^>]*>.*?</head>', '', text, flags=re.DOTALL | re.IGNORECASE)

    text = re.sub(r'<style[^>]*>.*?</style>', '', text, flags=re.DOTALL | re.IGNORECASE)

    text = re.sub(r'<script[^>]*>.*?</script>', '', text, flags=re.DOTALL | re.IGNORECASE)

    text = re.sub(r'<meta[^>]*>', '', text, flags=re.IGNORECASE)

    text = re.sub(r'<font[^>]*>', '', text, flags=re.IGNORECASE)
    text = re.sub(r'</font>', '', text, flags=re.IGNORECASE)

    text = re.sub(r'<span[^>]*>', '', text, flags=re.IGNORECASE)
    text = re.sub(r'</span>', '', text, flags=re.IGNORECASE)

    text = re.sub(r'<div[^>]*>', '\n', text, flags=re.IGNORECASE)
    text = re.sub(r'</div>', '', text, flags=re.IGNORECASE)

    text = re.sub(r'<p[^>]*>', '\n', text, flags=re.IGNORECASE)
    text = re.sub(r'</p>', '\n', text, flags=re.IGNORECASE)

    text = re.sub(r'<br\s*/?>', '\n', text, flags=re.IGNORECASE)
    text = re.sub(r'<hr\s*/?>', '\n---\n', text, flags=re.IGNORECASE)

    text = re.sub(r'<tr[^>]*>', '\n', text, flags=re.IGNORECASE)
    text = re.sub(r'</tr>', '\n', text, flags=re.IGNORECASE)
    text = re.sub(r'<td[^>]*>', ' | ', text, flags=re.IGNORECASE)
    text = re.sub(r'</td>', '', text, flags=re.IGNORECASE)
    text = re.sub(r'<th[^>]*>', ' ** ', text, flags=re.IGNORECASE)
    text = re.sub(r'</th>', ' ** ', text, flags=re.IGNORECASE)

    text = re.sub(r'<h1[^>]*>', '\n# ', text, flags=re.IGNORECASE)
    text = re.sub(r'</h1>', '\n', text, flags=re.IGNORECASE)
    text = re.sub(r'<h2[^>]*>', '\n## ', text, flags=re.IGNORECASE)
    text = re.sub(r'</h2>', '\n', text, flags=re.IGNORECASE)
    text = re.sub(r'<h3[^>]*>', '\n### ', text, flags=re.IGNORECASE)
    text = re.sub(r'</h3>', '\n', text, flags=re.IGNORECASE)
    text = re.sub(r'<h4[^>]*>', '\n#### ', text, flags=re.IGNORECASE)
    text = re.sub(r'</h4>', '\n', text, flags=re.IGNORECASE)

    text = re.sub(r'<b[^>]*>', '**', text, flags=re.IGNORECASE)
    text = re.sub(r'</b>', '**', text, flags=re.IGNORECASE)
    text = re.sub(r'<strong[^>]*>', '**', text, flags=re.IGNORECASE)
    text = re.sub(r'</strong>', '**', text, flags=re.IGNORECASE)
    text = re.sub(r'<i[^>]*>', '*', text, flags=re.IGNORECASE)
    text = re.sub(r'</i>', '*', text, flags=re.IGNORECASE)

    text = re.sub(r'<a[^>]*>', '', text, flags=re.IGNORECASE)
    text = re.sub(r'</a>', '', text, flags=re.IGNORECASE)

    text = re.sub(r'<table[^>]*>', '\n', text, flags=re.IGNORECASE)
    text = re.sub(r'</table>', '\n', text, flags=re.IGNORECASE)
    text = re.sub(r'<tbody[^>]*>', '', text, flags=re.IGNORECASE)
    text = re.sub(r'</tbody>', '', text, flags=re.IGNORECASE)

    text = re.sub(r'<!--.*?-->', '', text, flags=re.DOTALL)

    text = re.sub(r'<[^>]+>', '', text)

    text = re.sub(r'&nbsp;', ' ', text)
    text = re.sub(r'&amp;', '&', text)
    text = re.sub(r'&lt;', '<', text)
    text = re.sub(r'&gt;', '>', text)
    text = re.sub(r'&quot;', '"', text)
    text = re.sub(r'&#\d+;', '', text)

    text = re.sub(r'\n\s*\n', '\n\n', text)
    text = re.sub(r' +', ' ', text)

    lines = text.split('\n')
    result = []
    for line in lines:
        line = line.strip()
        if line:
            result.append(line)
    return '\n\n'.join(result)


def process_file(input_path: str, output_path: str) -> bool:
    """处理单个 HTML 文件"""
    try:
        with open(input_path, 'r', encoding='gbk', errors='ignore') as f:
            html_content = f.read()
    except Exception as e:
        print(f"  [错误] 读取文件失败: {e}")
        return False

    text = extract_text_from_html(html_content)

    os.makedirs(os.path.dirname(output_path), exist_ok=True)

    with open(output_path, 'w', encoding='utf-8') as f:
        f.write(text)

    return True


def process_folder(source_folder: str, output_folder: str = None) -> dict:
    """批量处理文件夹中的所有 HTML 文件"""
    source_path = Path(source_folder)

    if output_folder:
        output_path = Path(output_folder)
    else:
        output_path = source_path

    if not source_path.exists():
        print(f"错误: 源文件夹不存在: {source_folder}")
        return {"error": "源文件夹不存在"}

    html_files = list(source_path.glob("*.html"))
    if not html_files:
        html_files = list(source_path.glob("*.htm"))

    if not html_files:
        print(f"警告: 源文件夹中没有找到 HTML 文件: {source_folder}")
        return {"total": 0, "success": 0, "failed": 0}

    print(f"找到 {len(html_files)} 个 HTML 文件")
    print(f"输出目录: {output_path}")
    print("-" * 40)

    success = 0
    failed = 0

    for html_file in sorted(html_files):
        output_file = html_file.with_suffix('.txt')

        print(f"处理: {html_file.name} -> {output_file.name}", end=" ... ")

        if process_file(str(html_file), str(output_file)):
            print("✓")
            success += 1
        else:
            print("✗")
            failed += 1

    result = {
        "total": len(html_files),
        "success": success,
        "failed": failed,
        "output_folder": str(output_path)
    }

    print("-" * 40)
    print(f"完成: {success} 成功, {failed} 失败")
    print(f"输出目录: {output_path}")

    return result


def main():
    if len(sys.argv) < 2:
        print(__doc__)
        sys.exit(1)

    source_folder = sys.argv[1]
    output_folder = None

    if len(sys.argv) >= 4 and sys.argv[2] == '--output':
        output_folder = sys.argv[3]

    print(f"源文件夹: {source_folder}")
    if output_folder:
        print(f"输出文件夹: {output_folder}")
    print("=" * 40)

    result = process_folder(source_folder, output_folder)

    if "error" in result:
        print(f"错误: {result['error']}")
        sys.exit(1)


if __name__ == '__main__':
    main()
