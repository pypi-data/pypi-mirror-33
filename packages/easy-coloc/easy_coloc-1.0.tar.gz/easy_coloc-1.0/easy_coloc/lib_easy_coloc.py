import ESMF as _ESMF
from easy_coloc import lib_ioncdf as _ncdf
import numpy as _np

class easy_coloc():

	def __init__(self, model_gridfile, from_global=True, coord_names=['lon','lat'],mask_var=None,mask_value=0):
		# create a grid object for model grid
		self.model_grid = _ESMF.Grid(filename=model_gridfile,filetype=_ESMF.FileFormat.GRIDSPEC,
                                             is_sphere=from_global, coord_names=coord_names)

		# the array is masked when mask = mask_value
		self.mask_values = _np.array([mask_value])
		if mask_var is not None:
			mask = self.model_grid.add_item(_ESMF.GridItem.MASK)
			mask[:] = _ncdf.read_field(model_gridfile,mask_var).transpose()

		return None


	def define_obs_position_from_gridded(self,obs_datafile,obs_var,level=None, frame=None, coord_names=['lon','lat'],spval=None):
		# read gridded observation data
		data_field     = _ncdf.read_field(obs_datafile,obs_var,level=level,frame=frame)
		# read observation grid
		lon_gridded  = _ncdf.read_field(obs_datafile,coord_names[0])
		lat_gridded  = _ncdf.read_field(obs_datafile,coord_names[1])

		# make grid 2d
		if len(lon_gridded.shape) == 1:
			self.lon_gridded_2d,self.lat_gridded_2d = _np.meshgrid(lon_gridded,lat_gridded)
		else:
			self.lon_gridded_2d = lon_gridded ; self.lat_gridded_2d = lat_gridded

		if spval == None:
			jindex_list, iindex_list = _np.where(data_field.mask == False)
			nindex = len(jindex_list)
			lon_obs = _np.empty((nindex)) ; lat_obs = _np.empty((nindex)) ; data_obs = _np.empty((nindex))
			for k in _np.arange(nindex):
				lon_obs[k] = self.lon_gridded_2d[jindex_list[k], iindex_list[k]]
				lat_obs[k] = self.lat_gridded_2d[jindex_list[k], iindex_list[k]]
				data_obs[k] = data_field[jindex_list[k], iindex_list[k]]
		else:
			exit('TO DO')

		return lon_obs, lat_obs, data_obs, jindex_list, iindex_list

	def define_obs_position_from_gridded_simple(self,obs_datafile, coord_names=['lon','lat']):
		# read observation grid
		lon_gridded  = _ncdf.read_field(obs_datafile,coord_names[0])
		lat_gridded  = _ncdf.read_field(obs_datafile,coord_names[1])

		# make grid 2d
		if len(lon_gridded.shape) == 1:
			self.lon_gridded_2d,self.lat_gridded_2d = _np.meshgrid(lon_gridded,lat_gridded)
		else:
			self.lon_gridded_2d = lon_gridded ; self.lat_gridded_2d = lat_gridded

		lon_obs = self.lon_gridded_2d.flatten()
		lat_obs = self.lat_gridded_2d.flatten()
		return lon_obs, lat_obs

	def compute_interpolator(self,lon_obs,lat_obs):
		''' return interpolator, special request from Ze Skud '''
		# create field object for model data
		field_model = _ESMF.Field(self.model_grid, staggerloc=_ESMF.StaggerLoc.CENTER)
		# import obs location into ESMF locstream object
		locstream_obs = _ESMF.LocStream(len(lon_obs), coord_sys=_ESMF.CoordSys.SPH_DEG)
		locstream_obs["ESMF:Lon"] = lon_obs[:]
		locstream_obs["ESMF:Lat"] = lat_obs[:]
		field_obs = _ESMF.Field(locstream_obs)

		interpolator = _ESMF.Regrid(field_model, field_obs,
                                            regrid_method=_ESMF.RegridMethod.BILINEAR,
		                            unmapped_action=_ESMF.UnmappedAction.IGNORE,
		                            src_mask_values = self.mask_values) # esmf uses mask value, not spval
		field_model.destroy()
		locstream_obs.destroy()
		field_obs.destroy()
		return interpolator


	def interpolate_model_onto_obs_space(self,lon_obs,lat_obs,model_datafile,model_var,level=None,frame=None,spval=1.0e+15,interpolator=None):

		data_model = _ncdf.read_field(model_datafile,model_var,level=level,frame=frame)

		# create field object for model data
		field_model = _ESMF.Field(self.model_grid, staggerloc=_ESMF.StaggerLoc.CENTER)
		field_model.data[:] = data_model.transpose()
		# import obs location into ESMF locstream object
		locstream_obs = _ESMF.LocStream(len(lon_obs), coord_sys=_ESMF.CoordSys.SPH_DEG)
		locstream_obs["ESMF:Lon"] = lon_obs[:]
		locstream_obs["ESMF:Lat"] = lat_obs[:]

		field_obs = _ESMF.Field(locstream_obs)

		if interpolator is None:
			interpolator = _ESMF.Regrid(field_model, field_obs,
                                                        regrid_method=_ESMF.RegridMethod.BILINEAR,
							unmapped_action=_ESMF.UnmappedAction.IGNORE,
		                                        src_mask_values = self.mask_values) # esmf uses mask value, not spval

		field_obs = interpolator(field_model, field_obs)
		data_model_interp = field_obs.data.copy()
		data_model_interp[_np.where(data_model_interp == 0)] = spval

		field_model.destroy()
		locstream_obs.destroy()
		field_obs.destroy()

		return data_model_interp

	def interpolate_array_onto_obs_space(self,lon_obs,lat_obs,data_model,spval=1.0e+15,interpolator=None):
		''' interpolate a pre-computed array onto observation location '''

		if _np.ma.is_masked(data_model):
			data_values = data_model.data
			mask_local = data_model.mask
		else:
			data_values = data_model
			mask_local = self.mask_values

		# create field object for model data
		field_model = _ESMF.Field(self.model_grid, staggerloc=_ESMF.StaggerLoc.CENTER)
		field_model.data[:] = data_values.transpose()
		# import obs location into ESMF locstream object
		locstream_obs = _ESMF.LocStream(len(lon_obs), coord_sys=_ESMF.CoordSys.SPH_DEG)
		locstream_obs["ESMF:Lon"] = lon_obs[:]
		locstream_obs["ESMF:Lat"] = lat_obs[:]

		field_obs = _ESMF.Field(locstream_obs)

		if interpolator is None:
			interpolator = _ESMF.Regrid(field_model, field_obs,
                                                        regrid_method=_ESMF.RegridMethod.BILINEAR,
							unmapped_action=_ESMF.UnmappedAction.IGNORE,
		                                        src_mask_values = mask_local) # esmf uses mask value, not spval

		field_obs = interpolator(field_model, field_obs)
		data_model_interp = field_obs.data.copy()
		data_model_interp[_np.where(data_model_interp == 0)] = spval

		field_model.destroy()
		locstream_obs.destroy()
		field_obs.destroy()

		return data_model_interp


	def reshape_interpolated_data(self,jindex_list,iindex_list,data_model_interp,spval=1.0e+15):
		data_model_reshape = _np.empty((self.lon_gridded_2d.shape))
		data_model_reshape[:] = spval
		for k in _np.arange(len(jindex_list)):
			jind = jindex_list[k]
			iind = iindex_list[k]
			data_model_reshape[jind,iind] = data_model_interp[k]
			data_model_reshape = _np.ma.masked_values(data_model_reshape,spval)
		return data_model_reshape



	def define_obs_position_from_text(self,data_obs_file,lon_col,lat_col,offset_line=0,separator=',',if_found=None):
		f = open(data_obs_file,'r')
		lines = f.readlines()
		f.close()

		lon_obs = [] ; lat_obs = []
		for line in lines[offset_line:]:
			if if_found is not None:
				if line.find(if_found) != -1:
					lon_obs.append(float(line.replace(separator,' ').split()[lon_col]))
					lat_obs.append(float(line.replace(separator,' ').split()[lat_col]))
			else:
				lon_obs.append(float(line.replace(separator,' ').split()[lon_col]))
				lat_obs.append(float(line.replace(separator,' ').split()[lat_col]))

		lon_obs = _np.array(lon_obs)
		lat_obs = _np.array(lat_obs)
		return lon_obs, lat_obs

	def read_obs_data_from_text(self,data_obs_file,lon_col,lat_col,data_col,offset_line=0,separator=',',if_found=None):
		f = open(data_obs_file,'r')
		lines = f.readlines()
		f.close()

		lon_obs = [] ; lat_obs = [] ; data_obs = []
		for line in lines[offset_line:]:
			if if_found is not None:
				if line.find(if_found) != -1:
					lon_obs.append(float(line.replace(separator,' ').split()[lon_col]))
					lat_obs.append(float(line.replace(separator,' ').split()[lat_col]))
					data_obs.append(float(line.replace(separator,' ').split()[data_col]))
			else:
				lon_obs.append(float(line.replace(separator,' ').split()[lon_col]))
				lat_obs.append(float(line.replace(separator,' ').split()[lat_col]))
				data_obs.append(float(line.replace(separator,' ').split()[data_col]))

		lon_obs = _np.array(lon_obs)
		lat_obs = _np.array(lat_obs)
		data_obs = _np.array(data_obs)
		return lon_obs, lat_obs, data_obs

	def write_to_file(self,fileout,lon,lat,data):
		f =  open(fileout,'w')
		for k in _np.arange(len(lon)):
			f.write(str(lon[k]) + ',' + str(lat[k]) + ',' + str(data[k]) + '\n' )
		f.close()

	def write_to_file_two_dataset(self,fileout,lon,lat,data1,data2):
		f =  open(fileout,'w')
		for k in _np.arange(len(lon)):
			f.write(str(lon[k]) + ',' + str(lat[k]) + ',' + str(data1[k]) + ',' + str(data2[k]) +'\n' )
		f.close()

	def write_to_file_with_date(self,fileout,lon,lat,data,its_date,writespval=True,spval=1.0e+15):
		''' write data with date flag '''
		f =  open(fileout,'w')
		for k in _np.arange(len(lon)):
			if writespval:
				f.write(str(its_date.year) + ',' + str(its_date.month) + ',' + str(its_date.day) + ',' + str(lon[k]) + ',' + str(lat[k]) + ',' + str(data[k]) + '\n' )
			else:
				if not data[k] == spval:
					f.write(str(its_date.year) + ',' + str(its_date.month) + ',' + str(its_date.day) + ',' + str(lon[k]) + ',' + str(lat[k]) + ',' + str(data[k]) + '\n' )
				else:
					pass
		f.close()

