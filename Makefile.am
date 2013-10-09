ACLOCAL_AMFLAGS = ${ACLOCAL_FLAGS}
AM_CFLAGS = ${EXTRA_INCLUDES}

bin_PROGRAMS = convert_geotiff

# LDADD = 

convert_geotiff_SOURCES = convert_geotiff.c geogrid_tiles.c read_geotiff.c write_geogrid.c
noinst_HEADERS = geogrid_index.h geogrid_tiles.h read_geotiff.h write_geogrid.h

dist_noinst_SCRIPTS = autogen.sh test

.PHONY: test
test: convert_geotiff
	@cd test && ./runtest.sh
