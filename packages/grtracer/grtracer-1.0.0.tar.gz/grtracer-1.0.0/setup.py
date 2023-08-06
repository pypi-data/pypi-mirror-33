from setuptools import setup

setup(
    name='grtracer',
    version='1.0.0',
    description='Simple tracing setup using Jaeger and Flask',
    url='https://github.com/ryzokuken/grtracer',
    author='Ujjwal Sharma',
    author_email='usharma1998@gmail.com',
    license='MIT',
    packages=['grtracer'],
    install_requires=[
        'flask',
        'flask_opentracing',
        'jaeger_client',
        'opentracing_instrumentation'
    ],
    zip_safe=False
)
