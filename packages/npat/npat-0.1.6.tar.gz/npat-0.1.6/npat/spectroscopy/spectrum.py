import os,matplotlib.pyplot as plt, numpy as np, datetime as dtm
from scipy.optimize import curve_fit
from scipy.special import erfc
from ast import literal_eval
import sqlite3
from npat.reactions.isotope import isotope
from npat.misc.plotter import plotter



class spectrum(object):
	def __init__(self,filename='',directory='',read_maestro=True):
		self.filename,self.directory = filename,directory+('' if directory.endswith('/') else '/') if directory!='' else ''
		self.peak_fits,self.calibrate,self.meta,self.spec,self.gamma_dict,self.A0_guess = None,False,{},[],None,None
		if read_maestro and filename!='':
			self.init_maestro(filename,directory)
		self.clr = plotter().pallate()
	def init_maestro(self,filename,directory=''):
		self.filename,self.directory = filename,directory+('' if directory.endswith('/') else '/') if directory!='' else ''
		word,data = '',{}
		for ln in open(self.directory+filename,'r').read().split('\n')[:-1]:
			if ln.startswith('$'):
				word = ln.strip().split('$')[1].split(':')[0]
				data[word] = []
				continue
			data[word].append(ln.strip())
		self.start_time = dtm.datetime.strptime(data['DATE_MEA'][0],'%m/%d/%Y %H:%M:%S')
		self.live_time = float(data['MEAS_TIM'][0].split(' ')[0])
		self.real_time = float(data['MEAS_TIM'][0].split(' ')[1])
		self.spec = np.fromiter(data['DATA'][1:],dtype=int,count=len(data['DATA'])-1)
		self.engcal = [float(i) for i in reversed(data['ENER_FIT'][0].split(' '))]
		self.effcal = [float(i) for i in data['SHAPE_CAL'][1].split(' ')]
		if self.effcal[0]==0.0: self.effcal = [0.04,-1.7,4.1]
		self.E_range = self.engcal[0]*np.arange(len(self.spec))+self.engcal[1]
		self.meta = literal_eval(self.filter_meta(''.join(data['META']))) if 'META' in data else {'res':0.05,'R':0.2,'alpha':0.9}
		self.meta['res'],self.meta['R'],self.meta['alpha'] = (self.meta['res'] if 'res' in self.meta else 0.05),(self.meta['R'] if 'R' in self.meta else 0.2),(self.meta['alpha'] if 'alpha' in self.meta else 0.9)
		self.errata = [data['SPEC_ID'],data['SPEC_REM'],data['ROI'],data['PRESETS'],data['MCA_CAL']]
		self.rescal = self.meta['res'] if 'res' in self.meta else 0.05
		self.SNP = self.SNIP()
		self.QSNP = np.zeros(len(self.spec))
	def filter_meta(self,meta):
		return meta.replace('inf','1E18')
	def init_db(self,db=None,db_connection=None,db_name=None,db_path=None):
		self.db,self.db_connection = None,None
		if db is not None and db_connection is not None:
			self.db = db
			self.db_connection = db_connection
		elif db_name is not None:
			db_path = './' if db_path is None else db_path
			db_fnm = db_path+('' if db_path.endswith('/') else '/')+db_name
			if not os.path.exists(db_fnm):
				f = open(db_fnm,'wb')
				f.close()
			self.db_connection = sqlite3.connect(db_fnm)
			self.db = self.db_connection.cursor()
		if self.db is not None:
			if len(list(self.db.execute('SELECT name FROM sqlite_master WHERE type="table" AND name="peaks"')))==0:
				self.db.execute("CREATE TABLE 'peaks' ( `idx` INTEGER, `isotope` TEXT, `energy` REAL, `intensity` REAL, `unc_intensity` REAL, `N` INTEGER, `unc_N` REAL, `efficiency` REAL, `unc_efficiency` REAL, `efficiency_correction` REAL, `chi2` REAL, `fit` TEXT, `unc_fit` TEXT )")
			if len(list(self.db.execute('SELECT name FROM sqlite_master WHERE type="table" AND name="spectra"')))==0:
				self.db.execute("CREATE TABLE `spectra` ( `idx` INTEGER, `filename` TEXT, `directory` TEXT, `start_time` TEXT, `live_time` REAL, `real_time` REAL, `meta` TEXT )")
			self.db_connection.commit()
	def write_db(self,calibrate=False):
		idx_ls = list(self.db.execute('SELECT idx FROM spectra WHERE filename=? AND directory=?',(self.filename,self.directory)))
		if len(idx_ls)==0:
			idx_tb = [i[0] for i in self.db.execute('SELECT idx FROM spectra')]
			idx = max(idx_tb)+1 if len(idx_tb)>0 else 1
			self.db.execute('INSERT INTO spectra VALUES (?,?,?,?,?,?,?)',(idx,self.filename,self.directory,self.start_time.strftime('%m/%d/%Y %H:%M:%S'),self.live_time,self.real_time,str(self.meta)))
		else:
			idx = idx_ls[0][0]
		self.db.execute('DELETE FROM peaks WHERE idx=?',(idx,))
		for pk in self.get_fmt_pks(calibrate):
			self.db.execute('INSERT INTO peaks VALUES(?,?,?,?,?,?,?,?,?,?,?,?,?)',(idx,pk['istp'],pk['E'],pk['I'],pk['unc_I'],pk['N'],pk['unc_N'],pk['eff'],pk['unc_eff'],pk['eff_corr'],pk['chi2'],str(pk['fit']),str(pk['unc'])))
		self.db_connection.commit()
	def get_fmt_pks(self,calibrate=False):
		pks = []
		for pk in self.fit_peaks(calibrate):
			N,M = len(pk['fit'])/(5 if self.calibrate else 3),(5 if self.calibrate else 3)
			for m in range(N):
				info,fit,unc = pk['pk_info'][m],pk['fit'][m*M:m*M+M],[u[m*M:m*M+M] for u in pk['unc'][m*M:m*M+M]]
				pks.append({'istp':info[3],'E':info[0],'I':info[1],'unc_I':info[2],'N':info[4],'unc_N':info[5],'eff':self.map_efficiency(info[0]),'unc_eff':self.map_unc_efficiency(info[0]),'eff_corr':self.map_efficiency_correction(info[0]),'chi2':info[6],'fit':fit,'unc':unc})
		return pks
	def read_db(self,update=False):
		idx_ls = list(self.db.execute('SELECT idx FROM spectra WHERE filename=? AND directory=?',(self.filename,self.directory)))
		if len(idx_ls)==0:
			return []
		peaks,idx = [],idx_ls[0][0]
		if update:
			rd = list(self.db.execute('SELECT * FROM spectra WHERE idx=?',(idx,)))[0]
			self.update_params(start_time=str(rd[3]),live_time=rd[4],real_time=rd[5],meta=literal_eval(rd[6]))
		return [{'istp':str(p[1]),'E':p[2],'I':p[3],'unc_I':p[4],'N':p[5],'unc_N':p[6],'eff':p[7],'unc_eff':p[8],'eff_corr':p[9],'chi2':p[10],'fit':literal_eval(str(p[11])),'unc':literal_eval(str(p[12]))} for p in self.db.execute('SELECT * FROM peaks WHERE idx=?',(idx,))]
	def update_params(self,start_time=None,live_time=None,real_time=None,engcal=None,effcal=None,meta=None):
		if start_time is not None:
			if type(start_time)==str:
				self.start_time = dtm.datetime.strptime(start_time,'%m/%d/%Y %H:%M:%S')
			self.start_time = start_time
		if live_time is not None:
			self.live_time = live_time
		if real_time is not None:
			self.real_time = real_time
		if engcal is not None:
			self.engcal = engcal
			self.E_range = self.engcal[0]*np.arange(len(self.spec))+self.engcal[1]
		if effcal is not None:
			self.effcal = effcal
		if meta is not None:
			for itm in meta:
				self.meta[itm] = meta[itm]
				if itm=='res':
					self.rescal = self.meta['res']
					self.SNP = self.SNIP()
	def write_maestro(self):
		groups = ['SPEC_ID','SPEC_REM','DATE_MEA','MEAS_TIM','DATA','ROI','PRESETS','ENER_FIT','MCA_CAL','SHAPE_CAL','META']
		data = self.errata[:2]+[[self.start_time.strftime('%m/%d/%Y %H:%M:%S')]]+[[str(int(self.live_time))+' '+str(int(self.real_time))]]
		data.append(['0 '+str(len(self.spec)-1)]+[''.join([' ' for i in range(7-int(np.log(max((s,1)))/np.log(10.0)))])+str(s) for s in self.spec])
		data += self.errata[2:4]+[[str(self.engcal[1])+' '+str(self.engcal[0])]]+[self.errata[4]]
		data += [[str(len(self.effcal)),' '.join(map(str,self.effcal))]]+[[str(self.meta),'']]
		f = open(self.directory+self.filename,'w+')
		f.write('\n'.join(['$'+groups[N]+':\n'+'\n'.join(d) for N,d in enumerate(data)]))
		f.close()
	def get_plot_spec(self,logscale=True):
		if logscale:
			return np.array([max((self.spec[0],1))]+[max((self.spec[i+m],1)) for i in np.arange(len(self.spec)-1) for m in [0,1]])
		return np.array([self.spec[0]]+[self.spec[i+m] for i in np.arange(len(self.spec)-1) for m in [0,1]])
	def get_plot_energy(self):
		return np.array([self.engcal[0]*(i-0.5-m)+self.engcal[1] for i in np.arange(1,len(self.spec),dtype=float) for m in [1.0,0.0]]+[self.map_energy(len(self.spec)-0.5)])
	def map_energy(self,indx,engcal=None):
		engcal = self.engcal if engcal is None else engcal
		if type(indx) in [int,float,np.float64]:
			return engcal[0]*indx+engcal[1]
		return np.array(indx)*engcal[0]+engcal[1]
	def map_index(self,energy,engcal=None):
		engcal = self.engcal if engcal is None else engcal
		if type(energy) in [int,float,np.float64]:
			return int(round((energy-engcal[1])/engcal[0]))
		return np.array(np.rint((np.array(energy)-engcal[1])/engcal[0]),dtype=int)
	def map_efficiency(self,energy,effcal=None):
		effcal = self.effcal if effcal is None else effcal
		if type(energy) in [int,float,np.float64]:
			return np.exp(effcal[0]*np.log(energy)**2+effcal[1]*np.log(energy)+effcal[2])
		return np.exp(effcal[0]*np.log(energy)**2+effcal[1]*np.log(energy)+effcal[2])
	def map_unc_efficiency(self,energy):
		if 'unc_eff' in self.meta:
			u = self.meta['unc_eff']
			if type(energy) in [int,float,np.float64]:
				return np.sqrt(np.log(energy)**4*u[0][0]+2.0*np.log(energy)**3*u[0][1]+2.0*np.log(energy)**2*u[0][2]+np.log(energy)**2*u[1][1]+2.0*np.log(energy)*u[1][2]+u[2][2])*self.map_efficiency(energy)
			return np.sqrt(np.log(energy)**4*u[0][0]+2.0*np.log(energy)**3*u[0][1]+2.0*np.log(energy)**2*u[0][2]+np.log(energy)**2*u[1][1]+2.0*np.log(energy)*u[1][2]+u[2][2])*self.map_efficiency(energy)
		else:
			if type(energy) in [int,float,np.float64]:
				return 0.05*self.map_efficiency(energy)
			return 0.05*self.map_efficiency(energy)
	def map_resolution(self,indx,rescal=None):
		rescal = self.rescal if rescal is None else rescal
		if type(indx) in [int,float,np.float64]:
			return rescal*np.sqrt(indx)
		return rescal*np.sqrt(indx)
	def map_efficiency_correction(self,energy):
		DT = self.dead_time_efficiency()
		SA = self.solid_angle_efficiency(self.meta['R_src'],self.meta['R_det'],self.meta['dist']) if 'R_src' in self.meta and 'R_det' in self.meta and 'dist' in self.meta else 1.0
		if type(energy) in [int,float,np.float64]:
			AT = self.self_attenuation_efficiency(energy,self.meta['Z'],self.meta['thickness']) if 'Z' in self.meta and 'thickness' in self.meta else 1.0
			return DT*AT*SA
		return DT*SA*self.self_attenuation_efficiency(energy,self.meta['Z'],self.meta['thickness']) if 'Z' in self.meta and 'thickness' in self.meta else DT*SA*np.ones(len(energy))
	def dead_time_efficiency(self):
		return self.live_time/self.real_time
	def self_attenuation_efficiency(self,energy,Z,thickness):
		if type(energy) in [int,float,np.float64]:
			return 1.0
		return np.ones(len(energy))
	def solid_angle_efficiency(self,R_src,R_det,dist):
		if R_src/R_det<0.1:
			return 1.0
		N,x,y = 50.0,R_src**2+R_det**2+dist**2/(2.0*R_src*R_det),dist**2/(2.0*R_src*R_det)
		sa_disk = (R_det/R_src)*(1.0/N)*sum([np.sin(np.pi*(n+0.5)/N)**2/(np.sqrt(x-np.cos(np.pi*(n+0.5)/N))*(np.sqrt(y)+np.sqrt(x-np.cos(np.pi*(n+0.5)/N)))) for n in range(int(N))])
		# sa_point = 1.0-1.0/np.sqrt(1.0+R_det**2/dist**2)
		R_point = 1.0
		N,x,y = 50.0,R_point**2+R_det**2+dist**2/(2.0*R_point*R_det),dist**2/(2.0*R_point*R_det)
		sa_point = (R_det/R_point)*(1.0/N)*sum([np.sin(np.pi*(n+0.5)/N)**2/(np.sqrt(x-np.cos(np.pi*(n+0.5)/N))*(np.sqrt(y)+np.sqrt(x-np.cos(np.pi*(n+0.5)/N)))) for n in range(int(N))])
		return sa_disk/sa_point
	def __add__(self,other):
		### add another spectrum to self.spec and add live and real time
		self.spec += other.spec
		self.live_time,self.real_time = self.live_time+other.live_time,self.real_time+other.real_time
		return self
	def __sub__(self,other):
		### subtract another spectrum multiplied ratio of live times (for bg subtraction)
		mult = self.real_time/other.real_time
		self.spec = np.array([max((0,int(self.spec[n]-mult*i))) for n,i in enumerate(other.spec)])
		return self
	def __mul__(self,other):
		### multiply self.spec by a float or int
		self.spec = np.array([max((0,int(i*other))) for i in self.spec])
		return self
	def exp_smooth(self,ls,alpha=0.3):
		R,RR,b = np.copy(ls),np.copy(np.flip(ls,axis=0)),1.0-alpha
		for n in np.arange(1,len(ls)):
			R[n] = alpha*R[n]+b*R[n-1]
			RR[n] = alpha*RR[n]+b*RR[n-1]
		return np.average([R,np.flip(RR,axis=-1)],axis=0)
	def SNIP(self,sig=4.5,offsig=1.5,alpha1=0.75,alpha2=0.15):
		dead,vi = 0,np.log(np.log(np.sqrt(self.exp_smooth(self.spec,alpha=alpha1)+1.0)+1.0)+1.0)
		while self.spec[dead]==0:
			dead+=1
		r,L,off,x = self.rescal,len(vi),int(self.rescal*sig*len(vi)**0.5),np.arange(len(self.spec))
		for M in np.linspace(0,sig,10):
			l,h = np.array(x-M*r*np.sqrt(x),dtype=int),np.array(x+M*r*np.sqrt(x),dtype=int)
			vi[dead+off:L-off] = np.fromiter((min((vi[n],0.5*(vi[l[n]]+vi[h[n]]))) for n in np.arange(dead+off,L-off)),dtype=float,count=L-2*off-dead)
		snip = self.exp_smooth((np.exp(np.exp(vi)-1.0)-1.0)**2-1.0,alpha=alpha2)
		snip += offsig*np.sqrt(snip+1.0)
		self.CLP = np.array(self.spec-snip,dtype=int)
		self.CLP[self.CLP<0] = 0
		return snip
	def QSNIP(self,L,H):
		self.QSNP = np.zeros(len(self.spec))
		for n,l in enumerate(L):
			A = self.quadratic_regression(range(l-1,H[n]+1),self.SNP[l-1:H[n]+1])
			for i in range(l-1,H[n]+1):
				self.QSNP[i] = sum([a*i**n for n,a in enumerate(A)])
	def find_pks(self):
		SNP,pks = self.SNIP(2.0),[]
		clip = [int(i-SNP[n]) if int(i-SNP[n])>3.5*np.sqrt(SNP[n]) else 0 for n,i in enumerate(self.exp_smooth(self.spec))]
		for n,i in enumerate(clip[1:]):
			if i>0 and clip[n]==0:
				pks.append({'l':n+1,'h':n+1,'m':i,'mu':n+1})
			elif i>0:
				pks[-1]['h'] = n+1
				if i>pks[-1]['m']:
					pks[-1]['m'],pks[-1]['mu'] = i,n+1
		return [p['mu'] for p in pks if 0.5*(p['h']-p['l'])>self.rescal*np.sqrt(p['mu'])]
	def linear_regression(self,x,y):
		xb,yb = np.average(x),np.average(y)
		m = sum([(i-xb)*(y[n]-yb) for n,i in enumerate(x)])/sum([(i-xb)**2 for i in x])
		return m,yb-m*xb
	def quadratic_regression(self,x,y):
		M = np.array([[sum([i**(m+n) for i in x]) for m in range(3)] for n in range(3)])
		b = np.array([sum([i**m*y[n] for n,i in enumerate(x)]) for m in range(3)])
		return np.dot(np.linalg.inv(M),b).tolist()
	def peak(self,x,A,mu,sig,R,alpha):
		r2 = 1.41421356237
		return A*np.exp(-0.5*((x-mu)/sig)**2)+R*A*np.exp((x-mu)/(alpha*sig))*erfc((x-mu)/(r2*sig)+1.0/(r2*alpha))
	def Npeak(self,x,*args,**kwargs):
		peak = np.array([self.QSNP[int(round(i))] for i in x])
		if (kwargs['cal'] if 'cal' in kwargs else self.calibrate):
			for n in range(len(args)/5):
				peak += self.peak(x,args[5*n],args[5*n+1],args[5*n+2],args[5*n+3],args[5*n+4])
		else:
			for n in range(len(args)/3):
				peak += self.peak(x,args[3*n],args[3*n+1],args[3*n+2],self.meta['R'],self.meta['alpha'])
		return peak
	def chi2(self,fn,x,y,b):
		if float(len(y)-len(b))<1:
			return float('Inf')
		return sum([(y[n]-i)**2/y[n] for n,i in enumerate(fn(x,*b)) if y[n]>0])/float(len(y)-len(b))
	def guess_A0(self,engcal=None,rescal=None):
		if self.A0_guess is not None and engcal is None and rescal is None:
			return self.A0_guess
		gammas,self.A0_guess,L = self.get_gamma_dict(),{},len(self.spec)
		for istp in self.meta['istp']:
			gm = gammas[istp]
			idx,eff = self.map_index(gm['E'],engcal),self.map_efficiency(gm['E'])
			sig = self.map_resolution(idx,rescal)
			self.A0_guess[istp] = abs(np.exp(np.average([0.0]+[np.log(2.5*sig[n]*self.CLP[i]/(gm['I'][n]*eff[n])+1.0) for n,i in enumerate(idx) if i<L],weights=[1e-9]+[gm['I'][n] for n,i in enumerate(idx) if i<L]))-1.0)
		return self.A0_guess
	def auto_calibrate(self):
		if len([g for istp,gm in self.get_gamma_dict().iteritems() for g in gm['E']])>2:
			obj = lambda x,m,b:self.simple_fit(x,self.guess_A0(engcal=[m,b]),engcal=[m,b])
			guess,x = [self.engcal[0],self.engcal[1]],np.arange(len(self.spec))
			for itr in np.arange(1.0,4.0):
				dm = np.linspace(1.0-0.05/itr**2,1.0+0.05/itr**2,100-30*itr)
				obm = [np.sum(obj(x,guess[0]*d,guess[1])) for d in dm]
				guess = [guess[0]*dm[obm.index(max(obm))],guess[1]]
				# db = np.linspace(-1.0/itr**2,1.0/itr**2,40-10*itr)
				# obb = [np.sum(obj(x,guess[0],guess[1]+d)) for d in db]
				# guess = [guess[0],guess[1]+db[obb.index(max(obb))]]
			self.update_params(engcal=guess)
			self.guess_A0(engcal=self.engcal)
	def get_gamma_dict(self):
		if self.gamma_dict is None:
			self.gamma_dict = {i:isotope(i).gammas(E_lim=[50,self.map_energy(0.99*len(self.spec))],I_lim=[0.05,None]) for i in self.meta['istp']}
		return self.gamma_dict
	def simple_fit(self,x,A,rescal=None,engcal=None,effcal=None):
		gammas,spec,L = self.get_gamma_dict(),np.zeros(len(self.spec)),len(self.spec)
		for istp in A:
			gm = gammas[istp]
			idx,eff = self.map_index(gm['E'],engcal=engcal),self.map_efficiency(gm['E'],effcal=effcal)
			sig = self.map_resolution(idx,rescal=rescal)
			h,l = np.array(idx+5.5*sig,dtype=int),np.array(idx-6.0*sig,dtype=int)
			for n,i in enumerate(idx):
				if l[n]>0 and h[n]<L:
					spec[l[n]:h[n]] += self.peak(x[l[n]:h[n]],A[istp]*gm['I'][n]*eff[n]/(2.5*sig[n]),i,sig[n],self.meta['R'],self.meta['alpha'])
		return spec
	def get_gammas(self,cutoff=2.5):
		A0,gammas,peaks = self.guess_A0(),self.get_gamma_dict(),{}
		obj = lambda x,*A:self.simple_fit(x,{i:A[n] for n,i in enumerate(self.meta['istp'])})
		try:
			fit,unc = curve_fit(obj,np.arange(len(self.spec)),self.CLP,p0=[A0[i] for i in A0],bounds=([0 for i in A0],[np.inf for i in A0]))
		except:
			fit = [A0[i] for i in A0]
		for n,istp in enumerate(self.meta['istp']):
			gm,N_D = gammas[istp],fit[n]
			idx,eff = self.map_index(gm['E']),self.map_efficiency(gm['E'])
			sig = self.map_resolution(idx)
			peaks[istp] = [{'p0':[N_D*gm['I'][n]*eff[n]/(2.5*sig[n]),i,sig[n]],'gm':[gm['E'][n],gm['I'][n],gm['dI'][n],istp],'l':int(i-max((6.5*sig[n],4))),'h':int(i+max((6.0*sig[n],4)))} for n,i in enumerate(idx) if N_D*gm['I'][n]*eff[n]/(2.5*sig[n])>cutoff*np.sqrt(self.SNP[i])]
		return peaks
	def get_bounds(self,n_par,val,upper=True):
		if upper:
			return {0:2.75*val,1:1.002*val,2:1.5*val,3:0.35,4:1.75}[n_par]
		return {0:0.0,1:0.998*val,2:0.35*val,3:0.01,4:0.1}[n_par]
	def zip_peaks(self,pks):
		l,h = min([p['l'] for p in pks]),max([p['h'] for p in pks])
		pk_info,p0 = [p['gm'] for p in pks],[p for pk in pks for p in pk['p0']]
		fit = [p for pk in pks for p in pk['fit']] if 'fit' in pks[0] else []
		N,L = len(fit)/len(pk_info),len(fit)
		unc = [np.zeros(N*n).tolist()+p+np.zeros(L-N*n-N).tolist() for n,pk in enumerate(pks) for p in pk['unc']] if 'unc' in pks[0] else []
		bounds = ([self.get_bounds(n,p,False) for pk in pks for n,p in enumerate(pk['p0'])],[self.get_bounds(n,p) for pk in pks for n,p in enumerate(pk['p0'])])
		return {'l':l,'h':h,'pk_info':pk_info,'p0':p0,'bounds':bounds,'fit':fit,'unc':unc}
	def get_p0(self):
		gammas = self.get_gammas()
		peaks = sorted([p for istp in gammas for p in gammas[istp]],key=lambda h:h['l'])
		if self.calibrate:
			peaks = [{'l':p['l'],'h':p['h'],'gm':p['gm'],'p0':p['p0']+[self.meta['R'],self.meta['alpha']]} for p in peaks]
		return self.group_peaks(peaks)
	def group_peaks(self,peaks):
		groups = [[peaks[0]]]
		if len(peaks)>1:
			for p in peaks[1:]:
				if p['l']<groups[-1][-1]['h']:
					groups[-1].append(p)
				else:
					groups.append([p])
		self.QSNIP([min([p['l'] for p in p0]) for p0 in groups],[max([p['h'] for p in p0]) for p0 in groups])
		return map(self.zip_peaks,groups)
	def filter_peaks(self,pks,cutoff=4.5):
		peaks = []
		for pk in pks:
			N = len(pk['p0'])/len(pk['pk_info'])
			for m in range(len(pk['pk_info'])):
				if len(pk['pk_info'])==1:
					x,y = np.arange(pk['l'],pk['h']),self.spec[pk['l']:pk['h']]
				else:
					p0 = [i for n,i in enumerate(pk['fit']) if int(n/N)!=m]
					x = np.arange(int(pk['fit'][N*m+1]-6.0*pk['fit'][N*m+2]),int(pk['fit'][N*m+1]+5.5*pk['fit'][N*m+2]))
					offs = self.Npeak(x,*p0)
					y = [i-offs[n]+self.SNP[n+x[0]] for n,i in enumerate(self.spec[x[0]:x[-1]+1])]
				if N==3:
					chi2 = self.chi2(self.Npeak,x,y,[i for n,i in enumerate(pk['fit']) if int(n/N)==m])
					N_cts = int(pk['fit'][N*m]*(2.506*pk['fit'][N*m+2]+2*self.meta['R']*self.meta['alpha']*pk['fit'][N*m+2]*np.exp(-0.5/self.meta['alpha']**2)))
				else:
					chi2 = self.chi2(self.Npeak,x,y,[i for n,i in enumerate(pk['fit']) if int(n/N)==m])
					N_cts = int(pk['fit'][N*m]*(2.506*pk['fit'][N*m+2]+2*pk['fit'][N*m+3]*pk['fit'][N*m+4]*pk['fit'][N*m+2]*np.exp(-0.5/pk['fit'][N*m+4]**2)))
				sig = pk['fit'][N*m]/max((np.sqrt(self.SNP[int(round(pk['fit'][N*m+1]))]),5.0))
				unc_N = (min((np.sqrt(abs(pk['unc'][N*m][N*m])*(N_cts/pk['fit'][N*m])**2+abs(pk['unc'][N*m+2][N*m+2])*(N_cts/pk['fit'][N*m+2])**2),1e18))) if not np.isinf(pk['unc'][N*m][N*m]) else np.sqrt(N_cts)
				if sig>cutoff and chi2*cutoff<N_cts:
					peaks.append({'l':x[0],'h':x[-1],'gm':pk['pk_info'][m]+[N_cts,unc_N,chi2],'p0':pk['p0'][N*m:N*m+N],'fit':pk['fit'][N*m:N*m+N],'unc':[u.tolist()[N*m:N*m+N] for u in pk['unc'][N*m:N*m+N]]})
		self.peak_fits = self.group_peaks(peaks)
		return self.peak_fits
	def fit_peaks(self,calibrate=False):
		if self.peak_fits is not None:
			return self.peak_fits
		self.calibrate = calibrate
		fits = []
		for p in self.get_p0():
			try:
				p['fit'],p['unc'] = curve_fit(self.Npeak,np.arange(p['l'],p['h']),self.spec[p['l']:p['h']],p0=p['p0'],bounds=p['bounds'],sigma=np.sqrt(self.SNP[p['l']:p['h']]))
				fits.append(p)
			except Exception, err:
				print 'Error on peak:',p['pk_info']
				print Exception, err
		return self.filter_peaks(fits)
	def plot_spectrum(self,logscale=True,wfit=False,bg=False,calibrate=False,subpeak=False,printout=False,saveas=None,p0=False):
		f,ax = plt.subplots(figsize=(16,4.5))
		ax.plot(self.get_plot_energy(),self.get_plot_spec(logscale),lw=1.2,color=self.clr['k'],zorder=1,label=(self.meta['name'] if 'name' in self.meta else self.filename))
		if wfit:
			for n,pk in enumerate(self.fit_peaks(calibrate)):
				if printout:
					print pk['pk_info']
				ax.plot(self.map_energy(np.arange(pk['l'],pk['h'],0.1)),self.Npeak(np.arange(pk['l'],pk['h'],0.1),*pk['fit']),lw=1.8,color=self.clr['r'],zorder=10,label=('Peak Fit'+('s' if len(self.peak_fits)>1 else '') if n==0 else None))
				if subpeak:
					N,M = len(pk['fit'])/(5 if calibrate else 3),(5 if calibrate else 3)
					if N>1:
						for m in range(N):
							ax.plot(self.map_energy(np.arange(pk['l'],pk['h'],0.1)),self.Npeak(np.arange(pk['l'],pk['h'],0.1),*pk['fit'][m*M:m*M+M]),lw=1.2,ls='--',color=self.clr['r'],zorder=5)
		if p0:
			ax.plot(self.E_range,self.SNP+self.simple_fit(np.arange(len(self.spec)),self.guess_A0()),lw=1.8,color=self.clr['b'],zorder=4,label=r'p$_0$')
		if bg:
			ax.plot(self.E_range,self.SNP,lw=1.2,color=self.clr['b'],zorder=3)
		if logscale:
			ax.set_yscale('log')
		ax.set_ylim((max((0.9,ax.get_ylim()[0])),ax.get_ylim()[1]))
		ax.set_xlim((self.E_range[0],self.E_range[-1]))
		ax.set_xlabel('Energy (keV)')
		ax.set_ylabel('Counts')
		ax.legend(loc=0)
		f.tight_layout()
		if saveas is None:
			plt.show()
		else:
			f.savefig(saveas)
			plt.close()

# if __name__=="__main__":
# 	sp = spectrum('eu_calib.Spe','/home/jmorrell/Documents/npat/test/test_spectra/')
# 	sp.plot_spectrum(p0=True)
# 	sp.plot_spectrum(wfit=True,calibrate=False,printout=False,subpeak=True)
