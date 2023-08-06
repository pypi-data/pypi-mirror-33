from flask import request

from opentracing_instrumentation.client_hooks import install_patches
from flask_opentracing import FlaskTracer
from jaeger_client import Config
from opentracing_instrumentation.request_context import RequestContextManager


def initialize_tracer(name, host):
    cfg = Config(
        config={
            'sampler': {'type': 'const', 'param': 1},
            'local_agent': {'reporting_host': host}
        },
        service_name=name
    )
    return cfg.initialize_tracer()


def initialize(app, name, host):
    tracer = initialize_tracer(name, host)
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
    def __init__(self, app, name, patches, host):
        self.app = app
        self.tracer, self.ftracer = initialize(app, name, host)
        install_patches(list(map(lambda x: 'opentracing_instrumentation.client_hooks.%s.install_patches' % x, patches)))

    def trace(self, func):
        return trace(self.tracer, self.ftracer)(func)

    def bootstrap(self):
        for k, f in self.app.view_functions.items():
            self.app.view_functions[k] = self.trace(f)
