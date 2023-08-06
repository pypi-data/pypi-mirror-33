from setuptools import setup

installation_requirements = ['requests', 'requests-toolbelt', 'six']

try:
    import enum
    del enum
except ImportError:
    installation_requirements.append('enum')

with open('README.rst') as readme:
    long_description = readme.read()

with open('requirements.txt') as requirements:
    required = requirements.read().splitlines()


setup(
    name='pymessenger3',
    packages=['pymessenger3'],
    version='1.0.0',
    install_requires=required,
    description="Python Wrapper for Facebook Messenger Platform",
    long_description=long_description,
    author='Max Tomah',
    author_email='tekillermd@gmail.com',
    url='https://github.com/Cretezy/pymessenger2',
    license='MIT',
    download_url='https://github.com/Cretezy/pymessenger2/archive/v3.1.0.tar.gz',
    keywords=[
        'facebook messenger', 'python', 'wrapper', 'bot', 'messenger bot'
    ],
    classifiers=[], )
