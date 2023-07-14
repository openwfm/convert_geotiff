/* 
 File:   geogrid_tiles.h
 Author: Jonathan Beezley <jon.beezley.math@gmail.com> 
 Date:   1-18-2010
 
 See geogrid_tiles.c for documentation.
 
 */

#ifndef _GEOGRID_TILES_H
#define _GEOGRID_TILES_H

#include "geogrid_index.h"

#include <stdint.h>

#ifdef __cplusplus
extern "C" {
#endif

  void write_index_file(const char *,const GeogridIndex);
  void write_tile(int64_t,int64_t,const GeogridIndex,float*);
  int64_t ntiles(int64_t,int64_t);
  int64_t nxtiles(const GeogridIndex);
  int64_t nytiles(const GeogridIndex);
  int64_t nzsize(const GeogridIndex);
  int64_t gettilestart(int64_t,int64_t,const GeogridIndex);
  int64_t globalystride(const GeogridIndex);
  int64_t globalzstride(const GeogridIndex);
  float *alloc_tile_buffer(const GeogridIndex);
  void get_tile_from_f(int64_t,int64_t,const GeogridIndex,const float*,float*);
  void convert_from_f(const GeogridIndex,const float*);
  void process_buffer_f(const GeogridIndex,float*);
  void set_tile_to(float*,const GeogridIndex,int64_t,int64_t);

#ifdef __cplusplus
}
#endif
  
#endif