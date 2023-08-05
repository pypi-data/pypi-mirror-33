import io
from os.path import abspath, dirname, join
from setuptools import find_packages, setup


HERE = dirname(abspath(__file__))
LOAD_TEXT = lambda name: io.open(join(HERE, name), encoding='UTF-8').read()
DESCRIPTION = '\n\n'.join(LOAD_TEXT(_) for _ in [
    'README.md'
])
setup(
    name='tyo-mq-client',
    version='0.0.1',
    description='A tyo-mq client library',
    long_description=DESCRIPTION,
    license='MIT',
    classifiers=[
        'Intended Audience :: Developers',
        'Programming Language :: Python',
        'License :: OSI Approved :: MIT License',
        'Development Status :: 5 - Production/Stable',
    ],
    keywords='tyo-mq socket.io node.js',
    author='Eric Tang',
    author_email='eric.tang@tyo.com.au',
    url='https://github.com/tyolab/tyo-mq-client-python.git',
    install_requires=[
        'socketIO-client>=0.7.2',
        'invisibleroads-macros>=0.9.4.4'
    ],
    tests_require=[
        'nose',
        'coverage',
    ],
    packages=find_packages(),
    include_package_data=True,
    zip_safe=False)