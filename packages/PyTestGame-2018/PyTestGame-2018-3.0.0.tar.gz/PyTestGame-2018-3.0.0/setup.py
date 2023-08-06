#coding=utf-8
"""
测试用下面一条命令完成 注册项目\创建发行版\上传发行版
可能注册项目已经不需要
"""
import setuptools
#from distutils.core import setup

with open('README') as file: #读取README文件内容到readme字符串
    readme = file.read()

# NOTE: change the 'name' field below with some unique package name.
# then update the url field accordingly.
#通过元参数调用setup函数,实现软件安装
setuptools.setup(
    name='PyTestGame-2018', #必需字段
    version='3.0.0',  #必需字段
    packages=['wargame'], #必需字段
    url='https://testpypi.python.org/pypi/PyTestGame-2018/',
    license='LICENSE.txt',
    description='test pkg ignore',
    long_description=readme,
    author='PythonTest',
    author_email='wangshilei@loongson.cn'
)

