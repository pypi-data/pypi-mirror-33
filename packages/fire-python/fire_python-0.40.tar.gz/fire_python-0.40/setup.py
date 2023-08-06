from setuptools import setup

setup(name='fire_python',
    version='0.40',
    description='Functional Inference and Reasoning Engine - Python',
    url='https://public.git.erdc.dren.mil/rdchlarb/fire_python.git',
    author='Aaron Byrd',
    author_email='AaronRByrd@gmail.com',
    license='FIRE-Python is licensed under the GNU General Public License version 3, 2007. FIRE-Python may also be available under alternative licenses (multi licensing model). This is so that it may be sold or licensed for use in proprietary applications. If you wish to use or incorporate this program (or parts of it) into other software that does not meet the GNU General Public License conditions contact the author to discuss a licensing agreement.',
    packages=['fire_python'],
    test_suite = 'nose.collector',
    tests_require = ['nose']
)
