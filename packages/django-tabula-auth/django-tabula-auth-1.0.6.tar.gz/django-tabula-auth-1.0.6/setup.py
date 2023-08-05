import os
from setuptools import find_packages, setup
from tabula_auth import __version__

with open(os.path.join(os.path.dirname(__file__), 'README.rst')) as readme:
    README = readme.read()

os.chdir(os.path.normpath(os.path.join(os.path.abspath(__file__), os.pardir)))
install_requires = ['Django>=2.0', 'django-phonenumber-field==2.0', 'twilio', 'freezegun', 'djangorestframework-jwt',  
                    'djangorestframework==3.8.2']

setup(
    name='django-tabula-auth',
    version=__version__,
    packages=find_packages(),
    include_package_data=True,
    install_requires=install_requires,

    license='BSD License',  # example license
    description='A simple Django app to conduct Web-based polls.',
    long_description=README,
    long_description_content_type="text/markdown",
    test_suite = "test_auth.runtests.runtests",

    # url='https://www.example.com/',
    author='Danil Lugovskou',
    author_email='danil@tar.fund',
    classifiers=[
        'Environment :: Web Environment',
        'Framework :: Django',
        'Framework :: Django :: 2.0', 
        'Intended Audience :: Developers',
        'License :: OSI Approved :: BSD License',  # example license
        'Operating System :: OS Independent',
        'Programming Language :: Python',
        'Programming Language :: Python :: 3.5',
        'Programming Language :: Python :: 3.6',
        'Topic :: Internet :: WWW/HTTP',
        'Topic :: Internet :: WWW/HTTP :: Dynamic Content',
    ],
)
