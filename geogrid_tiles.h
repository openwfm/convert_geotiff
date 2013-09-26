/* 
 File:   geogrid_tiles.h
 Author: Jonathan Beezley <jon.beezley.math@gmail.com> 
 Date:   1-18-2010
 
 See geogrid_tiles.c for documentation.
 
 */

#ifndef _GEOGRID_TILES_H
#define _GEOGRID_TILES_H

#include "geogrid_index.h"

#ifdef __cplusplus
extern "C" {
#endif

  void write_index_file(const char *,const GeogridIndex);
  void write_tile(int,int,const GeogridIndex,float*);
  int ntiles(int,int);
  int nxtiles(const GeogridIndex);
  int nytiles(const GeogridIndex);
  int nzsize(const GeogridIndex);
  int gettilestart(int,int,const GeogridIndex);
  int globalystride(const GeogridIndex);
  int globalzstride(const GeogridIndex);
  float *alloc_tile_buffer(const GeogridIndex);
  void get_tile_from_f(int,int,const GeogridIndex,const float*,float*);
  void convert_from_f(const GeogridIndex,const float*);
  void process_buffer_f(const GeogridIndex,float*);
  void set_tile_to(float*,const GeogridIndex,int,int);

#ifdef __cplusplus
}
#endif
  
#endif