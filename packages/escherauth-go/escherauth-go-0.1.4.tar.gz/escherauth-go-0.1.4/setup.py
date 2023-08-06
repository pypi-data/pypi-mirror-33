from setuptools import setup, Distribution

setup(
    name='escherauth-go',
    description='Python wrapper for the Go implementation of the AWS4 compatible Escher HTTP request signing protocol.',
    version='0.1.4',
    author='Istvan Szenasi',
    author_email='szeist@gmail.com',
    license='MIT',
    url='http://escherauth.io/',
    download_url='https://github.com/EscherAuth/escher-python',
    zip_safe=False,
    packages=['escherauth_go'],
    py_modules=['escherauth_go.escher_signer', 'escherauth_go.escher_validator'],
    package_data={
        'escherauth_go': ['*.so', '*.dylib']
    },
    classifiers=[
        'Development Status :: 4 - Beta',
        'Environment :: Console',
        'Programming Language :: Python',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: MIT License',
        'Topic :: Internet :: WWW/HTTP',
        'Topic :: Utilities'
    ],
)
