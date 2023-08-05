from distutils.core import setup

setup(
    name='pycpi',
    py_modules=['pycpi'],
    version='0.1.0',
    description='Library for downloading CPI (Consumer Price Index) data',
    install_requires=[
        'requests>=2,<3',
    ],
    author='Dan Tao',
    author_email='daniel.tao@gmail.com',
    url='https://bitbucket.org/teamdtao/pycpi',
    keywords=[],
    classifiers=[],
)
