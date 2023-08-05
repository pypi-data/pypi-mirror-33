import os
from setuptools import setup


readme_path = os.path.join(os.path.abspath('README.md'))

with open(readme_path, encoding='utf-8') as file:
    long_description = file.read()

setup(
    name='yamole',
    version='2.1.5',
    description='A YAML parser that resolves JSON references',
    long_description=long_description,
    long_description_content_type='text/markdown',
    author='Yago González',
    license='MIT',
    classifiers=[
        'Development Status :: 5 - Production/Stable',
        'Intended Audience :: Developers',
        'License :: DFSG approved',
        'License :: OSI Approved',
        'License :: OSI Approved :: MIT License',
        'Programming Language :: Python :: 2',
        'Programming Language :: Python :: 2.7',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.6',
    ],
    keywords='yaml json references parser openapi swagger',
    project_urls={
        'Source': 'https://github.com/YagoGG/yamole/',
        'Tracker': 'https://github.com/YagoGG/yamole/issues',
    },
    py_modules=['yamole'],
    install_requires=['pyyaml']
)
