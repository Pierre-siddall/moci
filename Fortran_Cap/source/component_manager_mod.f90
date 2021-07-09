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
!>  Handles passing processing to the correct component interfaces.
!>

module component_manager_mod
use cap_constants_mod, only : str_short
implicit none

private
public :: initialise_components, run_components, finalise_components, set_component_env_vars

character (len=*), dimension(3), public, parameter ::                      &
    supported_models = (/ character(len=str_short) :: "lfric","nemo","xios"/)

contains
subroutine initialise_components(components_info, component_id)
    use component_info_mod, only : component_info_type, component_env_vars_type
    use lfric_interface_mod, only : init_lfric
    use nemo_interface_mod, only : init_nemo
    use xios_interface_mod, only : init_xios
    implicit none

    type(component_info_type), dimension(:), intent(in   ) :: components_info
    integer, intent(in   ) :: component_id

    integer :: ierr

    if (trim(components_info(component_id)%component_name) == "lfric") then
        call init_lfric()
    else if (trim(components_info(component_id)%component_name) == "nemo") then
        call init_nemo()
    else if (trim(components_info(component_id)%component_name) == "xios") then
        call init_xios()
    end if
end subroutine initialise_components

subroutine run_components(components_info, component_id)
    use component_info_mod, only : component_info_type, component_env_vars_type
    use lfric_interface_mod, only : run_lfric
    use nemo_interface_mod, only : run_nemo
    implicit none

    type(component_info_type), dimension(:), intent(in   ) :: components_info
    integer, intent(in   ) :: component_id

    integer :: ierr

    if (trim(components_info(component_id)%component_name) == "lfric") then
        call run_lfric()
    else if (trim(components_info(component_id)%component_name) == "nemo") then
        call run_nemo()
    end if
end subroutine run_components

subroutine finalise_components(components_info, component_id)
    use component_info_mod, only : component_info_type, component_env_vars_type
    use lfric_interface_mod, only : finalise_lfric
    use nemo_interface_mod, only : finalise_nemo
    use xios_interface_mod, only : finalise_xios
    implicit none

    type(component_info_type), dimension(:), intent(in   ) :: components_info
    integer, intent(in   ) :: component_id

    integer :: ierr

    if (trim(components_info(component_id)%component_name) == "lfric") then
        call finalise_lfric()
    else if (trim(components_info(component_id)%component_name) == "nemo") then
        call finalise_nemo()
    else if (trim(components_info(component_id)%component_name) == "xios") then
        call finalise_xios()
    end if
end subroutine finalise_components

subroutine set_component_env_vars(component_name, component_env_vars)
    use component_info_mod, only : component_info_type, component_env_vars_type
    use cap_constants_mod, only : str_short
    use lfric_interface_mod, only : set_lfric_env_vars
    use nemo_interface_mod, only : set_nemo_env_vars
    use xios_interface_mod, only : set_xios_env_vars
    implicit none

    character (len=str_short), intent(in   ) :: component_name
    type(component_env_vars_type), intent(  out) :: component_env_vars

    if (trim(component_name) == "lfric") then
        call set_lfric_env_vars(component_env_vars)
    else if (trim(component_name) == "nemo") then
        call set_nemo_env_vars(component_env_vars)
    else if (trim(component_name) == "xios") then
        call set_xios_env_vars(component_env_vars)
    end if
end subroutine set_component_env_vars

end module component_manager_mod
