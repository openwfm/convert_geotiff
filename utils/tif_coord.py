# compute coordinates of tif pixel
# https://stackoverflow.com/questions/50191648/gis-geotiff-gdal-python-how-to-get-coordinates-from-pixel

import gdal,osr,pyproj,sys
import numpy as np

def crs_ref():
        # create lat/long crs with WGS84 datum
        # same as PROJ.4 : +proj=longlat +datum=WGS84 +no_defs
        # test with gdalsrsinfo epsg:4326
        crs = osr.SpatialReference()
        #crs.ImportFromEPSG(4326) # 4326 is the EPSG id of lat/long crs 
        crs.SetWellKnownGeogCS('WGS84')
        return crs

def crs_ds(ds):
        # get CRS from dataset 
        crs = osr.SpatialReference()
        crs.ImportFromWkt(ds.GetProjectionRef()) # same as GetProjection() ??
        return crs

def proj_ds(name):
        ds=gdal.Open(name)
        # get PROJ string of dataset
        crs = crs_ds(ds)
        return crs.ExportToProj4()

def xydist(name,x1,y1,x2,y2):
        ds=gdal.Open(name)
        xoffset, px_w, rot1, yoffset, rot2, px_h = ds.GetGeoTransform()
    
        # supposing x and y are your pixel coordinate this 
        # is how to get the coordinate in space.
        posX1 = px_w * x1 + rot1 * y1 + xoffset
        posY1 = rot2 * x1 + px_h * y1 + yoffset
        posX2 = px_w * x2 + rot1 * y2 + xoffset
        posY2 = rot2 * x2 + px_h * y2 + yoffset
    
        return np.sqrt((posX1-posX2)**2+(posY1-posY2)**2)

def xy2lonlat(name,x,y):
        ds=gdal.Open(name)
        xoffset, px_w, rot1, yoffset, rot2, px_h = ds.GetGeoTransform()
    
        # supposing x and y are your pixel coordinate this 
        # is how to get the coordinate in space.
        posX = px_w * x + rot1 * y + xoffset
        posY = rot2 * x + px_h * y + yoffset
    
        # shift to the center of the pixel
        posX += px_w / 2.0
        posY += px_h / 2.0

        t = osr.CoordinateTransformation(crs_ds(ds), crs_ref())
        lat, lon, z = t.TransformPoint(posX, posY)
        return lon, lat

def lonlat2xy(name,lon,lat):
        ds=gdal.Open(name)
	xoffset, px_w, rot1, yoffset, rot2, px_h = ds.GetGeoTransform()
        
        print 'xoff, dx, rot1, yoff, dy, rot2',xoffset, px_w, rot1, yoffset, px_h, rot2

        t = osr.CoordinateTransformation(crs_ref(),crs_ds(ds))
        posX, posY, z  = t.TransformPoint(lat,lon,0)

        posX -= px_w / 2.0
        posY -= px_h / 2.0

        transform = ds.GetGeoTransform()
        gt = [transform[0],transform[1],0,transform[3],0,transform[5]]
        inverse_gt = gdal.InvGeoTransform(gt)
  
        x = inverse_gt[0] + inverse_gt[1] * posX + inverse_gt[2] * posY
        y = inverse_gt[3] + inverse_gt[4] * posX + inverse_gt[5] * posY

        return x,y

def test_inv(name,x,y):
    print "converting to WGS84 lon lat and back"
    lon, lat = xy2lonlat(name,x,y)
    print 'pixel',x,y,'lon lat',lon,lat
    xx,yy = lonlat2xy(name,lon,lat)
    # print 'pixel',xx,yy,'lon lat',lon,lat
    print "error",xx-x,yy-y
    
if __name__ == '__main__':
    if len(sys.argv) in (2,4,6,8):
        name = sys.argv[1] 
        print proj_ds(name)
    else:
        print "convert pixel indices to lon lat:   file.tif x y"
        print "+ compute grid and geod distance:   file.tif x1 y1 x2 y2"
        print "+ compute Lambert conical distance: file.tif x1 y1 x2 y2 lon_0 lat_0"
        sys.exit(1)
    if len(sys.argv) in (4,6,8):
        x1=float(sys.argv[2])
        y1=float(sys.argv[3])
        test_inv(name,x1,y1)
    if len(sys.argv) in (6,8):
        x2=float(sys.argv[4])
        y2=float(sys.argv[5])
        test_inv(name,x2,y2)
        print 'grid distance',xydist(name,x1,y1,x2,y2)
        lon1, lat1 = xy2lonlat(name,x1,y1)
        lon2, lat2 = xy2lonlat(name,x2,y2)
        geod = pyproj.Geod(ellps='WGS84')
        azimuth1, azimuth2, distance = geod.inv(lon1, lat1, lon2, lat2)
        print 'geod distance', distance
        print 'azimuth', azimuth1, azimuth2
    if len(sys.argv) in (8,):
        lon_0=float(sys.argv[6])
        lat_0=float(sys.argv[7])
        print 'reference lon %s lat %s' % (lon_0,lat_0)
        print "Lambert conical distance not supported yet"
        sys.exit(1)


