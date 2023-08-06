from setuptools import setup
VERSION = "0.0.3.9"
setup(
    name='dict-to-protobuf',
    description='A teeny Python library for creating protobuf dicts from '
        'python dict. Useful when need to put dict on socket transmission.' 
        'You can not directly json a protobuf message object, it\'s not hashable'
        ,
    version=VERSION,
    author='davy zhang',
    author_email='davyzhang@gmail.com',
    maintainer='Dan Bauman',
    maintainer_email="dan@bauman.space",
    url='https://github.com/davyzhang/dict-to-protobuf',
    download_url='https://github.com/bauman/dict-to-protobuf/archive/%s.tar.gz' % (VERSION),
    license='Public Domain',
    keywords=['protobuf', 'dict'],
    install_requires=['protobuf>=2.3.0', "six"],
    package_dir={'':'src'},
    py_modules=['dict_to_protobuf'],
    classifiers=[
        'Programming Language :: Python',
        'Development Status :: 4 - Beta',
        'Intended Audience :: Developers',
        'License :: Public Domain',
        'Operating System :: OS Independent',
        'Topic :: Software Development :: Libraries :: Python Modules',
    ],
)
