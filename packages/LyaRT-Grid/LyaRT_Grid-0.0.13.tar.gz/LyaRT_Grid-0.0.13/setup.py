import setuptools

from setuptools.command.develop import develop
from setuptools.command.install import install

#####
import os
import sys
import urllib
import shutil
#####

#====================================================================#
#====================================================================#
def Check_if_DATA_files_are_found():

    this_dir, this_filename = os.path.split(__file__)

    Bool_1 = True

    arxiv_with_file_names = this_dir + 'LyaRT_Grid/DATA/List_of_DATA_files'

    with open( arxiv_with_file_names ) as fd:

        for line in fd.readlines():

            arxiv_name = line.strip('\n')

            Bool_1 = Bool_1 * os.path.isfile( this_dir + 'LyaRT_Grid/DATA/' + arxiv_name )

    return Bool_1
#====================================================================#
#====================================================================#
def Download_data():

    this_dir, this_filename = os.path.split(__file__)

    file_were_to_store_data = this_dir + 'LyaRT_Grid/DATA/'

    print( 'This package is stored in ', this_dir , '(Please, note that we are not spying you.)' )

    http_url = 'http://www.cefca.es/people/~sidgurung/ShouT/ShouT/DATA/'

    arxiv_with_file_names = this_dir + 'LyaRT_Grid/DATA/List_of_DATA_files'

    testfile = urllib.URLopener()

    with open( arxiv_with_file_names ) as fd:

        for line in fd.readlines():

            arxiv_name = line.strip('\n')

            print( 'Downloaing...' , http_url + arxiv_name )

            testfile.retrieve( http_url + arxiv_name , arxiv_name )

            print( '--> Done!' )

            print( 'Moving Downloaded file to' , file_were_to_store_data )

            shutil.move( arxiv_name , file_were_to_store_data + arxiv_name )

            print( '--> Done' )

    if Check_if_DATA_files_are_found():
        print( '\nHey man, looks like everything is done! That is brilliant!' )

    else:
        print( 'This is weird... We just downloaded everthing but the files are not found...Exiting.     ..')
        print( 'Error. Human is dead. Mismatch.')
        sys.exit()

    return
#====================================================================#
#====================================================================#

class PostDevelopCommand(develop):
    """Post-installation for development mode."""
    def run(self):
        # PUT YOUR POST-INSTALL SCRIPT HERE or CALL A FUNCTION
        Download_data()

        develop.run(self)

class PostInstallCommand(install):
    """Post-installation for installation mode."""
    def run(self):
        # PUT YOUR POST-INSTALL SCRIPT HERE or CALL A FUNCTION
        Download_data()

        install.run(self)

with open("README.md", "r") as fh:
    long_description = fh.read()

setuptools.setup(
    name="LyaRT_Grid",
    version="0.0.13",
    author="Example Author",
    author_email="author@example.com",
    description="A small example package",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/pypa/example-project",
    packages=setuptools.find_packages(),
    #install_requires=['scikit-learn'],
    install_requires=setuptools.find_packages(),
    include_package_data = True,
    classifiers=(
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ),
    cmdclass={ 'develop': PostDevelopCommand,
               'install': PostInstallCommand, },
    #test_suite='nose.collector',
    #tests_require=['nose'],
)

