from flask import request

from opentracing_instrumentation.client_hooks.requests import install_patches
from flask_opentracing import FlaskTracer
from jaeger_client import Config
from opentracing_instrumentation.request_context import RequestContextManager


def initialize_tracer(name):
    cfg = Config(
        config={
            'sampler': {'type': 'const', 'param': 1},
            'local_agent': {'reporting_host': 'jaeger'}
        },
        service_name=name
    )
    return cfg.initialize_tracer()


def initialize(app, name):
    install_patches()

    tracer = initialize_tracer(name)
    ftracer = FlaskTracer(tracer, False, app)
    return tracer, ftracer


def trace(tracer, ftracer):
    def decorator(f):
        def wrapper(*args, **kwargs):
            pspan = ftracer.get_span(request)
            with RequestContextManager(span=pspan):
                return f(*args, **kwargs)
        return ftracer.trace()(wrapper)
    return decorator


class GrTracer(object):
    def __init__(self, app, name):
        self.app = app
        self.tracer, self.ftracer = initialize(app, name)

    def trace(self, func):
        return trace(self.tracer, self.ftracer)(func)

    def bootstrap(self):
        for k, f in self.app.view_functions.items():
            self.app.view_functions[k] = self.trace(f)
