from setuptools import setup, find_packages

setup(
    name='pygments-shilldb',
    version='0.2',
    description='Pygments lexer for ShillDB.',
    author='Ezra Zigmond',
    url='https://github.com/hugomaiavieira/pygments-rspec',
    packages=find_packages(),
    install_requires=['pygments >= 2.2'],

    entry_points='''[pygments.lexers]
                    shilldb=pygments_shilldb:ShilldbLexer'''
)
