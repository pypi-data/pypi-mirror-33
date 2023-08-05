from setuptools import setup, find_packages
 
 
setup(
    name='starttoday_intern',
    version='0.0.1',
    description='Recomend System of Movie',
    long_description='https://github.com/T11Kobayashi/starttoday_intern/README.md',
    author='Takumi Kobayashi',
    author_email='tk11@keio.jp',
    install_requires=[
        'numpy',
        'pandas',
        'scipy',
    ],
    url='https://github.com/T11Kobayashi/starttoday_intern/',
    packages=find_packages(exclude=('tests', 'docs'))
)
