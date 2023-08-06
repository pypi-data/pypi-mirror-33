from setuptools import setup, find_packages

setup(
    name='opa',
    version='0.1',
    packages=find_packages(),
    include_package_data=True,
    install_requires=[
        'Click',
        'requests'
    ],
    entry_points='''
        [console_scripts]
        opa=opa:cli
    ''',
)

