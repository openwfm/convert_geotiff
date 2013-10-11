[![Build Status](https://travis-ci.org/jbeezley/convert_geotiff.png?branch=master)](https://travis-ci.org/jbeezley/convert_geotiff) convert_geotiff
===============

This is a small commandline utility for converting data from GeoTIFF to 
[geogrid format](http://www.mmm.ucar.edu/wrf/users/docs/user_guide_V3/users_guide_chap3.htm#_Writing_Static_Data)
used by [WRF](http://www.mmm.ucar.edu/wrf/users/).  

Getting the prerequisites
-------------------------

This program requires [GeoTIFF](http://trac.osgeo.org/geotiff/) and [LibTIFF](http://www.libtiff.org)
development libraries.  These should be available in most if not all package managers.  To install in Ubuntu,
you just need to install the package <tt>libgeotiff-dev</tt> like this
<pre>sudo apt-get install libgeotiff-dev</pre>
Using [Homebrew](http://brew.sh/) on Mac OSX, 
<pre>brew install libgeotiff</pre>

It is also possible to install the dependencies from source, but you may need to help the configure script below to 
find the libraries by setting configuration variables <tt>CFLAGS="-I$PREFIX/include"</tt> and 
<tt>LDFLAGS="-L$PREFIX/lib"</tt>.

Compiling the source
--------------------

Download the latest release tarball from [here](https://github.com/jbeezley/convert_geotiff/releases)
and extract it.  In the extracted directory, run <tt>./configure && make</tt>.  If everything built correctly,
you should now have <tt>convert_geotiff</tt> in the current directly.  You can either move this file into
your <tt>PATH</tt> or type <tt>sudo make install</tt> to install it.

Using convert_geotiff
---------------------

Running <tt>convert_geotiff</tt> with no arguments will produce a usage description as follows.
<pre>Usage: convert_geotiff [OPTIONS] FileName

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
</pre>
All of the files will be created in the current directory, so it is best to run the program from an empty directory.  
A more detailed description of the 
arguments to this program follows.
* <tt>-b</tt>
:<p>The data tiles in the geogrid binary format are allowed to overlap by a fixed number of grid points.  The extra border around the tile is called the halo, and this argument sets the width of the halo.  For instance with a halo of size three, the file named <tt>00101-00200.00051-00100</tt> would actually contain columns 98-203 and rows 48-103 of the full dataset.  This halo is necessary for the interpolation scheme inside of WPS.  The default should be acceptable for most situations.</p>
* <tt>-w</tt>
:<p>The number of bytes to represent each data point as an integer.  These integers are scaled by the scaling parameter before being truncated to an integer. scaledA lower value will make the output data smaller, at the cost of accuracy or the dynamic range of the input.</p>
* <tt> -m</tt>
:<p>Any grid point that is missing data, such as the outer border of the edge tiles, or grid points that the GeoTIFF file indicates as missing will be set to this value.  This argument is currently ignored when the categorical flag is set, instead missing data will be set to the maximum category + 1.</p>
*<tt>-s</tt>
:<p>Because the data is always stored as an integer, a scaling parameter is needed to represent fractional numbers or large values.  The data set will be divided by this number prior to being truncated to an integer.  If the data set has an accuracy of 2 decimal places, a reasonable scale to use would be 0.01.</p>
*<tt>-u, -d</tt>
:<p>The units and a small description of the data set should be included as arguments.  Multi-word arguments should be quoted as follows. <code><pre>-u meters -d "elevation above sea level"</pre></code></p>
* <tt>FileName</tt> 
:<p>The final argument must always be present.  This is the (absolute or relative) path to the GeoTIFF file to be converted.</p>

If you get an error that says something like 
"<tt>error while loading shared libraries: libgeotiff.so</tt>...", 
this means that GeoTIFF was compiled in as a shared library.  You just need to tell the system where to find this library.  This can be done by adding the path to the GeoTIFF library to the environment variable <tt>LD_LIBRARY_PATH</tt>.  For example, 
<pre>export LD_LIBRARY_PATH=${LD_LIBRARY_PATH}:${PREFIX}/lib</pre>
where <tt>$PREFIX</tt> is the location where you installed GeoTIFF.

Limitations
-----------

The current code has some limitations which are listed here.
* Datasets must not contain more than 99,999 grid points in each axis.  This is a limitation of the geogrid format itself, due to the naming convention of the tiles.  However, it is possible (but inefficient) to split a single dataset into multiple directories for this purpose.  A better solution would be to resample the data to a lower spatial resolution prior to converting.
* This program cannot convert between geographic projections, so the input data must be in a projection supported by WPS.  All of the projections [supported by WPS](http://www.mmm.ucar.edu/wrf/users/docs/user_guide_V3.5/users_guide_chap3.htm#_Description_of_index) should work for this conversion program; however, only UTM, Albers equal area, and lat-lon have been tested.  In addition, data sources may not conform to [EPSG standards](http://www.spatialreference.org/) in their projection tags; the output should always be checked before use.


[![Bitdeli Badge](https://d2weczhvl823v0.cloudfront.net/jbeezley/convert_geotiff/trend.png)](https://bitdeli.com/free "Bitdeli Badge")

