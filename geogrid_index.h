/* 
 File:   geogrid_index.h
 Author: Jonathan Beezley <jon.beezley.math@gmail.com> 
 Date:   1-18-2010
 
 Defines structures used to create geogrid files.
 
   enum   Projection   -- for supported projections.
   struct GeogridIndex -- for meta data which is written to and index file
 
 */

#ifndef _GEOGRID_INDEX_H_
#define _GEOGRID_INDEX_H_

/* okay, so c does have a bool type... */
#ifndef __cplusplus
typedef unsigned int bool;
#endif

/* maximum length of any string, so we don't have to do dynamic allocation */
#define STRING_LENGTH 256

extern const int GEO_DEBUG;

/* known projections */
typedef enum {
  lambert,           /* Lambert Conformal (geogrid code = PROJ_LC) */
  polar,             /* Polar Stereographic (geogrid code = PROJ_PS) */
  mercator,          /* Mercator (geogrid code = PROJ_MERC) */
  regular_ll,        /* Cylindrical (geographic) Lat/Lon (geogrid code = PROJ_LATLON) */
  /*polar_wgs84m,*/  /* Technically supported by geogrid, but I can't find the geogrid key. */
  albers_nad83       /* Albers Equal Area Conic (geogrid code PROJ_ALBERS_NAD83) */
} Projection;

/* geogrid index struct */
typedef struct {
  int tile_bdr;  /* border to put around each data tile */
  int nx;        /* global image size in longitude (x) */
  int ny;        /* global image size in latitude (y) */
  int nz;        /* global image size vertically (z) */
  int tx;        /* tile size in longitude (x) */
  int ty;        /* tile size in latitude (y) */
  int tz_s;      /* tile starting index in z (unused for 2d images) */
  int tz_e;      /* tile ending index in z (unused for 2d images) */
  bool isigned;  /* data is signed, true: yes, false: no */
  bool endian;   /* output endianness is, true: little, false: big */
  float scalefactor; /* amount to scale output before truncating to int */
  int wordsize;  /* number of bytes/value in output */
  Projection proj;   /* output projection */
  bool categorical;  /* is the data categorical, true: yes, false: no */
  char units[STRING_LENGTH]; /* units of the data */
  char description[STRING_LENGTH]; /* description of the data */
  int cat_min;   /* minimum category (unused for continuous data) */
  int cat_max;   /* maximum category (unused for continuous data) */
  float missing; /* value to enter for missing data (zero for categorical) */
  bool bottom_top; /* image is oriented bottom to top (true) or top to bottom (false) */
  
  /* The remaining elements are projection specific.  See geogrid documentation for details.*/
  
  float dx;         /* pixel resolution in x */
  float dy;         /* pixel resolution in y */
  int known_x;      /* index location of known_lon */
  int known_y;      /* index location of known_lat */
  float known_lat;  /* known latitude */
  float known_lon;  /* known longitude */
  float stdlon;     /* standard (central) longitude */
  float truelat1;   /* first latitude in projection spec */
  float truelat2;   /* second latitude in projection spec */
} GeogridIndex;

#endif