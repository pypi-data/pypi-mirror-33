========
monetary
========

Currency Convert

Installation
============

::

    pip install monetary


Usage
=====

::

    import monetary

    # Exchange Cent & Dollar
    monetary.cent(dollar, rate=100, cast_func=int)
    monetary.dollar(cent, rate=100, cast_func=float)

    # Mul & Div
    monetary.mul(multiplicand, multiplicator, cast_func=float)
    monetary.div(dividend, divisor, cast_func=float)

