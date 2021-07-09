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
!>  Provides a cap to run coupled models from a single executable.
!>

program cap
    use cap_mod, only : initialise, run, finalise
    implicit none

    call initialise()
    call run()
    call finalise()
end program cap