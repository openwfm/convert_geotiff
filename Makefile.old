
CC=gcc
DEBUG=-g -O0 -fbounds-check
OPT=#-O2
CFLAGS=$(OPT) $(DEBUG)
LINKER=$(CC)
LFLAGS=$(CFLAGS)

OBJ=convert_geotiff.o geogrid_tiles.o read_geotiff.o write_geogrid.o
EXE=convert_geotiff.x

INCLUDES=-I$(LIBTIFF)/include -I$(GEOTIFF)/include
LINKS=-L$(LIBTIFF)/lib -L$(GEOTIFF)/lib -lgeotiff -ltiff

.PHONY: all clean

all: $(EXE)
test: tester.x
clean:
	-rm -f *.x *.o

%.o:%.c
	$(CC) -c $< $(CFLAGS) $(INCLUDES)

%.x:%.o
	$(LINKER) $(LFLAGS) -o $@ $^ $(LINKS)

convert_geotiff.x: $(OBJ)
convert_geotiff.o: convert_geotiff.c geogrid_tiles.h geogrid_index.h read_geotiff.h
geogrid_tiles.o: geogrid_tiles.c geogrid_tiles.h geogrid_index.h
read_geotiff.o: read_geotiff.c read_geotiff.h geogrid_index.h
write_geogrid.o: write_geogrid.c

tester.o: tester.c geogrid_tiles.h geogrid_index.h
tester.x: tester.o geogrid_tiles.o write_geogrid.o
