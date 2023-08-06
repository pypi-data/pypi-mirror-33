from setuptools import setup, find_packages

setup(
    name='dophon_cloud',
    version='1.0.0',
    packages=find_packages(),
    url='https://github.com/Ca11MeE/dophon_cloud',
    license='Apache 2.0',
    author='CallMeE',
    author_email='ealohu@163.com',
    description='dophon cloud(import reg center)',
    install_requires=[
        'dophon>=1.0.1',
        'dophon_cloud_center>=1.0.0'
    ]
)
