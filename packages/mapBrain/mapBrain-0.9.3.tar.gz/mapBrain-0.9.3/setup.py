from setuptools import setup

with open('README.md') as file:
    long_description = file.read()

setup(
    name="mapBrain",
    version="0.9.3",
    description="Brain image feature extraction and visualization",
    long_description=long_description,
    author="SIPBA@UGR",
    author_email="sipba@ugr.es",
    url='https://github.com/SiPBA/mapBrain',
    license="GPL-3.0+",
    py_modules=["mapBrain"],
    install_requires=[
        "numpy",
		  "matplotlib",
		  "scipy",
        "mahotas",
    ],
    download_url='https://github.com/SiPBA/mapBrain/archive/0.9.1.tar.gz',
    keywords=['brain', 'image', 'analysis', 'feature', 'neuroimaging', 'texture', 'mapping', 'visualization'],
    classifiers=[
        # How mature is this project? Common values are
        #   3 - Alpha
        #   4 - Beta
        #   5 - Production/Stable
        'Development Status :: 4 - Beta',

        # Indicate who your project is intended for
        'Environment :: Console',
        'Intended Audience :: Science/Research',
        'Topic :: Scientific/Engineering',
        'Operating System :: OS Independent',

        # Pick your license as you wish (should match "license" above)
        'License :: OSI Approved :: GNU General Public License v3 (GPLv3)',

        # Specify the Python versions you support here. In particular, ensure
        # that you indicate whether you support Python 2, Python 3 or both.
        'Programming Language :: Python :: 3', 
        'Programming Language :: Python :: 3.5',
        'Programming Language :: Python :: 3.6',
    ],
    # ...
)
