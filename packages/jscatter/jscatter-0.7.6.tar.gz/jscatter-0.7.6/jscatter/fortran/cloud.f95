!    -*- f90 -*-
! -*- coding: utf-8 -*-
! written by Ralf Biehl at the Forschungszentrum Juelich ,
! Juelich Center for Neutron Science 1 and Institute of Complex Systems 1
!    jscatter is a program to read, analyse and plot data
!    Copyright (C) 2018  Ralf Biehl
!
!    This program is free software: you can redistribute it and/or modify
!    it under the terms of the GNU General Public License as published by
!    the Free Software Foundation, either version 3 of the License, or
!    (at your option) any later version.
!
!    This program is distributed in the hope that it will be useful,
!    but WITHOUT ANY WARRANTY; without even the implied warranty of
!    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
!    GNU General Public License for more details.
!
!    You should have received a copy of the GNU General Public License
!    along with this program.  If not, see <http://www.gnu.org/licenses/>.
!

! f2py -c fscatter.f95 -m fscatter


module cloud
    use typesandconstants
    use utils


contains

    function ffq(point,r,q,blength,formfactor,rms,ffpolydispersity) result(res)
        use typesandconstants
        use utils
        ! point point on unit sphere 3 x 1
        real(dp), intent(in) :: point(:)
        ! wavevector scalar
        real(8), intent(in) :: q
        ! positions N x 3, scattering length xN
        real(dp), intent(in) :: r(:,:) , blength(:)
        ! formfactor 2xN
        real(dp), intent(in) :: formfactor(:,:)
        ! rms , polydispersity real
        real(dp), intent(in) :: rms, ffpolydispersity
        ! scattering amplitude F and formfactor F*f.conj
        real(dp),dimension(3) :: res

        ! local variables
        real(dp)    :: sizerms(size(r,1)), volrmsfactor(size(r,1)), fa(size(r,1))
        real(dp)    :: qx(3), rg(size(r,1),3), rg1(size(r,1),1) !, rr(size(r,1),3)
        complex(dp) :: iqr(size(r,1))
        complex(dp) :: Fq

        Fq=0*j1
        iqr=0*j1
        rg1=0_dp
        qx=0_dp
        rg=0_dp
        res=0_dp
        sizerms=0_dp
        volrmsfactor=0_dp
        fa=0_dp

        if (ffpolydispersity>0) then
            ! normal distribution of size factor
            rg1=random_gauss(size(r,1),1)
            sizerms = rg1(:,1) * ffpolydispersity + 1_dp
            ! correponding relative volume change
            where( sizerms <= 0._dp )  sizerms=0._dp
            volrmsfactor=sizerms**3
            ! interpolate with rms
            fa = blength *volrmsfactor* interp(sizerms*q, formfactor(1,:), formfactor(2,:))
        else
            !fa=blength
            fa=blength*interp_s(q, formfactor(1,:), formfactor(2,:))
        endif

        qx=q*point
        if (rms>0) then
            rg=random_gauss(size(r,1),3)*rms
            iqr= j1 * matmul(r+rg,qx)
        else
            iqr= j1 * matmul(r   ,qx)
        end if

        Fq= sum( fa* exp(iqr) )
        res(1)=q
        res(2)=REALPART(Fq*conjg( Fq ))
        res(3)=REALPART(Fq)

    end function ffq

    function sphereaverage_ffq(q,r,blength,formfactor,rms,ffpolydispersity, relError) result(sphave)
        ! sphere average as average on fibonacci lattice for ffq
        ! returns mean
        ! not used as not faster than actual method
        use typesandconstants
        use utils
        real(dp), intent(in)    :: q, r(:,:), blength(:), formfactor(:,:),rms, ffpolydispersity
        integer, intent(in)     :: relError

        real(dp)                :: qfib(2*relError+1,3),points(2*relError+1,3),results(2*relError+1,3),sphave(3)
        integer                 :: i

        ! create fobonacci lattice
        qfib=fibonacciLatticePointsOnSphere(relError,1.0_dp)
        points=rphitheta2xyz(qfib)    ! to cartesian
        results=0
        do i=1,size(points,1)
            results(i,:)=ffq(points(i,:),r,q,blength,formfactor,rms,ffpolydispersity)
        end do

        sphave(1)=q
        ! calc averages over sphere
        sphave(2)=sum(results(:,2), 1)/size(results,1)
        sphave(3)=sum(results(:,3), 1)/size(results,1)

    end function sphereaverage_ffq

    function ffx(qx,r,fa,rms) result(Sq)
        use typesandconstants
        use utils
        ! point on unit sphere 3 x 1, scattering amplitude, positions , rms
        real(dp), intent(in) :: qx(3), fa, r(:,:), rms
        ! scattering  formfactor Sq
        real(dp)             :: Sq, rr(size(r,1),3)

        ! local variables
        complex(dp) :: iqr(size(r,1)), Fq

        if (rms>0) then
            rr=r+random_gauss(size(r,1),3)*rms
            iqr= j1 * matmul(rr,qx)
        else
            iqr= j1 * matmul( r,qx)
        end if

        Fq= sum( fa* exp(iqr) )
        Sq=REALPART(Fq*conjg( Fq ) )

    end function ffx

    function lhkl(q,center,sigma)
        use typesandconstants
        use utils
        ! wavevectors Nx3
        real(dp), intent(in) :: q(:,:), center(3),sigma(3)
        ! peakwidthsigma
        real(dp)             :: qc(size(q,1)),lhkl(size(q,1))

        qc(:)=q(:,1)-center(1)
        lhkl=exp(-0.5_dp*qc**2/sigma(1)**2)/sigma(1)/sqrt(pi2_dp)
        qc(:)=q(:,2)-center(2)
        lhkl=lhkl*exp(-0.5_dp*qc**2/sigma(2)**2)/sigma(2)/sqrt(pi2_dp)
        qc(:)=q(:,3)-center(3)
        lhkl=lhkl*exp(-0.5_dp*qc**2/sigma(3)**2)/sigma(3)/sqrt(pi2_dp)
    end function lhkl

end module cloud
