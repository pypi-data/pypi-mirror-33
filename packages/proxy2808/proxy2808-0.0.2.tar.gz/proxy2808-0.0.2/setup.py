from setuptools import setup, find_packages

setup(
    name='proxy2808',
    version='0.0.2',
    description=(
        '2808 http/socks5 proxy'
    ),
    long_description=open('README.rst').read(),
    author='huang dao xu',
    author_email='382619605@qq.com',
    maintainer='huang dao xu',
    maintainer_email='382619605@qq.com',
    license='BSD License',
    packages=find_packages(),
    platforms=["all"],
    url='https://www.2808proxy.com',
    classifiers=[
        'Programming Language :: Python :: 3.5',
        'Programming Language :: Python :: 3.6',
    ],
    install_requires=[
        'requests',
    ]
)

