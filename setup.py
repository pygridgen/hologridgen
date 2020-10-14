from setuptools import setup

required = {'param':">=1.10.0",
            'panel':">=0.10.0",
            'pygridgen':">0.2",
            'geopandas':">=0.8.1",
            'holoviews':">=1.0.1"}


setup_args['requires']=["%s (%s)" % (package, version)
                        for package,version in required.items()]

setup_args = dict(
    name='hologrid',
    version='0.0.1',
    description='',
    long_description=open('README.md').read(),
    author="jlstevens",
    author_email="jstevens@anaconda.com",
    platforms=['Windows', 'Mac OS X', 'Linux'],
    license='BSD',
    url='https://github.com/pygridgen/hologrid',
    packages=["hologrid"],
    provides=["hologrid"],
    include_package_data = True,
    python_requires=">=3.5",
    requires=requires,
    project_urls={
        "Bug Tracker": "https://github.com/pygridgen/hologrid/issues",
        "Source Code": "https://github.com/pygridgen/hologrid",
    },
    classifiers=[
        "License :: OSI Approved :: BSD License",
        "Development Status :: 5 - Production/Stable",
        "Programming Language :: Python :: 3.5",
        "Programming Language :: Python :: 3.6",
        "Programming Language :: Python :: 3.7",
        "Programming Language :: Python :: 3.8",
        "Operating System :: OS Independent",
        "Intended Audience :: Science/Research",
        "Intended Audience :: Developers",
        "Natural Language :: English",
        "Topic :: Scientific/Engineering",
        "Topic :: Software Development :: Libraries"]
)


if __name__=="__main__":
    setup(**setup_args)