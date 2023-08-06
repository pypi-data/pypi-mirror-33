from setuptools import setup


version = '1.0.2'

setup(
    name='django-mobi2',
    version=version,
    keywords='Django UserAgent',
    description='Django middleware and view decorator to detect phones and small-screen devices',
    long_description=open('README').read(),

    url='https://github.com/django-xxx/django-mobi2.git',

    author='Hackathon',
    author_email='kimi.huang@brightcells.com',

    packages=['mobi2'],
    py_modules=[],
    package_data={
        'mobi2': ['*.txt']
    },
    install_requires=['django-six'],

    classifiers=[
        'Development Status :: 5 - Production/Stable',
        'Environment :: Web Environment',
        'Framework :: Django',
        'Intended Audience :: Developers',
        'Programming Language :: Python',
        'Topic :: Software Development :: Libraries :: Python Modules',
        'Topic :: Office/Business :: Financial :: Spreadsheet',
    ],
)
