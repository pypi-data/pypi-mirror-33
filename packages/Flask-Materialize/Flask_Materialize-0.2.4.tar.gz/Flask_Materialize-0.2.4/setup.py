import os

from setuptools import setup


def read(fname):
    return open(os.path.join(os.path.dirname(__file__), fname)).read()


setup(
    name='Flask_Materialize',
    version='0.2.4',
    url='https://bitbucket.org/cyberspy/flask_materialize',
    license='MIT',
    author='Adam Cadman',
    author_email='cyberspy.oss@gmx.com',
    description='An extension that includes Materialize CSS (http://materializecss.com/) in your '
                'project, without any boilerplate code.',
    long_description=read('README.rst'),
    packages=['flask_materialize'],
    zip_safe=False,
    include_package_data=True,
    platforms='any',
    install_requires=[
        'Flask>=0.12',
        'Jinja2>=2.0',
    ],
    keywords="flask materialize materializecss material design css html layout bootstrap responsive widgets wtforms templates",
    classifiers=[
        'Environment :: Web Environment',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: MIT License',
        'Operating System :: OS Independent',
        'Framework :: Flask',
        'Development Status :: 5 - Production/Stable',
        'Programming Language :: Python',
        'Programming Language :: Python :: 2.7',
        'Programming Language :: Python :: 3',
        'Topic :: Internet :: WWW/HTTP :: Dynamic Content',
        'Topic :: Software Development :: Libraries :: Python Modules',
        'Topic :: Software Development :: User Interfaces',
    ]
)
