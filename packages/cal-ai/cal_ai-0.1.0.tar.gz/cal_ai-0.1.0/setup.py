import sys

reload(sys)
sys.setdefaultencoding('UTF8')

import io
from setuptools import setup
from setuptools.command.test import test as TestCommand
import sys

import cal_ai


class Tox(TestCommand):
    def finalize_options(self):
        TestCommand.finalize_options(self)
        self.test_args = []
        self.test_suite = True

    def run_tests(self):
        import tox
        errno = tox.cmdline(self.test_args)
        sys.exit(errno)


with io.open('README.md', encoding='UTF-8') as reader:
    readme = reader.read()


setup(
    name='cal_ai',
    version=cal_ai.__version__,
    description='Monitor live box.',
    long_description=readme,
    author='wu haifeng',
    author_email='wuhaifengdhu@163.com',
    url='https://github.paypal.com/haifwu/LiveBoxMonitor',
    py_modules=['cal_ai'],
    packages=[],
    package_data={},
    tests_require=['tox'],
    cmdclass={'test': Tox},
    license='Apache 2.0',
    install_requires=[],
    classifiers=[
        'Development Status :: 4 - Beta',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: Apache Software License',
        'Natural Language :: English',
        'Programming Language :: Python',
        'Programming Language :: Python :: 2',
        'Programming Language :: Python :: 2.6',
        'Programming Language :: Python :: 2.7',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.2',
        'Programming Language :: Python :: 3.3',
        'Programming Language :: Python :: 3.4',
        'Programming Language :: Python :: 3.5',
    ],
)
