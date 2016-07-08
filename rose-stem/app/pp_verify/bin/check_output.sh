#!/usr/bin/env bash

###############################################################################
# check_output.sh
#
# Purpose:  
#    To parse the job-archive.jog files ensure all has been archived 
#    which should have been archived
#
# Required Environment:
#
# Updates:
#   MOCI #62 - Moved start date to October to test acceptance of spinup period 
#              for means
#            - Removed archived files:
#                 hg3esa.da19811001_00
#                 hg3esa.ph19810901
#                 hg3esa.ph19810911
#                 hg3esa.ph19810921
#                 hg3esa.pj19810901
#                 hg3esa.pm1981sep
#                 hg3esi.1m.1981-09.nc
#                 hg3esi.1s.1981-11.nc
#                 hg3eso_1m_19810901_19810930_grid_V.nc
#                 hg3eso_1s_19810901_19811130_grid_V.nc
#   MOCI #94 - Change to the datestamp format for the CICE seasonal and 
#              annual means
#            - hg3esi.is.YYY2-M2.nc -> hg3esi.1s.YYY1-M1_YYY2-M2.nc
#            - hg3esi.iy.YYY2-11.nc -> hg3esi.1y.YYY1-12_YYY2-11.nc
#
###############################################################################

adumps="
hg3esa.da19811101_00
hg3esa.da19811201_00
hg3esa.da19820101_00
hg3esa.da19820201_00
hg3esa.da19820301_00
hg3esa.da19820401_00
hg3esa.da19820501_00
hg3esa.da19820601_00
hg3esa.da19820701_00
hg3esa.da19820801_00
hg3esa.da19820901_00
hg3esa.da19821001_00
hg3esa.da19821101_00
hg3esa.da19821201_00
hg3esa.da19830101_00"

apm="
hg3esa.pm1981oct
hg3esa.pm1981nov
hg3esa.pm1981dec
hg3esa.pm1982jan
hg3esa.pm1982feb
hg3esa.pm1982mar
hg3esa.pm1982apr
hg3esa.pm1982may
hg3esa.pm1982jun
hg3esa.pm1982jul
hg3esa.pm1982aug
hg3esa.pm1982sep
hg3esa.pm1982oct
hg3esa.pm1982nov
hg3esa.pm1982dec"

aps="
hg3esa.ps1981son
hg3esa.ps1982djf
hg3esa.ps1982mam
hg3esa.ps1982jja
hg3esa.ps1982son"

apy="hg3esa.py19821201"

aph="
hg3esa.ph19811001
hg3esa.ph19811011
hg3esa.ph19811021
hg3esa.ph19811101
hg3esa.ph19811111
hg3esa.ph19811121
hg3esa.ph19811201
hg3esa.ph19811211
hg3esa.ph19811221
hg3esa.ph19820101
hg3esa.ph19820111
hg3esa.ph19820121
hg3esa.ph19820201
hg3esa.ph19820211
hg3esa.ph19820221
hg3esa.ph19820301
hg3esa.ph19820311
hg3esa.ph19820321
hg3esa.ph19820401
hg3esa.ph19820411
hg3esa.ph19820421
hg3esa.ph19820501
hg3esa.ph19820511
hg3esa.ph19820521
hg3esa.ph19820601
hg3esa.ph19820611
hg3esa.ph19820621
hg3esa.ph19820701
hg3esa.ph19820711
hg3esa.ph19820721
hg3esa.ph19820801
hg3esa.ph19820811
hg3esa.ph19820821
hg3esa.ph19820901
hg3esa.ph19820911
hg3esa.ph19820921
hg3esa.ph19821001
hg3esa.ph19821011
hg3esa.ph19821021
hg3esa.ph19821101
hg3esa.ph19821111
hg3esa.ph19821121
hg3esa.ph19821201
hg3esa.ph19821211"

apj="
a.pj19811201
a.pj19820301
a.pj19820601
a.pj19820901"

ipm="
hg3esi.1m.1981-10.nc
hg3esi.1m.1981-11.nc
hg3esi.1m.1981-12.nc
hg3esi.1m.1982-01.nc
hg3esi.1m.1982-02.nc
hg3esi.1m.1982-03.nc
hg3esi.1m.1982-04.nc
hg3esi.1m.1982-05.nc
hg3esi.1m.1982-06.nc
hg3esi.1m.1982-07.nc
hg3esi.1m.1982-08.nc
hg3esi.1m.1982-09.nc
hg3esi.1m.1982-10.nc
hg3esi.1m.1982-11.nc"

ips="
hg3esi.1s.1981-12_1982-02.nc
hg3esi.1s.1982-03_1982-05.nc
hg3esi.1s.1982-06_1982-08.nc
hg3esi.1s.1982-09_1982-11.nc"

ipy="hg3esi.1y.1981-12_1982-11.nc"

idumps="
hg3esi.restart.1981-12-01-00000
hg3esi.restart.1982-06-01-00000
hg3esi.restart.1982-12-01-00000"

opm="
hg3eso_1m_19811001_19811030_grid_V.nc
hg3eso_1m_19811101_19811130_grid_V.nc
hg3eso_1m_19811201_19811230_grid_V.nc
hg3eso_1m_19820101_19820130_grid_V.nc
hg3eso_1m_19820201_19820230_grid_V.nc
hg3eso_1m_19820301_19820330_grid_V.nc
hg3eso_1m_19820401_19820430_grid_V.nc
hg3eso_1m_19820501_19820530_grid_V.nc
hg3eso_1m_19820601_19820630_grid_V.nc
hg3eso_1m_19820701_19820730_grid_V.nc
hg3eso_1m_19820801_19820830_grid_V.nc
hg3eso_1m_19820901_19820930_grid_V.nc
hg3eso_1m_19821001_19821030_grid_V.nc
hg3eso_1m_19821101_19821130_grid_V.nc"

#1st seasonal mean removed since MOCI #62 - start date moved to October
#hg3eso_1s_19810901_19811130_grid_V.nc
ops="
hg3eso_1s_19811201_19820230_grid_V.nc 
hg3eso_1s_19820301_19820530_grid_V.nc
hg3eso_1s_19820601_19820830_grid_V.nc
hg3eso_1s_19820901_19821130_grid_V.nc"

opy="
hg3eso_1y_19811201_19821130_grid_V.nc"

odumps="
hg3eso_19811130_restart.nc
hg3eso_19820530_restart.nc
hg3eso_19821130_restart.nc"

CYLC_SUITE_LOG_DIR=${CYLC_SUITE_LOG_DIR:-$HOME/cylc-run/test_postproc/log/suite}
logfile=job/1/postproc_[0-9][0-9][0-9][0-9][0-9][0-9][0-9][0-9]/[0-9][0-9]/job-arch*.log
search=$(grep -r ARCHIVE $CYLC_SUITE_LOG_DIR/../$logfile)
fails=$(grep -r FAILED $CYLC_SUITE_LOG_DIR/../$logfile)
ghost=$(grep -r "does not exist" $CYLC_SUITE_LOG_DIR/../$logfile)

RC=0

echo "[INFO] Checking Atmosphere output all present and correct..."
for fn in $adumps $aph $apj $apm $apm $aps $apy; do
    if [[ "$search" != *"$fn"* ]]; then 
        echo "[FAIL] File archive not logged: $fn"
        RC=$((RC + 1))
    fi
    if [[ "$fails" == *"$fn"* ]]; then 
        echo "[FAIL] File archive failed: $fn"
        RC=$((RC + 11))
    fi
    if [[ "$ghost" == *"$fn"* ]]; then 
        echo "[FAIL] File not archived - does not exist: $fn"
        RC=$((RC + 111))
    fi
done

echo "[INFO] Checking NEMO output all present and correct..."
for fn in $odumps $opm $opm $ops $opy; do
    if [[ "$search" != *"$fn"* ]]; then 
        echo "[FAIL] File archive not logged: $fn"
        RC=$((RC + 2))
    fi
    if [[ "$fails" == *"$fn"* ]]; then 
        echo "[FAIL] File archive failed: $fn"
        RC=$((RC + 22))
    fi
    if [[ "$ghost" == *"$fn"* ]]; then 
        echo "[FAIL] File not archived - does not exist: $fn"
        RC=$((RC + 222))
    fi
done

echo "[INFO] Checking CICE output all present and correct..."
for fn in $idumps $ipm $ipm $ips $ipy; do
    if [[ "$search" != *"$fn"* ]]; then 
        echo "[FAIL] File archive not logged: $fn"
        RC=$((RC + 3))
    fi
    if [[ "$fails" == *"$fn"* ]]; then 
        echo "[FAIL] File archive failed: $fn"
        RC=$((RC + 33))
    fi
    if [[ "$ghost" == *"$fn"* ]]; then 
        echo "[FAIL] File not archived - does not exist: $fn"
        RC=$((RC + 333))
    fi
done

exit $RC
