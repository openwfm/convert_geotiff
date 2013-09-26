AC_INIT([convert_geotiff], [0.0.0], [jon.beezley@gmail.com], [convert_geotiff], [https://github.com/jbeezley/convert_geotiff])
AC_PREREQ()
AM_INIT_AUTOMAKE([foreign])
AC_CONFIG_HEADERS([config.h])
LT_INIT()

GEOTIFF_INCLUDE=
AC_ARG_WITH(geotiff,[  --with-geotiff=ARG    Libgeotiff library to use (ARG=path)],,)

if test "$with_geotiff" = "yes" -o "$with_geotiff" = "" ; then

    dnl We now require libgeotiff 1.2.1 (for XTIFFClientOpen).
    AC_CHECK_LIB(geotiff,XTIFFClientOpen,GEOTIFF_SETTING=external,GEOTIFF_SETTING=internal)

  if test "$GEOTIFF_SETTING" = "external" ; then

    dnl Now search for headers
    if test -r /usr/include/geotiff.h ; then
      GEOTIFF_INCLUDE=
    dnl Debian (at least some versions of it) install in /usr/include/geotiff
    elif test -r /usr/include/geotiff/geotiff.h ; then
      GEOTIFF_INCLUDE="-I/usr/include/geotiff"
    dnl Fedora and OpenSuse in /usr/include/libgeotiff (#4706)
    elif test -r /usr/include/libgeotiff/geotiff.h ; then
      GEOTIFF_INCLUDE="-I/usr/include/libgeotiff"
    else
      AC_CHECK_HEADERS([geotiff.h])
      if test "$ac_cv_header_geotiff_h" = "no" ; then
        AC_MSG_ERROR([cannot find geotiff.h])
      fi
    fi

    LIBS="-lgeotiff $LIBS"
    echo "using pre-installed libgeotiff."

  fi

else

  GEOTIFF_SETTING=external

  dnl We now require libgeotiff 1.2.1 (for XTIFFClientOpen).
  dnl first check if $with_geotiff/lib has the library:
  AC_CHECK_LIB(geotiff,XTIFFClientOpen,GEOTIFF_SETTING=external,GEOTIFF_SETTING=not_found,-L$with_geotiff/lib)

  if test $GEOTIFF_SETTING = "external" ; then
    LIBS="-L$with_geotiff/lib -lgeotiff $LIBS"
    if test  -d $with_geotiff/include ; then
      EXTRA_INCLUDES="-I$with_geotiff/include $EXTRA_INCLUDES"
    fi
  else
    dnl check if $with_geotiff itself contains the header and library (e.g. as an uninstalled build directory would)
    AC_CHECK_LIB(geotiff,XTIFFClientOpen,GEOTIFF_SETTING=external,AC_MSG_ERROR([We require at least GeoTIFF 1]))
    if test $GEOTIFF_SETTING = "external" ; then
      LIBS="-L$with_geotiff -lgeotiff $LIBS"
      EXTRA_INCLUDES="-I$with_geotiff $EXTRA_INCLUDES"
    fi
  fi

  echo "using libgeotiff from $with_geotiff."
fi

AC_SUBST(GEOTIFF_SETTING,$GEOTIFF_SETTING)
AC_SUBST(GEOTIFF_INCLUDE,$GEOTIFF_INCLUDE)


AC_ARG_WITH(libtiff,[  --with-libtiff=ARG    Libtiff library to use (ARG=path)],,)

AC_MSG_CHECKING([for libtiff])

if test "x${with_libtiff}" = "xyes" -o "x${with_libtiff}" = "x" ; then

  dnl Only automatically pick up the external libtiff if it is >= 4.0.
  AC_CHECK_LIB(tiff,TIFFScanlineSize64,TIFF_SETTING=external HAVE_BIGTIFF=yes,TIFF_SETTING=internal HAVE_BIGTIFF=yes,)

  if test "$TIFF_SETTING" = "external" ; then
    dnl Cygwin takes a somewhat restrictive view of what should be exported
    dnl from the dll, so don't use the external library if missing semi-private
    dnl functions.
    AC_CHECK_LIB(tiff,_TIFFsetDoubleArray,TIFF_SETTING=external,TIFF_SETTING=internal,)
  fi

  if test "$TIFF_SETTING" = "external" ; then
    LIBS="-ltiff $LIBS"
    AC_MSG_RESULT([using pre-installed libtiff.])
  else
    AC_MSG_RESULT([using internal TIFF code.])
  fi

else

  TIFF_SETTING=external
  if test -r "$with_libtiff/tiff.h" ; then
    LIBS="-L$with_libtiff -ltiff $LIBS"
    EXTRA_INCLUDES="-I$with_libtiff $EXTRA_INCLUDES"
  else
    LIBS="-L$with_libtiff/lib -ltiff $LIBS"
    EXTRA_INCLUDES="-I$with_libtiff/include $EXTRA_INCLUDES"
  fi

  AC_MSG_RESULT([using libtiff from ${with_libtiff}.])

  dnl Check for the BigTIFF enabled library (libtiff >= 4.0)
  AC_CHECK_LIB(tiff,TIFFScanlineSize64,HAVE_BIGTIFF=yes,HAVE_BIGTIFF=no,)

fi

if test "${HAVE_BIGTIFF}" = "yes" ; then
  TIFF_OPTS="-DBIGTIFF_SUPPORT"

dnl   LOC_MSG([BigTIFF support enabled.])
fi

AC_SUBST(TIFF_SETTING,${TIFF_SETTING})
AC_SUBST(TIFF_OPTS,${TIFF_OPTS})

AC_PROG_CC
AC_CONFIG_FILES([Makefile])
AC_OUTPUT

dnl LOC_MSG([  TIFF support......: ${TIFF_CONFIG}])
dnl LOC_MSG([    -INCLUDE .......: ${TIFF_INC}])
dnl LOC_MSG([    -PREFIX ........: ${TIFF_PREFIX}])
