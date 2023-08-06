from setuptools import setup


def readme():
    with open('README.rst') as f:
        return f.read()

setup(
    name='upersetter',
    version='0.8.6',
    url='https://github.com/vaubarth/upersetter',
    license='Mozilla Public License 2.0 (MPL 2.0)',
    author='Vincent Barth',
    author_email='vdbarth@posteo.at',
    description='upersetter helps with automating basic setup tasks for any kind of project in a general way.',
    long_description=readme(),
    classifiers=[
        'Programming Language :: Python :: 3 :: Only',
        'Programming Language :: Python :: 3.6',
        'License :: OSI Approved :: Mozilla Public License 2.0 (MPL 2.0)'
    ],
    packages=['upersetter'],
    install_requires=[
        'jinja2',
        'pyyaml',
        'dpath',
        'click',
        'anypath'
    ]
)