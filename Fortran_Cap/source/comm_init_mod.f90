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
!>  Contains subroutines to split global MPI communicator into communicators
!>  for each component.
!>

module comm_init_mod

use cap_constants_mod,  only : str_short
use component_info_mod, only : component_info_type

implicit none

private
public :: split_communicator

character (len=*), dimension(1), public, parameter ::                               &
        supported_tasks_distribution = (/ character(len=str_short) :: "contiguous" /)

contains

subroutine set_cap_comm(cap_comm, nproc)
    use mpi
    use cap_utils_mod, only : error_end_execution
    use cap_constants_mod, only: str_short, str_med

    implicit none

    integer, intent(  out) :: cap_comm
    integer, intent(in   ) :: nproc

    integer :: ierr
    integer :: rank
    integer :: global_group, cap_group
    integer, dimension(:), allocatable :: rank_list
    integer :: i
    character (len=str_med) :: msg
    character (len=str_short) :: nproc_char

    allocate(rank_list(nproc))

    do i = 1,nproc
        rank_list(i) = i - 1
    end do

    call mpi_comm_rank(mpi_comm_world, rank, ierr)

    if (.not. any(rank_list == rank)) then
        ! PEs 0...nproc - 1 not running cap
        write (nproc_char, '(I6)') (nproc - 1)
        msg = "Processes 0 to "//trim(adjustl(nproc_char))//" not running cap executable. Cannot create a communicator for the cap."
        call error_end_execution(msg,.true.)
    end if

    ! Create an MPI group of processes running this executable
    call mpi_comm_group(mpi_comm_world, global_group, ierr)
    call mpi_group_incl(global_group, nproc, rank_list, cap_group, ierr)

    ! Create communicator for processes running this executable
    call mpi_comm_create_group(mpi_comm_world, cap_group, 0, cap_comm, ierr)

    call mpi_group_free(global_group, ierr)
    call mpi_group_free(cap_group, ierr)

    deallocate(rank_list)
end subroutine set_cap_comm

subroutine split_communicator(cap_comm, components_info, component_id)
    use mpi
    use cap_utils_mod, only: get_env_var, error_end_execution
    use cap_constants_mod, only: str_med, str_long

    implicit none

    integer, intent(out   ) :: cap_comm
    type(component_info_type), dimension(:), intent(inout) :: components_info
    integer, intent(  out) :: component_id

    character (len=*), parameter :: env_var_name = "TASKS_DISTRIBUTION"

    character (len=str_long) :: tasks_distribution

    character (len=str_med) :: msg
    integer :: ierr
    integer :: world_size, world_rank
    integer :: colour = MPI_UNDEFINED
    integer :: component_communicator

    integer :: i
    integer :: total_nproc = 0

    call mpi_comm_size(mpi_comm_world, world_size, ierr)
    call mpi_comm_rank(mpi_comm_world, world_rank, ierr)

    ! Check sum of component nproc does not exceed world size, shouldn't as calculated in suite/driver!
    do i = 1, size(components_info)
        total_nproc = total_nproc + components_info(i)%nproc
    end do

    if (total_nproc > world_size) then
        ! Output error, end execution
        msg = "Total nproc required more than available"
        call error_end_execution(msg)
    end if

    if (total_nproc < world_size) then
        ! May be more than one executable running, create new global communicator
        call set_cap_comm(cap_comm, total_nproc)
    else
        ! Duplicate mpi_comm_world
        call mpi_comm_dup(mpi_comm_world, cap_comm, ierr)
    end if

    call get_env_var(env_var_name, tasks_distribution)

    if (trim(tasks_distribution) == "contiguous") then
        call contiguous_split(components_info, total_nproc)
    else
        ! Tasks distribution method not supported, output error message and end execution... or default to something?
        msg = "Tasks distribution method, '"//trim(tasks_distribution)//"', not supported"
        call error_end_execution(msg)
    end if

    do i = 1, size(components_info)
        if (any(components_info(i)%proc_list == world_rank)) then
            component_id = i
            colour = i - 1
        end if
    end do

    call mpi_comm_split(cap_comm, colour, world_rank, component_communicator, ierr)

    components_info(component_id)%component_comm = component_communicator
end subroutine split_communicator

subroutine contiguous_split(components_info, total_nproc)
    implicit none

    type(component_info_type), dimension(:), intent(inout) :: components_info
    integer, intent(in   ) :: total_nproc
    integer :: i, j
    integer :: start
    
    start = 0

    do i = 1,size(components_info)
        do j = 1, components_info(i)%nproc
            components_info(i)%proc_list(j) = start + j - 1
        end do

        start =  start + components_info(i)%nproc
    end do
end subroutine contiguous_split

end module comm_init_mod
