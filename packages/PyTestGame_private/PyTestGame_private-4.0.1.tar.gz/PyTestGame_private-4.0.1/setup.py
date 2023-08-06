#coding=utf-8
"""
部署本地PyPiserver -- 基于本地的Http服务器 创建私有仓库
创建 PyTestGame 的私有发行版
"""
import setuptools
#from distutils.core import setup

with open('README') as file: #读取README文件内容到readme字符串
    readme = file.read()

# NOTE: change the 'name' field below with some unique package name.
# then update the url field accordingly.
#通过元参数调用setup函数,实现软件安装
setuptools.setup(
    name='PyTestGame_private', #必需字段
    version='4.0.1',  #必需字段
    packages=['wargame'], #必需字段
    url='http://localhost:8081/simple',
    license='LICENSE.txt',
    description='test pkg private',
    long_description=readme,
    author='PythonTest',
    author_email='wangshilei@loongson.cn'
)

