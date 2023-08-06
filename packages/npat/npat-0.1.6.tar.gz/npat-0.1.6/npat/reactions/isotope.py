import os,sqlite3,re,numpy as np
_db_connection = sqlite3.connect('/'.join(os.path.realpath(__file__).split('/')[:-2])+'/data/decay_data/decay.db')
_db = _db_connection.cursor()

class isotope(object):
	def __init__(self,istp):
		self.db = _db
		self.element = ''.join(re.findall('[A-Z]+',istp))
		self.A,self.isomer =  int(istp.split(self.element)[0]),istp.split(self.element)[1]
		self.isotope = str(self.A)+self.element
		if self.isomer=='':
			self.isomer = 'g'
		if self.isomer=='m':
			self.isomer = 'm1'
		self.name = self.isotope+self.isomer
		self.N_states = len([i[1] for i in self.db.execute('SELECT * FROM chart WHERE Isotope=?',(self.isotope,))])
		self.E_level,self.t_half,self.unc_t_half,self.stable,self.abundance,self.unc_abundance = [(float(i[1]),float(i[3]),float(i[4]),bool(int(i[5])),float(i[6]),float(i[7])) for i in self.db.execute('SELECT * FROM chart WHERE Isotope=? AND isomer=?',(self.isotope,self.isomer))][0]
		decay_modes = [i[0] for i in self.db.execute('SELECT decay_mode FROM chart WHERE Isotope=? AND isomer=?',(self.isotope,self.isomer))][0].replace('[','').replace(']','').replace('{','').replace('}','').replace("'",'')
		self.decay_modes = [{str(t.split(':')[0]).strip():float(t.split(':')[1])} for t in decay_modes.split(',')]
		self.mass = [float(i[0]) for i in self.db.execute('SELECT amu FROM mass WHERE A=? AND element=?',(self.A,self.element.title()))][0]
		self.t_half,self.unc_t_half = None,None
		self.gm,self.el,self.bm,self.bp,self.al = None,None,None,None,None
	def TeX(self):
		state = '' if self.N_states==1 else self.isomer
		if self.N_states==2:
			state = state[0]
		return r'$^{'+str(self.A)+state+r'}$'+self.element.title()
	def half_life(self,units='s',unc=False):
		half_conv = {'ns':1e-9,'us':1e-6,'ms':1e-3,'s':1.0,'m':60.0,'h':3600.0,'d':86400.0,'y':3.154e7}[units]
		if self.t_half is None:
			self.t_half,self.unc_t_half = [(float(i[0]),float(i[1])) for i in self.db.execute('SELECT half_life,unc_half_life FROM chart WHERE Isotope=? AND isomer=?',(self.isotope,self.isomer))][0]
		if unc:
			return self.t_half/half_conv,self.unc_t_half/half_conv
		return self.t_half/half_conv
	def decay_const(self,units='s',unc=False):
		if unc:
			T2,uT2 = self.half_life(units,unc)
			return np.log(2.0)/T2,np.log(2.0)*uT2/T2**2
		return np.log(2.0)/self.half_life(units)
	def optimum_units(self):
		opt = ['ns']
		for units in ['us','ms','s','m','h','d','y']:
			if self.half_life(units)>1.0:
				opt.append(units)
		return opt[-1]
	def gammas(self,I_lim=[None,None],E_lim=[None,None],xrays=False):
		if self.gm is None:
			self.gm = [[float(i[3]),float(i[4]),float(i[5]),str(i[6])] for i in self.db.execute('SELECT * FROM gammas WHERE Isotope=? AND isomer=?',(self.isotope,self.isomer))]
		gammas = list(self.gm)
		for n,L in enumerate([E_lim,I_lim]):
			if L[0] is not None:
				gammas = [g for g in gammas if g[n]>=L[0]]
			if L[1] is not None:
				gammas = [g for g in gammas if g[n]<=L[1]]
		if not xrays:
			gammas = [g for g in gammas if g[3]=='']
		return {l:[g[n] for g in gammas] for n,l in enumerate(['E','I','dI','notes'])}
	def electrons(self,I_lim=(None,None),E_lim=(None,None),CE_only=False,Auger_only=False):
		if self.el is None:
			self.el = [[float(i[3]),float(i[4]),float(i[5]),str(i[6])] for i in self.db.execute('SELECT * FROM electrons WHERE Isotope=? AND isomer=?',(self.isotope,self.isomer))]
		electrons = list(self.el)
		for n,L in enumerate([E_lim,I_lim]):
			if L[0] is not None:
				electrons = [e for e in electrons if e[n]>=L[0]]
			if L[1] is not None:
				electrons = [e for e in electrons if e[n]<=L[1]]
		if CE_only:
			electrons = [e for e in electrons if e[3].startswith('CE')]
		if Auger_only:
			electrons = [e for e in electrons if e[3].startswith('Aug')]
		return {l:[e[n]for e in electrons] for n,l in enumerate(['E','I','dI','notes'])}
	def beta_minus(self,I_lim=(None,None),Endpoint_lim=(None,None)):
		if self.bm is None:
			self.bm = [[float(i[3]),float(i[4]),float(i[5]),float(i[6])] for i in self.db.execute('SELECT * FROM beta_minus WHERE Isotope=? AND isomer=?',(self.isotope,self.isomer))]
		betas = list(self.bm)
		for n,L in zip([3,1],[Endpoint_lim,I_lim]):
			if L[0] is not None:
				betas = [b for b in betas if b[n]>=L[0]]
			if L[1] is not None:
				betas = [b for b in betas if b[n]<=L[1]]
		return {l:[b[n] for b in betas] for n,l in enumerate(['muE','I','dI','endE'])}
	def beta_plus(self,I_lim=(None,None),Endpoint_lim=(None,None)):
		if self.bp is None:
			self.bp = [[float(i[3]),float(i[4]),float(i[5]),float(i[6])] for i in self.db.execute('SELECT * FROM beta_plus WHERE Isotope=? AND isomer=?',(self.isotope,self.isomer))]
		betas = list(self.bp)
		for n,L in zip([3,1],[Endpoint_lim,I_lim]):
			if L[0] is not None:
				betas = [b for b in betas if b[n]>=L[0]]
			if L[1] is not None:
				betas = [b for b in betas if b[n]<=L[1]]
		return {l:[b[n] for b in betas] for n,l in enumerate(['muE','I','dI','endE'])}
	def alphas(self,I_lim=(None,None),E_lim=(None,None)):
		if self.al is None:
			self.al = [[float(i[3]),float(i[4]),float(i[5])] for i in self.db.execute('SELECT * FROM alphas WHERE Isotope=? AND isomer=?',(self.isotope,self.isomer))]
		alphas = list(self.al)
		for n,L in enumerate([E_lim,I_lim]):
			if L[0] is not None:
				alphas = [a for a in alphas if b[n]>=L[0]]
			if L[1] is not None:
				alphas = [a for a in betas if b[n]<=L[1]]
		return {l:[a[n] for a in alphas] for n,l in enumerate(['E','I','dI'])}

