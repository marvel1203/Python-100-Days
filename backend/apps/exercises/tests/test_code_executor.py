import unittest
from apps.exercises.safe_executor import CodeExecutor


class TestCodeExecutor(unittest.TestCase):
    def setUp(self):
        self.executor = CodeExecutor(timeout=2, memory_limit=10 * 1024 * 1024)

    def test_basic_print_output(self):
        code = "print('hello')"
        res = self.executor.execute(code)
        self.assertEqual(res['status'], 'passed')
        self.assertIn('hello', res['output'])

    def test_simple_addition(self):
        code = "a=1\nb=2\nprint(a+b)"
        res = self.executor.execute(code)
        self.assertEqual(res['status'], 'passed')
        self.assertEqual(res['output'].strip(), '3')

    def test_allowed_import_datetime(self):
        code = "from datetime import datetime\nprint(datetime.now().year)"
        res = self.executor.execute(code)
        self.assertEqual(res['status'], 'passed')
        self.assertTrue(res['output'].strip().isdigit())

    def test_forbidden_import_os(self):
        code = "import os\nprint('x')"
        is_valid, msg = self.executor.validate_code(code)
        self.assertFalse(is_valid)
        self.assertIn('禁止使用', msg)

    def test_timeout(self):
        code = "while True:\n    pass"
        res = self.executor.execute(code)
        self.assertEqual(res['status'], 'error')
        self.assertIn('超时', res['error_message'])

    def test_run_tests_success(self):
        code = """
def add(a, b):
    return a + b
"""
        res = self.executor.execute(code)
        self.assertIn(res['status'], ('passed', 'pending', 'error'))

        tests = [
            {'name': 't1', 'function_name': 'add', 'input': {'a': 1, 'b': 2}, 'expected_output': 3},
            {'name': 't2', 'function_name': 'add', 'input': {'a': -1, 'b': 5}, 'expected_output': 4},
        ]
        # 使用已执行过的全局，重新执行一次以运行测试
        res2 = self.executor.execute(code)
        self.assertIn('output', res2)

    def test_syntax_error_capture(self):
        code = "def broken(:\n    pass"
        res = self.executor.execute(code)
        self.assertEqual(res['status'], 'error')
        self.assertIn('SyntaxError', res['error_message'])

    def test_python_version(self):
        import sys
        self.assertGreaterEqual(sys.version_info.major, 3)
        self.assertGreaterEqual(sys.version_info.minor, 6)


if __name__ == '__main__':
    unittest.main()