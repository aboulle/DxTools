# coding: utf-8
# TODO:
# FIX AREA COMPARISON

#import matplotlib
#matplotlib.use('Qt5Agg')
import matplotlib.pyplot as plt
from matplotlib.widgets import Slider, Button#, TextBox
from matplotlib.colors import LogNorm
from matplotlib import ticker
import matplotlib.patches as patches
from VertSlider import VertSlider
import numpy as np
from scipy.optimize import leastsq

class coord_list:
	def __init__(self):
		self.value = []

	def add_to_list(self,new):
		self.value = np.concatenate((self.value,new))

	def remove_from_list(self,new):
		self.value = np.delete(self.value, new)

	def getvalue(self):
		return self.value

def process_matrix(file_name):
	plt.style.use('bmh')
	plt.rcParams['keymap.fullscreen'] = ''
	plt.rcParams['keymap.back'] = ''
	plt.rcParams['keymap.forward'] = ''

	rsm = np.loadtxt(file_name)
	Qx, Qz, intensity = rsm[0,1:], rsm[1:,0], rsm[1:,1:]
	step = Qx[1]-Qx[0]
	if intensity.max()<10:
		intensity=np.power(10,intensity)

	th=3 # Integration width
	thresh = 1 #minimum intensity
	bkg = 0.1
	# initialize global variables
	list_x = coord_list()
	list_z = coord_list()
	peak_list = coord_list()
	fit_matrix = np.zeros(np.shape(intensity))
	guess_list=[None]*10
	p_fit = [None]*10
	contour_list = [None]*10

# ███████ ██    ██ ███    ██  ██████ ████████ ██  ██████  ███    ██     ██████  ███████ ███████ ██ ███    ██ ██ ████████ ██  ██████  ███    ██ ███████
# ██      ██    ██ ████   ██ ██         ██    ██ ██    ██ ████   ██     ██   ██ ██      ██      ██ ████   ██ ██    ██    ██ ██    ██ ████   ██ ██
# █████   ██    ██ ██ ██  ██ ██         ██    ██ ██    ██ ██ ██  ██     ██   ██ █████   █████   ██ ██ ██  ██ ██    ██    ██ ██    ██ ██ ██  ██ ███████
# ██      ██    ██ ██  ██ ██ ██         ██    ██ ██    ██ ██  ██ ██     ██   ██ ██      ██      ██ ██  ██ ██ ██    ██    ██ ██    ██ ██  ██ ██      ██
# ██       ██████  ██   ████  ██████    ██    ██  ██████  ██   ████     ██████  ███████ ██      ██ ██   ████ ██    ██    ██  ██████  ██   ████ ███████

	# Slicing functions
	def extract_vprofile(intensity,coord,th):
		index = int((coord-Qx.min())/step)
		width = int((th-1.)/2)
		if th == 1:
			return intensity[:,index]
		else:
			return intensity[:,index-width:index+width+1:].sum(axis=1)

	def extract_hprofile(intensity,coord,th):
		index = int((coord-Qz.min())/step)
		width = int((th-1.)/2)
		if th == 1:
			return intensity[index,:]
		else:
			return intensity[index-width:index+width+1:,:].sum(axis=0)

	# A 2D Gaussian
	def NtwoD_Gaussian(coord, params):
		x=coord[0]
		y=coord[1]
		g = np.zeros(np.shape(x))
		for i in range(int((len(params)-1)/6)):
			amplitude = params[6*i]
			xo = float(params[6*i+1])
			yo = float(params[6*i+2])
			sigma_x = params[6*i+3]
			sigma_y = params[6*i+4]
			theta = params[6*i+5]

			a = (np.cos(theta)**2)/(2*sigma_x**2) + (np.sin(theta)**2)/(2*sigma_y**2)
			b = -(np.sin(2*theta))/(4*sigma_x**2) + (np.sin(2*theta))/(4*sigma_y**2)
			c = (np.sin(theta)**2)/(2*sigma_x**2) + (np.cos(theta)**2)/(2*sigma_y**2)
			g += (amplitude)*np.exp( -(a*((x-xo)**2) + 2*b*(x-xo)*(y-yo) + c*((y-yo)**2)))
		g += params[-1]
		return g.ravel()


	def my_curve_fit(data_x, data_y, p):
		errfunc = lambda p, data_x, data_y: NtwoD_Gaussian(data_x, p) - data_y
		rfit, success = leastsq(errfunc, p[:], args=(data_x, data_y))
		return rfit

# ███████ ██    ██ ███████ ███    ██ ████████     ███████ ██    ██ ███    ██  ██████ ████████ ██  ██████  ███    ██ ███████
# ██      ██    ██ ██      ████   ██    ██        ██      ██    ██ ████   ██ ██         ██    ██ ██    ██ ████   ██ ██
# █████   ██    ██ █████   ██ ██  ██    ██        █████   ██    ██ ██ ██  ██ ██         ██    ██ ██    ██ ██ ██  ██ ███████
# ██       ██  ██  ██      ██  ██ ██    ██        ██      ██    ██ ██  ██ ██ ██         ██    ██ ██    ██ ██  ██ ██      ██
# ███████   ████   ███████ ██   ████    ██        ██       ██████  ██   ████  ██████    ██    ██  ██████  ██   ████ ███████

	def fit2D(event, list_x, list_z, fit_matrix, guess_list, peak_list, p_fit, contour_list):
		kill_flag = []
		# Check if an area has been selected
		if len(list_x.getvalue()) == 0:
			print("No area selected. Using current window.")
			select_area(event, list_x, list_z)
		# else:
		#Check if some areas are included in others and remove the smallest
		for i in range(int(len(list_x.getvalue())/2)):
			for j in range(int(len(list_x.getvalue())/2)):
				if (list_x.getvalue()[2*i]>list_x.getvalue()[2*j])\
				and (list_x.getvalue()[2*i+1]<list_x.getvalue()[2*j+1])\
				and (list_z.getvalue()[2*i]>list_z.getvalue()[2*j])\
				and (list_z.getvalue()[2*i+1]<list_z.getvalue()[2*j+1]):
					kill_flag = np.concatenate((kill_flag,[i]))
		# print("kill flag", kill_flag)
		for i in kill_flag:
			list_x.remove_from_list([int(2*i), int(2*i+1)])
			list_z.remove_from_list([int(2*i), int(2*i+1)])
			print("Killed", len(kill_flag), "sub-areas")
			# print(list_z)
		# Fit in all selected areas
		for i in range(int(len(list_x.getvalue())/2)):
			print("AREA", i)
			first_peak = 1
			#convert Q coordinates in pixel
			ix0=int((list_x.getvalue()[2*i+0]-Qx.min())/step)
			ix1=int((list_x.getvalue()[2*i+1]-Qx.min())/step)
			iz0=int((list_z.getvalue()[2*i+0]-Qz.min())/step)
			iz1=int((list_z.getvalue()[2*i+1]-Qz.min())/step)
			#extract sub data ranges to be fitted
			zoomQx=Qx[ix0:ix1+1:]
			zoomQz=Qz[iz0:iz1+1:]
			zoomInt=intensity[iz0:iz1+1:,ix0:ix1+1:]
			zoomQx, zoomQz=np.meshgrid(zoomQx, zoomQz)
			#guess center and width of 2D gaussian
			xc=(list_x.getvalue()[2*i+0]+list_x.getvalue()[2*i+1])/2
			zc=(list_z.getvalue()[2*i+0]+list_z.getvalue()[2*i+1])/2
			w=list_x.getvalue()[2*i+1]-list_x.getvalue()[2*i+0]
			h=list_z.getvalue()[2*i+1]-list_z.getvalue()[2*i+0]
			exp_data=zoomInt.ravel()
			# Check if no peak has been selected: take center of area
			print("Area coordinates", list_x.getvalue(), list_z.getvalue())
			print("Peak coordinates", peak_list.getvalue())
			if len(peak_list.getvalue()) == 0:
				guess_list[i]=[exp_data.max(), xc, zc, w/3., h/3., 0*np.pi/180, exp_data.min()]
				peak_list.add_to_list([xc, zc])

			else:
				# If peaks have been manually selected, check if in area and add to guess
				for ii in range(int(len(peak_list.getvalue())/2)):
					# peak coordinates
					xc = peak_list.getvalue()[2*ii]
					yc = peak_list.getvalue()[2*ii+1]
					# check if peak in area
					if (xc>zoomQx.min()) and (xc<zoomQx.max()) and (yc>zoomQz.min()) and (yc<zoomQz.max()):
						print("Peak", ii, "is in area", i)
						if first_peak == 1:
							first_peak = 0
							print("Initialize first peak")
							# if area i has never been fitted before, create guess
							if p_fit[i] is None:
								print("Create new data")
								guess_list[i]=[exp_data.max(), xc, zc, w/3., h/3., 0*np.pi/180]
							else:
								print("Re-use previous data")
								guess_list[i] = p_fit[i][0:6]

						else:
							# if available use result of previous fit, otherwise create new
							print("Initialize other peaks")
							if p_fit[i] is not None:
								if len(p_fit[i][6*ii:6*ii+7:])==6:
									print("Re-use previous data")
									guess_list[i] = np.concatenate((guess_list[i], p_fit[i][6*ii:6*ii+7:]))
								else:
									print("Create new data")
									guess_list[i] = np.concatenate((guess_list[i], [exp_data.max(), xc, zc, w/3., h/3., 0*np.pi/180]))
							else:
								print("Create new data")
								guess_list[i] = np.concatenate((guess_list[i], [exp_data.max(), xc, zc, w/3., h/3., 0*np.pi/180]))
				guess_list[i]=np.concatenate((guess_list[i],[exp_data.min()]))

			# fit with N 2D gaussians and plot map and scans
			p_fit[i] = my_curve_fit([zoomQx, zoomQz], exp_data, guess_list[i])
			fit=NtwoD_Gaussian((zoomQx, zoomQz),p_fit[i]).reshape(np.shape(zoomQx)[0], np.shape(zoomQz)[1])
			# Print results

			for ii in range(int(len(peak_list.getvalue())/2)):
				# peak coordinates
				xc = peak_list.getvalue()[2*ii]
				yc = peak_list.getvalue()[2*ii+1]
				# check if peak in area
				if (xc>zoomQx.min()) and (xc<zoomQx.max()) and (yc>zoomQz.min()) and (yc<zoomQz.max()):
					print("************************************")
					print("AREA", i, "PEAK", ii, "FITTING RESULTS")
					print("Integrated intensity:", p_fit[i][6*ii])
					print("Qx:", p_fit[i][6*ii+1])
					print("Qz:", p_fit[i][6*ii+2])
					print("Sigma x:", p_fit[i][6*ii+3])
					print("Sigma z:", p_fit[i][6*ii+4])
					print("Rotation:", p_fit[i][6*ii+5])
					print("************************************")

			# Draw contour
			if contour_list[i] is not None:
				for coll in contour_list[i].collections:
					try:
						coll.remove()
					except:
						continue
			contour_list[i] = ax1.contour(zoomQx, zoomQz, np.log10(fit), 10, colors='w', linewidths=1)
			# Draw profiles
			fit_matrix[iz0:iz1+1:,ix0:ix1+1:]=fit
			l2fit.set_xdata(extract_vprofile(fit_matrix, x, th))
			l3fit.set_ydata(extract_hprofile(fit_matrix, z,th))

	# Event managing functions
	# Update scans when slider is modified
	def update(event, x, z):
		x = slider_Qx.val
		z = slider_Qz.val
		l0.set_xdata([x,x])
		l1.set_ydata([z,z])
		l2.set_xdata(extract_vprofile(intensity, x, th))
		l2fit.set_xdata(extract_vprofile(fit_matrix, x, th))
		l3.set_ydata(extract_hprofile(intensity, z, th))
		l3fit.set_ydata(extract_hprofile(fit_matrix, z,th))
		ax2.relim()
		ax2.autoscale_view()
		ax3.relim()
		ax3.autoscale_view()
		# fig.canvas.draw_idle()

	# Erase all selections and calculations
	def reset(event, list_x, list_z, x, z, fit_matrix, peak_list, guess_list, p_fit, contour_list):
		list_x.__init__()
		list_z.__init__()
		peak_list.__init__()
		fit_matrix = np.zeros(np.shape(intensity))
		guess_list=[None]*10
		p_fit=[None]*10
		contour_list = [None]*10

		slider_Qx.reset()
		slider_Qz.reset()
		x = slider_Qx.val
		z = slider_Qz.val

		ax1.clear()
		ax1.imshow(intensity+bkg, extent=(Qx.min(),Qx.max()+step,Qz.min(),Qz.max()+step), origin='lower', cmap='jet', vmin=thresh, aspect=1, norm=LogNorm())
		l0, = ax1.plot([x, x], [Qz.min(), Qz.max()], 'r-', alpha=0.5, linewidth=th)
		l1, = ax1.plot([Qx.min(), Qx.max()], [z, z], 'r-', alpha=0.5, linewidth=th)
		ax1.set_xlim(Qx.min(),Qx.max())
		ax1.set_ylim(Qz.min(),Qz.max())

		l0.set_xdata([x,x])
		l0.set_ydata([Qz.min(),Qz.max()])
		l2.set_xdata(extract_vprofile(intensity, x, th))
		l2fit.set_xdata(extract_vprofile(fit_matrix, x, th))
		ax2.relim()
		ax2.autoscale_view()

		l1.set_xdata([Qx.min(),Qx.max()])
		l1.set_ydata([z,z])
		l3.set_ydata(extract_hprofile(intensity, z, th))
		l3fit.set_ydata(extract_hprofile(fit_matrix, z,th))
		ax3.relim()
		ax3.autoscale_view()
		# fig.canvas.draw_idle()

	# Save extracted profiles
	def save_scans(event):
		outfile_name=file_name[:-4]
		np.savetxt(outfile_name+".xscan", np.column_stack((Qx,extract_hprofile(intensity, z,th))), fmt='%10.8f')
		np.savetxt(outfile_name+".zscan", np.column_stack((Qz,extract_vprofile(intensity, x,th))), fmt='%10.8f')

	def select_area(event, list_x, list_z):
		#global list_x, list_z, slider_Qx, slider_Qz, ax1, ax2, ax3
		xlo=ax1.get_xlim()[0]
		xhi=ax1.get_xlim()[1]
		ylo=ax1.get_ylim()[0]
		yhi=ax1.get_ylim()[1]
		if xlo < Qx.min(): xlo = Qx.min()
		if xhi > Qx.max(): xhi = Qx.max()
		if ylo < Qz.min(): ylo = Qz.min()
		if yhi > Qz.max(): yhi = Qz.max()
		w=xhi-xlo
		h=yhi-ylo
		# rectangle=patches.Rectangle((xlo,ylo),w,h, fill=False, linestyle='dotted', linewidth=2, edgecolor="orange")
		# ax1.add_patch(rectangle)
		# fig.canvas.draw_idle()

		list_x.add_to_list([xlo,xhi])
		list_z.add_to_list([ylo,yhi])


	def key_press(event, list_x, list_z, x, z):
		#global list_x, list_z, slider_Qx, slider_Qz, ax1, ax2, ax3, x, z
		i=0
		# Select fitting area and draw rectangle
		if event.key in ["enter", " "]:
			i+=1
			select_area(event, list_x, list_z)

		## Fitting shorcut
		#if event.key == "f":
			#fit2D(event)
		# Use arrows to modify slider
		if event.key == "left":
			slider_Qx.set_val(slider_Qx.val-step)
		if event.key == "right":
			slider_Qx.set_val(slider_Qx.val+step)
		if event.key == "up":
			slider_Qz.set_val(slider_Qz.val+step)
		if event.key == "down":
			slider_Qz.set_val(slider_Qz.val-step)

	def onclick(event, peak_list, x, z):
		#global peak_list, ax1, ax2, ax3, x, z, slider_Qx, slider_Qz
		# Double click to select peak
		if event.dblclick:
			ix, iy = event.xdata, event.ydata
			circle=patches.Circle((ix,iy),radius=5*step, fill=False, linestyle='solid', linewidth=2, edgecolor="yellow")
			ax1.add_patch(circle)
			# fig.canvas.draw_idle()
			peak_list.add_to_list([ix, iy])
		# Right click in map to select slider coordinates
		if event.button == 3:
			slider_Qx.set_val(event.xdata)
			slider_Qz.set_val(event.ydata)
			update(event, x, z)

#  ██████ ██████  ███████  █████  ████████ ███████     ███████ ██  ██████  ██    ██ ██████  ███████
# ██      ██   ██ ██      ██   ██    ██    ██          ██      ██ ██       ██    ██ ██   ██ ██
# ██      ██████  █████   ███████    ██    █████       █████   ██ ██   ███ ██    ██ ██████  █████
# ██      ██   ██ ██      ██   ██    ██    ██          ██      ██ ██    ██ ██    ██ ██   ██ ██
#  ██████ ██   ██ ███████ ██   ██    ██    ███████     ██      ██  ██████   ██████  ██   ██ ███████

	x = 0.5*(Qx.min()+Qx.max())
	z = 0.5*(Qz.min()+Qz.max())
	fig = plt.figure(1, figsize=(10,10))

	left, width = 0.15, 0.5
	bottom, height = 0.25, 0.5
	bottom_h = bottom + height + 0.035
	left_v = left + width + 0.035

	m_pos = [left, bottom, width, height]
	v_pos = [left_v, bottom, 0.15, height]
	h_pos = [left, bottom_h, width, 0.15]


	# Plot map
	ax1 = plt.axes(m_pos)
	ax1.imshow(intensity+bkg, extent=(Qx.min(),Qx.max()+step,Qz.min(),Qz.max()+step), origin='lower', cmap='jet', vmin=thresh, aspect=1, norm=LogNorm())
	l0, = ax1.plot([x, x], [Qz.min(), Qz.max()], 'r-', alpha=0.5, linewidth=th)
	l1, = ax1.plot([Qx.min(), Qx.max()], [z, z], 'r-', alpha=0.5, linewidth=th)
	ax1.set_xlim(Qx.min(),Qx.max())
	ax1.set_ylim(Qz.min(),Qz.max())

	# Plot vertical scan
	ax2 = plt.axes(v_pos,sharey=ax1)
	l2, = ax2.plot(extract_vprofile(intensity, x, th), Qz, '.-', color='steelblue', linewidth=0.5)
	l2fit, = ax2.plot(extract_vprofile(fit_matrix, x, th), Qz, 'r')
	ax2.set_ylim(Qz.min(),Qz.max())
	ax2.relim(visible_only=True)
	# ax2.set_xlim(0, extract_vprofile(intensity, x, th).max())
	# ax2.autoscale_view()
	# Plot horizontal scan
	ax3 = plt.axes(h_pos,sharex=ax1)
	l3, = ax3.plot(Qx,extract_hprofile(intensity, z,th), '.-', color='steelblue', linewidth=0.5)
	l3fit, = ax3.plot(Qx,extract_hprofile(fit_matrix, z,th), 'r')
	ax3.set_xlim(Qx.min(),Qx.max())
	ax3.relim(visible_only=True)
	# ax3.set_ylim(0, extract_hprofile(intensity, z, th).max())
	# ax3.autoscale_view()

	# Plot sliders
	axQx = plt.axes([left, bottom-0.1, 0.5, 0.03], facecolor='lightgrey')
	axQz = plt.axes([left-0.1, bottom, 0.03, 0.5], facecolor='lightgrey')
	slider_Qx = Slider(axQx, 'Qx', Qx.min(), Qx.max(), valinit=0.5*(Qx.min()+Qx.max()), valfmt='%5.4f', color='steelblue')
	slider_Qz = VertSlider(axQz, 'Qz', Qz.min(), Qz.max(), valinit=0.5*(Qz.min()+Qz.max()), valfmt='%5.4f', color='steelblue')

	#Text box
	# axThickness = plt.axes([left_v, bottom_h, 0.5, 0.03])
	# text_thickness = TextBox(axThickness, "Profile widthn(pxl):", initial = 1)


	# Buttons
	axSelect = plt.axes([0.15, 0.035, 0.15, 0.04])
	buttonSelect = Button(axSelect, 'Select area', color="lightgrey", hovercolor='steelblue')
	axFit = plt.axes([0.325, 0.035, 0.15, 0.04])
	buttonFit = Button(axFit, 'Fit 2D', color="lightgrey", hovercolor='steelblue')
	axSave = plt.axes([0.5, 0.035, 0.15, 0.04])
	buttonSave = Button(axSave, 'Save scans', color="lightgrey", hovercolor='steelblue')
	axReset = plt.axes([0.7, 0.035, 0.15, 0.04])
	buttonReset = Button(axReset, 'Reset', color="orange", hovercolor='red')

# ███████ ██    ██ ███████ ███    ██ ████████ ███████
# ██      ██    ██ ██      ████   ██    ██    ██
# █████   ██    ██ █████   ██ ██  ██    ██    ███████
# ██       ██  ██  ██      ██  ██ ██    ██         ██
# ███████   ████   ███████ ██   ████    ██    ███████

	slider_Qx.on_changed(lambda event: update(event, x, z))
	slider_Qz.on_changed(lambda event: update(event, x, z))
	buttonSave.on_clicked(save_scans)
	buttonReset.on_clicked(lambda event: reset(event, list_x, list_z, x, z, fit_matrix, peak_list, guess_list, p_fit, contour_list))
	buttonFit.on_clicked(lambda event: fit2D(event, list_x, list_z, fit_matrix, guess_list, peak_list, p_fit, contour_list))
	buttonSelect.on_clicked(lambda event: select_area(event, list_x, list_z))
	fig.canvas.mpl_connect('key_press_event', lambda event: key_press(event, list_x, list_z, x, z))
	fig.canvas.mpl_connect('button_press_event', lambda event: onclick(event, peak_list, x, z))

	plt.show()
