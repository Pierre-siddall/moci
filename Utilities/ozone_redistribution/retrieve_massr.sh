#!/usr/bin/env sh
#####################################################################
# NAME: retrieve_mass.sh
#
# PURPOSE:
#   Retrieve requested data from MASS archive
#
# Required Arguments
#   -a  Path to MASS archive collection
#   -y  Year of data to retrieve
#   -f  First month of data required
#   -l  Last month of data required
#   -s  STASHcode(s), comma separated
#   -o  Output filename
#
# Requried environment
#   OZONE_SHARE - Share directory to put final output
######################################################################
STDERR=select.err
STDOUT=select.out

RC_OK=0
RC_ERROR=99

error_analysis () {
  echo [MOOSE ERR] $(cat $STDERR) >&2
  case $(cat $STDERR) in
    *'command not found'* )
       RC=$RC_ERROR
       ;;
    *'no such data'*|*'no file atoms are matched'* )
        # No data - OK if within 1 year of Nrun
       echo [WARN] No data set/collection available.
       echo        This is acceptable for the PRIMARY archive within 1 year of NRun.
       RC=$RC_OK
       ;;
    * )
       RC=$RC_ERROR
       ;;
  esac
}

# Parse arguments
while getopts a:f:l:o:s:y: flag ; do
    case "$flag" in
	a) archive_path=${OPTARG};;
        f) first_month=${OPTARG};;
        l) last_month=${OPTARG};;
        y) year=${OPTARG};;
        s) stash=${OPTARG};;
        o) output_file=${OPTARG};;
    esac
done

# Select data 
echo "begin
stash = ($stash)
month = [$first_month .. $last_month]
year = $year
end" > query

echo [MOOSE] moo select -C query $archive_path $output_file
moo select -C query $archive_path $output_file > $STDOUT 2> $STDERR
RC=$?
months=$(grep -o months=.. $STDOUT)

case $months in 
    "months="?? )
        num=${months//[^0-9]/}
        echo [INFO] $num months extracted from $archive_path
        ;;
    * )
        error_analysis
        ;;
esac

if [[ "$RC" == "$RC_OK" ]] && [[ -f "$output_file" ]] ; then
    # echo [DEBUG] Copying $output_file tp $OZONE_SHARE 
    cp $output_file $OZONE_SHARE/
    $RC = $?
fi

exit $RC
