# compute coordinates of tif pixel
# https://stackoverflow.com/questions/50191648/gis-geotiff-gdal-python-how-to-get-coordinates-from-pixel

import gdal,osr

def xy2latlon(name,x,y):
    try:
        ds=gdal.Open(name)
    except:
        print "gdal cannot open file %s" % name
        raise
    finally:
        xoffset, px_w, rot1, yoffset, rot2, px_h = ds.GetGeoTransform()
    
        # supposing x and y are your pixel coordinate this 
        # is how to get the coordinate in space.
        posX = px_w * x + rot1 * y + xoffset
        posY = rot2 * x + px_h * y + yoffset
    
        # shift to the center of the pixel
        posX += px_w / 2.0
        posY += px_h / 2.0
    
        # get CRS from dataset 
        crs = osr.SpatialReference()
        crs.ImportFromWkt(ds.GetProjectionRef())
        # create lat/long crs with WGS84 datum
        crsGeo = osr.SpatialReference()
        crsGeo.ImportFromEPSG(4326) # 4326 is the EPSG id of lat/long crs 
        # same as PROJ.4 : +proj=longlat +datum=WGS84 +no_defs
        # test with gdalsrsinfo epsg:4326
        t = osr.CoordinateTransformation(crs, crsGeo)
        (lat, lon, z) = t.TransformPoint(posX, posY)
        return lon, lat, z

if __name__ == '__main__':
    name='ned_data.tif'
    x=0
    y=0
    lon, lat, z = xy2latlon(name,x,y)
    print lon,lat
