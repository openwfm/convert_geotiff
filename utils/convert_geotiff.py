# compute coordinates of tif pixel

import gdal,osr,pyproj,sys
import numpy as np
from math import floor,ceil

# pyproj.transform(ref_proj,p,lon,lat) is the same as p(lon,lat)
ref_proj = pyproj.Proj(proj='lonlat',ellps='WGS84',no_defs=True)

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

def wrf2pix(ds,wrf_proj,tif_proj,wrf_posX,wrf_posY):
    print 'WRF position',wrf_posX,wrf_posY
    lon, lat = pyproj.transform(wrf_proj,ref_proj,wrf_posX,wrf_posY)
    print 'lon lat',lon,lat
    tif_posX, tif_posY = pyproj.transform(wrf_proj,tif_proj,wrf_posX,wrf_posY)
    print 'tif position',tif_posX,tif_posY
    x, y = pos2pix(ds,tif_posX,tif_posY) 
    print 'pixel coord ',x,y
    print 'wrf_pos',wrf_posX,wrf_posY,'at pixel',x, y 
    tx, ty = pix2pos(ds,x,y) 
    print 'err',tif_posX-tx,tif_posY-ty
    
    return x, y

def get_bbox(ds,sizex, sizey, lon_0, lat_0, lat_1, lat_2):
    print 'geotiff file ', ' '.join(ds.GetFileList())
    print 'cutout size',sizex,sizey,'m','center lon lat',lon_0, lat_0
    print 'truelats',lat_1, lat_2
    radius = 6370e3
    wrf_proj = pyproj.Proj(proj='lcc',
            lat_0=lat_0,
            lon_0=lon_0,
            lat_1=lat_1,
            lat_2=lat_2,
            a=radius, b=radius, towgs84='0,0,0', no_defs=True)
    print 'wrf_proj=',wrf_proj.srs
    tif_proj = get_tif_proj(ds)
    print 'tif_proj=',tif_proj.srs
    print 'ref_proj=',ref_proj.srs
    # given midpoint to WRF coordinates
    wrf_ctrX, wrf_ctrY = pyproj.transform(ref_proj,wrf_proj,lon_0,lat_0)
    # center, for information only
    x_ct, y_ct = wrf2pix(ds,wrf_proj,tif_proj,wrf_ctrX,        wrf_ctrY        )
    # corners 
    x_ll, y_ll = wrf2pix(ds,wrf_proj,tif_proj,wrf_ctrX-sizex/2,wrf_ctrY-sizey/2)
    x_ul, y_ul = wrf2pix(ds,wrf_proj,tif_proj,wrf_ctrX-sizex/2,wrf_ctrY+sizey/2)
    x_lr, y_lr = wrf2pix(ds,wrf_proj,tif_proj,wrf_ctrX+sizex/2,wrf_ctrY-sizey/2)
    x_ur, y_ur = wrf2pix(ds,wrf_proj,tif_proj,wrf_ctrX+sizex/2,wrf_ctrY+sizey/2)
    x_min = min([x_ll,x_ul,x_lr,x_ur])
    x_max = max([x_ll,x_ul,x_lr,x_ur])
    y_min = min([y_ll,y_ul,y_lr,y_ur])
    y_max = max([y_ll,y_ul,y_lr,y_ur])
    print 'bounding box',x_min,y_min,x_max,y_max
    return x_min,x_max,y_min,y_max

def extract(ds,outputName,bbox):
    x_min,x_max,y_min,y_max = bbox
    x_min = floor(x_min)
    y_min = floor(y_min)
    x_max = ceil(x_max)
    y_max = ceil(y_max)
    srcWin = [x_min, y_max, x_max-x_min+1, y_max-y_min+1]
    print 'extracting from', ' '.join(ds.GetFileList()), 'to', outputName
    print 'left_x, top_y, width, height =',srcWin
    ds=gdal.Translate(outputName, ds, srcWin = srcWin)
    return ds
 
if __name__ == '__main__':
    if len(sys.argv) in (6,8):
        name = sys.argv[1] 
        sizex= float(sys.argv[2])
        sizey= float(sys.argv[3])
        lon_0= float(sys.argv[4])
        lat_0= float(sys.argv[5])
    else:
        print 'usage: python convert_geotif.py file_tif sizex sizey lon_0 lat_0 [lat_1 lat_2]'
        sys.exit(1)
    if len(sys.argv) in (8,):
        lat_1= float(sys.argv[6])
        lat_2= float(sys.argv[7])
    else:
        lat_1, lat_2 = lat_0, lat_0
    ds = gdal.Open(name)
    bbox=get_bbox(ds,sizex, sizey, lon_0, lat_0, lat_1, lat_2)
    extract(ds,'test.tif',bbox)

