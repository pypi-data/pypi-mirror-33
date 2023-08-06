from setuptools import find_packages, setup

VERSION = '0.2'


setup(
    name='github-rename',
    version=VERSION,
    description='GitHub rename helper to change .git configs',
    url='https://github.com/qqghst/GitHub-rename',
    author='Qiushi Pan',
    author_email='qqghst@gmail.com',
    license='MIT',
    keywords='github git rename',
    packages=find_packages(),
    install_requires=["click >= 6.7"],
    # scripts = ['directory/__main__.py'],
    entry_points={'console_scripts': 'github-rename = github_rename:main'},
    classifiers=[
        'Environment :: Console',
        'Intended Audience :: Developers',
        'Operating System :: MacOS :: MacOS X',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.3',
        'Programming Language :: Python :: 3.4',
        'Programming Language :: Python :: 3.5',
        'Programming Language :: Python :: 3.6',
    ],
)
