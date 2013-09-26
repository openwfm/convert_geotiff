/* 
 File:   read_geotiff.c
 Author: Jonathan Beezley <jon.beezley.math@gmail.com> 
 Date:   1-18-2010
 
 Functions for reading geotiff files, plus various utilities.
 
 GeogridIndex get_index_from_geotiff(TIFF*) : 
   Populate GeogridIndex structure with information that can be
   obtained from the geotiff tags.
 
 float* get_tiff_buffer(TIFF*) : 
   Read the data from the tiff image file cast as an array of floats.
 
 */

#include "read_geotiff.h"

#include <geo_tiffp.h>

#include <string.h>
#include <stdlib.h>
#include <stdio.h>
#include <math.h>

/* common buffer conversion code for different data formats */
#define CONV_CHAR_BUFFER_TO(_DTYPE,_DVAR)                       \
bufferasfloat=(float*) alloc_buffer(inx*iny*inz*sizeof(float)); \
for(i=0;i<inx*iny*inz;i++) {                                    \
  j=i*bytes_per_sample;                                         \
  _DVAR=*(_DTYPE*)(buffer+j);               \
  bufferasfloat[i]=(float) _DVAR;                               \
}                                                               \
free_buffer(buffer);

const int BIGENDIAN_TEST_VAL=1;

GeogridIndex get_index_from_geotiff(
  TIFF *file  /* handle to an open tiff file */
                                     ) {
  GTIF *gtifh;
  GTIFDefn gtifp;
  int projid,modeltype,count;
  GeogridIndex idx;
  double stdpar1,stdpar2,stdlon,olat,olon,dx,dy;
  double *pixelscale;
  uint32 inx,iny,inz;
  uint16 orientation,format;

  /* Try and initialize any fields possible. */
  /* Invalid fields are filled with 0. */
  gtifh = GTIFNew(file);
  GTIFGetDefn(gtifh,&gtifp);
  GTIFKeyGet(gtifh,ProjStdParallel1GeoKey,&stdpar1,0,1);
  idx.truelat1=stdpar1;
  GTIFKeyGet(gtifh,ProjStdParallel2GeoKey,&stdpar2,0,1);
  idx.truelat2=stdpar2;
  GTIFKeyGet(gtifh,ProjCenterLongGeoKey,&stdlon,0,1);
  idx.stdlon=stdlon;
  TIFFGetField(file,GTIFF_PIXELSCALE,&count,&pixelscale);
  idx.dx=pixelscale[0];
  idx.dy=pixelscale[1];
  
  /* Fill projection specific parameters. */
  /* WARNING: This is far from robust and will likely break 
              for certain geotiff files. */
  GTIFKeyGet(gtifh,GTModelTypeGeoKey,&modeltype,0,1);
  projid=gtifp.CTProjection;
  switch (projid) {
    case CT_AlbersEqualArea:
      idx.proj=albers_nad83;
      GTIFKeyGet(gtifh,ProjNatOriginLatGeoKey,&olat,0,1);
      idx.known_lat=olat;
      GTIFKeyGet(gtifh,ProjNatOriginLongGeoKey,&olon,0,1);
      idx.known_lon=olon;
      break;
    case CT_TransverseMercator:
      idx.proj=mercator;
      GTIFKeyGet(gtifh,ProjNatOriginLatGeoKey,&olat,0,1);
      idx.known_lat=olat;
      GTIFKeyGet(gtifh,ProjNatOriginLongGeoKey,&olon,0,1);
      idx.known_lon=olon;
      break;
    case CT_PolarStereographic:
      idx.proj=polar;
      GTIFKeyGet(gtifh,ProjNatOriginLatGeoKey,&olat,0,1);
      idx.known_lat=olat;
      GTIFKeyGet(gtifh,ProjNatOriginLongGeoKey,&olon,0,1);
      idx.known_lon=olon;
      break;
    case CT_LambertConfConic:
      idx.proj=lambert;
      GTIFKeyGet(gtifh,ProjFalseOriginLatGeoKey,&olat,0,1);
      idx.known_lat=olat;
      GTIFKeyGet(gtifh,ProjFalseOriginLongGeoKey,&olon,0,1);
      idx.known_lon=olon;
      break;
    default :
      if( modeltype == ModelTypeGeographic) {
        idx.proj=regular_ll;
        /*
        GTIFKeyGet(gtifh,ProjCenterLatGeoKey,&olat,0,1);
        idx.known_lat=olat;
        GTIFKeyGet(gtifh,ProjCenterLongGeoKey,&olon,0,1);
        idx.known_lon=olon; */
        //GTIFKeyGet(gtifh,TIFFTAG_GEOPIXELSCALE,&dx,0,1);
        //GTIFKeyGet(gtifh,TIFFTAG_GEOPIXELSCALE,&dy,1,1);
      }
      else {
        fprintf(stderr,"Unknown projection ID: %i\n",projid);
        exit(EXIT_FAILURE);
      }
  }
  
  /* get coordinates of lower left corner */
  
  olon=0;
  olat=0;
  idx.known_x=1;
  idx.known_y=1;
  if (modeltype == ModelTypeGeographic) {
    if ( ! GTIFImageToPCS(gtifh,&olon,&olat) ) {
      fprintf(stderr,"WARNING: cannot get coordinates of lower left corner.\n");
      fprintf(stderr,"You will have to edit the index file manually.\n");
    }
    idx.known_lat=olat;
    idx.known_lon=olon;
    
    olat=1;
    olon=1;
    GTIFImageToPCS(gtifh,&olon,&olat);
    if(idx.dx <= 0. && idx.dy <= 0) {
      // As a last resort, get dx/dy from projection conversion.
      idx.dx=(float)fabs(olon-(double)idx.known_lon);
      idx.dy=(float)fabs(olat-(double)idx.known_lat);
    }
  }
  else {
    if ( ! GTIFImageToPCS(gtifh,&olon,&olat) ) {
      fprintf(stderr,"WARNING: cannot get coordinates of lower left corner.\n");
      fprintf(stderr,"You will have to edit the index file manually.\n");
    }
    if (! GTIFProj4ToLatLong(&gtifp,1,&olon,&olat) ) {
      fprintf(stderr,"WARNING: cannot convert from PCS to lat/lon.\n");
    }
    idx.known_lat=olat;
    idx.known_lon=olon;
    
    olat=1;
    olon=1;
    GTIFImageToPCS(gtifh,&olon,&olat);
    GTIFProj4ToLatLong(&gtifp,1,&olon,&olat);
    if(idx.dx <= 0. && idx.dy <= 0) {
      // As a last resort, get dx/dy from projection conversion.
      idx.dx=(float)fabs(olon-(double)idx.known_lon);
      idx.dy=(float)fabs(olat-(double)idx.known_lat);
    }
  }
  
  /* fill parameters from TIFF i/o */
  
  if( ! TIFFGetField(file,TIFFTAG_IMAGEWIDTH,&inx) ||
      ! TIFFGetField(file,TIFFTAG_IMAGELENGTH,&iny)) {
    fprintf(stderr,"Could not find image dimensions in open file.\n");
    exit(EXIT_FAILURE);
  }
  idx.nx=inx;
  idx.ny=iny;
  
  if( TIFFGetField(file,TIFFTAG_IMAGEDEPTH,&inz) ) idx.nz=inz;
  else idx.nz=1;
  idx.tz_s=0;
  idx.tz_e=idx.tz_s+idx.nz-1;
  
  /* get orientation of the data, defaults to TOPLEFT */
  if ( ! TIFFGetField(file,TIFFTAG_ORIENTATION,&orientation) ) {
    orientation=ORIENTATION_TOPLEFT;
  }
  
  switch (orientation) {
    case ORIENTATION_TOPLEFT:
      idx.bottom_top=0;
      /* if TOPLEFT orientation pixel (0,0) is actually the top
         left pixel, adjusting known_y here */
      idx.known_y=idx.ny;
      break;
    case ORIENTATION_BOTLEFT:
      idx.bottom_top=1;
      break;
    default:
      fprintf(stderr,"Unsupported image orientation.\n");
      exit(EXIT_FAILURE);
  }
  
  /* get the data type of the pixels, only supporting b/w images */
  if( ! TIFFGetField(file,TIFFTAG_SAMPLEFORMAT,&format) ) 
    format=SAMPLEFORMAT_UINT;
  
  switch (format) {
    case SAMPLEFORMAT_UINT:
      idx.isigned=0;
      break;
    case SAMPLEFORMAT_INT:
      idx.isigned=1;
      break;
    case SAMPLEFORMAT_IEEEFP:
      idx.isigned=1;
      break;
    default:
      fprintf(stderr,"Unsupport pixel format.\n");
      exit(EXIT_FAILURE);
  }
  
  /* libtiff will always return the buffer in native machine endian */
  if ( IS_BIGENDIAN() ) idx.endian=0;
  else idx.endian=1;
  
  /* free the geotiff handle, and return */
  GTIFFree(gtifh);
  return (idx);
}

char* alloc_buffer(tsize_t n) {
  /* Use the libtiff macro for allocating an `n' byte array.
     Typically, this is just a call to malloc. */
  tdata_t buf;
  buf=_TIFFmalloc(n);
  //memset((void*)buf,0xEE,n);
  return ( (char*) buf );
}

void free_buffer( char *buf ) {
  /* Use the libtiff macro for deallocating an array. 
     Typically, this is just a call to free. */
  _TIFFfree( (tdata_t) buf );
}

float* get_tiff_buffer(
  TIFF *file   /* handle to an open tiff file */
                       ) {
  /* Read tiff file into a buffer cast as float. 
     Allocates the buffer, should be freed by caller after use. */
  uint32 inx,iny,inz;
  tsize_t buffersize;
  uint32 tileWidth, tileLength;
  uint16 bits_per_sample,samples_per_pixel,sample_format,/*fill_order,*/bytes_per_sample;
  long unsigned int stripMax,stripCount,i,j,k,i0,j0,j1,i1,cc,idx;
  tsize_t stripSize;
  unsigned long imageOffset,result;
  unsigned char *buffer;
  float *bufferasfloat;
  uint8 iutemp8;
  uint16 iutemp16;
  uint32 iutemp32;
  int8 itemp8;
  int16 itemp16;
  int32 itemp32;
  double dtemp;
  unsigned char *tilebuf,*tptr,*bptr;
  
  /* get the global dimensions of the image */
  if( ! TIFFGetField(file,TIFFTAG_IMAGEWIDTH,&inx) ||
      ! TIFFGetField(file,TIFFTAG_IMAGELENGTH,&iny)) {
    fprintf(stderr,"Could not find image dimensions in open file.\n");
    exit(EXIT_FAILURE);
  }
  if( ! TIFFGetField(file,TIFFTAG_IMAGEDEPTH,&inz) ) inz=1;
  
  /* get the number of bits in a pixel, determines how to cast to output */
  if( ! TIFFGetField(file,TIFFTAG_BITSPERSAMPLE,&bits_per_sample) ) {
    fprintf(stderr,"Could not find TIFFTAG_BITSPERSAMPLE.\n");
    exit(EXIT_FAILURE);
  }
  
  /* only 1,2, and 4 byte are supported for now */
  switch (bits_per_sample) {
    case 8:
      bytes_per_sample=1;
      break;
    case 16:
      bytes_per_sample=2;
      break;
    case 32:
      bytes_per_sample=4;
      break;
    default:
      fprintf(stderr,"Unsupport bits_per_sample=%i.\n",bits_per_sample);
      exit(EXIT_FAILURE);
  }
  
  /* we only support scalar valued data (no color images) */
  if( ! TIFFGetField(file,TIFFTAG_SAMPLESPERPIXEL,&samples_per_pixel) ) {
    fprintf(stderr,"Could not find TIFFTAG_SAMPLESPERPIXEL.\n");
    exit(EXIT_FAILURE);
  }
  if (samples_per_pixel != 1 ) {
    fprintf(stderr,"Currently only single channel images (black and white) are supported.\n");
    exit(EXIT_FAILURE);
  }
  if( ! TIFFGetField(file,TIFFTAG_SAMPLEFORMAT,&sample_format) ) 
    sample_format=SAMPLEFORMAT_UINT;
  
  /* This next bit was supposed to check bit ordering, but most files 
     don't seem to contain the information. TIFF should do the conversion anyway. */
  /*
  if( ! TIFFGetField(file,TIFFTAG_FILLORDER,&fill_order) 
     || fill_order != FILLORDER_MSB2LSB) {
    fprintf(stderr,"Undefined or unsupported bit order.\n");
    exit(EXIT_FAILURE);
  }
   */

     /* allocate data buffer for image pixel size */
    buffersize=((size_t) inx)*((size_t) iny)*((size_t) inz)*((size_t) samples_per_pixel)*((size_t) bytes_per_sample);
    buffer=alloc_buffer(buffersize);

 
  /* tiff images can be tiled or striped, we handle each seperately. */
  if ( TIFFIsTiled(file) ) {
    /* set up a buffer for reading each tile, this is copied to the global buffer */
    tilebuf = _TIFFmalloc(TIFFTileSize(file));
    
    /* get the tile dimensions in bytes */
    TIFFGetField(file, TIFFTAG_TILEWIDTH, &tileWidth);
    TIFFGetField(file, TIFFTAG_TILELENGTH, &tileLength);
 
     for(i=0;i<buffersize;i++) buffer[i]=2;
  
    for(k=0;k<inz;k++) {                    /* loop over vertical levels */
      for(j=0;j<iny;j += tileLength) {      /* loop over columns of tiles */
        for(i=0;i<inx;i += tileWidth) {     /* loop over rows of tiles */

          /* read the tile into memory, check for error */
          //memset((void*)tilebuf,0xFF,TIFFTileSize(file));
          if( (result=TIFFReadTile (file,tilebuf,i,j,k,0)) == -1){
            fprintf(stderr, "Read error on input tile number %d,%d\n", i,j);
            exit(EXIT_FAILURE);
          }
          
          /* copy tile into global buffer */
          cc=0;
          tptr=tilebuf;
          for(j0=0;j0<tileLength;j0++) {  /* loop over columns in the tile */
            j1=j0+j;
            i1=i;
            
            /* here we set a pointer to the first element of current column in the current tile. */
	    idx=k*inx*iny+j1*inx+i1;
	    if(idx < inx*iny*inz) {
            bptr=( buffer + (k*inx*iny+j1*inx+i1)*bytes_per_sample);
            //fprintf(stdout,"%i\n",k*inx*bytes_per_sample*iny*bytes_per_sample+j1*inx*bytes_per_sample+i1);
            for(i0=0;i0<tileWidth*bytes_per_sample;i0++) {
	      //fprintf(stdout,"%i ",*(unsigned char*)tptr);
              *bptr++=*tptr++;
              cc++;  /* keep track of number of bytes copied to compare to what was read from TIFFReadTile */
            } /* i0 */
	    }
	    //fprintf(stdout,"\n");
          } /* j0 */
          /* sanity check my programming skills */
          //if (cc > result) {  /* this might be possible for imcomplete tiles */
          //  fprintf(stderr,"WARNING: Tile size=%i < copy size=%i.  This could indicate a bug.\n",(int)result,(int)cc);
          //}
          //if (cc < result) { /* this is almost certainly a bug */
          //  fprintf(stderr,"ERROR: Tile size=%i > copy size=%i!\n",(int)result,(int)cc); 
          // }
          
        } /* i */
      } /* j */
    } /* k */
  } /* endif tiled */
  else {
    /* Read in the possibly multiple strips.  This is easier than tiles because
       we don't have to worry about strides. */
    stripSize = TIFFStripSize (file);
    stripMax = TIFFNumberOfStrips (file);
    imageOffset = 0;
    for (stripCount = 0; stripCount < stripMax; stripCount++){
      if((result = TIFFReadEncodedStrip (file, stripCount,
                                         buffer + imageOffset,
                                         stripSize)) == -1){
        fprintf(stderr, "Read error on input strip number %d\n", stripCount);
        exit(EXIT_FAILURE);
      }
      
      imageOffset += result;
    }
  }
  
  /* convert image buffer into float */
  switch (sample_format) {
    case SAMPLEFORMAT_UINT:
      switch (bytes_per_sample) {
        case 1:
          CONV_CHAR_BUFFER_TO(uint8,iutemp8)
          break;
        case 2:
          CONV_CHAR_BUFFER_TO(uint16,iutemp16)
          break;
        case 4:
          CONV_CHAR_BUFFER_TO(uint32,iutemp32)
          break;
        default:
          fprintf(stderr,"Unsupported bytes per sample=%i for uint.\n",bytes_per_sample);
          exit(EXIT_FAILURE);
      }
      break;
    case SAMPLEFORMAT_INT:
      switch (bytes_per_sample) {
        case 1:
          CONV_CHAR_BUFFER_TO(int8,itemp8)
          break;
        case 2:
          CONV_CHAR_BUFFER_TO(int16,itemp16)
          break;
        case 4:
          CONV_CHAR_BUFFER_TO(int32,itemp32)
          break;
        default:
          fprintf(stderr,"Unsupported bytes per sample=%i for int.\n",bytes_per_sample);
          exit(EXIT_FAILURE);
      }
      break;
    case SAMPLEFORMAT_IEEEFP:
      switch (bytes_per_sample) {
        case sizeof(float):
          /* no conversion needs to be done if image is single precision float */
          bufferasfloat = (float*) buffer;
          break;
        case sizeof(double):
          CONV_CHAR_BUFFER_TO(double,dtemp)
          break;
        default:
          fprintf(stderr,"Unsupported bytes per sample=%i for IEEEFP.\n",bytes_per_sample);
          exit(EXIT_FAILURE);
      }
      break;
    default:
      fprintf(stderr,"Unsupported data type in image.\n");
      exit(EXIT_FAILURE);
  }
  
  return bufferasfloat;
}
