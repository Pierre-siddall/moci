#!/usr/bin/env python2.7
#
#*****************************COPYRIGHT******************************
#(C) Crown copyright Met Office. All rights reserved.
#For further details please refer to the file COPYRIGHT.txt
#which you should have received as part of this distribution.
#*****************************COPYRIGHT******************************
#
# CODE OWNER
#   Stephen Haddad

import os
import sys
import subprocess 
import shutil
import abc

class OasisTestFailedException(Exception):
    '''
    Raised when the execution of the oasis3-mct test command fails.
    '''
    pass

class MissingTestOutputException(Exception):
    '''
    Raised when an expected test output is missing after the test 
    has been run. 
    '''
    pass

class OasisTestSystem(object):
    '''
    Class to test basic functionality of the Oasis3-MCT library. 
    '''
    __metaclass__ = abc.ABCMeta
    #Class (static) variable definitions
    SYSTEM_NAME = "BASE_CLASS"
    TEST_SCRIPT_FILENAME = 'oasisRunTutorialScript.sh'
    
    OUTPUT_FILE_NAMES = ['FRECVATM_model2_01.nc',
                         'FRECVOCN_model1_03.nc',
                         'FSENDATM_model2_03.nc',
                         'FSENDOCN_model1_01.nc',
                         'FSENDOCN_model1_02.nc']  
    
    TUTORIAL_DATA_FILE_LIST = ['my_remapping_file_bilinear.nc', 
                               'fdocn.nc', 
                               'grid_model2.nc', 
                               'fdatm.nc', 
                               'grid_model1.nc']    

    def __init__(self, settingsDict):
        '''
        Constructor
        '''
        self.WorkingDir = os.getcwd() 
        self.Verbose = settingsDict['VERBOSE']
        self.SystemName = settingsDict['SYSTEM_NAME']
        self.LibraryName = settingsDict['OASIS3_MCT']
        self.OasisRootDir = settingsDict['OASIS_ROOT']
        self.BuildPlatformName = settingsDict['OASIS_PLATFORM_NAME']
        self.OasisTutorialDataDir = settingsDict['OASIS_DATA_DIRECTORY']
        self.OasisModuleVersion = settingsDict['OASIS_MODULE_VERSION']
        
        self.OasisBuildOutputDir = settingsDict['OASIS_DIR']
        self.TutorialSrcDir =  '{0}/examples/tutorial/'
        self.TutorialSrcDir = \
            self.TutorialSrcDir.format(self.OasisBuildOutputDir)
        try:
            self.TestName = settingsDict['OASIS_TEST_NAME']
        except KeyError:
            self.TestName = 'oasis3mct_tutorial'
        self.TutorialWorkingDir = '{0}/{1}/'.format(self.WorkingDir, 
                                                    self.TestName)
        self.TutorialOutputDir = '{0}/runDir/'.format(self.TutorialWorkingDir)
        self.SuiteMode = settingsDict.has_key('ROSE_DATA')
        if self.SuiteMode:
            self.RunTutCmd = 'run_tutorial_ukmo_cray_xc40_rose'
        else:
            self.RunTutCmd = 'run_tutorial_ukmo_cray_xc40'
            
        try:
            self.ResultDestDir = settingsDict['OASIS_RESULT_DIR']
            self.DoResultCopy = True
        except KeyError:
            self.ResultDestDir = ''
            self.DoResultCopy = False
            
        #create a fresh working dir for test
        if os.path.exists(self.TutorialWorkingDir):
            shutil.rmtree(self.TutorialWorkingDir)
        #os.mkdir(self.TutorialWorkingDir)
        
        shutil.copytree(self.TutorialSrcDir, self.TutorialWorkingDir)
        #copy data files
        for fileName1 in self.TUTORIAL_DATA_FILE_LIST:
            srcPath = '{0}/{1}'.format(self.OasisTutorialDataDir, fileName1)
            destPath = '{0}/data_oasis3/{1}'.format(self.TutorialWorkingDir,
                                                    fileName1) 
            shutil.copyfile(srcPath, destPath)

    def RunTest(self):
        '''
        Main umbrella method which runs all methods that are part of the 
        oasis3-mct test. 
        '''
        runCmdString = self.CreateTestCommand()
        if self.Verbose:
            runTestScriptPath = '{0}/{1}'.format(self.WorkingDir,
                                                 self.TEST_SCRIPT_FILENAME)
            with open(runTestScriptPath,'w') as testScript1:
                testScript1.write(runCmdString + '\n')
        
        self.ExecuteTestCmd(runCmdString)
        
        if self.SuiteMode:
            self.CopyResults()
        
            
    def ExecuteTestCmd(self, runCmd):
        '''
        Execute the given test command in a subprocess. The command is given 
        in shell script. It will usually have been create by CreateTestCommand.
        
        testObject.ExecuteTestCmd(runCmd)
        
        Arguments:
        runCmd - A string containing shell commands to execute the test.
        
        Exceptions:
        OasisTestFailedException - If the execution fails i.e. the subprocess 
                                   has non zero return value.
        '''
        result1 = subprocess.call(runCmd, shell=True)
        if result1 != 0:
            raise OasisTestFailedException()
        
   
    @abc.abstractmethod
    def CreateTestCommand(self):
        '''
        Create command to run oasis3-mct test.
        
        commadString = testObj.CreateTestCommand()
        
        Return:
        A string with shell commands to execute the oasis3-mct test.
        '''
        pass
    
    
    def CopyResults(self):
        '''
        Copies the contents of the result directory to destination specified
        by the ResultDestDir object member variable.
        '''
        if not self.DoResultCopy:
            sys.stderr.write('output not being copied')
            return
        
        if not os.path.exists(self.ResultDestDir):
            os.makedirs(self.ResultDestDir)
    
        for fileName1 in self.OUTPUT_FILE_NAMES:
            path1 = '{0}/{1}'.format(self.TutorialOutputDir, fileName1)
            msg1 = 'copying from {src} to {dest} \n'
            msg1 = msg1.format(src=path1,
                               dest=self.ResultDestDir)
            sys.stdout.write(msg1)
            resultDestFileName = '{0}/{1}'.format(self.ResultDestDir, 
                                                  fileName1)
            shutil.copyfile(path1,
                            resultDestFileName)
    
            
class OasisCrayTestSystem(OasisTestSystem):
    '''
    Class to run the Oasis3-mct test on the Met Office Cray XC40. 
    '''
    SYSTEM_NAME = 'UKMO_CRAY_XC40'
    def __init__(self, settingsDict):
        OasisTestSystem.__init__(self, settingsDict)
    
    def __str__(self):
        retVal = 'Class to test Oasis 3-MCT library on the '
        retVal += 'Met Office Cray XC40 architecture'  
        return retVal
    
    def CreateTestCommand(self):
        testCmd1 = """#!/bin/sh

cd {TutorialWorkingDir}
./{RunTutCmd}
"""
        testCmd1 = testCmd1.format(**self.__dict__)
        return testCmd1
        
    
class OasisLinuxIntelTestSystem(OasisTestSystem):
    SYSTEM_NAME = 'UKMO_LINUX_INTEL'
    def __init__(self, settingsDict):
        OasisTestSystem.__init__(self, settingsDict)
    
    def __str__(self):
        retVal = ( 'Class to test Oasis 3-MCT library on the Met '
                 + 'Office Linux Desktop architecture' )
        return retVal
    
    def CreateTestCommand(self):
        pass

def createTestSystem(systemName, settingsDict):
    '''
    Factory method to create a class to run the tests.
    
    Usage:
    testObject = createTestSystem(systemName)
    
    Arguments:
    systemName - A string containing the name of the platform for the test.
    
    Return:
    An object derived from OasisBuildSystem which has the correct test 
    settings for the specified platform.    
    '''
    testSystem1 = None
    if systemName == OasisCrayTestSystem.SYSTEM_NAME: 
        testSystem1 = OasisCrayTestSystem(settingsDict)
    elif systemName == OasisLinuxIntelTestSystem.SYSTEM_NAME: 
        testSystem1 = OasisLinuxIntelTestSystem(settingsDict)
    return testSystem1 

def main():
    systemName1 = os.environ['SYSTEM_NAME']
    testSystem1 = createTestSystem(systemName1, os.environ)
    testSystem1.RunTest() 
    
if __name__ == '__main__':
    main()
