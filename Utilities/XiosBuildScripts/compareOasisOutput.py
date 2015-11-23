#!/usr/bin/env python2.7
import sys
import compareUtils
from oasisTest import OasisTestSystem
import os
import subprocess

def main():
    oasisKgoDir = os.environ['OASIS_KGO_DIR']
    oasisResultDir = os.environ['OASIS_RESULT_DIR']
    oasisRemoteResultDir = os.environ['OASIS_REMOTE_RESULT_DIR']    
    
    #copy files
    subprocess.call('scp {remoteDir}/*.nc {resultDir}'.format(remoteDir=oasisRemoteResultDir,
                                                              resultDir=oasisResultDir),
                    shell=True)
    
    print 'comparing Oasis3-mct output files'

    for fileName1 in OasisTestSystem.OUTPUT_FILE_NAMES:
        print 'evaluating file {filename}'.format(filename=fileName1)
        try:
            compareUtils.compareCubeListFiles(oasisKgoDir, oasisResultDir, fileName1)
        except Exception as e1:
            sys.stderr.write(str(e1))
            raise e1            
        
    print 'Oasis3-mct output data match successful'
    sys.exit(0)            

if __name__ == '__main__':
    main()