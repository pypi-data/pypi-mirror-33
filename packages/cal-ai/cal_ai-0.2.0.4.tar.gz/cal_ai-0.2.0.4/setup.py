import setuptools


# Change this line to the module name you want to create
__title__ = "cal_ai"
__summary__ = "An end-to-end machine learning and data mining framework on Hadoop CAL."
__uri__ = "https://github.paypal.com/haifwu/LiveBoxMonitor"

__author__ = "Wu Haifeng"
__email__ = "wuhaifengdhu@163.com"

# Change the version when you want to release new version.
__version__ = "0.2.0.4"


with open("README.rst", "r") as fh:
    long_description = fh.read()


setuptools.setup(
    name=__title__,
    version=__version__,
    author=__author__,
    author_email=__email__,
    description=__summary__,
    long_description=long_description,
    long_description_content_type="text/markdown",
    url=__uri__,
    packages=setuptools.find_packages(),
    package_data={'cal_ai': ['README.rst', 'LICENCE']},
    classifiers=(
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
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
        'Programming Language :: Python :: 3.6',
        'Programming Language :: Python :: 3.7',
    ),
)