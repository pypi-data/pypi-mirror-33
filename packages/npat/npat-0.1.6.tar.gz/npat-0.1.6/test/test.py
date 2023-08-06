from npat import isotope, calibration, spectrum

if __name__=='__main__':

	sp = spectrum('eu_calib.Spe','test_spectra')
	sp.auto_calibrate()
	print sp.engcal
	sp.plot_spectrum(p0=True)
	sp.plot_spectrum(wfit=True,calibrate=False,printout=True,subpeak=True)

	sp = spectrum('cs_calib.Spe','test_spectra')
	# sp.auto_calibrate()
	sp.plot_spectrum(p0=True)
	sp.plot_spectrum(wfit=True,calibrate=False,printout=True,subpeak=True)

	sp = spectrum('La01.Spe','test_spectra')
	sp.init_db(db_name='test.db')
	sp.write_db()
	sp.read_db()
	# sp.auto_calibrate()
	sp.plot_spectrum(wfit=True,calibrate=False,printout=True,subpeak=True)



	cb = calibration(db_name='test.db')
	# cb.append_spec('eu_calib.Spe','test_spectra',{'istp':['152EU'],'A0':39.368E3,'ref_date':'01/15/2009 12:00:00'})
	for dist,fnm in zip([1.0,5.0,10.0,15.0],['AA170825_1cm_Eu152','AE170825_5cm_Eu152','AG170825_10cm_Eu152','AO170825_15cm_Eu152']):
		cb.append_spec(fnm+'.Spe','test_spectra/Calibration',{'istp':['152EU'],'A0':39.29E3,'ref_date':'01/01/2009 12:00:00','dist':dist})
	cb.calibrate(save=True)
	cb.save_all_plots(directory='cal')
	# cb.show_all_plots()


	# ISTP = isotope('137CEm')
	# print ISTP.name
	# print ISTP.element
	# print ISTP.A
	# print ISTP.isomer
	# print ISTP.isotope
	# print ISTP.E_level
	# print ISTP.decay_modes
	# print ISTP.TeX()
	# print ISTP.mass
	# print ISTP.half_life(ISTP.optimum_units(),unc=True),ISTP.optimum_units()
	# print ISTP.gammas()
	# print ISTP.electrons()
	# print ISTP.beta_minus()
	# print ISTP.beta_plus()
	# print ISTP.alphas()