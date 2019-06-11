# compute coordinates of tif pixel

import gdal,os,osr,pyproj,sys
import numpy as np
from math import floor,ceil

# pyproj.transform(ref_proj,p,lon,lat) should be the same as p(lon,lat)
# ref_proj = pyproj.Proj(proj='lonlat',ellps='WGS84',datum='WGS84',no_defs=True)
ref_proj = pyproj.Proj(proj='lonlat')
# ref_proj = pyproj.Proj(init="epsg:4326")

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
    # *********************************************************************************
    # IMPORTANT NOTE: have to transform through ref_proj otherwise resulting cutout has
    # wrong coordinates according to gdalinfo. Not sure why.
    # Apparently pyproj.transform is not transitive? 
    # *********************************************************************************

    print 'WRF position',wrf_posX,wrf_posY 
    lon, lat = pyproj.transform(wrf_proj,ref_proj,wrf_posX,wrf_posY)
    print 'lon lat',lon,lat,deg2str(lon,0),deg2str(lat,1)
    tif_posX, tif_posY = pyproj.transform(ref_proj,tif_proj,lon,lat)
    print 'tif position',tif_posX,tif_posY
    x, y = pos2pix(ds,tif_posX,tif_posY) 
    print 'pixel coord',x,y
    tx, ty = pix2pos(ds,x,y) 
    if abs(tif_posX-tx)>1e-8 or abs(tif_posY-ty)>1e-8 :
        print 'err',tif_posX-tx,tif_posY-ty
    lon, lat = pyproj.transform(tif_proj, ref_proj, tif_posX, tif_posY)
    print 'lon lat',lon,lat,deg2str(lon,0),deg2str(lat,1)
    return x, y

def deg2str(deg,islat):
      # convert decimal degrees to degress minutes seconds.xx E/W/S/N string
      deg = round(deg*3600.0,4)/3600.0
      d = int(deg)
      m = int((deg - d) * 60)
      s = (deg - d - m/60.0) * 3600.00
      z= round(s, 2)
      NSEW = [['E', 'W'], ['N', 'S']]
      return '%3.0fd%2.0fm%7.4fs%s' %   (abs(d), abs(m), abs(z),NSEW[islat][d<0])


def get_bbox(ds,sizex, sizey, lon_0, lat_0, lat_1, lat_2):
    print 'geotiff file ', ' '.join(ds.GetFileList())
    print 'cutout size',sizex,sizey,'m','center lon lat',lon_0, lat_0,'in the projection used by WRF, centered at ',lon_0, lat_0
    radius = 6370e3
    wrf_proj = pyproj.Proj(proj='lcc',
            lon_0=lon_0,
            lat_0=lat_0,
            lat_1=lat_1,
            lat_2=lat_2,
            a=radius, b=radius, no_defs=True)
            # a=radius, b=radius, towgs84='0,0,0', no_defs=True)
    tif_proj = get_tif_proj(ds)
    print 'wrf_proj=',wrf_proj.srs
    print 'tif_proj=',tif_proj.srs
    print 'ref_proj=',ref_proj.srs
    # given midpoint to WRF coordinates
    wrf_ctrX, wrf_ctrY = pyproj.transform(ref_proj,wrf_proj,lon_0,lat_0)
    print 'center'
    x_ct, y_ct = wrf2pix(ds,wrf_proj,tif_proj,wrf_ctrX,        wrf_ctrY        )
    print 'll corner'
    x_ll, y_ll = wrf2pix(ds,wrf_proj,tif_proj,wrf_ctrX-sizex/2,wrf_ctrY-sizey/2)
    print 'ul corner'
    x_ul, y_ul = wrf2pix(ds,wrf_proj,tif_proj,wrf_ctrX-sizex/2,wrf_ctrY+sizey/2)
    print 'lr corner'
    x_lr, y_lr = wrf2pix(ds,wrf_proj,tif_proj,wrf_ctrX+sizex/2,wrf_ctrY-sizey/2)
    print 'ur corner'
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
    gdal.Translate(outputName, ds, srcWin = srcWin)
    return srcWin 

def write_geogrid(ds):
    gdal.Translate('data.bil',ds,format='ENVI')
    with open('idata.hdr') as fp:
	line = fp.readline()
        while line:
                recol =  re.match(r'samples\s+=\s+([0-9]+)',line)
                rerow =  re.match(r'lines\s+=\s+([0-9]+)',line)
                if recol:
                        ncols = int(recol.groups()[0])
                if rerow:
                        nrows = int(rerow.groups()[0])
                line = fp.readline()

    geogrid_out = '00001-%05d.00001-%05d' % (ncols,nrows)
    os.rename('data.bil',geogrid_out)
    os.remove('data.*')
    print 'geogrid file %s written properly' % geogrid_out


if __name__ == '__main__':
    if len(sys.argv) in (7,9):
        input_name = sys.argv[1] 
        output_name = sys.argv[2]
        sizex= float(sys.argv[3])
        sizey= float(sys.argv[4])
        lon_0= float(sys.argv[5])
        lat_0= float(sys.argv[6])
    else:
        print 'usage: python subset_geotif.py input.tif output.tif sizex_m sizey_m lon_0 lat_0 [lat_1 lat_2]'
        sys.exit(1)
    if len(sys.argv) in (9,):
        lat_1= float(sys.argv[7])
        lat_2= float(sys.argv[8])
    else:
        lat_1, lat_2 = lat_0, lat_0
    ds = gdal.Open(input_name)
    bbox=get_bbox(ds,sizex, sizey, lon_0, lat_0, lat_1, lat_2)
    srcWin = extract(ds,output_name,bbox)
    print 'Done. To verify:'
    print 'gdalinfo',output_name,'| tail'

    x_min, y_max, x_size, y_size = srcWin 
    check_srcwin=0
    check_srcwin=1
    if check_srcwin>0:
        import tif_coord
        tif_coord.xy2lonlat_print(output_name,1,y_size)
        tif_coord.xy2lonlat_print(output_name,1,y_size)
        tif_coord.xy2lonlat_print(output_name,x_size,1)
        tif_coord.xy2lonlat_print(output_name,x_size,y_size)
    if check_srcwin>1:
        print 'checking  approx compatible with gdalinfo'
        print 'checking sides'
        #tif_coord.lccdist(output_name,lon_0,lat_0,x_size,y_size, x_size,y_size)
        print 'left'
        lccd=tif_coord.lccdist(output_name,lon_0,lat_0,1.0   ,1.0   , 1.0   ,y_size)
        print 'LCC distance',lccd
        print 'bottom'
        lccd=tif_coord.lccdist(output_name,lon_0,lat_0,1.0   ,1.0   , x_size,1.0   )
        print 'LCC distance',lccd
        print 'top'
        lccd=tif_coord.lccdist(output_name,lon_0,lat_0,1.0   ,y_size, x_size,y_size)
        print 'LCC distance',lccd
        print 'right'
        lccd=tif_coord.lccdist(output_name,lon_0,lat_0,x_size,1.0   , x_size,y_size)
        print 'LCC distance',lccd

