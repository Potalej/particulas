MODULE particulas_mod
  IMPLICIT NONE
  PRIVATE
  PUBLIC :: atualizar_particulas
CONTAINS

  SUBROUTINE atualizar_particulas(pos, vel, mx, my, mvx, mvy, dt, R, strength)
    IMPLICIT NONE
    REAL(8), INTENT(IN) :: mx, my, mvx, mvy, R, strength, dt
    REAL(8), INTENT(INOUT) :: pos(:,:), vel(:,:)

    INTEGER :: i, n
    REAL(8) :: dx, dy, dist, w
    REAL(8), PARAMETER :: eps = 1.0d-6

    ! Tamanho do grid
    n  = SIZE(pos, 2)

    ! Integracao e forcas
    !$omp parallel do private(i,dx,dy,r2)
    DO i = 1, n
      dx = pos(1,i) - mx
      dy = pos(2,i) - my
      dist = SQRT(dx*dx + dy*dy)

      IF (dist < R) THEN
        w = (1.0d0 - dist/R)
        w = w*w

        vel(1,i) = vel(1,i) + strength * w * mvx
        vel(2,i) = vel(2,i) + strength * w * mvy
      END IF

      ! Perda de energia
      vel(1,i) = vel(1,i)*0.975
      vel(2,i) = vel(2,i)*0.975

      ! Integra as posicoes
      pos(1,i) = pos(1,i) + vel(1,i) * dt
      pos(2,i) = pos(2,i) + vel(2,i) * dt

      ! Se esta saindo pela direita
      IF (pos(1,i) > 1.0d0) THEN
        pos(1,i) = 1.0d0
        IF (vel(1,i) >= 0) vel(1,i) = - vel(1,i)
      ENDIF
      ! Se esta saindo pela esquerda
      IF (pos(1,i) < -1.0d0) THEN
        pos(1,i) = -1.0d0
        IF (vel(1,i) <= 0) vel(1,i) = - vel(1,i)
      ENDIF

      ! Se esta saindo por cima
      IF (pos(2,i) > 1.0d0) THEN
        pos(2,i) = 1.0d0
        IF (vel(2,i) >= 0) vel(2,i) = - vel(2,i)
      ENDIF
      ! Se esta saindo por baixo
      IF (pos(2,i) < -1.0d0) THEN
        pos(2,i) = -1.0d0
        IF (vel(2,i) <= 0) vel(2,i) = - vel(2,i)
      ENDIF
    END DO
    !$omp end parallel do

  END SUBROUTINE atualizar_particulas

END MODULE particulas_mod
