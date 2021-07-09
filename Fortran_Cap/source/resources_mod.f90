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
!>  Contains subroutines for managing MPI.
!>

module resources_mod

implicit none

private
public :: init_mpi, finalise_mpi

contains
subroutine init_mpi()
    use mpi, only : mpi_init, MPI_SUCCESS
    use cap_utils_mod, only : error_end_execution
    use cap_constants_mod, only : str_med
    implicit none

    integer :: ierr
    character (len=str_med) :: msg

    call mpi_init(ierr)

    if (ierr /= MPI_SUCCESS) then
        msg = "MPI initialisation not successful."
        call error_end_execution(msg)
    end if
end subroutine init_mpi

subroutine finalise_mpi(cap_comm, component_comm)
    use mpi, only : mpi_comm_free, mpi_finalize, MPI_SUCCESS
    use cap_utils_mod, only : error_end_execution
    use cap_constants_mod, only : str_med
    implicit none

    integer, intent(in   ) :: cap_comm
    integer, intent(in   ) :: component_comm
    integer :: ierr
    character (len=str_med) :: msg

    call mpi_comm_free(component_comm, ierr)
    call mpi_comm_free(cap_comm, ierr)
    call mpi_finalize(ierr)

    if (ierr /= MPI_SUCCESS) then
        msg = "MPI finalisation not sucessful."
        call error_end_execution(msg,.true.)
    end if
end subroutine finalise_mpi
end module resources_mod