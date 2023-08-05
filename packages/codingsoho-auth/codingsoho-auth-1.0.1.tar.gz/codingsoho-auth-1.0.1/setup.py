import os
from setuptools import find_packages, setup

with open(os.path.join(os.path.dirname(__file__), 'README.rst')) as readme:
    README = readme.read()

REQUIREMENTS = [i.strip() for i in open("requirements.txt").readlines()]

# allow setup.py to be run from any path
os.chdir(os.path.normpath(os.path.join(os.path.abspath(__file__), os.pardir)))

setup(
    name='codingsoho-auth',
    version='1.0.1',
    packages=find_packages(),
    include_package_data=True,
    license='BSD License',  # example license
    description='this project is wrapper for auth',
    long_description=README,
    url='http://www.codingsoho.com/',
    author='Horde Chief',
    author_email='hordechief@qq.com',
	install_requires=REQUIREMENTS,
    classifiers=[
        'Environment :: Web Environment',
        'Framework :: Django',
        'Framework :: Django :: 1.11',  # replace "X.Y" as appropriate
        'Intended Audience :: Developers',
        'License :: OSI Approved :: BSD License',  # example license
        'Operating System :: OS Independent',
        'Programming Language :: Python',
        # Replace these appropriately if you are stuck on Python 2.
        'Programming Language :: Python :: 2',
        'Programming Language :: Python :: 2.7',
        'Topic :: Internet :: WWW/HTTP',
        'Topic :: Internet :: WWW/HTTP :: Dynamic Content',
    ],
)