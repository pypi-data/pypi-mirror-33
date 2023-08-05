from setuptools import setup, Extension, find_packages
from distutils.core import setup
from Cython.Build import cythonize


from codecs import open
from os import path

here = path.abspath(path.dirname(__file__))

# Get the long description from the README file
with open(path.join(here, 'kernelml-README.md'), encoding='utf-8') as f:
    long_description = f.read()
    

# setup(
#     name = "Kernel Machine Learning",
#     ext_modules = cythonize('kernelml.pyx'),  # accepts a glob pattern
# )

setup(
    # Information
    name = "kernelml",
    version = "2.558",
    description='generalized machine learning algorithm for complex loss functions and non-linear coefficients',
    url = "https://github.com/Freedomtowin/kernelml",
    author = "Rohan Kotwani",
    
    
    license = "MIT",
    classifiers=[  # Optional
        'Development Status :: 3 - Alpha',

        # Indicate who your project is intended for
        "Intended Audience :: Developers",
        "Intended Audience :: Science/Research",
        "Topic :: Software Development",
        "Topic :: Scientific/Engineering",

        # Pick your license as you wish
        'License :: OSI Approved :: MIT License',

        # Specify the Python versions you support here. In particular, ensure
        # that you indicate whether you support Python 2, Python 3 or both.
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.4',
        'Programming Language :: Python :: 3.5',
        'Programming Language :: Python :: 3.6',
    ],
    keywords = "kernel machine learning nonlinear",
    packages=find_packages(exclude=['contrib', 'docs', 'tests']),  # Required
    install_requires = ["numpy","scikit-learn","matplotlib"],
#     data_files=[('my_data', ['kc_house_test_data.csv','kc_house_train_data.csv'])],
    
    # Build instructions
    ext_modules = [Extension("kernelml",
                             ["kernelml.bycython.c"],
                             include_dirs=["kernelml/include"])]
)