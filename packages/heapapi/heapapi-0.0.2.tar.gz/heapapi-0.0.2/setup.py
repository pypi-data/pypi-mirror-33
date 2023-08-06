from setuptools import setup, find_packages


VERSION = '0.0.2'


setup(
    name='heapapi',
    version=VERSION,
    description='Heap Analytics Python SDK (unofficial)',
    author='Maxime Vdb',
    author_email='me@maxvdb.com',
    packages=find_packages(),
    install_requires=['requests'],
    license="MIT",
    keywords="heap analytics api sdk",
    url='https://github.com/m-vdb/heap-analytics-python-client',
    download_url='https://github.com/m-vdb/heap-analytics-python-client/archive/v{}.tar.gz'.format(VERSION),
    project_urls={
        "Source Code": "https://github.com/m-vdb/heap-analytics-python-client",
    }
)
