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
!>  Contains data structures to store information about individual components.
!>

module component_info_mod

use cap_constants_mod, only : str_short

implicit none

private
public :: component_info_type, component_env_vars_type

type component_info_type
    character (len=str_short) :: component_name
    integer :: nproc
    integer :: ompthr
    integer :: hyperthreads
    integer, dimension(:), allocatable :: proc_list
    integer :: component_comm
end type component_info_type

type component_env_vars_type
    character (len=str_short) :: nproc
    character (len=str_short) :: ompthr
    character (len=str_short) :: hyperthreads
end type component_env_vars_type

end module component_info_mod