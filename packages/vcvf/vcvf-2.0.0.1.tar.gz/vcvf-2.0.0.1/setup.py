from distutils.core import setup
from setuptools import setup
from setuptools import find_packages


with open("README.md", "r") as fh:
    long_description = fh.read()
setup(
    name="vcvf",
    version="2.0.0.1",
    description="very nb computer vision",
    long_description=long_description,
    long_description_content_type="text/markdown",
    


    # You can just specify package directories manually here if your project is
    # simple. Or you can use find_packages().
    #
    # Alternatively, if you just want to distribute a single Python file, use
    # the `py_modules` argument instead as follows, which will expect a file
    # called `my_module.py` to exist:
    #
    #   py_modules=["my_module"],
    #
    #packages=find_packages(exclude=['contrib', 'docs', 'tests']),  # Required
    #packages=find_packages(include=['contrib', 'docs', 'ai_tools']),  # Required
    packages=find_packages(),  # Required
    #packages = find_packages('vcv'),  # include all packages under src
    #package_dir = {'':'vcv'},   # tell distutils packages are under src

    include_package_data = True,    # include everything in source control

    #test_suite='tests',
    #py_modules=["ai_tools_draw"],
    #py_modules=["ai_tools/ai_tools_save2server.py"],
    # This field lists other packages that your project depends on to run.
    # Any package you put here will be installed by pip when your project is
    # installed, so they must be valid existing projects.
    #
    # For an analysis of "install_requires" vs pip's requirements files see:
    # https://packaging.python.org/en/latest/requirements.html
    #install_requires=['opencv'],  # Optional

    # List additional groups of dependencies here (e.g. development
    # dependencies). Users will be able to install these using the "extras"
    # syntax, for example:
    #
    #   $ pip install sampleproject[dev]
    #
    # Similar to `install_requires` above, these must be valid existing
    # projects.
    extras_require={  # Optional
        'dev': ['check-manifest'],
        'test': ['coverage'],
    },

    # If there are data files included in your packages that need to be
    # installed, specify them here.
    #
    # If using Python 2.6 or earlier, then these have to be included in
    # MANIFEST.in as well.
    #package_data={  # Optional
    #    'package': ['data/hdm41754'],
    #},
     package_data = {
        # If any package contains *.txt or *.rst files, include them:
        #'': ['*.txt', '*.rst'],
        # And include any *.msg files found in the 'hello' package, too:
        #'hello': ['*.msg'],
        #'vcv':['data/hdm41754'],
        #'vcv':['data/test.jpg']
        'vcvf':['data/test.jpg','data/lbp_face_20180629']
    },
    # Although 'package_data' is the preferred approach, in some case you may
    # need to place data files outside of your packages. See:
    # http://docs.python.org/3.4/distutils/setupscript.html#installing-additional-files
    #
    # In this case, 'data_file' will be installed into '<sys.prefix>/my_data'
    data_files=[('vcvf', ['vcvf/data/datafile'])],  # Optional

    # To provide executable scripts, use entry points in preference to the
    # "scripts" keyword. Entry points provide cross-platform support and allow
    # `pip` to create the appropriate form of executable for the target
    # platform.
    #
    # For example, the following would provide a command called `sample` which
    # executes the function `main` from this package when invoked:
    entry_points={  # Optional
        'console_scripts': [
            'sample=sample:main',
        ],
    },




    #scripts = ['drawlib.py','save2server.py'], 
    license = "MIT",
    author="zhaomingming",
    author_email="13271929138@163.com",
    url="http://www.zhaomingming.cn",
    #py_modules=['ai_tools'],
    platforms = 'any'
)
