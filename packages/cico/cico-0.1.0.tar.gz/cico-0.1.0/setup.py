from setuptools import setup


def readme():
    with open('README.md') as f:
        return f.read()


setup(
    name='cico',
    version='0.1.0',
    description='stores results created during a CI in a special git branch',
    long_description=readme(),
    long_description_content_type="text/markdown",
    classifiers=[
        'Development Status :: 4 - Beta',
        'License :: OSI Approved :: MIT License',
        'Intended Audience :: Developers',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.6',
        'Programming Language :: Python :: 3.5',
        'Operating System :: MacOS :: MacOS X',
        'Operating System :: POSIX :: Linux',
        'Topic :: Software Development',
        'Topic :: Software Development :: Version Control :: Git'
    ],
    keywords='ci travis git badge',
    url='http://github.com/stefanhoelzl/cico',
    author='Stefan Hoelzl',
    author_email='stefan.hoelzl@posteo.de',
    license='MIT',
    packages=['cico'],
    install_requires=[
        'anybadge==1.1.1',
        'GitPython==2.1.10',
        'CairoSVG==2.1.3',
    ],
    include_package_data=True,
    zip_safe=False
)
