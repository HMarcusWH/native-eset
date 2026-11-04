"""Knot-free rational brackets selected for certification (selection itself is NOT proof)."""
from fractions import Fraction as F
from affine_kernel import kernel,kernel_integral
from real_integral_bessel import X

PAIRLIST={
 0:[('1.924','2.004'),('2.19','2.27'),('2.612','2.672')],
 1:[('1.919','2.009'),('2.185','2.275')],
 2:[('5.57','5.63'),('5.9815','6.0215'),('6.252','6.292')],
 3:[('1.21','1.34'),('1.468','1.628'),('1.925','2.005')],
 4:[('4.619','4.699'),('4.888','4.968')],
 5:[('3.284','3.344'),('3.552','3.612'),('3.957','4.017')]
}

def D_at(nodes,panels,A,E):
    """Outward enclosure of D(A)=Q_Mprime(A)-P_Mprime(A) at exact rational A."""
    Q=X(0);L=X(0)
    for r,w,mp in nodes:Q+=X(w)*mp*kernel(A,r)
    for t in panels:L+=t['slope']*kernel_integral(A,t['a'],t['b'])
    return X(Q.lower()-L.upper()-E,Q.upper()-L.lower()+E)
