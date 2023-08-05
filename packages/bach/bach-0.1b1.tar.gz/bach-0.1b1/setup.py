from setuptools import setup

setup(name='bach',
    version='0.1b1',
    description='An XML-interoperable general-purpose semantic document markup language*',
    long_description='An XML-interoperable general-purpose semantic document markup language*',
    url='https://github.com/tawesoft/bach',
    author='Ben Golightly',
    author_email='ben@tawesoft.co.uk',
    maintainer='Tawesoft Ltd',
    maintainer_email='opensource@tawesoft.co.uk',
    license='MIT',
    packages=['python/bach'],
    classifiers=[
        'Development Status :: 4 - Beta',
        'Intended Audience :: Developers',
        'License :: OSI Approved',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.4',
        'Topic :: Software Development :: Libraries :: Python Modules',
        'Topic :: Documentation',
        'Topic :: Office/Business',
        'Topic :: Software Development :: Interpreters',
        'Topic :: Text Processing :: Markup',
        'Topic :: Text Processing :: Markup :: XML'
    ],
    zip_safe=True)
