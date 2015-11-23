#!/bin/bash
# Script to setup up environment variables for xiosBuild.py. 
# This is for debugging purposes, the build script should
# normally be part of a suite.

module load cray-hdf5-parallel/1.8.13
module load cray-netcdf-hdf5parallel/4.3.2

export TEST_SYSTEM=UKMO_CRAY_XC40
export XIOS_DO_CLEAN_BUILD=true
export XIOS_POST_BUILD_CLEANUP=false
export XIOS_REPO_URL=svn://fcm1/xios.xm_svn/XIOS/branchs/xios-1.0
export XIOS_REV=684
export XIOS=XIOS
export USE_OASIS=true
#export OASIS_ROOT=/data/d02/shaddad/oasisTest_20150825/install
export BUILD_PATH=$(pwd)/install
export MTOOLS=$NETCDF_DIR
export XIOS_NUM_CORES=8
export XLF_MODULE=
export XLCPP_MODULE=
export DEPLOY_AS_MODULE=true
export MODULE_INSTALL_PATH=$(pwd)/modules
export XIOS_MODULE_VERSION=1.0
export XIOS_PRGENV_VERSION=1.0
export OASIS_MODULE_VERSION=1.0
export OASIS3_MCT=oasis3-mct
#export XIOS_USE_PREBUILT_LIB=true
#export XIOS_PREBUILT_DIR=/home/d02/shaddad/cylc-run/XBS_oasisTest/share/XIOS


module use $PWD/modules/modules
module load $OASIS3_MCT/$OASIS_MODULE_VERSION

