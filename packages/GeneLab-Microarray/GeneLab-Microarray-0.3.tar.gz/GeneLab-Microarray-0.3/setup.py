from setuptools import setup


setup(name='GeneLab-Microarray',version='0.3', 
    description='Standardized processing pipeline for microarray data on GeneLab.', 
    url='https://github.com/jdrubin91/GeneLab-Microarray', 
    author='Jonathan Rubin & Daniel Mattox', 
    author_email='jonathan.d.rubin@nasa.gov', 
    license='GPL-3.0',
    packages=['GeneLab-Microarray'], 
    package_data={'R_scripts': ['R_scripts/*']},
    include_package_data=True,
    install_requires=['scipy', 'mpld3','jinja2'],
    zip_safe=False,
    scripts=['bin/GeneLab-Microarray'])
