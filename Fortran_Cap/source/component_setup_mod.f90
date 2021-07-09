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
!>  Handles gathering of information required to split global communicator.
!>

module component_setup_mod

implicit none

private
public :: init_components

contains
subroutine init_components(components_info)
    use component_info_mod, only : component_info_type
    use cap_constants_mod, only : str_short
    implicit none

    type(component_info_type), dimension(:), allocatable, intent(  out) :: components_info
    character (len=str_short), dimension(:), allocatable :: component_names
    
    call get_component_names(component_names)

    allocate(components_info(size(component_names)))

    call get_component_data(component_names, components_info)

    deallocate(component_names)
end subroutine init_components

subroutine get_component_names(component_names)
    use cap_utils_mod, only: get_env_var, split_string, error_end_execution
    use component_manager_mod, only: supported_models
    use cap_constants_mod, only : str_short, str_med, str_long
    implicit none

    character (len=str_short), dimension(:), allocatable, intent(  out) :: component_names
    character (len=str_long) :: all_component_names

    character (len=*), parameter :: env_var_name = "spmd_components"
    character (len=*), parameter :: delimiter = " "

    integer :: i
    character (len=str_med) :: msg

    call get_env_var(env_var_name, all_component_names)

    if (len_trim(all_component_names) == 0) then
        msg = "Environment variable " // env_var_name // " not set"
        call error_end_execution(msg)
    end if

    call split_string(trim(all_component_names), delimiter, component_names)

    ! Check components are supported
    do i = 1, size(component_names)
        if (.not. any(supported_models == component_names(i))) then
            ! Component not supported, output error
            msg = "Component " // trim(component_names(i)) // " not currently supported"
            call error_end_execution(msg)
        end if
    end do
end subroutine get_component_names

subroutine get_component_data(component_names, components_info)
    use mpi, only : MPI_COMM_NULL
    use component_info_mod
    use cap_utils_mod
    use component_manager_mod, only : set_component_env_vars
    use cap_constants_mod, only : str_short
    implicit none

    character (len=str_short), dimension(:), intent(in   ) :: component_names
    type(component_info_type),    dimension(:), intent(  out) :: components_info
    integer :: i
    type(component_env_vars_type) :: component_env_vars

    do i = 1,size(component_names)
        call set_component_env_vars(component_names(i), component_env_vars)

        components_info(i)%component_name = component_names(i)

        call get_env_var(component_env_vars%nproc, components_info(i)%nproc)

        ! Allocate proc_list using nproc
        allocate(components_info(i)%proc_list(components_info(i)%nproc))

        if (len_trim(component_env_vars%ompthr) > 0) then
            call get_env_var(component_env_vars%ompthr, components_info(i)%ompthr)
        else
            components_info(i)%ompthr = 1
        end if

        if (len_trim(component_env_vars%hyperthreads) > 0) then
            call get_env_var(component_env_vars%hyperthreads, components_info(i)%hyperthreads)
        else
            components_info(i)%hyperthreads = 1
        end if

        components_info(i)%component_comm = MPI_COMM_NULL
    end do
end subroutine get_component_data

end module component_setup_mod