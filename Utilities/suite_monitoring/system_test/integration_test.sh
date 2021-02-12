#!/usr/bin/env sh
#*****************************COPYRIGHT******************************
# (C) Crown copyright 2019-2020 Met Office. All rights reserved.
#
# Use, duplication or disclosure of this code is subject to the restrictions
# as set forth in the licence. If no licence has been raised with this copy
# of the code, the use, duplication or disclosure of it is strictly
# prohibited. Permission to do so must first be obtained in writing from the
# Met Office Information Asset Owner at the following address:
#
# Met Office, FitzRoy Road, Exeter, Devon, EX1 3PB, United Kingdom
#*****************************COPYRIGHT******************************

# Run a series of integration tests to check various calls to the script
# Expects a test database in log/db in the current directory

rm -f *output

failed_tests=""
failed_number=0


echo "Testing raw output"
../suite_run_rates.py -r raw ./ > raw_output
diff_output=$(diff raw_output kgo/raw_kgo)
if [ -z "$diff_output" ]
then
    echo "  Raw output test has succeeded";
    echo ""
    rm raw_output
else
    echo "$diff_output" > diff_raw_output;
    echo "  Raw output test has failed, see diff in diff_raw_output"
    echo ""
    failed_tests="$failed_tests raw_output"
    failed_number=$((failed_number+1))
fi


echo "Testing summary output"
../suite_run_rates.py -r summary ./ > summary_output
diff_output=$(diff summary_output kgo/summary_kgo)
if [ -z "$diff_output" ]
then
    echo "  Summary output test has succeeded";
    echo ""
    rm summary_output
else
    echo "$diff_output" > diff_summary_output;
    echo "  Summary output test has failed, see diff in diff_summary_output"
    echo ""
    failed_tests="$failed_tests summary_output"
    failed_number=$((failed_number+1))
fi


echo "Testing detailed output"
../suite_run_rates.py -r detailed ./ > detailed_output
diff_output=$(diff detailed_output kgo/detailed_kgo)
if [ -z "$diff_output" ]
then
    echo "  Detailed output test has succeeded";
    echo ""
    rm detailed_output
else
    echo "$diff_output" > diff_detailed_output;
    echo "  Detailed output test has failed, see diff in diff_detailed_output"
    echo ""
    failed_tests="$failed_tests detailed_output"
    failed_number=$((failed_number+1))
fi


echo "Testing interpolated output"
../suite_run_rates.py -r interpolated ./ > interpolated_output
diff_output=$(diff interpolated_output kgo/interpolated_kgo)
if [ -z "$diff_output" ]
then
    echo "  Interpolated output test has succeeded";
    echo ""
    rm interpolated_output
else
    echo "$diff_output" > diff_interpolated_output;
    echo "  Interpolated output test has failed, see diff in"
    echo "  diff_interpolated_output"
    echo ""
    failed_tests="$failed_tests interpolated_output"
    failed_number=$((failed_number+1))
fi

echo "Testing detailed unformatted output"
../suite_run_rates.py -p -r detailed ./ > detailed_unformatted_output
diff_output=$(diff detailed_unformatted_output kgo/detailed_unformatted_kgo)
if [ -z "$diff_output" ]
then
    echo "  Detailed unformatted output test has succeeded";
    echo ""
    rm detailed_unformatted_output
else
    echo "$diff_output" > diff_detailed_unformatted_output;
    echo "  Detailed unformatted output test has failed, see diff in"
    echo "  diff_detailed_unformatted_output"
    echo ""
    failed_tests="$failed_tests detailed_unformatted_output"
    failed_number=$((failed_number+1))
fi

echo "Testing all options"
../suite_run_rates.py -c 2 -m 20 -y 300 -a 0.1 -i 0.01 -j coupled -s 0.5 -e 1.8 -p -r raw ./ > all_options_output
diff_output=$(diff all_options_output kgo/all_options_kgo)
if [ -z "$diff_output" ]
then
    echo "  All command line options test has succeeded";
    echo ""
    rm all_options_output
else
    echo "$diff_output" > diff_all_options_output;
    echo "  Detailed unformatted output test has failed, see diff in"
    echo "  diff_all_options_output"
    echo ""
    failed_tests="$failed_tests all_options_output"
    failed_number=$((failed_number+1))
fi

if [ -z "$failed_tests" ]
then
    echo "All tests have succeeded"
else
    echo "$failed_number task(s) failed"
    echo "  $failed_tests"
fi

