from setuptools import setup


setup(
    name='lavalink',
    packages=['lavalink'],
    version='2.1.6',
    description='A lavalink interface built for discord.py',
    author='Luke, William',
    author_email='luke@serux.pro',
    url='https://github.com/Devoxin/Lavalink.py',
    download_url='https://github.com/Devoxin/Lavalink.py/archive/2.1.6.tar.gz',
    keywords=['lavalink'],
    include_package_data=True,
    install_requires=['websockets>=4.0.0,<5.0.0', 'aiohttp']
)
