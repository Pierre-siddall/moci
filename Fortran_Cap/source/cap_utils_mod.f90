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
!>  Contains subroutines required throughout program.
!>

module cap_utils_mod

implicit none

private
public :: get_env_var, split_string, error_end_execution

interface get_env_var
  module procedure get_env_var_int
  module procedure get_env_var_string  
end interface get_env_var

contains
subroutine get_env_var_int(var_name, value)
    use cap_constants_mod, only : str_long
    implicit none

    character (len=*), intent(in   ) :: var_name
    integer, intent(  out) :: value

    character (len=str_long) :: value_char

    call get_environment_variable(trim(var_name), value_char)

    ! Convert to integer
    read(value_char, *) value
end subroutine get_env_var_int

subroutine get_env_var_string(var_name, value)
    use cap_constants_mod, only : str_long
    implicit none

    character (len=*), intent(in   ) :: var_name
    character (len=str_long), intent(  out) :: value

    call get_environment_variable(trim(var_name), value)
end subroutine get_env_var_string

subroutine split_string(string, delimiter, values)
    use cap_constants_mod, only : str_short
    implicit none

    character (len=*), intent(in  ) :: string
    character (len=*), intent(in   ) :: delimiter
    character (len=str_short), dimension(:), allocatable, intent(  out) :: values

    character (len=len(string)) :: splitting_string
    integer :: n_vals
    integer :: split_index
    integer :: i

    splitting_string = string
    n_vals = count((/(string(i:i),i=1,len_trim(string))/) == delimiter) + 1
    allocate(values(n_vals))

    do i = 1, n_vals
        split_index = index(trim(splitting_string), delimiter)

        if (split_index /= 0) then
                values(i) = splitting_string(1:(split_index-1))
                splitting_string = splitting_string((split_index+len(delimiter)):len(splitting_string))
        else
                values(i) = trim(splitting_string)
        end if
    end do
end subroutine split_string

subroutine error_end_execution(msg, abort)
    use mpi
    use, intrinsic :: iso_fortran_env, only : error_unit

    implicit none

    character (len=*), intent(in   ) :: msg
    logical, intent(in   ), optional :: abort

    integer, parameter :: errorcode = 1
    
    logical :: initialised
    integer :: ierr

    logical :: use_abort

    write(error_unit,*) '[ERROR] ', trim(msg)

    call mpi_initialized(initialised, ierr)

    use_abort = .false.
    if (present(abort)) use_abort = abort

    if (initialised) then
        if (use_abort) then
            call mpi_abort(mpi_comm_world, errorcode, ierr)
        else
            call mpi_finalize(ierr)
        end if
    end if

    stop 1
end subroutine error_end_execution

end module cap_utils_mod