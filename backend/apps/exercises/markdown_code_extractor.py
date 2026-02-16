"""
Markdown代码提取器 - 从MD文件中提取代码块并验证可执行性
"""
import re
import os
from pathlib import Path
from .safe_executor import CodeExecutor


class MarkdownCodeExtractor:
    """从Markdown文件提取并验证Python代码"""

    # Python代码块正则 (支持```python和```标记)
    CODE_BLOCK_PATTERN = re.compile(
        r'```(?:python)?\s*\n(.*?)```',
        re.DOTALL
    )

    # 内联代码检测 (排除文件路径和URL)
    INLINE_CODE_PATTERN = re.compile(
        r'`([^`]+)`'
    )

    def __init__(self, timeout=5):
        self.timeout = timeout
        self.executor = CodeExecutor(timeout=timeout)

    def extract_code_blocks(self, content):
        """提取所有代码块"""
        blocks = []
        for match in self.CODE_BLOCK_PATTERN.finditer(content):
            code = match.group(1).strip()
            # 过滤掉非Python代码(如shell、sql等)
            if self._is_python_code(code):
                blocks.append(code)
        return blocks

    def _is_python_code(self, code):
        """判断是否为Python代码(排除明显非代码的内容)"""
        # 排除非常短的片段
        if len(code) < 10:
            return False
        # 排除纯文字说明
        python_keywords = ['def ', 'class ', 'import ', 'from ', 'if ', 'for ', 'while ', 'print(', '#']
        return any(kw in code for kw in python_keywords)

    def extract_from_file(self, file_path):
        """从文件提取代码"""
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()
        return self.extract_code_blocks(content)

    def extract_from_markdown_dir(self, dir_path, recursive=True):
        """从目录中提取所有MD文件的代码"""
        results = {}
        path = Path(dir_path)

        pattern = '**/*.md' if recursive else '*.md'
        for md_file in path.glob(pattern):
            codes = self.extract_from_file(md_file)
            if codes:
                results[str(md_file)] = {
                    'file': str(md_file),
                    'code_count': len(codes),
                    'codes': codes
                }

        return results

    def validate_code(self, code):
        """验证代码是否可执行"""
        is_valid, message = self.executor.validate_code(code)
        if not is_valid:
            return False, message

        # 尝试执行代码
        try:
            result = self.executor.execute(code)
            if result['status'] == 'passed':
                return True, result['output'].strip() if result['output'] else '执行成功(无输出)'
            else:
                return False, result['error_message']
        except Exception as e:
            return False, str(e)

    def validate_and_report(self, dir_path, recursive=True):
        """验证目录中所有代码并生成报告"""
        extracted = self.extract_from_markdown_dir(dir_path, recursive)
        report = {
            'total_files': len(extracted),
            'total_code_blocks': 0,
            'executable': 0,
            'failed': 0,
            'details': []
        }

        for file_path, info in extracted.items():
            file_report = {
                'file': file_path,
                'blocks': []
            }

            for i, code in enumerate(info['codes'], 1):
                is_valid, message = self.validate_code(code)
                block_result = {
                    'block': i,
                    'executable': is_valid,
                    'message': message[:200] if len(message) > 200 else message
                }
                file_report['blocks'].append(block_result)

                report['total_code_blocks'] += 1
                if is_valid:
                    report['executable'] += 1
                else:
                    report['failed'] += 1

            report['details'].append(file_report)

        return report


def extract_code_from_md(file_path):
    """从MD文件提取Python代码(简单封装)"""
    extractor = MarkdownCodeExtractor()
    return extractor.extract_from_file(file_path)


def validate_code_syntax(code):
    """验证代码语法(仅检查不执行)"""
    try:
        compile(code, '<string>', 'exec')
        return True, "语法正确"
    except SyntaxError as e:
        return False, f"语法错误: {e}"


if __name__ == '__main__':
    import sys

    if len(sys.argv) > 1:
        path = sys.argv[1]
        extractor = MarkdownCodeExtractor()

        if os.path.isfile(path) and path.endswith('.md'):
            # 验证单个文件
            codes = extractor.extract_from_file(path)
            print(f"找到 {len(codes)} 个代码块:\n")
            for i, code in enumerate(codes, 1):
                is_valid, msg = extractor.validate_code(code)
                print(f"--- 代码块 {i} ---")
                print(f"可执行: {is_valid}")
                print(f"结果: {msg}")
                print(code[:200])
                print()
        elif os.path.isdir(path):
            # 验证整个目录
            report = extractor.validate_and_report(path)
            print(f"文件数: {report['total_files']}")
            print(f"代码块: {report['total_code_blocks']}")
            print(f"可执行: {report['executable']}")
            print(f"失败: {report['failed']}")
    else:
        print("用法: python markdown_code_extractor.py <文件或目录>")
