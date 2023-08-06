# coding=utf-8

from setuptools import setup, find_packages

with open("README.md", "r") as fh:
    long_description = fh.read()

'''
setup(
    name="multiprocessing_log_manager",
    version="0.0.3",
    author="bfzs",
    author_email="909686719@qq.com",
    description="A small example package",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/pypa/example-project",
    packages=find_packages(),
    # classifiers=(
    #     "Programming Language :: Python :: 3",
    #     "License :: OSI Approved :: MIT License",
    #     "Operating System :: OS Independent",
    # ),
)



'''
setup(
    name='multiprocessing_log_manager',  # '<项目的名称>',
    version="0.1.1",
    description=(
        'Multi-process secure logs both in linux and windows'
    ),
    long_description=open('README.md', 'r').read(),
    long_description_content_type="text/markdown",
    author='bfzs',
    author_email='909686719@qq.com',
    maintainer='ydf',
    maintainer_email='909686719@qq.com',
    license='BSD License',
    # packages=['douban'], # 发布的包名
    packages=find_packages(),
    platforms=["all"],
    url='https://baike.baidu.com/item/%E9%82%93%E4%B8%BD%E5%90%9B/27007?fr=aladdin',
    classifiers=[
        'Development Status :: 4 - Beta',
        'Operating System :: OS Independent',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: BSD License',
        'Programming Language :: Python',
        'Programming Language :: Python :: Implementation',
        'Programming Language :: Python :: 2',
        'Programming Language :: Python :: 2.7',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.4',
        'Programming Language :: Python :: 3.5',
        'Programming Language :: Python :: 3.6',
        'Topic :: Software Development :: Libraries'
    ],
    install_requires=[
        'pymongo',
    ]
)
