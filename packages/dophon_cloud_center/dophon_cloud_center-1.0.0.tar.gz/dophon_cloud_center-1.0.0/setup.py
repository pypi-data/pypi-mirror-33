from setuptools import setup, find_packages

setup(
    name='dophon_cloud_center',
    version='1.0.0',
    packages=find_packages(),
    url='https://github.com/Ca11MeE/dophon_cloud_center',
    license='Apache 2.0',
    author='CallMeE',
    author_email='ealohu@163.com',
    description='dophon cloud reg center',
    install_requires=[
        'flask>=1.0.2',
        'schedule>=0.5.0',
        'urllib3>=1.23',
        'Flask_Bootstrap>=3.3.7.1'
    ]
)
