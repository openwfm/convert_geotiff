import pyproj, sys

lat_0 = sys.argv[0]

lat_0 = 38.0
lon_0 = -119.0

lambert_grid = pyproj.Proj(proj='lcc',
            lat_1=lat_0,
            lat_2=lat_0,
            lat_0=lat_0,
            lon_0=lon_0,
            a=radius, b=radius, towgs84='0,0,0', no_defs=True)

latlon_sphere = pyproj.Proj(proj='latlong',
                a=radius, b=radius, towgs84='0,0,0', no_defs=True)

lon, lat = pyproj.transform(lambert_grid, latlon_sphere, x, y)

xx,yy = pyproj.transform(latlon_sphere, lambert_grid, lon, lat)

if __name__ == '__main__':
    if len(sys.argv) == 4:
        name = sys.argv[1]
        x=float(sys.argv[2])
        y=float(sys.argv[3])
