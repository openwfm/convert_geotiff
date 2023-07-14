
#ifndef _WRITE_GEOGRID_H
#define _WRITE_GEOGRID_H

#include <stdint.h>

#ifdef __cplusplus
extern "C" {
#endif
int write_geogrid(
                 const float * rarray,          /* The array to be written */
                 const int64_t * nx,            /* x-dimension of the array */
                 const int64_t * ix,            /* starting x-index of the tile */
                 const int64_t * ny,            /* y-dimension of the array */
                 const int64_t * iy,            /* starting y-index of the tile */
                 const int64_t * nz,            /* z-dimension of the array */
                 const int * bdr,               /* tile border width */
                 const int * isigned,           /* 0=unsigned data, 1=signed data */
                 const int * endian,            /* 0=big endian, 1=little endian */
                 const float * scalefactor,     /* value to divide array elements by before truncation to integers */
                 const int * wordsize );        /* number of bytes to use for each array element */
#ifdef __cplusplus
}
#endif

#endif
