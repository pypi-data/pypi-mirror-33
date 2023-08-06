from setuptools import setup


def read_file():
    with open('README.rst',encoding='utf-8') as f:
        return f.read()


setup(name='xfdtest', version='1.0.3', description='niuB', packages=['xfdtest'], py_modules=['tool'], author='xf', author_email='1271454083@qq.com', long_description=read_file(), url='https://github.com')