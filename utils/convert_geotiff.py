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

def wrf2pix(ds,wrf_proj,tif_proj,wrf_posX,wrf_posY):
    tif_posX, tif_posY = pyproj.transform(wrf_proj,tif_proj,wrf_posX,wrf_posY)
    x, y = pos2pix(ds,tif_posX,wrf_posY) 
    print 'wrf_pos',wrf_posX,wrf_posY,'at pixel',x, y 
    return x, y

def get_bbox(name,sizex, sizey, lon_0, lat_0, lat_1, lat_2):
    print 'getiff file ',name
    print 'cutout size',sizex,sizey,'m','center lon lat',lon_0, lat_0
    print 'truelats',lat_1, lat_2
    ds = gdal.Open(name)
    radius = 6370e3
    wrf_proj = pyproj.Proj(proj='lcc',
            lat_1=lat_0,
            lat_2=lat_0,
            lat_0=lat_0,
            lon_0=lon_0,
            a=radius, b=radius, towgs84='0,0,0', no_defs=True)
    print 'wrf_proj=',wrf_proj.srs
    tif_proj = get_tif_proj(ds)
    print 'tif_proj=',tif_proj.srs
    ref_proj = pyproj.Proj(proj='lonlat',datum='WGS84',no_defs=True)
    print 'ref_proj=',ref_proj.srs
    # given midpoint to WRF coordinates
    wrf_ctrX, wrf_ctrY = pyproj.transform(ref_proj,wrf_proj,lon_0,lat_0)
    # corners 
    x_ll, y_ll = wrf2pix(ds,wrf_proj,tif_proj,wrf_ctrX-sizex/2,wrf_ctrY-sizey/2)
    x_ul, y_ul = wrf2pix(ds,wrf_proj,tif_proj,wrf_ctrX-sizex/2,wrf_ctrY+sizey/2)
    x_lr, y_lr = wrf2pix(ds,wrf_proj,tif_proj,wrf_ctrX+sizex/2,wrf_ctrY-sizey/2)
    x_ur, y_ur = wrf2pix(ds,wrf_proj,tif_proj,wrf_ctrX+sizex/2,wrf_ctrY+sizey/2)
    x_min = min([x_ll,x_ul,x_lr,x_ur])
    x_max = max([x_ll,x_ul,x_lr,x_ur])
    y_min = min([y_ll,y_ul,y_lr,y_ur])
    y_max = max([y_ll,y_ul,y_lr,y_ur])
    print 'bounding box x',x_min,x_max,'y',y_min,y_max
    return x_min,x_max,y_min,y_max
 
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
    get_bbox(name,sizex, sizey, lon_0, lat_0, lat_1, lat_2)

