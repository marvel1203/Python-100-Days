"""
Python代码执行引擎
使用安全的沙箱环境执行用户提交的代码
"""
import sys
import io
import signal
import traceback
import resource
from contextlib import contextmanager
import json


class CodeExecutor:
    """代码执行器"""
    
    def __init__(self, timeout=5, memory_limit=50*1024*1024):
        """
        初始化代码执行器
        :param timeout: 超时时间(秒)
        :param memory_limit: 内存限制(字节)
        """
        self.timeout = timeout
        self.memory_limit = memory_limit
    
    @contextmanager
    def time_limit(self, seconds):
        """时间限制上下文管理器"""
        def signal_handler(signum, frame):
            raise TimeoutError(f"代码执行超时({seconds}秒)")
        
        signal.signal(signal.SIGALRM, signal_handler)
        signal.alarm(seconds)
        try:
            yield
        finally:
            signal.alarm(0)
    
    def set_memory_limit(self):
        """设置内存限制"""
        try:
            resource.setrlimit(resource.RLIMIT_AS, (self.memory_limit, self.memory_limit))
        except Exception:
            pass  # Windows不支持resource模块
    
    def execute(self, code, test_cases=None):
        """
        执行代码
        :param code: 要执行的Python代码
        :param test_cases: 测试用例列表 [{'input': {...}, 'expected_output': ...}, ...]
        :return: 执行结果字典
        """
        result = {
            'status': 'pending',
            'output': '',
            'error_message': '',
            'test_results': [],
            'execution_time': 0,
            'memory_usage': 0
        }
        
        # 捕获标准输出
        old_stdout = sys.stdout
        old_stderr = sys.stderr
        sys.stdout = io.StringIO()
        sys.stderr = io.StringIO()
        
        try:
            # 设置内存限制
            self.set_memory_limit()
            
            # 创建受限的全局命名空间
            restricted_globals = {
                '__builtins__': {
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
                    'abs': abs,
                    'max': max,
                    'min': min,
                    'sum': sum,
                    'sorted': sorted,
                    'enumerate': enumerate,
                    'zip': zip,
                    'map': map,
                    'filter': filter,
                    'True': True,
                    'False': False,
                    'None': None,
                }
            }
            
            # 执行代码
            with self.time_limit(self.timeout):
                exec(code, restricted_globals)
            
            # 获取输出
            output = sys.stdout.getvalue()
            error = sys.stderr.getvalue()
            
            if error:
                result['status'] = 'error'
                result['error_message'] = error
            else:
                result['status'] = 'passed'
                result['output'] = output
            
            # 如果有测试用例，运行测试
            if test_cases:
                result['test_results'] = self.run_tests(code, test_cases, restricted_globals)
                # 检查是否所有测试都通过
                if all(test['passed'] for test in result['test_results']):
                    result['status'] = 'passed'
                else:
                    result['status'] = 'failed'
        
        except TimeoutError as e:
            result['status'] = 'error'
            result['error_message'] = str(e)
        
        except MemoryError:
            result['status'] = 'error'
            result['error_message'] = '内存使用超出限制'
        
        except Exception as e:
            result['status'] = 'error'
            result['error_message'] = f"{type(e).__name__}: {str(e)}\n{traceback.format_exc()}"
        
        finally:
            # 恢复标准输出
            sys.stdout = old_stdout
            sys.stderr = old_stderr
        
        return result
    
    def run_tests(self, code, test_cases, globals_dict):
        """
        运行测试用例
        :param code: 已执行的代码
        :param test_cases: 测试用例
        :param globals_dict: 全局命名空间
        :return: 测试结果列表
        """
        results = []
        
        for i, test_case in enumerate(test_cases):
            test_result = {
                'test_name': test_case.get('name', f'测试用例 {i+1}'),
                'passed': False,
                'input': test_case.get('input', {}),
                'expected_output': test_case.get('expected_output'),
                'actual_output': None,
                'error': None
            }
            
            try:
                # 获取测试输入
                test_input = test_case.get('input', {})
                expected_output = test_case.get('expected_output')
                
                # 如果有函数名，调用函数
                function_name = test_case.get('function_name')
                if function_name and function_name in globals_dict:
                    func = globals_dict[function_name]
                    
                    # 根据输入类型调用函数
                    if isinstance(test_input, dict):
                        actual_output = func(**test_input)
                    elif isinstance(test_input, (list, tuple)):
                        actual_output = func(*test_input)
                    else:
                        actual_output = func(test_input)
                    
                    test_result['actual_output'] = actual_output
                    
                    # 比较输出
                    if actual_output == expected_output:
                        test_result['passed'] = True
                    else:
                        test_result['error'] = f'期望输出: {expected_output}, 实际输出: {actual_output}'
                else:
                    test_result['error'] = f'未找到函数: {function_name}'
            
            except Exception as e:
                test_result['error'] = f"{type(e).__name__}: {str(e)}"
            
            results.append(test_result)
        
        return results
    
    def validate_code(self, code):
        """
        验证代码安全性
        :param code: 要验证的代码
        :return: (is_valid, error_message)
        """
        # 禁止的关键字和模块
        forbidden_keywords = [
            'import os', 'import sys', 'import subprocess', 
            'import socket', 'import requests',
            '__import__', 'eval', 'exec', 'compile',
            'open(', 'file(', 'input(',
        ]
        
        code_lower = code.lower()
        for keyword in forbidden_keywords:
            if keyword.lower() in code_lower:
                return False, f'禁止使用: {keyword}'
        
        return True, ''
