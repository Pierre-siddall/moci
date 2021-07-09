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
!>  Contains subroutines for initialising, running, and finalising the separate
!>  components. Handles generic processes, while component_manager_mod contains
!>  subroutines to handle model specific processing.
!>

module cap_mod

use component_info_mod, only : component_info_type

implicit none

private
public :: initialise, run, finalise

integer, private :: cap_comm
type(component_info_type), dimension(:), allocatable, private :: components_info
integer, private :: component_id

contains
subroutine initialise()
    use resources_mod, only : init_mpi
    use component_setup_mod, only : init_components
    use comm_init_mod, only : split_communicator
    use component_manager_mod, only : initialise_components
    implicit none

    integer :: ierr

    call init_mpi()

    call init_components(components_info)

    call split_communicator(cap_comm, components_info, component_id)

    call initialise_components(components_info, component_id)
end subroutine initialise

subroutine run()
    use component_manager_mod, only : run_components
    implicit none

    call run_components(components_info, component_id)
end subroutine run

subroutine finalise()
    use resources_mod, only : finalise_mpi
    use component_manager_mod, only : finalise_components
    implicit none

    call finalise_components(components_info, component_id)

    call finalise_mpi(cap_comm, components_info(component_id)%component_comm)
end subroutine finalise

end module cap_mod