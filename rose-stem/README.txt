MOCI Rose stem test Suite
=========================

The MOCI rose stem test suite tests the contents of the MOCI repository. It
is run in the standard way using the command
rose stem --group=TEST_GROUP. 

See the Rose documentation for more details:
http://metomi.github.io/rose/doc/rose.html

Some parts of the test suite have platform specific settings. For supported 
sites, there are platform specific optional configurations which will set these 
values correctly for the chosen platform. To use of these configurations
start the test suite as follows:
rose stem --group=TEST_GROUP --opt-conf-key=PLATFORM_NAME

Each of the suppported platforms has a rose-app-PLATFORM_NAME.conf file
in the opt sub-directory. Alternatively you can use custom settings by modifying
the rose-suite.conf file. This can be done using the Rose Edit GUI, which can
be launched calling the command "rose edit" from the rose-stem directory.


