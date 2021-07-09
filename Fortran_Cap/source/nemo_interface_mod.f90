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
!>  Interface to NEMO.
!>

module nemo_interface_mod

implicit none

private
public :: init_nemo, run_nemo, finalise_nemo, set_nemo_env_vars

contains
subroutine init_nemo()
    use nemogcm, only : nemo_gcm_init
    implicit none

    call nemo_gcm_init()
end subroutine init_nemo

subroutine run_nemo()
    use nemogcm, only : nemo_gcm_run
    implicit none

    call nemo_gcm_run()
end subroutine run_nemo

subroutine finalise_nemo()
    use nemogcm, only : nemo_gcm_finalise
    implicit none

    call nemo_gcm_finalise()
end subroutine finalise_nemo

subroutine set_nemo_env_vars(nemo_env_vars)
    use component_info_mod, only : component_env_vars_type
    implicit none

    type(component_env_vars_type), intent(  out) :: nemo_env_vars

    nemo_env_vars%nproc = "NEMO_NPROC"
    nemo_env_vars%ompthr = "OMPTHR_OCN"
    nemo_env_vars%hyperthreads = "OHYPERTHREADS"
end subroutine set_nemo_env_vars
    
end module nemo_interface_mod