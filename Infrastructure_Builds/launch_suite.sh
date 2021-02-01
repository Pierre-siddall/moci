#!/usr/bin/env bash

if [ $# -ne 2 ]; then
    echo 'This script takes two arguments, the deployment host, and the deployment path for the modules'
    exit 999;
fi

specified_host=$1
deployment_location=$2

# Ensure that the suite is checked in
fcm_status=$(fcm stat)
if [ -z "$fcm_status" ]; then
    suite_url=$(fcm info | grep URL | grep -v Relative);
    suite_revision=$(fcm info | grep Revision);
else
    echo "The suite working copy must be checked in to run in deployment mode"
    exit 999
fi

cd infrastructure_suite

# Test the versioning fits our specifications (YYYY-mm-compiler)
gc_version=$(grep '^GC_PRG_ENV_VERSION=' rose-suite.conf | cut -d '=' -f 2-)
xios_version=$(grep '^XIOS_MOD_VERSION=' rose-suite.conf | cut -d '=' -f 2-)
oasis_version=$(grep '^OASIS_MOD_VERSION=' rose-suite.conf | cut -d '=' -f 2-)

#check this isn't the default value
version_default=\'YYYY-mm-compiler\'
if [ $gc_version == $version_default ] || [ $xios_version == $version_default ] || [ $oasis_version == $version_default ]; then
    1>&2 echo "At least one module version is set to the default value, please verify"
    exit 999
fi

# Check we deploy only when extracting code from the Cerfacs GIT repository
cerfacs_repo_url=\'git@nitrox.cerfacs.fr:globc/OASIS3-MCT/oasis3-mct.git\'
l_extract_oasis=$(grep '^EXTRACT_OASIS=' rose-suite.conf | cut -d '=' -f 2-)
oasis_repo_conf=$(grep -E '^\!{0,2}OASIS_REPOSITORY=' rose-suite.conf | cut -d '=' -f 2-)
if [ $l_extract_oasis != "true" ] || [ $cerfacs_repo_url != $oasis_repo_conf ]; then
    1>&2 echo "Must extract oasis from Cerfacs repository to run in deployment mode"
    exit 999
fi

current_directory=$(basename "$PWD")
run_name="${current_directory}_deploy_${specified_host}"
echo "Running launch suite as $run_name. Deploying modules to $specified_host"


echo $suite_url
echo $suite_revision

rose suite-run --define-suite="DEPLOYMENT_HOST='$specified_host'" --define-suite="MODULE_BASE='$deployment_location'" --define-suite="SUITE_URL='$suite_url'" --define-suite="SUITE_REVISION='$suite_revision'" --name="$run_name" --new
