import salem
import xarray as xr
nds = xr.open_dataset('/home/mowglie/Documents/for_fabi_Columbia_data/11J249_S1.nc')
nds = nds.transpose()
nds.attrs['pyproj_srs'] = 'epsg:26906'
nds['X'] = nds.X.isel(r=0)
nds['Y'] = nds.Y.isel(c=0)
print(nds.info())
nds.salem
t = 1