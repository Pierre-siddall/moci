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
!>  Interface to XIOS server.
!>

module xios_interface_mod

implicit none

private
public :: init_xios, finalise_xios, set_xios_env_vars

contains
subroutine init_xios()
    use xios
    use mod_oasis

    implicit none

    character (len=*), parameter :: xios_oasis_id = "xios.x"

    integer :: ierr
    integer :: comp_id

    call oasis_init_comp(comp_id, xios_oasis_id, ierr)

    call xios_init_server
end subroutine init_xios

subroutine finalise_xios()
    use mod_oasis

    implicit none

    integer :: ierr

    call oasis_terminate(ierr)
end subroutine finalise_xios

subroutine set_xios_env_vars(xios_env_vars)
    use component_info_mod, only : component_env_vars_type
    use cap_constants_mod, only : missing_env_var_name
    implicit none

    type(component_env_vars_type), intent(  out) :: xios_env_vars

    xios_env_vars%nproc = "XIOS_NPROC"
    xios_env_vars%ompthr = missing_env_var_name
    xios_env_vars%hyperthreads = missing_env_var_name
end subroutine set_xios_env_vars

end module xios_interface_mod