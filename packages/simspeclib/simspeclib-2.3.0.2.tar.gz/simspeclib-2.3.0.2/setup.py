import setuptools
import PkgHelper

from setuptools.command.install import install

with open("README.md", "r") as fh:
    long_description = fh.read()


with open('SimSpecLib/simspec.py', 'r') as infile:
    for line in infile:
        if line.strip().startswith("__ver__"):
            ver=eval(line.split('=')[1].strip())
        elif line.strip().startswith("__author__"):
            author=eval(line.split('=')[1].strip())


class PostInstallCommand(install):
    """Post-installation for installation mode."""
    def run(self):
        # PUT YOUR POST-INSTALL SCRIPT HERE or CALL A FUNCTION
        install.run(self)
        from SimSpecLib import SimSpec
        import subprocess
        if not SimSpec.os.path.exists( SimSpec.ConfDir ):
            SimSpec.os.mkdir(SimSpec.ConfDir)
        subprocess.check_output("cp -rf "+SimSpec.ProDir+'DefMod '+SimSpec.ConfDir+'default',
           shell=True,stderr=subprocess.STDOUT)
        #print '####################################'

PkgName='simspeclib'

setuptools.setup(
    name=PkgName,
    version=ver+PkgHelper.getsubver(PkgName,ver,'.'),
    author=author,
    author_email="email@subhashbose.com",
    description="SimSpec library. SIMplified SPECtrum reduction package for astronomy.",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="http://astro.subhashbose.com/simspec",
    packages=setuptools.find_packages(),
    package_data={'SimSpecLib.extern': ['*'],'SimSpecLib': ['stdlib/*']},
    include_package_data=True,
    #scripts=['simspec/simspec'],
    cmdclass={'install': PostInstallCommand},
    classifiers=(
        "Programming Language :: Python :: 2",
        "License :: Other/Proprietary License",
        "Operating System :: OS Independent",
    ),
)
