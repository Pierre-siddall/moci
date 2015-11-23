#!/usr/bin/env python2.7
#*****************************COPYRIGHT******************************
#(C) Crown copyright Met Office. All rights reserved.
#For further details please refer to the file COPYRIGHT.txt
#which you should have received as part of this distribution.
#*****************************COPYRIGHT******************************
#
# CODE OWNER
#   Stephen Haddad
#
# NAME
#   oasisBuild.py
# 
# DESCRIPTION
#    Buids the Oasis3-mct library and tutorials and creates associated 
#    environment modules.
#
# ENVIRONMENT VARIABLES
#
#   SYSTEM_NAME
#   BUILD_OASIS
#   OASIS3_MCT
#   OASIS_PLATFORM_NAME
#   OASIS_REPO_URL
#   OASIS_REV_NO
#   OASIS_DIR
#   VERBOSE (optional)
#   DEPLOY_AS_MODULE (optional)
#   MODULE_INSTALL_PATH (optional)
#   OASIS_MODULE_VERSION (optional)
#   OASIS_BUILD_TUTORIAL (optional)
#
import os
import sys
import abc
import subprocess
import shutil
import textwrap

import EnvironmentModules 

EXTRACT_SCRIPT_FILE_NAME = 'oasisExtractScript01.sh'
BUILD_SCRIPT_FILENAME = 'oasisBuildScript01.sh'

class MissingVariableException(Exception):
    '''
    Exception raised when an required environment variable is missing. 
    '''
    pass

def formattedWrite(output, text):
    output.write('\n'.join(textwrap.wrap(text)) )

class OasisModuleWriter(EnvironmentModules.SingleModuleWriter):
    '''
    Class responsible for writing Oasis3-mct environment module
    '''
    def __init__(self, 
                 version, 
                 modulePath, 
                 prerequisites, 
                 srcUrl, 
                 revNo, 
                 moduleName, 
                 parents, 
                 platform):
        EnvironmentModules.SingleModuleWriter.__init__(self)
        self.ModuleName = moduleName
        self.ModuleVersion = version
        self.ModuleHomePath = modulePath
        self.ParentModules = parents
        self.Platform = platform
        self.OasisRepoUrl = srcUrl
        self.OasisRevisionNumber = revNo
        self.HelpMsg = """Sets up Oasis3-MCT coupler I/O server for use. Built 
from source branch {srcUrl} 
at revision {revNo}"""
        self.HelpMsg = self.HelpMsg.format(srcUrl=self.OasisRepoUrl,
                                           revNo=self.OasisRevisionNumber)
        self.WhatIsMsg = 'The Oasis3-mct coupler for use '\
                         'with weather/climate models'
        
        self.LocalVariablesList = [('module_base', self.ModuleHomePath)]
        moduleDirStr = '$module_base/packages/{1}/{0}'
        moduleDirStr = moduleDirStr.format(self.ModuleVersion, 
                                           self.ModuleName)
        self.LocalVariablesList += [('oasisdir', moduleDirStr)]

        self.PrerequisiteList = prerequisites

        self.PrependPathList = []

        self.SetEnvList = [('OASIS_ROOT', '$oasisdir'),
                           ('prism_path', '$oasisdir'),
                           ('OASIS_INC', '$oasisdir/inc'),
                           ('OASIS_LIB', '$oasisdir/lib'),
                           ('OASIS3_MCT', self.ModuleName),
                           ('OASIS_MODULE_VERSION', self.ModuleVersion)]
     

class OasisBuildFailedException(Exception):
    '''
    Exception raised if there is any problem found with building oasis.
    '''
    pass

class OasisBuildSystem(object):
    '''
    Base class for building Oasis3-mct library on different platforms. Specific
    platforms will have a class that inherits from this to implement 
    platform-specific build elements.
    '''
    __metaclass__ = abc.ABCMeta
    
    
    SUB_DIRECTORY_LIST = ['lib',
                          'build']
    
    def __init__(self, settingsDict):
        '''
        Constructor for base build class for Oasis. 
        Arguments:
        settingsDict - A dictionary with settings object. This will often
                       be just the os.environ object, but doesn't need to be.
        '''
        self.WorkingDir = os.getcwd()
        self.SystemName = settingsDict['SYSTEM_NAME']
        self.DoBuild = settingsDict['BUILD_OASIS'] == 'true'

        self.LibraryName = settingsDict['OASIS3_MCT']
        self.BuildPlatformName = settingsDict['OASIS_PLATFORM_NAME']
            
        if self.DoBuild:
            # if we are building oasis, then get relevant repository settings
            self.OasisRepositoryUrl = settingsDict['OASIS_REPO_URL']
            self.OasisRevisionNumber = settingsDict['OASIS_REV_NO']
            self.OasisSrcDir = '{0}/{1}'.format(self.WorkingDir,
                                                self.LibraryName)
            try:
                self.OasisOutputDir = settingsDict['OASIS_DIR']
            except KeyError:
                self.OasisOutputDir = None
        
        else:  
            # if we are not building oasis, then we will be copying the output
            # to be used in a module.
            try:
                self.OasisSrcDir = settingsDict['OASIS_DIR']
            except KeyError:
                self.OasisSrcDir = None

            try:
                self.OasisRepositoryUrl = settingsDict['OASIS_REPO_URL']
                self.OasisRevisionNumber = settingsDict['OASIS_REV_NO']
            except KeyError:
                self.OasisRepositoryUrl = 'unknown'
                self.OasisRevisionNumber = 'unknown'

            if  self.OasisSrcDir == None:
                msg1 = 'Variable OASIS_DIR must be defined if '\
                       'not building Oasis library'    
                raise MissingVariableException(msg1)
        
        try:
            self.Verbose = settingsDict['VERBOSE'] == 'true'
        except KeyError:
            self.Verbose = False

        # module writing related settings
        try:
            self.DeployOasisAsModule = \
                settingsDict['DEPLOY_AS_MODULE'] == 'true'
            self.ModuleRootDir = settingsDict['MODULE_INSTALL_PATH']
            self.ModuleVersion = settingsDict['OASIS_MODULE_VERSION']
        except KeyError:
            formattedWrite(sys.stdout, 
                           'Module related environment variables missing '
                           'or invalid, default settings used.')
            
            self.DeployOasisAsModule = False
            self.ModuleRootDir = ''
            self.ModuleVersion = ''
            
        try:
            self.BuildTutorial = settingsDict['OASIS_BUILD_TUTORIAL'] == 'true'
        except KeyError:
            formattedWrite(sys.stdout,
                           'OASIS_BUILD_TUTORIAL environment variable '
                           'missing or invalid, default settings of false ' 
                           'will be used.')
            self.BuildTutorial = False
            
    def __str__(self):
        retStr1 = ''
        if self.DoBuild:
            retStr1 += 'Building oasis3-mct library\n'
            if self.BuildTutorial:
                retStr1 += 'Tutorial executables will be built\n'
            else:
                retStr1 += 'Tutorial will NOT be built\n'
            retStr1 += 'Source code to be retrieved from repository:\n'
            retStr1 += '{0}@{1}'.format(self.OasisRepositoryUrl,
                                        self.OasisRevisionNumber)
        else:
            retStr1 += 'Library will not be built, module files will be \n'
            retStr1 += 'created at {0} \n'.format(self.ModuleRootDir)
            retStr1 += 'using library files copied from '
            retStr1 += '{0}\n'.format(self.OasisSrcDir)
        return retStr1
    
    def RunBuild(self):
        '''
        Main build function. This function is typically called to run the 
        build procedure. 
        ''' 
        if self.DoBuild:
            self.ExtractSourceCode()
            self.WriteIncludeFile()
            
            buildCommand1 = self.CreateBuildCommand()
            self.ExecuteBuildCommand(buildCommand1)
            
            if not (self.OasisOutputDir == None or self.OasisOutputDir == ''):
                self.CopyFiles(self.OasisOutputDir)
        
        if self.DeployOasisAsModule:
            self.CreateModule()

    def ExtractSourceCode(self):
        '''
        Extract source code from the repository using FCM. 
        '''
        # if source code directory already exists, delete to ensure correct
        # version of code is present. 
        if os.path.exists(self.OasisSrcDir):
            extractString1 = 'fcm update --non-interactive '\
                                ' {OasisSrcDir} -r {OasisRevisionNumber}'
            extractString1 = extractString1.format(**self.__dict__)
        else:
            extractString1 = ( 'fcm co {OasisRepositoryUrl}@{OasisRevisionNumber} '
                             + '{OasisSrcDir}' ).format(**self.__dict__)
        if self.Verbose:
            extractScriptPath = '{0}/{1}'.format(self.WorkingDir,
                                                 EXTRACT_SCRIPT_FILE_NAME)
            with open(extractScriptPath,'w') as extractScript:
                extractScript.write(extractString1 + '\n')
                
        subprocess.call(extractString1, shell=True)
         
    def WriteIncludeFile(self):
        '''
        Write the make.inc file to be used by the oasis3-mct build process.
        This tells the main makefile which architecture file to use.
        Usage:
        buildObject.WriteIncludeFile()
        '''
        headerFilePath = '{0}/util/make_dir/make.inc'
        headerFilePath = headerFilePath.format(self.OasisSrcDir)
        os.remove(headerFilePath)
        
        headerFileStr = """
PRISMHOME = {OasisSrcDir}
include $(PRISMHOME)/util/make_dir/make.cray_xc40_mo
"""
        headerFileStr = headerFileStr.format(OasisSrcDir=self.OasisSrcDir)
             
        with open(headerFilePath,'w') as headerFile:
            headerFile.write(headerFileStr)
        
    @abc.abstractmethod
    def CreateBuildCommand(self):
        '''
        Creates the series of commands to build the library (and tutorial
        files if required). The command is returned as a string and can then be
        executed using the subprocess module.
         
        Usage:
        buildCommandString = buildObject.CreateBuildCommand()
        
        Return value:
        A string with the command to be executed when building using subprocess
        module.
        '''
        pass

    def ExecuteBuildCommand(self, buildCommand):
        '''
        Takes in a string containing the build commands and executes the 
        commands using subprocess. If the commands fail, an exception is raised.
        
        Usage:
        self.ExecuteBuildCommand(buildCommand)
        
        Arguments:
        buildCommand - string containing build commands.
        '''
        result1 = subprocess.call(buildCommand, shell=True)
        if result1 != 0:
            raise OasisBuildFailedException()

    def CopyFiles(self, dest):
        '''
        Copy the build output files to the specified directory. The directories 
        copied will include the $ARCH/build and $ARCH/lib, where $ARCH is
        the name of the build directory created in the root oasis3-mct 
        directory.
        If the BuildTutorial member variable is True, the 
        $OASIS_ROOT/examples/tutorial will also be copied to allow the 
        tutorial example to be run.
        
        Usage:
        buildObject.CopyFile(dest)
        
        Arguments:
        dest - string containing path to destination directory of copied files.          
        '''
        srcDirs = []
        if self.DoBuild:
            for subdir1 in self.SUB_DIRECTORY_LIST:
                srcDirs += ['{0}/{1}/{2}'.format(self.OasisSrcDir,
                                                 self.BuildPlatformName,
                                                 subdir1) ]
            
            if self.BuildTutorial:
                srcDirs += ['{0}/examples/tutorial'.format(self.OasisSrcDir)] 
            
        else:
            for subdir1 in self.SUB_DIRECTORY_LIST:
                srcDirs += ['{0}/{1}'.format(self.OasisSrcDir,
                                            subdir1) ]
            
        destDirs = []
        for subdir1 in self.SUB_DIRECTORY_LIST:
            destDirs += ['{0}/{1}'.format(dest,
                                          subdir1) ]
        
        if self.BuildTutorial:
            destDirs += ['{0}/examples/tutorial'.format(dest)] 
                    
        if os.path.exists(dest) and os.path.isdir(dest):
            sys.stdout.write('removing dir {0}\n'.format(dest))
            shutil.rmtree(dest)
            
        for src1, dest1 in zip(srcDirs, destDirs):
            shutil.copytree(src1, dest1)
            
        
    @abc.abstractmethod
    def CreateModule(self):
        '''
        Creates environment modules for using the Oasis3-mct library in other
        applications.
        
        Usage:
        buildObject.CreateModule()
        '''
        pass
 
    
class OasisCrayModuleWriter(OasisModuleWriter):
    '''
    Class to write out the Oasis3-mct CRAY XC40 environment module.
    '''
    def __init__(self, 
                 version, 
                 modulePath, 
                 srcUrl, 
                 revNo, 
                 moduleName, 
                 platform):
        prereq = ['PrgEnv-cray/5.2.40',
                  'cray-mpich/7.0.4']
        OasisModuleWriter.__init__(self, 
                                   version = version, 
                                   modulePath=modulePath, 
                                   prerequisites=prereq,
                                   srcUrl=srcUrl, 
                                   revNo=revNo, 
                                   moduleName=moduleName,
                                   parents='',
                                   platform=platform)

class OasisCrayRemoteModuleWriter(OasisModuleWriter):
    '''
    Class to write out the Oasis3-mct CRAY XC40 environment module for use on
    remote systems. This allows one to create a script to run on the cray
    on a different system. This is typically used with the FCM build system 
    where the build may be setup on one platform and built on another.
    '''
    def __init__(self, 
                 version, 
                 modulePath, 
                 srcUrl, 
                 revNo, 
                 moduleName, 
                 platform):
        prereq = []
        OasisModuleWriter.__init__(self, 
                                   version = version, 
                                   modulePath=modulePath, 
                                   prerequisites=prereq, 
                                   srcUrl=srcUrl,
                                   revNo=revNo, 
                                   moduleName=moduleName,
                                   parents='remote/{0}/'.format(platform),
                                   platform=platform)

class OasisCrayBuildSystem(OasisBuildSystem):
    '''
    Class to build the Oasis3-mct libraries and tutorial on the Met Office
    Cray XC40 platform.
    '''
    SYSTEM_NAME = 'UKMO_CRAY_XC40'
    def __init__(self, settingsDict):
        OasisBuildSystem.__init__(self, settingsDict)
        
    def __str__(self):
        retStr1 = OasisBuildSystem.__str__(self)
        retStr1 += '\nBuild is system is {0}.\n'.format(self.SYSTEM_NAME)
        return retStr1

    def CreateBuildCommand(self):
        buildStr1  = """#!/bin/sh

module load PrgEnv-cray/5.2.40
module load cray-netcdf-hdf5parallel/4.3.2

cd {OasisSrcDir}/util/make_dir
make -f TopMakefileOasis3
"""
        
        buildStr1  = buildStr1.format(**self.__dict__)
        if self.BuildTutorial:  
            tutBuildStr1 = """
cd {OasisSrcDir}/examples/tutorial/
rm *.o
rm *.mod

rm model1.F90
mv model1_ukmo_cray_xc40.F90 model1.F90
rm model2.F90
mv model2_ukmo_cray_xc40.F90 model2.F90
rm data_oasis3/namcouple
mv data_oasis3/namcouple_TP data_oasis3/namcouple 
make model1
make model2
"""
            buildStr1 += tutBuildStr1.format(OasisSrcDir=self.OasisSrcDir)
        
        if self.Verbose:
            buildScriptPath1 = '{0}/{1}'.format(self.WorkingDir,
                                                BUILD_SCRIPT_FILENAME)
            with open(buildScriptPath1,'w') as buildScript1:
                buildScript1.write(buildStr1)
        
        return buildStr1

    def CreateModule(self):
        moduleWriter1 = OasisCrayModuleWriter(version = self.ModuleVersion, 
                                              modulePath = self.ModuleRootDir,
                                              srcUrl=self.OasisRepositoryUrl,
                                              revNo = self.OasisRevisionNumber,
                                              moduleName = self.LibraryName,
                                              platform=self.SYSTEM_NAME)
        moduleWriter1.WriteModule()

        modulePackageDirectory = ( '{ModuleRootDir}/packages/'
                                 + '{LibraryName}/{ModuleVersion}')
        modulePackageDirectory = modulePackageDirectory.format(**self.__dict__)
        
        self.CopyFiles(modulePackageDirectory)
        
        remoteWriter1 = \
            OasisCrayRemoteModuleWriter(version = self.ModuleVersion,
                                        modulePath = self.ModuleRootDir,
                                        srcUrl = self.OasisRepositoryUrl,
                                        revNo = self.OasisRevisionNumber,
                                        moduleName = self.LibraryName,
                                        platform = self.SYSTEM_NAME)
        remoteWriter1.WriteModule()
    

def createBuildSystem(systemName):
    '''
    Factory method to construct oasis3-mct build object for the correct
    platform.
    
    Usage:
    buildObject = createBuildSystem(systemName)
    
    Arguments:
    systemName - A string containing the name of the platform for the build.
    
    Return:
    An object derived from OasisBuildSystem which has the correct build 
    settings for the specified platform.
    '''
    bs1 = None
    if systemName == OasisCrayBuildSystem.SYSTEM_NAME:
        bs1 = OasisCrayBuildSystem(os.environ)
    return bs1
    
def main():
    systemName = os.environ['SYSTEM_NAME']
    try :
        doModule = os.environ['USE_OASIS'] == 'true'
        doBuild =  os.environ['BUILD_OASIS'] == 'true'
    except KeyError:
        formattedWrite(sys.stdout, 
                       'USE_OASIS and/or BUILD_OASIS environment variables '
                       'not found, using default values of False.')
        doBuild = False
        doModule = False
        
    # if not using and not building oasis, exit immediately
    if not doModule and not doBuild:
        formattedWrite(sys.stdout,
                       'oasis will not be built and module '
                       'will not be created.')
        return
    
    buildSystem1 = createBuildSystem(systemName)
    sys.stdout.write(str(buildSystem1) + '\n')
    buildSystem1.RunBuild()

if __name__ == '__main__':
    main()
