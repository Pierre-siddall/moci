#!/usr/bin/env bash
#
# NAME: run_xios_toy.sh
#
# DESCRIPTION: Runs the XIOS toy test
#
# ENVIRONMENT VARIABLES (COMPULSORY):
#    XIOS_ONLY
#    XIOS_TEST_MODE - takes two values, either 'attached' or 'server'

if ! [[ "$XIOS_TEST_MODE" =~ ^(attached|server)$ ]]; then
    echo "Script must have XIOS_TEST_MODE either attached or server" 2>&1;
    exit 1;
fi

source_file=xios_toy.F90
executable_file=xios_toy.exe

cp -f $CYLC_SUITE_RUN_DIR/src/$source_file ./

if [ -f $executable_file ]; then
    echo "File $executable_file exists - removing before compilation"
    rm $executable_file
fi

echo "Building $executable_file"
if [ "$XIOS_ONLY" = "True" ]; then
    build_flags="-I$XIOS_INC -L$XIOS_LIB -lxios -lfmpich"
else
    build_flags="-I$OASIS_INC -L$OASIS_LIB -lpsmile.MPI1 -lscrip -lmct -lmpeu -I$XIOS_INC -L$XIOS_LIB -I$OASIS_INC -L$OASIS_LIB -lxios -lpsmile.MPI1 -lscrip -lmct -lmpeu -lfmpich"
fi

ftn -o $executable_file $build_flags $source_file
#check the build has run ok
[ $? -eq 0 ] || exit 1

if [ "$XIOS_TEST_MODE" = "attached" ]; then
    echo "Preparing to run in attached mode..."
    echo "Updating iodef.xml if required...."
    sed -i 's;          <variable id="using_server" type="bool">true</variable>;          <variable id="using_server" type="bool">false</variable>;g' iodef.xml
    echo "Running in attached mode....";
    mpiexec -n 1 ./$executable_file;
elif [ "$XIOS_TEST_MODE" = "server" ]; then
    echo "Preparing to run in server mode"
    echo "Updating iodef.xml if required...."
    sed -i 's;          <variable id="using_server" type="bool">false</variable>;          <variable id="using_server" type="bool">true</variable>;g' iodef.xml
    echo "Running in server mode....";
    mpiexec -n 1 ./$executable_file : -n 1 $XIOS_EXEC;
fi
    
#check mpiexec has run ok
[ $? -eq 0 ] || exit 1

#check the output file is produced
ls output.nc
[ $? -eq 0 ] || exit 1

# Check we have run in the correct mode and the server has run if needed
if [ "$XIOS_TEST_MODE" = "attached" ]; then
    ls xios_client*out
    [ $? -eq 0 ] || exit 1
    ls xios_server*out
    [ $? -ne 0 ] || exit 1
elif [ "$XIOS_TEST_MODE" = "server" ]; then
    ls xios_client*out xios_server*out
    [ $? -eq 0 ] || exit 1
fi
