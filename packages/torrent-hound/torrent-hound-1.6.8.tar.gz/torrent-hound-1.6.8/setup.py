from setuptools import setup

def readme():
    with open('README.rst') as f:
        return f.read()

setup(
    name='torrent-hound',          # This is the name of your PyPI-package.
    version='1.6.8',                 # Update the version number for new releases
    scripts=['torrent-hound'],     # The name of your scipt, and also the command you'll be using for calling it
    description='Search torrents from multiple websites via the CLI',
    long_description=readme(),
    url='https://github.com/baddymaster/torrent-hound',
    install_requires=[
        'bs4',
        'requests',
        'clint',
        'pyperclip',
        'humanize',
        'VeryPrettyTable'
    ],
    author='Yashovardhan Sharma',
    author_email='yashovardhan@tuta.io',
    license='AGPL-3.0',
)