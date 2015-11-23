export SYSTEM_NAME=UKMO_CRAY_XC40
export OASIS3_MCT=oasis3-mct

#export OASIS_DIR=/data/d02/shaddad/oasisTest_20150910/install/oasis3-mct/
export OASIS_DIR=$PWD/install/${OASIS3_MCT}
 
#export OASIS_REPO_URL=svn://fcm2/PRISM_svn/OASIS3_MCT/branches/dev/frrj/r1217_port_mct_xcf/oasis3-mct
#export OASIS_REV_NO=1313

#export OASIS_REPO_URL=svn://fcm2/PRISM_svn/OASIS3_MCT/branches/dev/frrh/r1217_put_inquire_vn2.0.2/oasis3-mct
#export OASIS_REPO_URL=svn://fcm2/PRISM_svn/OASIS3_MCT/branches/dev/shaddad/r1267_GC3_projOceanTutorial/oasis3-mct
#export OASIS_REV_NO=1325

export OASIS_REPO_URL=svn://fcm2/PRISM_svn/OASIS3_MCT/branches/dev/shaddad/r1267_GC3_projOceanTutorial/oasis3-mct
export OASIS_REV_NO=1327


export OASIS_PLATFORM_NAME=crayxc40
export VERBOSE=true
export DEPLOY_AS_MODULE=true
export MODULE_INSTALL_PATH=$PWD/modules
export OASIS_MODULE_VERSION=1.0
export BUILD_OASIS=true
export OASIS_BUILD_TUTORIAL=false
export USE_OASIS=true
