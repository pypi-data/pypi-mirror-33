from distutils.core import setup


def readme():
    with open('README.rst') as f:
        return f.read()


setup(
    name='optmatch',
    py_modules=['optmatch'],
    version='0.9.2',
    description='command line parsing library',
    author='coderazzi (LuisM Pena)',
    author_email='coderazzi@gmail.com',
    url='http://coderazzi.net/python/optmatch',
    long_description=readme(),
    keywords=['args', 'parsing', 'easy'],
    classifiers=[
        'Development Status :: 4 - Beta',
        'Intended Audience :: Developers',
        'Topic :: Software Development :: Build Tools',
        'License :: OSI Approved :: MIT License',
        'Programming Language :: Python :: 2',
        'Programming Language :: Python :: 3',
    ],
)
