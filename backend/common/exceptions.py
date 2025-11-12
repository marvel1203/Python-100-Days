"""
DRF 全局异常处理器
实现标准化错误响应并记录完整异常上下文
"""

import logging
import traceback
from django.utils.timezone import now
from rest_framework import status
from rest_framework.response import Response
from rest_framework.views import exception_handler as drf_exception_handler

logger = logging.getLogger(__name__)


def _build_error_payload(exc, context, default_status):
    """
    构造统一的错误响应载荷。

    参数:
    - exc: 异常实例
    - context: DRF 提供的上下文，包含 request 和 view
    - default_status: HTTP 状态码

    返回:
    - dict: 标准化的错误响应内容
    """
    request = context.get('request')
    view = context.get('view')
    message = str(exc) if exc else '服务内部错误'
    exc_class = f"{exc.__class__.__module__}.{exc.__class__.__name__}" if exc else 'Exception'

    return {
        'success': False,
        'code': exc_class,
        'message': message,
        'details': None,
        'path': getattr(request, 'path', None),
        'method': getattr(request, 'method', None),
        'view': getattr(view, '__class__', type(view)).__name__ if view else None,
        'timestamp': now().isoformat(),
        'status': default_status,
    }


def custom_exception_handler(exc, context):
    """
    自定义 DRF 异常处理函数。

    - 先委托 DRF 默认处理以覆盖常见异常类型（ValidationError、NotFound 等）。
    - 记录异常日志（包含堆栈、视图、请求方法与路径）。
    - 将错误响应格式化为统一结构。
    - 对未识别的异常统一返回 500，并附带简化的堆栈信息。
    """
    # 调用 DRF 默认异常处理
    response = drf_exception_handler(exc, context)

    # 记录完整异常上下文和堆栈
    logger.error(
        'API异常: %s | view=%s | path=%s | method=%s',
        exc,
        context.get('view'),
        getattr(context.get('request'), 'path', None),
        getattr(context.get('request'), 'method', None),
        exc_info=True,
    )

    if response is not None:
        # 使用统一格式包装 DRF 默认响应
        payload = _build_error_payload(exc, context, response.status_code)
        payload['details'] = response.data
        return Response(payload, status=response.status_code)

    # 未被 DRF 默认处理识别的异常，统一返回 500
    payload = _build_error_payload(exc, context, status.HTTP_500_INTERNAL_SERVER_ERROR)
    payload['details'] = {
        'traceback': traceback.format_exception_only(type(exc), exc)
    }
    return Response(payload, status=status.HTTP_500_INTERNAL_SERVER_ERROR)