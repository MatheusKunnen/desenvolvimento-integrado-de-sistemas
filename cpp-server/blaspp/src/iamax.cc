// Copyright (c) 2017-2023, University of Tennessee. All rights reserved.
// SPDX-License-Identifier: BSD-3-Clause
// This program is free software: you can redistribute it and/or modify it under
// the terms of the BSD 3-Clause license. See the accompanying LICENSE file.

#include "blas/fortran.h"
#include "blas.hh"
#include "blas_internal.hh"
#include "blas/counter.hh"

#include <limits>
#include <string.h>

namespace blas {

//==============================================================================
namespace internal {

//------------------------------------------------------------------------------
/// Low-level overload wrapper calls Fortran, float version.
/// @ingroup iamax_internal
inline blas_int iamax(
    blas_int n,
    float const* x, blas_int incx )
{
    return BLAS_isamax( &n, x, &incx );
}

//------------------------------------------------------------------------------
/// Low-level overload wrapper calls Fortran, double version.
/// @ingroup iamax_internal
inline blas_int iamax(
    blas_int n,
    double const* x, blas_int incx )
{
    return BLAS_idamax( &n, x, &incx );
}

//------------------------------------------------------------------------------
/// Low-level overload wrapper calls Fortran, complex<float> version.
/// @ingroup iamax_internal
inline blas_int iamax(
    blas_int n,
    std::complex<float> const* x, blas_int incx )
{
    return BLAS_icamax( &n,
                        (blas_complex_float*) x, &incx );
}

//------------------------------------------------------------------------------
/// Low-level overload wrapper calls Fortran, complex<double> version.
/// @ingroup iamax_internal
inline blas_int iamax(
    blas_int n,
    std::complex<double> const* x, blas_int incx )
{
    return BLAS_izamax( &n,
                        (blas_complex_double*) x, &incx );
}

}  // namespace internal

//==============================================================================
namespace impl {

//------------------------------------------------------------------------------
/// Mid-level templated wrapper checks and converts arguments,
/// then calls low-level wrapper.
/// @ingroup iamax_internal
///
template <typename scalar_t>
int64_t iamax(
    int64_t n,
    scalar_t const* x, int64_t incx )
{
    // check arguments
    blas_error_if( n < 0 );      // standard BLAS returns, doesn't fail
    blas_error_if( incx <= 0 );  // standard BLAS returns, doesn't fail

    #ifdef BLAS_HAVE_PAPI
        // PAPI instrumentation
        counter::iamax_type element;
        memset( &element, 0, sizeof( element ) );
        element = { n };
        counter::insert( element, counter::Id::iamax );
    #endif

    // convert arguments
    blas_int n_    = to_blas_int( n );
    blas_int incx_ = to_blas_int( incx );

    // call low-level wrapper
    return internal::iamax( n_, x, incx_ ) - 1;
}

}  // namespace impl

//==============================================================================
// High-level overloaded wrappers call mid-level templated wrapper.

//------------------------------------------------------------------------------
/// CPU, float version.
/// @ingroup iamax
int64_t iamax(
    int64_t n,
    float const* x, int64_t incx )
{
    return impl::iamax( n, x, incx );
}

//------------------------------------------------------------------------------
/// CPU, double version.
/// @ingroup iamax
int64_t iamax(
    int64_t n,
    double const* x, int64_t incx )
{
    return impl::iamax( n, x, incx );
}

//------------------------------------------------------------------------------
/// CPU, complex<float> version.
/// @ingroup iamax
int64_t iamax(
    int64_t n,
    std::complex<float> const* x, int64_t incx )
{
    return impl::iamax( n, x, incx );
}

//------------------------------------------------------------------------------
/// CPU, complex<double> version.
/// @ingroup iamax
int64_t iamax(
    int64_t n,
    std::complex<double> const* x, int64_t incx )
{
    return impl::iamax( n, x, incx );
}

}  // namespace blas
