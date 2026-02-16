import sys
import io
import threading
import traceback
import resource
from contextlib import contextmanager
import importlib


class TimeoutException(Exception):
    """代码执行超时异常"""
    pass


class CodeExecutor:
    def __init__(self, timeout=5, memory_limit=50*1024*1024):
        self.timeout = timeout
        self.memory_limit = memory_limit

    @contextmanager
    def time_limit(self, seconds):
        """使用线程定时器实现超时控制,适用于子线程环境"""
        timeout_occurred = threading.Event()

        def timeout_handler():
            timeout_occurred.set()
            raise TimeoutException(f"代码执行超时({seconds}秒)")

        timer = threading.Timer(seconds, timeout_handler)
        timer.start()
        try:
            yield
        finally:
            timer.cancel()

    def set_memory_limit(self):
        try:
            resource.setrlimit(resource.RLIMIT_AS, (self.memory_limit, self.memory_limit))
        except Exception:
            pass

    def execute(self, code, test_cases=None):
        result = {
            'status': 'pending',
            'output': '',
            'error_message': '',
            'test_results': [],
            'execution_time': 0,
            'memory_usage': 0
        }

        old_stdout = sys.stdout
        old_stderr = sys.stderr
        sys.stdout = io.StringIO()
        sys.stderr = io.StringIO()

        try:
            self.set_memory_limit()

            allowed_modules = {'math', 'random', 'datetime', 'statistics', 're'}

            def safe_import(name, globals=None, locals=None, fromlist=(), level=0):
                base = name.split('.')[0]
                if base not in allowed_modules:
                    raise ImportError(f'禁止导入模块: {base}')
                return importlib.import_module(name)

            # 获取原始的 __build_class__ (Python 3.11+)
            build_class = __builtins__['__build_class__'] if isinstance(__builtins__, dict) else __builtins__.__build_class__

            restricted_globals = {
                '__builtins__': {
                    # 基础类型和转换
                    'print': print,
                    'range': range,
                    'len': len,
                    'int': int,
                    'float': float,
                    'str': str,
                    'list': list,
                    'dict': dict,
                    'tuple': tuple,
                    'set': set,
                    'frozenset': frozenset,
                    'bool': bool,
                    'bytes': bytes,
                    'bytearray': bytearray,
                    'memoryview': memoryview,
                    'type': type,
                    'isinstance': isinstance,
                    'issubclass': issubclass,
                    'hasattr': hasattr,
                    'getattr': getattr,
                    'setattr': setattr,
                    'delattr': delattr,
                    'property': property,
                    # 数学运算
                    'abs': abs,
                    'max': max,
                    'min': min,
                    'sum': sum,
                    'pow': pow,
                    'round': round,
                    'divmod': divmod,
                    'bin': bin,
                    'oct': oct,
                    'hex': hex,
                    'ord': ord,
                    'chr': chr,
                    # 序列操作
                    'sorted': sorted,
                    'reversed': reversed,
                    'enumerate': enumerate,
                    'zip': zip,
                    'map': map,
                    'filter': filter,
                    'next': next,
                    'iter': iter,
                    'all': all,
                    'any': any,
                    # 对象操作
                    'id': id,
                    'hash': hash,
                    'repr': repr,
                    'format': format,
                    'vars': vars,
                    'dir': dir,
                    'help': help,
                    # 类的创建(必须)
                    '__build_class__': build_class,
                    # 其他
                    'open': None,  # 禁用文件操作
                    '__import__': safe_import,
                    '__name__': '__main__',
                    '__doc__': None,
                    '__package__': None,
                    '__spec__': None,
                    'True': True,
                    'False': False,
                    'None': None,
                    'Exception': Exception,
                }
            }

            with self.time_limit(self.timeout):
                exec(code, restricted_globals)

            output = sys.stdout.getvalue()
            error = sys.stderr.getvalue()

            if error:
                result['status'] = 'error'
                result['error_message'] = error
            else:
                result['status'] = 'passed'
                result['output'] = output

        except TimeoutException as e:
            result['status'] = 'error'
            result['error_message'] = str(e)
        except MemoryError:
            result['status'] = 'error'
            result['error_message'] = '内存使用超出限制'
        except Exception as e:
            result['status'] = 'error'
            result['error_message'] = f"{type(e).__name__}: {str(e)}\n{traceback.format_exc()}"
        finally:
            sys.stdout = old_stdout
            sys.stderr = old_stderr

        return result

    def validate_code(self, code):
        forbidden_keywords = [
            'import os', 'import sys', 'import subprocess',
            'import socket', 'import requests',
            'eval', 'exec',
            'open(', 'file(', 'input(',
        ]
        lower = code.lower()
        for kw in forbidden_keywords:
            if kw in lower:
                return False, f'禁止使用: {kw}'

        # 特殊处理 compile 关键字，允许 re.compile 但禁止内置 compile 函数
        import re
        compile_pattern = r'(?<!\.)\bcompile\s*\('  # 匹配不是以 . 结尾的 compile(
        if re.search(compile_pattern, code):
            return False, '禁止使用: compile'

        return True, ''