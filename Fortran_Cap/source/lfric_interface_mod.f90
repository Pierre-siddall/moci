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
!>  Interface to LFRic.
!>

module lfric_interface_mod

implicit none

private
public :: init_lfric, run_lfric, finalise_lfric, set_lfric_env_vars

contains
subroutine init_lfric()
    use cli_mod,           only : get_initial_filename
    use gungho_driver_mod, only : initialise
    implicit none

    character(:), allocatable :: filename

    call get_initial_filename( filename )
    call initialise( filename )
    deallocate( filename )
end subroutine init_lfric

subroutine run_lfric()
    use gungho_driver_mod, only : run
    implicit none

    call run()
end subroutine run_lfric

subroutine finalise_lfric()
    use gungho_driver_mod, only : finalise
    implicit none

    call finalise()
end subroutine finalise_lfric

subroutine set_lfric_env_vars(lfric_env_vars)
    use component_info_mod, only : component_env_vars_type
    implicit none

    type(component_env_vars_type), intent(  out) :: lfric_env_vars

    lfric_env_vars%nproc = "LFRIC_NPROC"
    lfric_env_vars%ompthr = "OMPTHR_ATM"
    lfric_env_vars%hyperthreads = "HYPERTHREADS"
end subroutine set_lfric_env_vars

end module lfric_interface_mod