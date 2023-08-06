from setuptools import setup

def readme():
    with open('README.md') as f:
        return f.read()

setup(name='tnthai',
    version='1.6',
    description='tnthai for Python',
    long_description=readme(),
    url='https://gitlab.thinknet.co.th/research/swathclone',
    author='Supphawit',
    author_email='supphawit@thinknet.co.th',
    license='Thinknet',
    install_requires=[
        'datrie',
    ],
    scripts=['bin/tnthai-run','bin/tnthai-test'],
    keywords='tnthai thinknet thai wordsegment',
    packages=['tnthai'],
    package_dir={'tnthai': 'src/tnthai'},
    package_data={
        'tnthai': ['swathclone/*','*.md','swathclone/dict/*.trie','swathclone/tests/*.py']
    },
)