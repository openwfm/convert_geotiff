# compute coordinates of tif pixel
# https://stackoverflow.com/questions/50191648/gis-geotiff-gdal-python-how-to-get-coordinates-from-pixel

import gdal,osr,pyproj,sys

ref_proj = pyproj.Proj(proj='lonlat',ellps='WGS84',datum='WGS84',no_defs=True)
#ref_proj = pyproj.Proj(init="epsg:4326")

def pix2pos(ds,x,y):
    # position coordinates from geotiff pixel indices
    gt = ds.GetGeoTransform()
    xoffset, px_w, rot1, yoffset, rot2, px_h = gt
    posX, posY = gdal.ApplyGeoTransform(gt, x, y)
    posX += px_w / 2.0
    posY += px_h / 2.0
    return posX, posY

def print_lonlat(ds,tif_proj,ref_proj,x,y):
    posX, posY = pix2pos(ds,x,y) 
    lon, lat =pyproj.transform(tif_proj,ref_proj,posX,posY)
    print 'pixel ',x,y,'lon lat',lon,lat,deg2str(lon,0),deg2str(lat,1)

def deg2str(deg,islat):
    # convert decimal degrees to degress minutes seconds.xx E/W/S/N string
    deg = round(deg*3600.0,4)/3600.0
    d = int(deg)
    m = int((deg - d) * 60)
    s = (deg - d - m/60.0) * 3600.00
    z= round(s, 2)
    NSEW = [['E', 'W'], ['N', 'S']]
    return '%3.0fd%2.0fm%7.4fs%s' %   (abs(d), abs(m), abs(z),NSEW[islat][d<0])

if __name__ == '__main__':
    if len(sys.argv) != 2:
       print 'Usage: python tif_corners.py file.tif'
       sys.exit(1)
    name = sys.argv[1]
    ds=gdal.Open(name)      
    wkt=ds.GetProjectionRef() 
    crs = osr.SpatialReference()
    crs.ImportFromWkt(wkt)
    proj4 = crs.ExportToProj4()
    tif_proj = pyproj.Proj(proj4)
    ref_proj = pyproj.Proj(proj='lonlat',ellps='WGS84',datum='WGS84',no_defs=True)
    print "tif_proj:",tif_proj.srs
    print "ref_proj:",ref_proj.srs
    width = ds.RasterXSize
    height = ds.RasterYSize
    print_lonlat(ds,tif_proj,ref_proj,1,1)
    print_lonlat(ds,tif_proj,ref_proj,1,height)
    print_lonlat(ds,tif_proj,ref_proj,width,1)
    print_lonlat(ds,tif_proj,ref_proj,width,height)
    print 'To compare: gdalinfo',name,'| tail'

