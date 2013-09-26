/* 
 File:   read_geotiff.h
 Author: Jonathan Beezley <jon.beezley.math@gmail.com> 
 Date:   1-18-2010
 
See read_geotiff.c for documentation.
 
 */


#ifndef _READ_GEOTIFF_H
#define _READ_GEOTIFF_H

#include "geogrid_index.h"

#include <geotiffio.h>
#include <xtiffio.h>
#include <tiffio.h>
#include <geo_normalize.h>

extern const int BIGENDIAN_TEST_VAL;
#define IS_BIGENDIAN() ( (*(char*)&BIGENDIAN_TEST_VAL) == 0 )

#ifdef __cplusplus
extern "C" {
#endif

  GeogridIndex get_index_from_geotiff(TIFF *);
  char* alloc_buffer(tsize_t);
  void free_buffer(char*);
  float* get_tiff_buffer(TIFF*);

#ifdef __cplusplus
}
#endif

#endif