from setuptools import setup
from glob import glob
import os

try:
    from Cython.Build import cythonize
    from Cython.Distutils.extension import Extension
    from Cython.Distutils import build_ext
except ImportError:
    from setuptools.extension import Extension
    USING_CYTHON = False
else:
    USING_CYTHON = True

ext = 'pyx' if USING_CYTHON else 'c'

sources = glob('mata/api/*.' + ext) + glob('mata/api/gui/*.' + ext)
extensions = [
    Extension(source.split('.')[0].replace(os.path.sep, '.'),
              sources=[source],
    )
for source in sources]
cmdclass = {'build_ext': build_ext} if USING_CYTHON else {}



setup(  name = "mata",
        version = "0.1.1",
        description = "Medieval Attack-Trade-Alliance Game Engine",
        author="mpbagot",
        author_email="mitchell.bagot@education.nsw.gov.au",
        license="MIT",
        long_description=open('README.rst').read(),
        packages=["mata", "mata.api"],
        include_package_data=True,
        scripts=["bin/mata_create_project"],
        install_requires=["noise", "pygame", "cython"],
        url="https://gitlab.com/mpbagot/mata",
        keywords=["engine", "game", "pygame"],
        ext_modules=(cythonize(extensions) if USING_CYTHON else extensions),#"mata/api/*.pyx") + cythonize("mata/api/gui/*.pyx")
        cmdclass=cmdclass

)
