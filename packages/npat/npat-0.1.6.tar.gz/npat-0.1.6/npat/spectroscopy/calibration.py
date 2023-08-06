import os,matplotlib.pyplot as plt, numpy as np, datetime as dtm
from scipy.optimize import curve_fit
from npat.reactions import isotope
from npat.spectroscopy.spectrum import spectrum
from npat.misc.plotter import plotter

class calibration(object):
	def __init__(self,calibration_spectra=[],experiment_spectra=[],db=None,db_connection=None,db_name=None,db_path=None):
		self.cspec,self.espec = calibration_spectra,experiment_spectra
		self.rescal,self.R,self.alpha = 0.05,0.2,0.9
		self.engcal = [0.4,0.0]
		self.init_eff()
		self.clr = plotter().pallate()
		if (db is not None and db_connection is not None) or (db_name is not None):
			self.init_db(db=db,db_connection=db_connection,db_name=db_name,db_path=db_path)
		else:
			self.db,self.db_connection = None,None
	def init_eff(self):
		self.effcal,self.unc_effcal = [0.04,-1.7,4.1],[[0.04,0,0],[0,0.17,0],[0,0,0.41]]
		self.disteff = False
		if len(self.cspec)>0:
			if all(['dist' in s.meta for s in self.cspec]):
				self.effcal = {d:[0.04,-1.7,4.1] for d in list(set([s.meta['dist'] for s in self.cspec]))}
				self.unc_effcal = {d:[[0.04,0,0],[0,0.17,0],[0,0,0.41]] for d in list(set([s.meta['dist'] for s in self.cspec]))}
				self.disteff = True
	def init_db(self,db=None,db_connection=None,db_name=None,db_path=None):
		sp = spectrum(read_maestro=False)
		sp.init_db(db=db,db_connection=db_connection,db_name=db_name,db_path=db_path)
		self.db,self.db_connection = sp.db,sp.db_connection
	def map_efficiency(self,energy,a,b,c):
		if type(energy) in [int,float,np.float64]:
			return np.exp(a*np.log(energy)**2+b*np.log(energy)+c)
		return [np.exp(a*np.log(e)**2+b*np.log(e)+c) for e in energy]
	def map_unc_efficiency(self,energy,eff,unc_eff):
		u = unc_eff
		if type(energy) in [int,float,np.float64]:
			return np.sqrt(np.log(energy)**4*u[0][0]+2.0*np.log(energy)**3*u[0][1]+2.0*np.log(energy)**2*u[0][2]+np.log(energy)**2*u[1][1]+2.0*np.log(energy)*u[1][2]+u[2][2])*self.map_efficiency(energy,*eff)
		return [np.sqrt(np.log(energy[n])**4*u[0][0]+2.0*np.log(energy[n])**3*u[0][1]+2.0*np.log(energy[n])**2*u[0][2]+np.log(energy[n])**2*u[1][1]+2.0*np.log(energy[n])*u[1][2]+u[2][2])*e for n,e in enumerate(self.map_efficiency(energy,*eff))]
	def append_spec(self,filename='',directory='',meta={},cal=True):
		sp = spectrum(filename,directory)
		sp.update_params(meta=meta)
		sp.write_maestro()
		if cal:
			self.cspec.append(sp)
			self.init_eff()
		else:
			self.espec.append(sp)
	def guess_calibration(self):
		self.engcal = [np.average([sp.engcal[0] for sp in self.cspec]),np.average([sp.engcal[1] for sp in self.cspec])]
		self.apply_calibration(spectra=self.cspec,write=False)
		m,b = [],[]
		for sp in self.cspec[:min(10,len(self.cspec))]:
			if len([g for istp in sp.meta['istp'] for g in isotope(istp).gammas(E_lim=[50,None],I_lim=[1.0,None])['E']])>1:
				sp.auto_calibrate()
				m.append(sp.engcal[0])
				b.append(sp.engcal[1])
		self.engcal = [np.average(m),np.average(b)]
		self.apply_calibration(spectra=self.cspec,write=False)
	def apply_calibration(self,spectra=None,write=True):
		if spectra is not None:
			for sp in spectra:
				sp.update_params(meta={'res':self.rescal,'R':self.R,'alpha':self.alpha})
				sp.update_params(engcal=self.engcal)
				if 'dist' in sp.meta:
					sp.update_params(effcal=self.effcal[sp.meta['dist']])
					sp.update_params(meta={'unc_eff':self.unc_effcal[sp.meta['dist']]})
				else:
					sp.update_params(effcal=self.effcal)
					sp.update_params(meta={'unc_eff':self.unc_effcal})
				if write:
					sp.write_maestro()
		else:
			self.apply_calibration(spectra=self.cspec,write=write)
			self.apply_calibration(spectra=self.espec,write=write)
	def calc_engcal(self,peaks):
		self.engcal_data = []
		for pk in [p for pk in peaks for p in pk['pks']]:
			if np.sqrt(pk['unc'][1][1])<0.05*pk['fit'][1] and np.sqrt(pk['unc'][1][1])<25.0/self.engcal[0]:
				self.engcal_data.append([pk['fit'][1],pk['E'],self.engcal[0]*np.sqrt(pk['unc'][1][1])])
		fit,unc = curve_fit(lambda x,m,b:[m*i+b for i in x],[i[0] for i in self.engcal_data],[i[1] for i in self.engcal_data],p0=self.engcal,sigma=[i[2] for i in self.engcal_data])
		self.engcal = fit.tolist()
	def calc_effcal(self,peaks):
		self.effcal_data = {d:[] for d in self.effcal} if self.disteff else []
		for fl in peaks:
			lm,unc_lm = isotope(fl['pks'][0]['istp']).decay_const(unc=True)
			A0,t_d,t_m = fl['meta']['A0'],(fl['start_time']-dtm.datetime.strptime(fl['meta']['ref_date'],'%m/%d/%Y %H:%M:%S')).total_seconds(),fl['real_time']
			for pk in fl['pks']:
				eff = pk['N']*lm/(A0*(1.0-np.exp(-lm*t_m))*np.exp(-lm*t_d)*0.01*pk['I']*pk['eff_corr'])
				unc_eff = np.sqrt((eff/pk['N'])**2*(pk['N']+pk['unc_N']**2)+(eff/A0)**2*(0.01*A0)**2+(eff/lm)**2*unc_lm**2+((eff/pk['I'])**2*pk['unc_I']**2))
				if unc_eff<eff and pk['E']>55.0:
					if self.disteff:
						self.effcal_data[fl['meta']['dist']].append([pk['E'],eff,unc_eff])
					else:
						self.effcal_data.append([pk['E'],eff,unc_eff])
		if self.disteff:
			for dist in self.effcal_data:
				print dist,self.effcal_data[dist]
				fit,unc = curve_fit(self.map_efficiency,[i[0] for i in self.effcal_data[dist]],[i[1] for i in self.effcal_data[dist]],p0=self.effcal[dist],sigma=[i[2] for i in self.effcal_data[dist]])
				self.effcal[dist],self.unc_effcal[dist] = fit.tolist(),unc.tolist()
		else:
			fit,unc = curve_fit(self.map_efficiency,[i[0] for i in self.effcal_data],[i[1] for i in self.effcal_data],p0=self.effcal,sigma=[i[2] for i in self.effcal_data])
			self.effcal,self.unc_effcal = fit.tolist(),unc.tolist()
	def calc_rescal(self,peaks):
		self.rescal_data = []
		for pk in [p for pk in peaks for p in pk['pks']]:
			if np.sqrt(pk['unc'][2][2])<pk['fit'][2]:
				self.rescal_data.append([np.sqrt(pk['fit'][1]),pk['fit'][2],np.sqrt(pk['unc'][2][2])])
		fit,unc = curve_fit(lambda x,r:[r*i for i in x],[i[0] for i in self.rescal_data],[i[1] for i in self.rescal_data],p0=[self.rescal],sigma=[i[2] for i in self.rescal_data])
		self.rescal = fit[0]
	def calc_pk_params(self,peaks):
		self.R_data,self.alpha_data = [],[]
		for pk in [p for pk in peaks for p in pk['pks']]:
			if np.sqrt(pk['unc'][3][3])*0.5<pk['fit'][3]:
				self.R_data.append([pk['fit'][3],pk['E'],np.sqrt(pk['unc'][3][3]),pk['N']])
			if np.sqrt(pk['unc'][4][4])*0.5<pk['fit'][4]:
				self.alpha_data.append([pk['fit'][4],pk['E'],np.sqrt(pk['unc'][4][4]),pk['N']])
		self.R = np.average([i[0] for i in self.R_data],weights=[i[3] for i in self.R_data]) if len(self.R_data)>0 else self.R
		self.alpha = np.average([i[0] for i in self.alpha_data],weights=[i[3] for i in self.alpha_data]) if len(self.alpha_data)>0 else self.alpha
	def calibrate(self,save=False):
		self.guess_calibration()
		for sp in self.cspec:
			sp.peak_fits = None
		peaks = [{'meta':sp.meta,'pks':sp.get_fmt_pks(True),'start_time':sp.start_time,'real_time':sp.real_time} for sp in self.cspec]
		self.calc_engcal(peaks)
		self.calc_effcal(peaks)
		self.calc_rescal(peaks)
		self.calc_pk_params(peaks)
		self.apply_calibration()
		if save and self.db is not None and self.db_connection is not None:
			for sp in self.cspec:
				sp.init_db(db=self.db,db_connection=self.db_connection)
				sp.write_db(calibrate=True)
	def save_all_plots(self,directory='./',extension=['png','pdf']):
		directory = directory if directory.endswith('/') else directory+'/'
		extension = extension if type(extension)==list else [extension]
		for ext in extension:
			if not os.path.exists(directory):
				os.system('mkdir '+directory)
			if not os.path.exists(directory+'/peak_fits'):
				os.system('mkdir '+directory+'/peak_fits')
			self.plot_peak_fits(saveas=[directory+'peak_fits/'+sp.filename.split('/')[-1].split('.')[0]+'.'+ext for sp in self.cspec])
			self.plot_energy_calibration(saveas=directory+'engcal.'+ext)
			self.plot_efficiency_calibration(saveas=directory+'effcal.'+ext)
			self.plot_resolution_calibration(saveas=directory+'rescal.'+ext)
			self.plot_pk_param_calibration(saveas=directory+'pk_param_cal.'+ext)
	def show_all_plots(self):
		self.plot_peak_fits()
		self.plot_energy_calibration()
		self.plot_efficiency_calibration()
		self.plot_resolution_calibration()
		self.plot_pk_param_calibration()
	def plot_peak_fits(self,saveas=[],subpeak=False):
		for n,sp in enumerate(self.cspec):
			sp.plot_spectrum(wfit=True,subpeak=subpeak,saveas=(saveas[n] if n<len(saveas) else None))
	def plot_energy_calibration(self,saveas=None):
		f,ax = plt.subplots(2,sharex=True,gridspec_kw = {'height_ratios':[3, 2]})
		ax[0].errorbar([i[0] for i in self.engcal_data],[i[1] for i in self.engcal_data],yerr=[i[2] for i in self.engcal_data],ls='None',marker='o',color=self.clr['k'])
		idx_range = np.arange(min([i[0] for i in self.engcal_data]),max([i[0] for i in self.engcal_data]),0.5)
		ax[0].plot(idx_range,[self.engcal[0]*i+self.engcal[1] for i in idx_range],lw=1.8,color=self.clr['gy'])
		ax[1].plot(idx_range,np.zeros(len(idx_range)),ls='--',lw=1.8,color=self.clr['gy'])
		ax[1].errorbar([i[0] for i in self.engcal_data],[i[1]-self.engcal[0]*i[0]-self.engcal[1] for i in self.engcal_data],yerr=[i[2] for i in self.engcal_data],ls='None',marker='o',color=self.clr['k'])
		ax[1].set_xlabel('Bin Number (a.u.)')
		ax[0].set_ylabel('Energy (keV)')
		ax[1].set_ylabel('Residual (keV)')
		f.tight_layout()
		if saveas is None:
			plt.show()
		else:
			f.savefig(saveas)
			plt.close()
	def plot_efficiency_calibration(self,saveas=None):
		f,ax = plt.subplots()
		if self.disteff:
			E_range = np.arange(min([i[0] for dist in self.effcal_data for i in self.effcal_data[dist]]),max([i[0] for dist in self.effcal_data for i in self.effcal_data[dist]]),0.5)
			for dist in self.effcal_data:
				ax.errorbar([i[0] for i in self.effcal_data[dist]],[i[1] for i in self.effcal_data[dist]],yerr=[i[2] for i in self.effcal_data[dist]],ls='None',marker='o',color=self.clr['k'])
				eff = np.array(self.map_efficiency(E_range,*self.effcal[dist]))
				ax.plot(E_range,eff,lw=1.8,color=self.clr['gy'])
				ax.fill_between(E_range,eff+np.array(self.map_unc_efficiency(E_range,self.effcal[dist],self.unc_effcal[dist])),eff-np.array(self.map_unc_efficiency(E_range,self.effcal[dist],self.unc_effcal[dist])),color=self.clr['gy'],alpha=0.5)
		else:
			ax.errorbar([i[0] for i in self.effcal_data],[i[1] for i in self.effcal_data],yerr=[i[2] for i in self.effcal_data],ls='None',marker='o',color=self.clr['k'])
			E_range = np.arange(min([i[0] for i in self.effcal_data]),max([i[0] for i in self.effcal_data]),0.5)
			eff = np.array(self.map_efficiency(E_range,*self.effcal))
			ax.plot(E_range,eff,lw=1.8,color=self.clr['gy'])
			ax.fill_between(E_range,eff+np.array(self.map_unc_efficiency(E_range,self.effcal,self.unc_effcal)),eff-np.array(self.map_unc_efficiency(E_range,self.effcal,self.unc_effcal)),color=self.clr['gy'],alpha=0.5)
		ax.set_xlabel('Energy (keV)')
		ax.set_ylabel('Efficiency (a.u.)')
		ax.set_yscale('log')
		f.tight_layout()
		if saveas is None:
			plt.show()
		else:
			f.savefig(saveas)
			plt.close()
	def plot_resolution_calibration(self,saveas=None):
		f,ax = plt.subplots()
		ax.errorbar([i[0] for i in self.rescal_data],[i[1] for i in self.rescal_data],yerr=[i[2] for i in self.rescal_data],ls='None',marker='o',color=self.clr['k'])
		idx_range = np.arange(min([i[0] for i in self.rescal_data]),max([i[0] for i in self.rescal_data]),0.1)
		ax.plot(idx_range,[self.rescal*i for i in idx_range],lw=1.8,color=self.clr['gy'])
		ax.set_xlabel(r'Bin Number$^{1/2}$ (a.u.)')
		ax.set_ylabel('Peak Width (a.u.)')
		f.tight_layout()
		if saveas is None:
			plt.show()
		else:
			f.savefig(saveas)
			plt.close()
	def plot_pk_param_calibration(self,saveas=None):
		f,ax = plt.subplots(2,sharex=True)
		ax[0].errorbar([i[1] for i in self.R_data],[i[0] for i in self.R_data],yerr=[i[2] for i in self.R_data],ls='None',marker='o',color=self.clr['k'])
		E_range = np.arange(min([i[1] for dat in [self.R_data,self.alpha_data] for i in dat]),max([i[1] for dat in [self.R_data,self.alpha_data] for i in dat]),0.5)
		ax[0].plot(E_range,[self.R for i in E_range],ls='--',lw=1.8,color=self.clr['gy'])
		ax[1].errorbar([i[1] for i in self.alpha_data],[i[0] for i in self.alpha_data],yerr=[i[2] for i in self.alpha_data],ls='None',marker='o',color=self.clr['k'])
		ax[1].plot(E_range,[self.alpha for i in E_range],ls='--',lw=1.8,color=self.clr['gy'])
		ax[0].set_ylabel('R (a.u.)')
		ax[1].set_ylabel(r'$\alpha$ (a.u.)')
		ax[1].set_xlabel('Energy (keV)')
		f.tight_layout()
		if saveas is None:
			plt.show()
		else:
			f.savefig(saveas)
			plt.close()
