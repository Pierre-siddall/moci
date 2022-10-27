#!/usr/bin/env bash
#
# NAME: xios_build.sh
#
# DESCRIPTION: Creates .arch files and builds XIOS
#
# ENVIRONMENT VARIABLES (COMPULSORY):
#    BLITZ_INCDIR
#    BLITZ_LIBDIR
#    BOOST_INCDIR
#    BOOST_LIBDIR  
#    OASIS_ROOT
#    OASIS_LIB
#    XIOSPATH
#

echo OASIS_ROOT
echo $OASIS_ROOT
echo OASIS_LIBDIR
echo $OASIS_LIB

cd $XIOSPATH/arch

cat << EOF > arch-EX_UKMO.env
export HDF5_INC_DIR=""
export HDF5_LIB_DIR=""

export NETCDF_INC_DIR=""
export NETCDF_LIB_DIR=""

export BOOST_INC_DIR=""
export BOOST_LIB_DIR=""

export BLITZ_INC_DIR=""
export BLITZ_LIB_DIR=""

export OASIS_INCDIR="-I$OASIS_ROOT/build/lib/psmile.MPI1"
export OASIS_LIBDIR="-L$OASIS_LIB"
export OASIS_LIB="-lpsmile.MPI1 -lscrip -lmct -lmpeu"
EOF

cat << EOF > arch-EX_UKMO.fcm
################################################################################
###################                Projet XIOS               ###################
################################################################################

# CrayEX build instructions for XIOS/branchs/xios-2.5@1873

# Cray XC build instructions for XIOS/xios-1.0
# These files have been tested on 
# Twister (CrayEX)
# Need to also:
#    module load cray-netcdf-hdf5parallel/4.7.4.4
# Harry Shepherd 2021/06/25

%CCOMPILER      CC
%FCOMPILER      ftn
%LINKER         CC

%BASE_CFLAGS     -std=c++03 -DMPICH_SKIP_MPICXX 

## Otherwise take your pick of these, refer to information above.
%PROD_CFLAGS    -O1 -DBOOST_DISABLE_ASSERTS 
%DEV_CFLAGS     -O2
%DEBUG_CFLAGS   -g

%BASE_FFLAGS    -em -m 4 -e0 -eZ
%PROD_FFLAGS    -O1
%DEV_FFLAGS     -G2
%DEBUG_FFLAGS   -g

%BASE_INC       -D__NONE__
%BASE_LD        -D__NONE__ -stdlib=libstdc++

%CPP            cpp 
%FPP            cpp
%MAKE           gmake

bld::tool::fc_modsearch -J
EOF

cat << EOF > arch-EX_UKMO.path
NETCDF_INCDIR=""
NETCDF_LIBDIR=""
NETCDF_LIB=""

MPI_INCDIR=""
MPI_LIBDIR=""
MPI_LIB=""

HDF5_INCDIR=""
HDF5_LIBDIR=""
HDF5_LIB=""

MPI_LIB="-lfmpich -lmpich"

BOOST_INCDIR="-I$BOOST_INCDIR"
BOOST_LIBDIR="-L$BOOST_LIBDIR"
BOOST_LIB=""

BLITZ_INCDIR="-I$BLITZ_INCDIR"
BLITZ_LIBDIR="-L$BLITZ_LIBDIR"
BLITZ_LIB=""

OASIS_INCDIR="-I$OASIS_ROOT/build/lib/psmile.MPI1"
OASIS_LIBDIR="-L$OASIS_LIB"
OASIS_LIB="-lpsmile.MPI1 -lscrip -lmct -lmpeu"
EOF

cd $XIOSPATH

./make_xios --use_oasis oasis3_mct --job 8 --arch EX_UKMO
if [ $? -ne 0 ]; then
    1>&2 echo "Unable to succesfully build XIOS. Please see compiler output for more informaton"
    exit 999;
fi


#End of script tests
ls $XIOSPATH/bin
[ $? -eq 0 ] || exit 1
ls $XIOSPATH/lib
[ $? -eq 0 ] || exit 1
ls $XIOSPATH/inc
[ $? -eq 0 ] || exit 1

