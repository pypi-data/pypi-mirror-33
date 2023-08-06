# coding: utf-8

from setuptools import find_packages, setup


def install_requires():
    """
    Return requires in requirements.txt
    :return:
    """
    try:
        with open("requirements.txt") as f:
            return [line.strip() for line in f.readlines() if line.strip()]
    except OSError:
        return []

setup(
    name='paas-star',
    version='0.1.13',
    packages=find_packages('src'),
    package_dir={'': 'src'},
    include_package_data=True,
    install_requires=install_requires(),
    author='shichao.ma',
    author_email='shichao.ma@yiducloud.cn',
    description='''package description here''',
    entry_points={
        'console_scripts': [
            'paas-create = paas_star:main',
        ],
    },
    keywords='',
    
)