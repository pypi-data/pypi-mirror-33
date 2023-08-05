from distutils.core import setup

from setuptools import find_packages

setup(
    name='downloader-py3',
    version='1.0.1',
    keywords='downloader dwonloader-py3',
    author='Bohan Zhang',
    author_email='zhangbohan.dell@gmail.com',
    url='https://github.com/ice1995/downloader-py3',
    project_urls={'Source': 'https://github.com/gtzampanakis/downloader'},
    py_modules=['downloader', 'memoize'],
    packages=find_packages(exclude=['contrib', 'docs', 'tests*', 'test*']),
    license='MIT',
    platforms='Any',
    python_requires='>=3',
    requires=[
        'lxml (> 3.2.1)',
    ],
    description='Download URLs using a compressed disk cache and a random throttling interval.',
    long_description=open('README').read(),
    classifiers=['Programming Language :: Python',
                 'License :: OSI Approved :: MIT License',
                 'Operating System :: OS Independent',
                 'Development Status :: 4 - Beta',
                 'Intended Audience :: Developers',
                 'Topic :: Internet :: WWW/HTTP',
                 'Topic :: Internet :: WWW/HTTP :: Indexing/Search',
                 ],
)
