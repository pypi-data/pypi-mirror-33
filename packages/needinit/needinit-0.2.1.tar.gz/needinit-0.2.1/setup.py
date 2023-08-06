import os
from setuptools import setup, find_packages

try:  # for pip >= 10
    from pip._internal.req import parse_requirements
except ImportError:  # for pip <= 9.0.3
    from pip.req import parse_requirements

try:  # for pip >= 10
    from pip._internal.download import PipSession
except ImportError:  # for pip <= 9.0.3
    from pip.download import PipSession


def get_requirements():
    req_file = os.path.join(os.path.dirname(__file__), "requirements.txt")
    if os.path.exists(req_file):
        requirements = parse_requirements(
            os.path.join(os.path.dirname(__file__), "requirements.txt"),
            session=PipSession())
        return [str(req.req) for req in requirements]
    return []


def get_version():
    __version__ = None
    with open('needinit/_version.py') as version_src:
        namespace = {}
        exec(version_src.read(), namespace)
        __version__ = namespace.get('__version__')
    return __version__


setup(
    name='needinit',
    version=get_version(),
    description='Prevent callability on un-initialized objects',
    url='https://github.com/steinnes/needinit',
    author='Steinn Eldjarn Sigurdarson',
    author_email='steinnes@gmail.com',
    keywords=['library', 'object initialization'],
    install_requires=get_requirements(),
    packages=find_packages(),
)
