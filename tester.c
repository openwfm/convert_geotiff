

#include "geogrid_index.h"
#include "geogrid_tiles.h"

#include <unistd.h>
#include <stdio.h>
#include <stdlib.h>
#include <string.h>

const int GEO_DEBUG=1;

void print_usage(FILE* f,const char* name) {
  fprintf(f,"Usage: %s [OPTIONS]\n",name);
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
  
  int c;
  int categorical_range,border_width,word_size,isigned,tile_size;
  float scale,missing,missing0;
  GeogridIndex idx;
  char units[STRING_LENGTH],description[STRING_LENGTH];
  float *buffer;
  int i,j,ix,iy;
  unsigned char v;
  
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
           word_size != 1 && word_size != 2 && word_size != 3 && word_size != 4)
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
           scale != 0.)
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
  
  if(optind != argc) {
    fprintf(stderr,"No positional arguments used.\n");
    print_usage(stderr,argv[0]);
    exit(EXIT_FAILURE);
  }
  
  idx.nx=128;
  idx.ny=256;
  idx.nz=1;
  
  /* set index options given from command line */
  strcpy(idx.description,description);
  strcpy(idx.units,units);
  idx.missing=missing;
  if(categorical_range) {
    idx.categorical=1;
    idx.cat_max=categorical_range;
    idx.cat_min=1;
    idx.missing=0.;
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

  buffer=NULL;
  convert_from_f(idx,buffer);
  
  free((void*)buffer);
  
}


