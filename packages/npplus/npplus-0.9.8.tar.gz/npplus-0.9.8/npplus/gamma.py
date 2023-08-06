from numpy import (array, asfarray, zeros_like, ones_like, absolute, log, exp,
                   where, arange)


def gammpq(a, x):
    # same as gammainc(a, x), gammaincc(a, x)
    lg = ln_gamma(a)  # before broadcast
    x = asfarray(x) + zeros_like(lg)
    scalar = not x.shape
    if scalar:
        x.reshape(1)
    p = zeros_like(x)
    a = asfarray(a) + p
    q = (x == 0.).astype(float)
    q = (1. - q) * exp(-x + a*log(x+q) - lg)
    mask = x < a + 1.
    if mask.any():
        p[mask] = _gammp(a[mask], x[mask])
    mask = ~mask
    if mask.any():
        p[mask] = _gammq(a[mask], x[mask])
    p *= q
    p, q = where(mask, 1.-p, p), where(mask, p, 1.-p)
    if scalar:
        p, q = p[0], q[0]
    return p, q


def _gammp(a, x):
    term = 1. / a
    tot, total = term.copy(), term.copy()
    mleft = arange(x.size)
    nleft = _gamm_max
    while nleft > 0:
        a += 1.
        term *= x / a
        tot += term
        mask = absolute(term) < absolute(tot) * _gamm_err
        if mask.any():
            total[mleft[mask]] = tot[mask]
        if mask.all():
            break
        mask = ~mask
        a, x, term, tot = a[mask], x[mask], term[mask], tot[mask]
        mleft = mleft[mask]
        nleft -= 1
    else:
        raise("failed to converge")
    return total


def _gammq(a, x):
    r, ren = zeros_like(x), ones_like(x)
    rold = r.copy()
    ab0 = array([ren, r])
    ab1 = array([x, ren])
    mleft = arange(x.size)
    i = 1
    while i <= _gamm_max:
        tmp = i - a
        ab0 = (ab1 + ab0*tmp) * ren
        tmp = i * ren
        ab1 = ab0*x + ab1*tmp
        a1, b1 = ab1
        mask = absolute(b1-a1*rold) < absolute(b1) * _gamm_err
        if mask.any():
            r[mleft[mask]] = b1[mask] / a1[mask]
        if mask.all():
            break
        mask = ~mask
        a, x, ab0, ab1 = a[mask], x[mask], ab0[:, mask], ab1[:, mask]
        a1, b1 = ab1
        ren = 1. / where(a1, a1, 1.)
        rold = b1 * ren
        mleft = mleft[mask]
        i += 1
    else:
        raise("failed to converge")
    return r


_gamm_err = 1.e-13
_gamm_max = 200


def ln_gamma(x):
    ser = (1.000000000000000174663 +
           5716.400188274341379136/x +
           -14815.30426768413909044/(x+1.) +
           14291.49277657478554025/(x+2.) +
           -6348.160217641458813289/(x+3.) +
           1301.608286058321874105/(x+4.) +
           -108.1767053514369634679/(x+5.) +
           2.605696505611755827729/(x+6.) +
           -0.7423452510201416151527e-2/(x+7.) +
           0.5384136432509564062961e-7/(x+8.) +
           -0.4023533141268236372067e-8/(x+9.))
    tmp = x + 8.5
    return log(2.506628274631000502416*ser) + (x-0.5)*log(tmp) - tmp
