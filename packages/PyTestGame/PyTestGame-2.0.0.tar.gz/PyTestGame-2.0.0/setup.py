#coding=utf-8
import setuptools
#from distutils.core import setup

with open('README') as file: #读取README文件内容到readme字符串
    readme = file.read()

# NOTE: change the 'name' field below with some unique package name.
# then update the url field accordingly.
#通过元参数调用setup函数,实现软件安装
setuptools.setup(
    name='PyTestGame', #必需字段
    version='2.0.0',  #必需字段
    packages=['wargame'], #必需字段
    url='https://testpypi.python.org/pypi/PyTestGame/',
    license='LICENSE.txt',
    description='test pkg ignore',
    long_description=readme,
    author='PythonTest',
    author_email='wangshilei@loongson.cn'
)

