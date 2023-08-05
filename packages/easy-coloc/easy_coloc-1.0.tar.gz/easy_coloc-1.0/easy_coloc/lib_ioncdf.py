import netCDF4 as _nc
import numpy as _np

def read_field(file_name,variable_name,level=None,frame=None):
    fid = _nc.Dataset(file_name,'r')
    if frame is not None:
        if level is not None:
            out = fid.variables[variable_name][frame,level,:].squeeze()
        else:
            out = fid.variables[variable_name][frame,:].squeeze()
    else:
        if level is not None:
            out = fid.variables[variable_name][level,:].squeeze()
        else:
            out = fid.variables[variable_name][:].squeeze()
    fid.close()
    return out

