import os
import sys
import platform

from setuptools import setup
from numpy.distutils.core import setup
from numpy.distutils.core import Extension
#from numpy.distutils.misc_util import Configuration

from pyGDM2 import __name__, __version__, __author__



def read(fname):
    return open(os.path.join(os.path.dirname(__file__), fname)).read()

def check_openmp():
    """
    compile with OpenMP ?
    """
    if "WITH_OPENMP" in os.environ and os.environ["WITH_OPENMP"] == "False":
        print "No OpenMP requested by environment"
        return False

    if ("--no-openmp" in sys.argv):
        sys.argv.remove("--no-openmp")
        os.environ["WITH_OPENMP"] = "False"
        print "No OpenMP requested by command line"
        return False
    
    if ("--with-openmp" in sys.argv):
            sys.argv.remove("--with-openmp")
            os.environ["WITH_OPENMP"] = "True"
            print "OpenMP explicitly requested by command line"
            return True
        
    if platform.system() == 'Darwin':
        print "Running OSX: OpenMP not implemented in default 'clang'. \nIf you encounter problems, you might try '--no-openmp' to compile without OpenMP"
        return True
    
    print "Compiling with OpenMP. Use '--no-openmp' to deactivate."
    return True

print "\n" + 60*'#' + "\n"

if check_openmp():
    openmp = "-fopenmp" 
    openmp_linker = "-lgomp"
else:
    openmp = "" 
    openmp_linker = ""

print "\n" + 60*'#' + 2*"\n"



setup(
    name = __name__,
    version = __version__,
    author = __author__,
    author_email = "wiechapeter@gmail.com",
    description = ("A python full-field electrodynamical solver, "
                   "based on the Green dyadic method (volume integral technique "
                   "in frequency domain)."),
    license = "GPLv3+",
    long_description=read('README.rst'),
    packages=['pyGDM2', 'pyGDM2.EO', 'pyGDM2.EO1'],
    ext_modules=[Extension(name = 'pyGDM2.pyGDMfor', 
                           sources = ['fortranBase/precision_single.f90',
                                'fortranBase/propagator_elec_elec_123.f90',
                                'fortranBase/propagator_elec_mag_freespace.f90',
                                'fortranBase/propagator_generalized.f90',
                                'fortranBase/routines_linear.f90',
                                'fortranBase/routines_incidentfields.f90',
                                'fortranBase/routines_decayrate.f90',
                                'fortranBase/routines_other.f90',
                                     ],
                           define_macros = [('F2PY_REPORT_ON_ARRAY_COPY','1')],
                           extra_compile_args = [openmp, '-O3', '-mcmodel=medium'],
                           extra_link_args = [openmp_linker, '-O3'],
                           )],
    classifiers=[
        "Development Status :: 5 - Production/Stable",
        "Topic :: Scientific/Engineering :: Physics",
        "Environment :: Console",
        "Programming Language :: Python :: 2.7",
        "License :: OSI Approved :: GNU General Public License v3 or later (GPLv3+)",
        "Intended Audience :: Science/Research"
    ],
    url = 'https://gitlab.com/wiechapeter/pyGDM2',
    download_url = '',
    keywords = ['coupled dipoles method', 'green dyadic method', 'electrodynamical simulations', 'nano optics', 'frequency-domain'],
    install_requires=['numpy'],
    python_requires='>=2.7',
) 
