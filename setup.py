from setuptools import setup, find_packages
import versioneer

setup(
    name='qtwirl',
    version=versioneer.get_version(),
    cmdclass=versioneer.get_cmdclass(),
    description='qtwirl (quick-twirl), a one-function interface to alphatwirl',
    author='Tai Sakuma',
    author_email='tai.sakuma@gmail.com',
    url='https://github.com/alphatwirl/qtwirl',
    classifiers=[
        'Development Status :: 4 - Beta',
        'Intended Audience :: Science/Research',
        'License :: OSI Approved :: BSD License',
        'Programming Language :: Python :: 2.7',
        'Programming Language :: Python :: 3.6',
    ],
    packages=find_packages(exclude=['docs', 'tests']),
)
