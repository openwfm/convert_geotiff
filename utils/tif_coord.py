# compute coordinates of tif pixel
# https://stackoverflow.com/questions/50191648/gis-geotiff-gdal-python-how-to-get-coordinates-from-pixel

import gdal,osr,pyproj,sys
import numpy as np

ref_proj = pyproj.Proj(proj='lonlat',ellps='WGS84',datum='WGS84',no_defs=True)
ref_proj = pyproj.Proj(init="epsg:4326")

def crs_ref():
        # create lat/long crs with WGS84 
        # same as PROJ.4 : +proj=longlat +ellps=WGS84 +no_defs
        # test with gdalsrsinfo epsg:4326
        crs = osr.SpatialReference()
        crs.ImportFromEPSG(4326) # 4326 is the EPSG id of lat/long crs 
        #crs.SetWellKnownGeogCS('WGS84')
        return crs

def crs_ds(ds):
        # get CRS from dataset 
        crs = osr.SpatialReference()
        crs.ImportFromWkt(ds.GetProjectionRef()) # same as GetProjection() ??
        return crs

def proj_string(name):
        ds=gdal.Open(name)
        # get PROJ string of dataset
        crs = crs_ds(ds)
        return crs.ExportToProj4()

def deg2str(deg,islat):
      # convert decimal degrees to degress minutes seconds.xx E/W/S/N string
      deg = round(deg*3600.0,4)/3600.0
      d = int(deg)
      m = int((deg - d) * 60)
      s = (deg - d - m/60.0) * 3600.00
      z= round(s, 2)
      NSEW = [['E', 'W'], ['N', 'S']]
      return '%3.0fd%2.0fm%7.4fs%s' %   (abs(d), abs(m), abs(z),NSEW[islat][d<0])

def xy2lcc(name,lon_0,lat_0,x,y):
      radius = 6370e3
      lcc_proj = pyproj.Proj(proj='lcc',
            lat_1=lat_0,
            lat_2=lat_0,
            lat_0=lat_0,
            lon_0=lon_0,
            a=radius, b=radius, towgs84='0,0,0', no_defs=True)
      print 'lcc:',lcc_proj.srs
      tif_proj = pyproj.Proj(projparams=proj_string(name))
      print 'tif:',tif_proj.srs
      print 'ref:',ref_proj.srs 

      ds=gdal.Open(name)
      xoffset, px_w, rot1, yoffset, rot2, px_h = ds.GetGeoTransform()
      posX = px_w * x + rot1 * y + xoffset
      posY = rot2 * x + px_h * y + yoffset
      gX, gY = gdal.ApplyGeoTransform(ds.GetGeoTransform(),x,y)
      print posX, posY
      print gX, gY
      posX += px_w / 2.0
      posY += px_h / 2.0

      print 'tif:', posX, posY 
      lon, lat = pyproj.transform(tif_proj, ref_proj, posX, posY)
      print "ref lon lat:", lon, lat, deg2str(lon,0), deg2str(lat,1)
      lccX, lccY = pyproj.transform(ref_proj,lcc_proj,lon, lat)
      print "lcc x y:", lccX, lccY
      lcc2X, lcc2Y = pyproj.transform(tif_proj, lcc_proj, posX, posY) # different result?
      print "lcc2 x y:", lcc2X, lcc2Y
      lcc3X, lcc3Y = lcc_proj(lon, lat)
      print "lcc3 x y:", lcc3X, lcc3Y
      return lccX, lccY

def lccdist(name,lon_0,lat_0,x1,y1,x2,y2):
        lccX1, lccY1 = xy2lcc(name,lon_0,lat_0,x1,y1)
        lccX2, lccY2 = xy2lcc(name,lon_0,lat_0,x2,y2)
        return np.sqrt((lccX1-lccX2)**2+(lccY1-lccY2)**2)

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

def xy2lonlat_print(name,x,y):
	lon, lat = xy2lonlat(name,x,y)
        print name,'pixel',x,y,'lon lat',lon,lat,deg2str(lon,0),deg2str(lat,1)

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
    print 'pixel',x,y,'lon lat',lon,lat,deg2str(lon,0),deg2str(lat,1)
    xx,yy = lonlat2xy(name,lon,lat)
    # print 'pixel',xx,yy,'lon lat',lon,lat
    print "error",xx-x,yy-y
    
if __name__ == '__main__':
    if len(sys.argv) in (2,4,6,8):
        name = sys.argv[1] 
        print proj_string(name)
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
        print 'lon1, lat1, lon2, lat2',lon1, lat1, lon2, lat2
        print 'diff lon lat',lon2-lon1,lat2-lat1
        print 'midpoint lon lat',(lon2+lon1)*0.5,(lat2+lat1)*0.5
        try:
            azimuth1, azimuth2, distance = geod.inv(lon1, lat1, lon2, lat2)
            print 'geod distance', distance
            print 'azimuth', azimuth1, azimuth2
        except ValueError as e:
            print e
    if len(sys.argv) in (8,):
        lon_0=float(sys.argv[6])
        lat_0=float(sys.argv[7])
        print 'reference lon %s lat %s' % (lon_0,lat_0)
        lccd = lccdist(name,lon_0,lat_0,x1,y1,x2,y2)
        print 'LCC distance ',lccd

