from setuptools import setup

setup(name='TM_CommonPy'
    ,version='0.1'
    ,description='Troy1010\'s common python library'
    ,author='Troy1010'
    #,author_email=''
    ,url='https://github.com/Troy1010/TM_CommonPy'
    ,license='MIT'
    ,packages=['TM_CommonPy']
    ,zip_safe=False
    ,test_suite='nose.collector'
    ,tests_require=['nose']
    ,python_requires=">=3.6"
    ,setup_requires=['nose']
    )
