##############################################################################
# (c) Crown copyright 2021 Met Office. All rights reserved.
# 
# Use, duplication or disclosure of this code is subject to the restrictions
# as set forth in the licence. If no licence has been raised with this copy
# of the code, the use, duplication or disclosure of it is strictly
# prohibited. Permission to do so must first be obtained in writing from the
# Met Office Information Asset Owner at the following address:
#
# Met Office, FitzRoy Road, Exeter, Devon, EX1 3PB, United Kingdom
##############################################################################

# The default value of FC is almost always "f77" which is of no use to us.
# An empty FC is also of no use.
ifneq "$(or $(filter default, $(origin FC)), $(filter x, x$(FC)))" ""
  $(error The FC environment variable must be set to a Fortran compiler command)
endif

# Set up verbose logging...
ifdef VERBOSE
  Q :=
  VERBOSE_ARG = -verbose
  SHORT_VERBOSE_ARG = -v
  DOUBLE_VERBOSE_ARG = --verbose
else
  Q := @
  QUIET_ARG = --quiet
  VERBOSE_REDIRECT = >/dev/null
endif

export Q QUIET_ARG VERBOSE_REDIRECT

# We only want to send terminal control characters if there is a terminal to
# interpret them...
#
_NOW = `date +%H:%M:%S`
ifneq 'x$(TERM)' 'x'
  MESSAGE = $(Q)printf "%s \\033[1m$(1)\\033[0m %s\n" $(_NOW) $(2)
else
  MESSAGE = $(Q)echo $(_NOW) *$(1)* $(2)
endif

# Compiling on Cray so set dynamic to static and combine static libs
EXTERNAL_STATIC_LIBRARIES	:= $(EXTERNAL_STATIC_LIBRARIES) $(EXTERNAL_DYNAMIC_LIBRARIES) $(EXTERNAL_COUPLING_LIBRARIES)
EXTERNAL_DYNAMIC_LIBRARIES	:=

export PROJECT_DIR := $(realpath $(dir $(lastword $(MAKEFILE_LIST))))

$(info Project Directory $(PROJECT_DIR))

# Build a set of "-I" arguments to seach the whole object tree:
INCLUDE_ARGS := $(subst ./,-I,$(shell find . -mindepth 1 -type d -print))

ALL_OBJECTS = cap_constants_mod.o cap_utils_mod.o component_info_mod.o xios_interface_mod.o nemo_interface_mod.o lfric_interface_mod.o component_manager_mod.o component_setup_mod.o comm_init_mod.o resources_mod.o cap_mod.o cap.o

# Set option to check Fortran standard
ifdef PE_ENV
  $(info PE_ENV $(PE_ENV))
  ifeq ($(PE_ENV),INTEL)
    STANDARDS_CHECK_ARG = -stand f03
  else ifeq ($(PE_ENV),CRAY)
    STANDARDS_CHECK_ARG = -en
  else ifeq ($(PE_ENV),GNU)
    STANDARDS_CHECK_ARG = -std=f2003
  else ifeq ($(PE_ENV),PGI)
    STANDARDS_CHECK_ARG = 
  endif
endif

.PHONY: build
build: BIN_DIR	   ?= $(PROJECT_DIR)/bin
build: applications

.PHONY: applications
applications: $(addprefix $(BIN_DIR)/,cap)
	$(call MESSAGE,Checking,cap)

$(BIN_DIR)/cap: cap.x | $(BIN_DIR)
	$(call MESSAGE,Installing,$@)
	$(Q)cp $< $@

.PRECIOUS: cap.x
cap.x: $(ALL_OBJECTS)
	$(call MESSAGE,Linking,$@)
	$(Q)$(FC) $(LDFLAGS_COMPONENTS) $(LDFLAGS) \
		-o $@ \
		$(patsubst %,-l%,$(EXTERNAL_DYNAMIC_LIBRARIES)) \
		$^ \
		$(COMPONENT_LIBRARIES) \
		$(patsubst %,-l%,$(EXTERNAL_STATIC_LIBRARIES)) $(OPENMP_ARG)

.PRECIOUS: %.o %.mod
%.o %.mod: source/%.f90
	$(call MESSAGE,Compiling,$<)
	$(Q)$(FC) -c $< \
		$(STANDARDS_CHECK_ARG) $(FFLAGS) $(INCLUDE_ARGS) $(FFLAGS_COMPONENTS)

# Directories
#
$(BIN_DIR):
	$(call MESSAGE,Creating,$@)
	$(Q)mkdir -p $@