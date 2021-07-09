!-----------------------------------------------------------------------------
! (C) Crown copyright 2021 Met Office. All rights reserved.
! 
! Use, duplication or disclosure of this code is subject to the restrictions
! as set forth in the licence. If no licence has been raised with this copy
! of the code, the use, duplication or disclosure of it is strictly
! prohibited. Permission to do so must first be obtained in writing from the
! Met Office Information Asset Owner at the following address:
!
! Met Office, FitzRoy Road, Exeter, Devon, EX1 3PB, United Kingdom
!-----------------------------------------------------------------------------
!> 
!> DESCRIPTION
!>  Contains constants for use throughout the cap.
!>

module cap_constants_mod

implicit none

private
public :: str_short, str_med, str_long, missing_env_var_name

! Define lengths for string variables
integer, parameter :: str_short = 16
integer, parameter :: str_med   = 128
integer, parameter :: str_long  = 255

! Define missing data constants
character (len=*), parameter :: missing_env_var_name = ""

end module cap_constants_mod