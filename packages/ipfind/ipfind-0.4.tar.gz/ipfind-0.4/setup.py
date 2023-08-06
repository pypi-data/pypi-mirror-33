from setuptools import setup, find_packages

setup(
    name='ipfind',
    packages=find_packages(),
    version='0.4',
    description='simple tools by MrY86 and Mr.K3R3H',
    author='MrY86',
    author_email='www.mryama@gmail.com',
    url='https://github.com/MrY86',
    download_url='https://github.com/MrY86',
    keywords=['dev3l', 'archetype', 'pypi', 'package'],  # arbitrary keywords
    install_requires=[
        'pytest==2.9.2'
    ],
    classifiers=[
        'Environment :: Console',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: MIT License',
        'Operating System :: OS Independent',
        'Programming Language :: Python',
        'Programming Language :: Python :: 2',
        'Programming Language :: Python :: 3',
        'Topic :: Software Development :: Libraries :: Python Modules'],
    entry_points={
        'console_scripts': [
            'ipfind = ipfind.ipfind:menu'
        ]},
)