
# Copyright (C) 2011 Mattias Slabanja <slabanja@chalmers.se>
#
# This program is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation; either version 2 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful, but
# WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the GNU
# General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program; if not, write to the Free Software
# Foundation, Inc., 51 Franklin Street, Fifth Floor, Boston, MA
# 02110-1301, USA.

"""
This module provides an implementation of Filon's integration formula.
For information about Filon's formula, see e.g.
`Abramowitz and Stegun, Handbook of Mathematical Functions,
section 25 <http://mathworld.wolfram.com/FilonsIntegrationFormula.html>`_ or
Allen and Tildesley, *Computer Simulation of Liquids*, Appendix D.

Integration is performed along one dimension (default ``axis=0``), e.g.,

.. code::

    [F0[0]  F1[0] ..  FN[0] ]     [f0[0]  f1[0] ..  fN[0] ]
    [   .      .         .  ]     [   .      .         .  ]
    [F0[.]  F1[.] ..  FN[.] ] = I([f0[.]  f1[.] ..  fN[.] ], dx, [k[0] .. k[Nk]])
    [   .      .         .  ]     [   .      .         .  ]
    [F0[Nk] F1[Nk] .. FN[Nk]]     [f0[Nx] f1[Nx] .. fN[Nx]]

where ``k`` and ``Fj`` have end index ``Nk``, and ``fj`` has end index ``Nx``.
``Nk`` is automatically set by the length of ``k``. Due to the algorithm,
``fj[Nx]`` must be of odd length (``Nx`` must be an even number), and should
correspond to a linearly spaced set of data points (separated by `dx` along the
integration axis).

:func:`sin_integral` and :func:`cos_integral` allow for shifted integration
intervals by the optional argument ``x0``.

"""

__all__ = ['fourier_cos', 'sin_integral', 'cos_integral']

from numpy import (sin, cos, pi, mod, zeros, arange,
                   linspace, require, where, sum)


def fourier_cos(f, dx, k=None, axis=0):
    """Calculates the direct Fourier cosine transform :math:`F(k)` of a
    function :math:`f(x)` using Filon's integration method.

    The array values ``f[0]..f[2n]`` are expected to correspond to
    :math:`f(0.0)\ldots f(2n\Delta x)`. Hence, ``f`` should contain an odd
    number of elements.

    The transform is approximated by the integral
    :math:`F(k) = 2\int_{0}^{x_{max}} f(x) \cos(k x) dx`,
    where :math:`x_{max} = 2n \Delta x`.

    Parameters
    ----------
    f : array
        function values; must contain an odd number of elements
    dx : float
        spacing of x-axis (:math:`\Delta x`)
    k : array
        values of reciprocal axis, at which to evaluate transform;
        if ``k`` is not provided, ``linspace(0.0, 2*pi/dx, f.shape[axis])``,
        will be used.
    axis : int
        axis along which to carry out integration

    Returns
    -------
    (array, array)
        tuple of ``k`` and ``F`` values

    Example
    -------
    A common use case is

    .. code-block:: python

        k, F = fourier_cos(f, dx)
    """

    if k is None:
        k = linspace(0.0, 2 * pi / dx, f.shape[axis])

    return k, 2 * cos_integral(f, dx, k, x0=0.0, axis=axis)


def cos_integral(f, dx, k, x0=0.0, axis=0):
    """Calculates the integral
    :math:`\int_{x_0}^{2n\Delta x} f(x) \cos(k x) dx`.

    Parameters
    ----------
    f : array
        function values; must contain an odd number of elements
    dx : float
        spacing of x-axis (:math:`\Delta x`)
    k : array
        values of reciprocal axis, at which to evaluate transform;
        if ``k`` is not provided, ``linspace(0.0, 2*pi/dx, f.shape[axis])``,
        will be used.
    x0 : float
        offset for integration interval
    axis : int
        axis along which to carry out integration

    Returns
    -------
    float
        tuple of ``k`` and ``F`` values
    """
    return _gen_sc_int(f, dx, k, x0, axis, cos)


def sin_integral(f, dx, k, x0=0.0, axis=0):
    """Calculates the integral
    :math:`\int_{x_0}^{2n\Delta x} f(x) \sin(k x) dx`.

    Parameters
    ----------
    f : array
        function values; must contain an odd number of elements
    dx : float
        spacing of x-axis (:math:`\Delta x`)
    k : array
        values of reciprocal axis, at which to evaluate transform;
        if ``k`` is not provided, ``linspace(0.0, 2*pi/dx, f.shape[axis])``,
        will be used.
    x0 : float
        offset for integration interval
    axis : int
        axis along which to carry out integration

    Returns
    -------
    float
        tuple of ``k`` and ``F`` values
    """
    return _gen_sc_int(f, dx, k, x0, axis, sin)


def _gen_sc_int(f, dx, k, x0, axis, sc):

    f = require(f)
    k = require(k)

    try:
        axis = range(f.ndim)[axis]
    except (IndexError, TypeError):
        raise Exception('axis(={}) is invalid'.format(str(axis)))

    if k.ndim != 1:
        raise ValueError('k must be one-dimensional')

    Nk = len(k)
    Nx = f.shape[axis]
    x_shape = [1] * f.ndim + [Nx]  # We'll transpose axis and put it last
    k_shape = [1] * (f.ndim + 1)  #
    k_shape[axis] = Nk  #

    if mod((Nx - 1), 2) != 0 or Nx < 3:
        raise ValueError('len f must be odd and >2 along its integration axis')

    s = (slice(None),) * f.ndim
    odd_index = s + (slice(1, None, 2),)
    even_index = s + (slice(0, None, 2),)
    first_index = s + ((0,),)
    last_index = s + ((-1,),)

    alpha, beta, gamma = [x.reshape(k_shape[:-1])
                          for x in _alpha_beta_gamma(dx * k)]
    x = (x0 + dx * arange(0.0, Nx)).reshape(x_shape)
    k = k.reshape(k_shape)

    # Add an extra dimension to f, and transpose it to put the x-dimension at
    # axis=-1
    t = list(range(f.ndim + 1))
    t[axis], t[-1] = t[-1], t[axis]
    f = f.reshape(f.shape + (1,)).transpose(t)

    sc_k_x = sc(k * x)
    sc_k_x[first_index] *= 0.5
    sc_k_x[last_index] *= 0.5

    if sc == sin:
        return dx * (alpha * sum((f[first_index] * cos(k * x0) -
                                  f[last_index] * cos(k * x[last_index])),
                                 axis=-1) +
                     beta * sum(f[even_index] * sc_k_x[even_index], axis=-1) +
                     gamma * sum(f[odd_index] * sc_k_x[odd_index], axis=-1))
    elif sc == cos:
        return dx * (alpha * sum((f[last_index] * sin(k * x[last_index]) -
                                  f[first_index] * sin(k * x0)), axis=-1) +
                     beta * sum(f[even_index] * sc_k_x[even_index], axis=-1) +
                     gamma * sum(f[odd_index] * sc_k_x[odd_index], axis=-1))

    raise RuntimeError('Internal error, this should not happen')


def _alpha_beta_gamma(theta):
    # From theta, calculate alpha, beta, and gamma

    N = len(theta)
    alpha = zeros(N)
    beta = zeros(N)
    gamma = zeros(N)

    # theta==0 needs special treatment
    I_nz, = theta.nonzero()
    I_z, = where(theta == 0.0)
    if len(I_z) > 0:
        beta[I_z] = 2.0 / 3.0
        gamma[I_z] = 4.0 / 3.0
        theta = theta[I_nz]

    sin_t = sin(theta)
    cos_t = cos(theta)
    sin2_t = sin_t * sin_t
    cos2_t = cos_t * cos_t
    theta2 = theta * theta
    itheta3 = 1.0 / (theta2 * theta)

    alpha[I_nz] = itheta3 * (theta2 + theta * sin_t * cos_t - 2 * sin2_t)
    beta[I_nz] = 2 * itheta3 * (theta * (1 + cos2_t) - 2 * sin_t * cos_t)
    gamma[I_nz] = 4 * itheta3 * (sin_t - theta * cos_t)

    return alpha, beta, gamma
