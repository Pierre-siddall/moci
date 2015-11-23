export SYSTEM_NAME=UKMO_CRAY_XC40
export OASIS3_MCT=oasis3-mct
export OASIS_DATA_DIRECTORY=/data/d02/shaddad/oasis3-mct_tutorialData/
export OASIS_PLATFORM_NAME=crayxc40
export OASIS_MODULE_VERSION=1.0
export VERBOSE=true
export OASIS_DIR=$PWD/install/${OASIS3_MCT}
export OASIS_RESULT_DIR=$PWD/oasisOutput/
mkdir -p $OASIS_RESULT_DIR
export OASIS_TEST_NAME=oasis3mct_tutorial

module use $PWD/modules/modules
module load $OASIS3_MCT/$OASIS_MODULE_VERSION
