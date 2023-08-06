from setuptools import setup, find_packages
from distutils.extension import Extension

    
try:
    from Cython.Distutils import build_ext
except ImportError:
    use_cython = False
else:
    use_cython = True

cmdclass = {}
ext_modules = []

##if use_cython:
##    ext_modules.append(Extension("joblist.trees_cython", ['joblist/trees_cython.pyx']))
##    cmdclass.update({'build_ext': build_ext})
##else:
##    ext_modules.append(Extension("joblist.trees_cython", ['joblist/trees_cython.c']))


setup(name='joblist',
      version='2.0.3',
      description="A Python implementation of joblist",
      long_description="A Python implementation of JobList (Data Extraction with Partial Tree Alignment)",
      author="Sellamani",
      author_email="mail2.sella@gmail.com",
      install_requires=['w3lib'],
      packages=find_packages(),
      include_package_data=True,
      #package_data={'joblist': ['joblist/Lookup_data_new_v2.pickle']},
      package_data={'joblist': ['*.pickle', 'joblist/Lookup_data_new_v2.pickle']},
      cmdclass=cmdclass,
      ext_modules=ext_modules
)
