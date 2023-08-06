from setuptools import setup
import sys

if not sys.version_info[0] == 3 and sys.version_info[1] < 5:
    sys.exit('Python < 3.5 is not supported')

version = '0.1'

setup(
    name='steampy_by_eshao_for_fun',
    packages=['steampy', 'test', 'examples', ],
    version=version,
    description='A Steam lib for trade automation',
    author='Eshao',
    author_email='46996302@qq.com',
    license='MIT',
    url='https://github.com/eshao731/steampy',
    keywords=['steam', 'trade'],
    classifiers=[],
    install_requires=[
        "requests",
        "beautifulsoup4",
        "rsa",
        "pandas"
    ],
)
