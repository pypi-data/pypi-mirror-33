import logging
import subprocess
import os
from setuptools import find_packages, setup


logging.basicConfig(level=logging.INFO)
log = logging.getLogger(__name__)


NAME = 'catchbot'
DESCRIPTION = 'Telegram bot to catch your hooks from Github, Gitlab and more'
URL = 'https://github.com/grihabor/catch-hook-telegram-bot'
EMAIL = 'grihabor@gmail.com'
AUTHOR = 'Borodin Gregory'

REQUIRED = [
    'python-telegram-bot==10.1.0',
    'flask==1.0.2',
    'gunicorn==19.8.1',
    'celery==4.2.0',
    'pyyaml==3.12',
    'beautifulsoup4',
    'requests==2.19.1',
    'furl==1.1',
]


def _get_project_path():
    return os.path.abspath(os.path.join(__file__, os.pardir))


def get_version():
    v = subprocess.check_output([
        "make",
        "--no-print-directory",
        "version-minor",
    ]).decode('utf-8').strip()
    log.info('Version {}'.format(v))
    return v


def get_readme():
    project_path = _get_project_path()
    readme_path = os.path.join(project_path, 'README.rst')
    with open(readme_path, 'r') as f:
        return f.read()


def main():
    setup(
        name=NAME,
        version=get_version(),
        description=DESCRIPTION,
        author=AUTHOR,
        author_email=EMAIL,
        url=URL,
        package_dir={'': 'src'},
        packages=find_packages('src'),
        install_requires=REQUIRED,
        setup_requires=[
            'pytest-runner',
        ],
        tests_require=[
            'pytest',
            'pytest-cov',
        ],
        include_package_data=True,
        license='MIT',
        long_description=get_readme(),
        classifiers=[
            "Intended Audience :: Developers",
            "License :: OSI Approved :: MIT License",
            "Programming Language :: Python :: 3",
            "Programming Language :: Python :: 3.6",
        ],
    )


if __name__ == '__main__':
    main()
