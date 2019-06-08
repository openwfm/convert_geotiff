# compute coordinates of tif pixel

import gdal,osr,pyproj,sys
import numpy as np

def get_tif_proj(ds):
    """
    Create projection object of geotiff file
    """
    crs = osr.SpatialReference()
    crs.ImportFromWkt(ds.GetProjectionRef())
    proj = pyproj.Proj(projparams=crs.ExportToProj4())
    return proj

def pix2pos(ds,x,y):
    """
    Compute position coordinates from geotiff pixel indices
    """
    gt = ds.GetGeoTransform()
    xoffset, px_w, rot1, yoffset, rot2, px_h = gt
    posX, posY = gdal.ApplyGeoTransform(gt, x, y)
    posX += px_w / 2.0
    posY += px_h / 2.0
    return posX, posY

def pos2pix(ds,posX,posY):
    """
    Compute geotiff pixel indices from position coordinates 
    """
    gt = ds.GetGeoTransform()
    xoffset, px_w, rot1, yoffset, rot2, px_h = gt
    posX -= px_w / 2.0
    posY -= px_h / 2.0
    inverse_gt = gdal.InvGeoTransform(gt)
    x, y = gdal.ApplyGeoTransform(inverse_gt, posX, posY)
    return x,y

def wrf2pix(ds,wrf_proj,wrf_posX,wrf_posY):
    tif_proj = get_tif_proj(ds)
    tif_posX, tif_posY = pyproj.transform(wrf_proj,tif_proj,wrf_posX,wrf_posY)
    x, y = pos2pix(ds,tif_posX,wrf_posY) 
    

def get_bbox(name,sizex, sizey, lon_0, lat_0, lat_1, lat_2)
    gs = gdal.Open(name)
    radius = 6370e3
    wrf_proj = pyproj.Proj(proj='lcc',
            lat_1=lat_0,
            lat_2=lat_0,
            lat_0=lat_0,
            lon_0=lon_0,
            a=radius, b=radius, towgs84='0,0,0', no_defs=True)
    tif_proj = get_tif_proj(ds)
    ref_proj = pyproj.Proj(proj='lonlat',datum='WGS84',no_defs=True)
    # given midpoint to WRF coordinates
    ctrX_wrf, ctrY_wrf = pyproj.transform(ref_proj,wrf_proj,lon_0,lat_0)
    # corners 
    tif_posX_ll, tif_posY_ll = pyproj.transform(wrf_proj,tif_proj,wrf_posX-sizex/2,wrf_posY-sizey/2)
    tif_posX_ul, tif_posY_ul = pyproj.transform(wrf_proj,tif_proj,wrf_posX-sizex/2,wrf_posY+sizey/2)
    tif_posX_lr, tif_posY_lr = pyproj.transform(wrf_proj,tif_proj,wrf_posX+sizex/2,wrf_posY-sizey/2)
    tif_posX_ur, tif_posY_ur = pyproj.transform(wrf_proj,tif_proj,wrf_posX+sizex/2,wrf_posY+sizey/2)
    tif_posX_min = min([tif_posX_ll,tif_posX_ul,tif_posX_lr,tif_posX_ur])
    tif_posX_max = max([tif_posX_ll,tif_posX_ul,tif_posX_lr,tif_posX_ur])
    

if __name__ == '__main__':
    if len(sys.argv) in (4,6):
        name = sys.argv[1] 
        xsize= sys.argv[2]
        ysize= sys.argv[3]
        lon_0= sys.argv[4]
        lat_0= sys.argv[5]
    else 
        usage: python convert_geotif.py xsize ysize lon_0 lat_0 lat_1 lat_2
        sys.exit(1)
    if len(sys.argv) in (6,):
        lat_1= sys.argv[6]
        lat_2= sys.argv[7]
    else
        lat_1, lat_2 = lat_0, lat_0


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
        lccd = lccdist(name,lon_0,lat_0,x1,y1,x2,y2)
        print 'LCC distance ',lccd

