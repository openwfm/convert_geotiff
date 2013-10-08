AC_INIT([convert_geotiff], [0.0.0], [jon.beezley@gmail.com], [convert_geotiff], [https://github.com/jbeezley/convert_geotiff])
AM_INIT_AUTOMAKE([foreign])
AC_PROG_CC


AC_MSG_CHECKING([for libtiff])
AC_CHECK_LIB(tiff, TIFFGetField, HAVE_TIFF=yes, AC_MSG_ERROR([Cannot find TIFF library.  Try setting CFLAGS and LDFLAGS if it is installed in a non-standard location.]),)

AC_MSG_CHECKING([for BigTIFF])  
AC_CHECK_LIB(tiff, TIFFScanlineSize64, HAVE_BIGTIFF=yes, AC_MSG_WARN([BigTiff is not supported by libtiff.]),)

AC_MSG_CHECKING([for geotiff])
AC_CHECK_LIB(geotiff, GTIFNew, HAVE_GEOTIFF=yes, AC_MSG_ERROR([Cannot find GEOTIFF library.  Try setting CFLAGS and LDFLAGS if it is installed in a non-standard location.]),)

AC_MSG_CHECKING([for libproj])
AC_CHECK_DECL(HAVE_LIBPROJ, HAVE_LIBPROJ=yes, AC_MSG_WARN([libproj support is not compiled into geotiff.  convert_geotiff will not be able to work with projected files.]), [[#include <geo_config.h>]])

LIBS="-lgeotiff -ltiff"
AM_MAINTAINER_MODE([enable])
AC_CONFIG_FILES([Makefile])
AC_OUTPUT
