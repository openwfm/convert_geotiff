/* 
 File:   convert_geotiff.c
 Author: Jonathan Beezley <jon.beezley.math@gmail.com> 
 Date:   1-18-2010
 
 Main program for converting geotiff files into binary geogrid format.  This 
 program is _NOT_ capable of converting between different projections. The
 projection in the geotiff file must be supported by WPS, and specifically
 have be an element of the enum type Projection in geogrid_index.h.  Geogrid
 files can differ dramatically from source to source... The functions in
 read_geotiff.c attempt to account for these differences and check for sanity
 of the output; however, one should always compare the index file created with
 the output of listgeo to ensure the conversion has been done correctly.
 
 WARNING: This program will read the entire data set into memory all at once.
          Reading and writing on a per-tile basis is an enhancement for future
          implementation.
 
 Usage: ./convert_geotiff.x [OPTIONS] FileName
 
 Converts geotiff file `FileName' into geogrid binary format
 into the current directory.
 
 Options:
 -h         : Show this help message and exit
 -c NUM     : Indicates categorical data (NUM = number of categories)
 -b NUM     : Tile border width (default 3)
 -w [1,2,4] : Word size in output in bytes (default 2)
 -z         : Indicates unsigned data (default FALSE)
 -t NUM     : Output tile size (default 100)
 -s SCALE   : Scale factor in output (default 1.)
 -m MISSING : Missing value in output (default 0., ignored for categorical data)
 -u UNITS   : Units of the data (default "NO UNITS")
 -d DESC    : Description of data set (default "NO DESCRIPTION")
 
 On successful exit, the current directory will contain a text file called index, 
 plus several binary files with names formatted as `%05i-%05i,%05i-%05i'.  See
 
 http://www.mmm.ucar.edu/wrf/users/docs/user_guide/users_guide_chap3.html
 
 for details of this file format.
 
 */


#include "geogrid_index.h"
#include "geogrid_tiles.h"
#include "read_geotiff.h"

#include "xtiffio.h"

#include <unistd.h>
#include <stdio.h>
#include <stdlib.h>
#include <string.h>

const int GEO_DEBUG=0;

void print_usage(FILE* f,const char* name) {
  fprintf(f,"Usage: %s [OPTIONS] FileName\n",name);
  fprintf(f,"\n");
  fprintf(f,"Converts geotiff file `FileName' into geogrid binary format\n");
  fprintf(f,"into the current directory.\n");
  fprintf(f,"\n");
  fprintf(f,"Options:\n");
  fprintf(f,"-h         : Show this help message and exit\n");
  fprintf(f,"-c NUM     : Indicates categorical data (NUM = number of categories)\n");
  fprintf(f,"-b NUM     : Tile border width (default 3)\n");
  fprintf(f,"-w [1,2,4] : Word size in output in bytes (default 2)\n");
  fprintf(f,"-z         : Indicates unsigned data (default FALSE)\n");
  fprintf(f,"-t NUM     : Output tile size (default 100)\n");
  fprintf(f,"-s SCALE   : Scale factor in output (default 1.)\n");
  fprintf(f,"-m MISSING : Missing value in output (default 0., ignored for categorical data)\n");
  fprintf(f,"-u UNITS   : Units of the data (default \"NO UNITS\")\n");
  fprintf(f,"-d DESC    : Description of data set (default \"NO DESCRIPTION\")\n");
}

int main (int argc, char * argv[]) {
  
  int c,i,j;
  int categorical_range,border_width,word_size,isigned,tile_size;
  float scale,missing,missing0;
  GeogridIndex idx;
  char units[STRING_LENGTH],description[STRING_LENGTH],filename[STRING_LENGTH];
  TIFF *file;
  float *buffer,swp;
  
  /* set up defaults */
  border_width=3;
  word_size=2;
  isigned=1;
  scale=1.;
  strcpy(units,"\"NO UNITS\"");
  strcpy(description,"\"NO DESCRIPTION\"");
  categorical_range=0;
  tile_size=100;
  missing0=0.;
  
  /* parse options */
  while ( (c = getopt(argc, argv, "hzs:c:b:w:t:m:u:d:") ) != -1) {
    switch (c) {
      case 'c':
        if(sscanf(optarg,"%i",&categorical_range) != 1 ||
           categorical_range <= 0)
        {
          fprintf(stderr,"Invalid argument to -c.\n");
          print_usage(stderr,argv[0]);
          exit(EXIT_FAILURE);
        }
        break;
      case 'b':
        if(sscanf(optarg,"%i",&border_width) != 1 ||
           border_width < 0)
        {
          fprintf(stderr,"Invalid argument to -b.\n");
          print_usage(stderr,argv[0]);
          exit(EXIT_FAILURE);
        }
        break;
      case 'w':
        if(sscanf(optarg,"%i",&word_size) != 1 ||
           word_size != 1 && word_size != 2 && word_size != 4)
        {
          fprintf(stderr,"Invalid argument to -w.\n");
          print_usage(stderr,argv[0]);
          exit(EXIT_FAILURE);
        }
        break;
      case 'z':
        isigned=0;
        break;
      case 't':
        if(sscanf(optarg,"%i",&tile_size) != 1 ||
           tile_size <= 0)
        {
          fprintf(stderr,"Invalid argument to -t.\n");
          print_usage(stderr,argv[0]);
          exit(EXIT_FAILURE);
        }
        break;
      case 's':
        if(sscanf(optarg,"%f",&scale) != 1 ||
           scale == 0.)
        {
          fprintf(stderr,"Invalid argument to -s.\n");
          print_usage(stderr,argv[0]);
          exit(EXIT_FAILURE);
        }
        break;
      case 'm':
        if(sscanf(optarg,"%f",&missing) != 1)
        {
          fprintf(stderr,"Invalid argument to -m.\n");
          print_usage(stderr,argv[0]);
          exit(EXIT_FAILURE);
        }
        break;
      case 'u':
        sprintf(units,"\"%s\"",optarg);
        break;
      case 'd':
        sprintf(description,"\"%s\"",optarg);
        break;
      case 'h':
        print_usage(stdout,argv[0]);
        exit(EXIT_SUCCESS);
        break;
      default:
        print_usage(stderr,argv[0]);
        exit(EXIT_FAILURE);
    }
  }
  
  if(optind == argc) {
    fprintf(stderr,"Missing FileName.\n");
    print_usage(stderr,argv[0]);
    exit(EXIT_FAILURE);
  }
  else if(optind < argc - 1) {
    fprintf(stderr,"Too many positional arguments.\n");
    print_usage(stderr,argv[0]);
    exit(EXIT_FAILURE);
  }
  
  strcpy(filename,argv[optind]);
  
  /* open geotiff file */
  file=XTIFFOpen(filename,"r");
  if (file == NULL) {
    fprintf(stderr,"Could not open file %s.\n",filename);
    exit(EXIT_FAILURE);
  }
  
  /* initialize index structure from geotiff file */
  idx=get_index_from_geotiff(file);
    
  /* set index options given from command line */
  strcpy(idx.description,description);
  strcpy(idx.units,units);
  idx.missing=missing;
  if(categorical_range) {
    idx.categorical=1;
    idx.cat_max=categorical_range+1;
    idx.cat_min=1;
    idx.missing=idx.cat_max;
  }
  else {
    idx.categorical=0;
  }

  idx.tile_bdr=border_width;
  idx.wordsize=word_size;
  idx.isigned=isigned;
  idx.tx=tile_size;
  idx.ty=tile_size;
  idx.scalefactor=scale;
  
  /* check if the data set is too large for geogrid format */
  if (idx.nx > 99999 - idx.tx || idx.ny > 99999 - idx.ty) {
    fprintf(stderr,"The data set is too large for geogrid format!\n");
    exit(EXIT_FAILURE);
  }  
  
  /* write index file to disk */
  write_index_file("index",idx);
  
  /* read geotiff file */
  buffer=get_tiff_buffer(file);
 
  if(!idx.bottom_top) {
    for(i=0;i<idx.ny/2;i++) {
      for(j=0;j<idx.nx;j++) {
	swp=buffer[i*idx.nx+j];
	buffer[i*idx.nx+j]=buffer[(idx.ny-i-1)*idx.nx+j];
	buffer[(idx.ny-i-1)*idx.nx+j]=swp;
      }
    }
    idx.bottom_top=1;
  }

  /* do any processing of data buffer needed */
  process_buffer_f(idx,buffer);
  
  /* write data tiles */
  convert_from_f(idx,buffer);
  
  /* free up memory */
  free_buffer((char*) buffer);
  
}
