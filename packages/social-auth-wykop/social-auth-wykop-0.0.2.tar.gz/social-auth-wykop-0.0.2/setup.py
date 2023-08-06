from setuptools import setup, find_packages


setup(
    name='social-auth-wykop',
    version='0.0.2',
    packages=find_packages(),
    author='Krzysztof @noisy Szumny',
    author_email='noisy.pl@gmail.com',
    description='Wykop backend for python-social-auth.',
    long_description=open('README.md').read(),
    license='LICENSE',
    url='https://github.com/noisy/python-social-auth-wykop',
    keywords='django social auth oauth2 social-auth wykop wykop.pl',
    classifiers=[
        'Development Status :: 3 - Alpha',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: MIT License',
        'Programming Language :: Python :: 3.6',
    ],
    install_requires=[
        'python-social-auth',
        'wykop-sdk'
    ]
)
