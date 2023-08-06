# coding: utf-8
from functools import wraps, partial

from werkzeug.exceptions import BadRequest
from werkzeug.local import LocalProxy
from flask import request, current_app, _app_ctx_stack

from commony import PropertyDict, instance_args


@instance_args
def validate_request(in_schema, query=True, body=True, json_body=True):
    """装饰器将 Flask 请求数据根据 in_schema 验证并将有效数据以名为 request_data 的关键字参数传递给函数"""
    def decorator(func):
        @wraps(func)
        def decoration_function(*args, **kwargs):
            data = _get_request_data(query, body, json_body)
            valid_data, errors = in_schema.load(data)
            if errors:
                raise BadRequest({'errors': errors})
            data = PropertyDict(**valid_data)
            return func(*args, request_data=data, **kwargs)
        return decoration_function
    return decorator


def jsonify(func=None, **options):
    """装饰器对函数的返回结果使用 flask.jsonify 转换"""
    from flask import jsonify as jsonify_

    if func is None:
        return partial(jsonify, **options)

    @wraps(func)
    def decorated_function(*args, **kwargs):
        return jsonify_(func(*args, **kwargs), **kwargs)

    return decorated_function


def extension(name):
    return LocalProxy(lambda: current_app.extensions[name])


def model(name):
    return LocalProxy(lambda: getattr(current_app.extensions['pony'], name))


def _get_request_data(query, body, json_body):
    result = {}
    if query:
        query_data = request.args.to_dict(flat=False)
        result.update(**query_data)
    if body:
        body_data = request.get_json(force=True) if json_body else request.form.to_dict(flat=False)
        result.update(**body_data)
    return result
