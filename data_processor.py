# -*- coding: utf-8 -*-
"""
DxTools: Processing XRD data files recorded with the Bruker D8 diffractometer
Copyright 2016, Alexandre  Boulle
alexandre.boulle@unilim.fr
"""
from scipy import loadtxt, savetxt, pi, log10, sin, cos, mgrid, column_stack, row_stack, append, shape, loadtxt, zeros, meshgrid, nan
from scipy.interpolate import griddata
from scipy.optimize import leastsq
import matplotlib.pyplot as plt
import sys
from misc import *
plt.style.use('bmh')

def crop_data(input_data, nlines, start, stop, start2, stop2):
    start = int(start)
    stop = int(stop)
    start2 = int(start2)
    stop2 = int(stop2)
    nlines = int(nlines)
    nscans = int(len(input_data)/nlines)
    data_matrix = input_data.reshape(nscans, nlines)
    data_matrix = data_matrix[start2:nscans-stop2:, start:nlines-stop:]
    return data_matrix.flatten()

def generate_RSM(cleaned, file_name, scantype, line_count, wl, state_log, state_angmat, state_qmat, state_xyz, step, start, stop, start2, stop2, thresh, threshmax):
    line_count = int(line_count)
    start = int(start)
    stop = int(stop)
    start2 = int(start2)
    stop2 = int(stop2)
    phi = cleaned[:,2]
    om = cleaned[:,5]
    offset = cleaned[:,6]
    tth = cleaned[:,7]
    scanning = cleaned[:,8]
    intensity = cleaned[:,9]
    bkg = intensity[intensity!=0].min()
    if threshmax == 0.0:
        threshmax = log10(intensity.max())

    # Check data validity
    if ((om[1:]-om[:-1]).sum() == 0) and ((phi[1:]-phi[:-1]).sum() == 0):
        status = 0
    else:
        status = 1
        if state_log == 1:
            intensity = log10(intensity+bkg)

        # Crop data to desired dimensions
        if ((start!=0) or (stop!=0) or (start2!=0) or (stop2!=0)):
            intensity = crop_data(intensity, line_count, start, stop, start2, stop2)
            om = crop_data(om, line_count, start, stop, start2, stop2)
            offset = crop_data(offset, line_count, start, stop, start2, stop2)
            tth = crop_data(tth, line_count, start, stop, start2, stop2)
            scanning = crop_data(scanning, line_count, start, stop, start2, stop2)
            phi = crop_data(phi, line_count, start, stop, start2, stop2)

            line_count = line_count - start - stop

        # Compute Q, Qz for different scanning geometries
        if "PSDFIXED" in scantype:
            inplane = 0
            Qx = 4*pi*sin(scanning*pi/360)*sin((om-scanning/2)*pi/180) / wl
            Qz = 4*pi*sin(scanning*pi/360)*cos((om-scanning/2)*pi/180) / wl

        if "COUPLED" in scantype:
            inplane = 0
            # Check if theta is the scanning motor and correct accordingly
            if (scanning[::line_count]-om[::line_count]).sum() == 0:
                scanning = 2*(scanning - offset)
                print("test")
            Qx = 4*pi*sin(scanning*pi/360)*sin((offset)*pi/180) / wl
            Qz = 4*pi*sin(scanning*pi/360)*cos((offset)*pi/180) / wl

        if "THETA" in scantype and ((phi[1:]-phi[:-1]).sum() != 0):
            inplane = 1
            Qx = (4*pi*sin(tth*pi/360)*sin((scanning-tth/2)*pi/180) / wl)*cos(phi*pi/180)
            Qz = (4*pi*sin(tth*pi/360)*sin((scanning-tth/2)*pi/180) / wl)*sin(phi*pi/180) #Actually correspond to Qy

        # interpolate intensity to a square mesh in reciprocal space
        grid_x, grid_z = mgrid[Qx.min():Qx.max()+step:step,Qz.min():Qz.max()+step:step]
        grid_I = griddata(column_stack((Qx, Qz)), intensity, (grid_x, grid_z), fill_value = 0, method='linear')
        #grid_I[grid_I<=thresh] = nan


        #Export data files
        if state_angmat == 1 and inplane == 0:
            scanning = scanning[:line_count:]
            if ((om[1:]-om[:-1]).sum() != 0):
                om = om[::line_count]
            else:
                om = tth[::line_count]
            int_matrix = intensity.reshape(int(len(intensity)/line_count), int(line_count))
            int_matrix = column_stack((om, int_matrix))
            int_matrix = row_stack((append([0], scanning), int_matrix))
            savetxt(file_name + '_angular_matrix.txt', int_matrix.T, fmt = '%10.8f')

        if state_angmat == 1 and inplane == 1:
            scanning = scanning[:line_count:]
            phi = phi[::line_count]
            int_matrix = intensity.reshape(int(len(intensity)/line_count), int(line_count))
            int_matrix = column_stack((phi, int_matrix))
            int_matrix = row_stack((append([0], scanning), int_matrix))
            savetxt(file_name + '_angular_matrix.txt', int_matrix.T, fmt = '%10.8f')

        if state_qmat == 1:
            qx = grid_x[:,0]
            qz = grid_z[0,:]
            out_I = column_stack((qx, grid_I[:]))
            out_I = row_stack((append([0],qz), out_I))
            savetxt(file_name + '_Q_matrix.txt', out_I.T, fmt = '%10.8f')

        if state_xyz == 1:
            if inplane == 0:
                savetxt(file_name + '_QxQzlogI.txt', column_stack((Qx,Qz, intensity)), fmt = '%10.8f')
            if inplane == 1:
                savetxt(file_name + '_QxQylogI.txt', column_stack((Qx,Qz, intensity)), fmt = '%10.8f')

        if state_log == 0:
            grid_I = log10(grid_I+bkg)

        plt.ion()
        fig=plt.figure()
        ax = fig.add_subplot(111)
        ax.set_xlabel(r"$Q_x (2 \pi / \AA)$", fontsize=16)
        if inplane == 0:
            ax.set_ylabel(r"$Q_z (2 \pi / \AA)$", fontsize=16)
        if inplane == 1:
            ax.set_ylabel(r"$Q_y (2 \pi / \AA)$", fontsize=16)
        plt.imshow(grid_I.T, extent=(Qx.min(),Qx.max()+step,Qz.min(),Qz.max()+step), origin='lower', cmap='jet', vmin=thresh, vmax=threshmax)
        plt.tight_layout()
        plt.show()

    return status

def generate_Temp(cleaned, file_name, line_count, state_indv, state_matrix, state_fit, start, stop, startT, stopT):
    line_count = int(line_count)
    start = int(start)
    stop = int(stop)
    startT = int(startT)
    stopT = int(stopT)
    temperature = cleaned[:,0]
    angle = cleaned[:,8]
    intensity = cleaned[:,9]
    bkg = intensity[intensity!=0].min()
    # Check data validity
    if (temperature[1:]-temperature[:-1]).sum() == 0:
        status = 0
    else:
        status = 1
        # Crop data to desired dimensions
        if ((start!=0) or (stop!=0) or (startT!=0) or (stopT!=0)):
                intensity = crop_data(intensity,line_count, start, stop, startT, stopT)
                angle = crop_data(angle,line_count, start, stop, startT, stopT)
                temperature = crop_data(temperature,line_count, start, stop, startT, stopT)
                line_count = line_count - start - stop

        int_matrix = intensity.reshape(int(len(intensity)/line_count), int(line_count))
        angle = angle[:int(line_count):]
        temperature = temperature[::int(line_count)]

        #Export data files
        if state_matrix == 1:
            out_I = column_stack((temperature, int_matrix))
            out_I = row_stack((append([0],angle), out_I))
            savetxt(file_name + '_matrix.txt', out_I.T, fmt = '%10.8f')

        # Compute integrated intensity + plotting
        if state_fit == 0:
            out_Ii = int_matrix.sum(axis=1)
            #writes result file
            savetxt(file_name + "_int_I.txt", column_stack((temperature, out_Ii)), fmt = '%10.8f')
            #writes individual files
            if state_indv == 1:
                for i in range(len(temperature)):
                    out_scan = column_stack((angle, int_matrix[i,:]))
                    savetxt(file_name + "_Scan"+str(i+1)+" T="+str(round(temperature[i],2))+".txt", out_scan, fmt = '%10.8f')

            plt.ion()
            fig=plt.figure()
            ax0 = fig.add_subplot(211)
            ax0.set_xlabel(r"$Temperature\ (deg.)$", fontsize = 14)
            ax0.set_ylabel(r"$Scanning\ angle\ (deg.)$", fontsize = 14)
            plt.imshow(log10(int_matrix+bkg).T, extent=(temperature.min(), temperature.max(), angle.min(),angle.max()), origin='lower', aspect="auto", cmap='jet')
            ax = fig.add_subplot(212, sharex=ax0)
            ax.set_xlabel(r"$Temperature\ (deg.)$", fontsize = 14)
            ax.set_ylabel(r"$Integrated\ intensity\ (counts)$", fontsize = 14)
            plt.xlim(temperature.min(), temperature.max())
            plt.plot(temperature, out_Ii)
            plt.tight_layout()
        # Fit diffraction profiles with a pseudo Voigt + plotting
        else:
            outfile = open(file_name+ "_fit_params.txt", "w")
            outfile.write("#temperature   area esd   position esd   FWHM esd\n")
            for i in range(len(temperature)):
                p, err = pVfit_param_err(angle,int_matrix[i,:])
                outfile.write(str(temperature[i])+" "+str(pVoigt_area(p))+" "+str(pVoigt_area_err(p,err))+" "+str(p[1])+" "+str(err[1])+" "+str(p[2])+" "+ str(err[2]) + "\n")
                #plt.plot(angle, int_matrix[i,:], 'ok', angle, pVoigt(angle, p), '-r')
                #plt.show() #uncomment to check fits
                #writes individual files (exp and fit)
                if state_indv == 1:
                    out_scan = column_stack((angle, int_matrix[i,:]))
                    out_scan = column_stack((out_scan, pVoigt(angle, p)))
                    savetxt(file_name + "_Scan"+str(i+1)+" T="+str(round(temperature[i],2))+".txt", out_scan, fmt = '%10.8f')
            outfile.close()

            fit_p = loadtxt(file_name.split(".")[0]+ "_fit_params.txt")
            plt.ion()
            fig=plt.figure()
            ax0 = fig.add_subplot(221)
            ax0.set_xlabel(r"$Temperature\ (deg.)$", fontsize = 14)
            ax0.set_ylabel(r"$Scanning\ angle\ (deg.)$", fontsize = 14)
            plt.imshow(log10(int_matrix+bkg).T, extent=(temperature.min(), temperature.max(), angle.min(),angle.max()), origin='lower', aspect="auto", cmap='jet')

            ax = fig.add_subplot(223)
            ax.set_xlabel(r"$Temperature\ (deg.)$", fontsize = 14)
            ax.set_ylabel(r"$Integrated\ intensity\ (counts)$", fontsize = 14)
            plt.xlim(temperature.min(), temperature.max())
            plt.plot(temperature, fit_p[:,1])

            ax = fig.add_subplot(222)
            ax.set_xlabel(r"$Temperature\ (deg.)$", fontsize = 14)
            ax.set_ylabel(r"$Peak\ position\ (deg.)$", fontsize = 14)
            plt.xlim(temperature.min(), temperature.max())
            plt.plot(temperature, fit_p[:,3])

            ax = fig.add_subplot(224)
            ax.set_xlabel(r"$Temperature\ (deg.)$", fontsize = 14)
            ax.set_ylabel(r"$FWHM\ (deg.)$", fontsize = 14)
            plt.xlim(temperature.min(), temperature.max())
            plt.plot(temperature, fit_p[:,5])
            plt.tight_layout()
        plt.show()
    return status

def generate_Xscan(cleaned, file_name, line_count, state_indv, state_matrix, state_fit, start, stop, startX, stopX ):
    line_count = int(line_count)
    start = int(start)
    stop = int(stop)
    startX = int(startX)
    stopX = int(stopX)
    tx = cleaned[:,3]
    ty = cleaned[:,4]
    angle = cleaned[:,8]
    intensity = cleaned[:,9]
    bkg = intensity[intensity!=0].min()
    # Check data validity
    if ((tx[1:]-tx[:-1]).sum()==0) and ((ty[1:]-ty[:-1]).sum()== 0):
        status = 0
    else:
        status = 1
        # Determine the scanning motor, x or y
        if tx[int(line_count)]!=tx[0]:
            print("X translation")
            tscan = tx
        else:
            print("Y translation")
            tscan = ty

        # Crop data to desired dimensions
        if ((start!=0) or (stop!=0) or (startX!=0) or (stopX!=0)):
                intensity = crop_data(intensity,line_count, start, stop, startX, stopX)
                angle = crop_data(angle,line_count, start, stop, startX, stopX)
                tscan = crop_data(tscan,line_count, start, stop, startX, stopX)
                line_count = line_count - start - stop

        int_matrix = intensity.reshape(int(len(intensity)/line_count), int(line_count))
        angle = angle[:int(line_count):]
        tscan = tscan[::int(line_count)]

        if state_matrix == 1:
            out_I = column_stack((tscan, int_matrix))
            out_I = row_stack((append([0],angle), out_I))
            savetxt(file_name + '_matrix.txt', out_I.T, fmt = '%10.8f')

        #if state_indv == 1:
            #for i in range(len(tscan)):
                #out_scan = column_stack((angle, int_matrix[i,:]))
                #savetxt(file_name + "_Scan"+str(i+1)+" Tr="+str(int(tscan[i]))+".txt", out_scan, fmt = '%10.8f')

        if state_fit == 0:
            out_Ii = int_matrix.sum(axis=1)
            savetxt(file_name + "_int_I.txt", column_stack((tscan, out_Ii)), fmt = '%10.8f')
            #writes individual files
            if state_indv == 1:
                for i in range(len(tscan)):
                    out_scan = column_stack((angle, int_matrix[i,:]))
                    savetxt(file_name + "_Scan"+str(i+1)+" Tr="+str(round(tscan[i],2))+".txt", out_scan, fmt = '%10.8f')

            plt.ion()
            fig=plt.figure()
            ax0 = fig.add_subplot(211)
            ax0.set_xlabel(r"$Translation\ (mm)$", fontsize = 14)
            ax0.set_ylabel(r"$Scanning\ angle\ (deg.)$", fontsize = 14)
            plt.imshow(log10(int_matrix+bkg).T, extent=(tscan.min(), tscan.max(), angle.min(),angle.max()), origin='lower', aspect="auto", cmap='jet')
            ax = fig.add_subplot(212, sharex=ax0)
            ax.set_xlabel(r"$Translation\ (mm)$", fontsize = 14)
            ax.set_ylabel(r"$Integrated\ intensity\ (counts)$", fontsize = 14)
            plt.xlim(tscan.min(), tscan.max())
            plt.plot(tscan, out_Ii)
            plt.tight_layout()
        else:
            outfile = open(file_name+ "_fitparams.txt", "w")
            outfile.write("#translation   area esd   position esd   FWHM esd\n")
            for i in range(len(tscan)):
                p, err = pVfit_param_err(angle,int_matrix[i,:])
                outfile.write(str(tscan[i])+" "+str(pVoigt_area(p))+" "+str(pVoigt_area_err(p,err))+" "+str(p[1])+" "+str(err[1])+" "+str(p[2])+" "+ str(err[2]) + "\n")
                #plt.plot(angle, int_matrix[i,:], 'ok', angle, pVoigt(angle, p), '-r')
                #plt.show() #uncomment to check fits
                #writes individual files (exp + fit)
                if state_indv == 1:
                    out_scan = column_stack((angle, int_matrix[i,:]))
                    out_scan = column_stack((out_scan, pVoigt(angle, p)))
                    savetxt(file_name + "_Scan"+str(i+1)+" Tr="+str(round(tscan[i],2))+".txt", out_scan, fmt = '%10.8f')
            outfile.close()

            fit_p = loadtxt(file_name.split(".")[0]+ "_fitparams.txt")
            plt.ion()
            fig=plt.figure()
            ax0 = fig.add_subplot(221)
            ax0.set_xlabel(r"$Translation\ (mm)$", fontsize = 14)
            ax0.set_ylabel(r"$Scanning\ angle\ (deg.)$", fontsize = 14)
            plt.imshow(log10(int_matrix+bkg).T, extent=(tscan.min(), tscan.max(), angle.min(),angle.max()), origin='lower', aspect="auto", cmap='jet')

            ax = fig.add_subplot(223)
            ax.set_xlabel(r"$Translation\ (mm)$", fontsize = 14)
            ax.set_ylabel(r"$Integrated\ intensity\ (Counts)$", fontsize = 14)
            plt.xlim(tscan.min(), tscan.max())
            plt.plot(tscan, fit_p[:,1])

            ax = fig.add_subplot(222)
            ax.set_xlabel(r"$Translation\ (mm)$", fontsize = 14)
            ax.set_ylabel(r"$Peak\ position\ (deg.)$", fontsize = 14)
            plt.xlim(tscan.min(), tscan.max())
            plt.plot(tscan, fit_p[:,3])

            ax = fig.add_subplot(224)
            ax.set_xlabel(r"$Translation\ (mm)$", fontsize = 14)
            ax.set_ylabel(r"$FWHM\ (deg.)$", fontsize = 14)
            plt.xlim(tscan.min(), tscan.max())
            plt.plot(tscan, fit_p[:,5])
            plt.tight_layout()
        plt.show()
    return status

def generate_Timescan(cleaned, file_name, line_count, state_indv, state_matrix, state_fit, start, stop, startX, stopX ):
    line_count = int(line_count)
    start = int(start)
    stop = int(stop)
    startX = int(startX)
    stopX = int(stopX)
    tx = cleaned[:,3]
    ty = cleaned[:,4]
    angle = cleaned[:,8]
    intensity = cleaned[:,9]
    time = cleaned[:,10]
    bkg = intensity[intensity>0].min()
    # Check data validity
    if ((time[1:]-time[:-1]).sum()==0):
        status = 0
    else:
        status = 1
        try:
            time_corr = loadtxt("time_correction.txt")
        except:
            time_corr = 0
        tscan = time + time_corr #manual correction of time

        # Crop data to desired dimensions
        if ((start!=0) or (stop!=0) or (startX!=0) or (stopX!=0)):
                intensity = crop_data(intensity,line_count, start, stop, startX, stopX)
                angle = crop_data(angle,line_count, start, stop, startX, stopX)
                tscan = crop_data(tscan,line_count, start, stop, startX, stopX)
                line_count = line_count - start - stop

        int_matrix = intensity.reshape(int(len(intensity)/line_count), int(line_count))
        angle = angle[:int(line_count):]
        tscan = tscan[int(line_count/2)::int(line_count)]

        if state_matrix == 1:
            out_I = column_stack((tscan, int_matrix))
            out_I = row_stack((append([0],angle), out_I))
            savetxt(file_name + '_matrix.txt', out_I.T, fmt = '%10.8f')

        #if state_indv == 1:
            #for i in range(len(tscan)):
                #out_scan = column_stack((angle, int_matrix[i,:]))
                #savetxt(file_name + "_Scan"+str(i+1)+" Tr="+str(int(tscan[i]))+".txt", out_scan, fmt = '%10.8f')

        if state_fit == 0:
            out_Ii = int_matrix.sum(axis=1)
            savetxt(file_name + "_int_I.txt", column_stack((tscan, out_Ii)), fmt = '%10.8f')
            #writes individual files
            if state_indv == 1:
                for i in range(len(tscan)):
                    out_scan = column_stack((angle, int_matrix[i,:]))
                    savetxt(file_name + "_Scan"+str(i+1)+" Tr="+str(round(tscan[i],2))+".txt", out_scan, fmt = '%10.8f')

            plt.ion()
            fig=plt.figure()
            ax0 = fig.add_subplot(211)
            ax0.set_xlabel(r"$Time\ (sec.)$", fontsize = 14)
            ax0.set_ylabel(r"$Scanning\ angle\ (deg.)$", fontsize = 14)
            plt.imshow(log10(int_matrix+bkg).T, extent=(tscan.min(), tscan.max(), angle.min(),angle.max()), origin='lower', aspect="auto", cmap='jet')
            ax = fig.add_subplot(212, sharex=ax0)
            ax.set_xlabel(r"$Time\ (sec.)$", fontsize = 14)
            ax.set_ylabel(r"$Integrated\ intensity\ (counts)$", fontsize = 14)
            plt.xlim(tscan.min(), tscan.max())
            plt.plot(tscan, out_Ii)
            plt.tight_layout()
        else:
            outfile = open(file_name+ "_fitparams.txt", "w")
            outfile.write("#translation   area esd   position esd   FWHM esd\n")
            for i in range(len(tscan)):
                p, err = pVfit_param_err(angle,int_matrix[i,:])
                outfile.write(str(tscan[i])+" "+str(pVoigt_area(p))+" "+str(pVoigt_area_err(p,err))+" "+str(p[1])+" "+str(err[1])+" "+str(p[2])+" "+ str(err[2]) + "\n")
                #plt.plot(angle, int_matrix[i,:], 'ok', angle, pVoigt(angle, p), '-r')
                #plt.show() #uncomment to check fits
                #writes individual files (exp + fit)
                if state_indv == 1:
                    out_scan = column_stack((angle, int_matrix[i,:]))
                    out_scan = column_stack((out_scan, pVoigt(angle, p)))
                    savetxt(file_name + "_Scan"+str(i+1)+" Tr="+str(round(tscan[i],2))+".txt", out_scan, fmt = '%10.8f')
            outfile.close()

            fit_p = loadtxt(file_name.split(".")[0]+ "_fitparams.txt")
            plt.ion()
            fig=plt.figure()
            ax0 = fig.add_subplot(221)
            ax0.set_xlabel(r"$Time\ (sec)$", fontsize = 14)
            ax0.set_ylabel(r"$Scanning\ angle\ (deg.)$", fontsize = 14)
            plt.imshow(log10(int_matrix+bkg).T, extent=(tscan.min(), tscan.max(), angle.min(),angle.max()), origin='lower', aspect="auto", cmap='jet')

            ax = fig.add_subplot(223)
            ax.set_xlabel(r"$Time\ (sec.)$", fontsize = 14)
            ax.set_ylabel(r"$Integrated\ intensity\ (Counts)$", fontsize = 14)
            plt.xlim(tscan.min(), tscan.max())
            plt.plot(tscan, fit_p[:,1])

            ax = fig.add_subplot(222)
            ax.set_xlabel(r"$Time\ (sec.)$", fontsize = 14)
            ax.set_ylabel(r"$Peak\ position\ (deg.)$", fontsize = 14)
            plt.xlim(tscan.min(), tscan.max())
            plt.plot(tscan, fit_p[:,3])

            ax = fig.add_subplot(224)
            ax.set_xlabel(r"$Time\ (sec.)$", fontsize = 14)
            ax.set_ylabel(r"$FWHM\ (deg.)$", fontsize = 14)
            plt.xlim(tscan.min(), tscan.max())
            plt.plot(tscan, fit_p[:,5])
            plt.tight_layout()
        plt.show()
    return status

def generate_Stress(cleaned, file_name, line_count, wl, state_indv, state_fit, start, stop, startpsi, stoppsi ):
    line_count = int(line_count)
    start = int(start)
    stop = int(stop)
    startpsi = int(startpsi)
    stoppsi = int(stoppsi)
    chi = cleaned[:,1]
    phi = cleaned[:,2]
    offset = cleaned[:,6]
    angle = cleaned[:,8]
    intensity = cleaned[:,9]
    bkg = intensity[intensity!=0].min()
    startpsi=int(startpsi)
    stoppsi=int(stoppsi)

    if ((chi[1:]-chi[:-1]).sum()==0) and ((offset[1:]-offset[:-1]).sum()== 0):
        status = 0
    else:
        status = 1

        # Determine tilting motor, chi or omega
        if ((chi[1:]-chi[:-1]).sum()==0):
            psi = offset
        else:
            psi = chi
        # Crop data to desired dimensions
        if ((start!=0) or (stop!=0)):
                intensity = crop_data(intensity,line_count, start, stop, 0, 0)
                angle = crop_data(angle,line_count, start, stop, 0, 0)
                #chi = crop_data(chi,line_count, start, stop, 0, 0)
                psi = crop_data(psi,line_count, start, stop, 0, 0)
                phi = crop_data(phi,line_count, start, stop, 0, 0)
                #offset = crop_data(offset,line_count, start, stop, 0, 0)
                line_count = line_count - start - stop

        #chi = chi[::int(line_count)]
        psi = psi[::int(line_count)]
        phi = phi[::int(line_count)]
        #offset = offset[::int(line_count)]
        angle = angle[:int(line_count):]
        int_matrix = intensity.reshape(int(len(intensity)/line_count), int(line_count))

        #if state_indv == 1:
            #for i in range(shape(int_matrix)[0]):
                #out_scan = column_stack((angle, int_matrix[i,:]))
                #savetxt(file_name + "_Scan"+str(i+1)+" PSI="+str(round(psi[i],2))+" PHI="+str(round(phi[i],2))+".txt", out_scan, fmt = '%10.8f')

        if state_fit == 0:
            #writes individual files
            if state_indv == 1:
                for i in range(shape(int_matrix)[0]):
                    out_scan = column_stack((angle, int_matrix[i,:]))
                    savetxt(file_name + "_Scan"+str(i+1)+" PSI="+str(round(psi[i],2))+" PHI="+str(round(phi[i],2))+".txt", out_scan, fmt = '%10.8f')

            plt.ion()
            dif_phi = phi[1:]-phi[:-1]
            n_phi = 1+len(dif_phi[dif_phi!=0]) #count how many values of phi
            psi = psi[:int(len(psi)/n_phi):] # resize psi and phi to their actual size
            phi = phi[::int(len(psi))]
            pos = zeros(shape(int_matrix)[0])
            fig=plt.figure()
            ax0=fig.add_subplot(211)
            ax0.set_xlabel(r"$Angle\ (deg.)$", fontsize = 14)
            ax0.set_ylabel(r"$Intensity\ (counts)$", fontsize = 14)
            for i in range(len(pos)):
                pos[i] = angle[int_matrix[i,:]==int_matrix[i,:].max()][0]
                plt.plot(angle, int_matrix[i,:])

            pos=pos.reshape(len(psi),len(phi))
            dspacing = wl / (2*sin(pos*pi/360))

            ax0 = fig.add_subplot(212)
            ax0.set_xlabel(r"$\sin^2 \psi$", fontsize = 14)
            ax0.set_ylabel(r"$d-spacing\ (\AA)$", fontsize = 14)
            psic = psi[startpsi:len(psi)-stoppsi]
            dspacingc = dspacing[startpsi:len(psi)-stoppsi,:]
            for i in range(len(phi)):
                plt.plot((sin(psic*pi/180))**2, dspacingc[:,i], '-o', label="phi="+str(phi[i]))
            plt.rcParams['legend.loc'] = 'best'
            plt.legend()
            plt.tight_layout()

            #export results
            outfile = open(file_name+ "_position.txt", "w")
            outfile.write("#Psi    ")
            for i in range(len(phi)):
                outfile.write("position(Phi="+str(phi[i])+")   ")
            outfile.write("\n")
            for j in range(len(psi)):
                outfile.write(str(psi[j])+"    ")
                for k in range(len(phi)):
                    outfile.write(str(pos[j,k])+"    ")
                outfile.write("\n")
            outfile.write("\n")
            outfile.close()

        else:
            plt.ion()
            dif_phi = phi[1:]-phi[:-1]
            n_phi = 1+len(dif_phi[dif_phi!=0]) #count how many values of phi
            psi = psi[:int(len(psi)/n_phi):] # resize psi and phi to their actual size
            phi = phi[::int(len(psi))]
            pos = zeros(shape(int_matrix)[0])
            err_pos = zeros(shape(int_matrix)[0])
            fig=plt.figure()
            ax0=fig.add_subplot(211)
            ax0.set_xlabel(r"$Angle\ (deg.)$", fontsize = 14)
            ax0.set_ylabel(r"$Intensity\ (counts)$", fontsize = 14)
            for i in range(len(pos)):
                p, err = pVfit_param_err(angle,int_matrix[i,:])
                pos[i] = p[1]
                err_pos[i] = err[1]
                plt.plot(angle, int_matrix[i,:], 'ok', angle, pVoigt(angle, p), '-r')
                #write individual files (exp and fit)
                if state_indv == 1:
                    out_scan = column_stack((angle, int_matrix[i,:]))
                    out_scan = column_stack((out_scan, pVoigt(angle, p)))
                    savetxt(file_name + "_Scan"+str(i+1)+" PSI="+str(round(psi[int(i%len(psi))],2))+" PHI="+str(round(phi[int(i//len(psi))],2))+".txt", out_scan, fmt = '%10.8f')
            pos=pos.reshape(len(psi),len(phi))
            err_pos=err_pos.reshape(len(psi),len(phi))
            dspacing = wl / (2*sin(pos*pi/360))

            ax0 = fig.add_subplot(212)
            ax0.set_xlabel(r"$\sin^2 \psi$", fontsize = 14)
            ax0.set_ylabel(r"$d-spacing\ (\AA)$", fontsize = 14)
            psic = psi[startpsi:len(psi)-stoppsi]
            dspacingc = dspacing[startpsi:len(psi)-stoppsi,:]
            for i in range(len(phi)):
                plt.plot((sin(psic*pi/180))**2, dspacingc[:,i], '-o', label="phi="+str(phi[i]))
            plt.rcParams['legend.loc'] = 'best'
            plt.legend()
            plt.tight_layout()
            #out_I = column_stack((psi, pos))
            #out_I = row_stack((append([0],phi), out_I))
            #savetxt(file_name + '_position_fit.txt', out_I, fmt = '%10.8f')

            #export results
            outfile = open(file_name+ "_position_fit.txt", "w")
            outfile.write("#Psi    ")
            for i in range(len(phi)):
                outfile.write("position(Phi="+str(phi[i])+")   esd    ")
            outfile.write("\n")
            for j in range(len(psi)):
                outfile.write(str(psi[j])+"    ")
                for k in range(len(phi)):
                    outfile.write(str(pos[j,k])+"    "+str(err_pos[j,k])+"    ")
                outfile.write("\n")
            outfile.write("\n")
            outfile.close()

    return status

def generate_Pole(cleaned, file_name, scantype, line_count, state_indv, state_angmat, state_xyz, start, stop, start2, stop2):
    line_count = int(line_count)
    start = int(start)
    stop = int(stop)
    start2 = int(start2)
    stop2 = int(stop2)
    khi = cleaned[:,1]
    phi = cleaned[:,2]
    scanning = cleaned[:,8]
    intensity = cleaned[:,9]
    bkg = intensity[intensity!=0].min()

    # Determine azimuth and zenith scanning motors
    if (scanning[::int(line_count)]-khi[::int(line_count)]).sum()!=0:
        azimuth = scanning
        zenith = khi
        stepa = (azimuth.max()-azimuth.min())/(line_count-1)
        stepz = (zenith.max()-zenith.min())/((len(zenith)/line_count)-1)
        fast_phi = 1
        print("Phi is the fast scanning motor.")
    #elif (scanning[::line_count]-khi[::line_count]).sum()==0:
    else:
        zenith = scanning
        azimuth = phi
        stepa = (azimuth.max()-azimuth.min())/((len(zenith)/line_count)-1)
        stepz = (zenith.max()-zenith.min())/(line_count-1)
        fast_phi = 0
        print("Khi is the fast scanning motor.")
    #else:
        #return 0

    # Check data validity
    if ((azimuth[1:]-azimuth[:-1]).sum() == 0) and ((zenith[1:]-zenith[:-1]).sum() == 0):
        status = 0
    else:
        status = 1
        # Crop data to desired dimensions
        if ((start!=0) or (stop!=0) or (start2!=0) or (stop2!=0)):
            intensity = crop_data(intensity, line_count, start, stop, start2, stop2)
            azimuth = crop_data(azimuth, line_count, start, stop, start2, stop2)
            zenith = crop_data(zenith, line_count, start, stop, start2, stop2)
            line_count = line_count - start - stop

        #Export data files
        if state_xyz == 1:
            savetxt(file_name + '_ChiPhiInt.txt', column_stack((zenith,azimuth, intensity)), fmt = '%10.8f')

        #Convert to matrix for further processing
        if (azimuth[1] != azimuth[0]):
            azimuth = azimuth[:int(line_count):]
            zenith = zenith[::int(line_count)]
        else:
            azimuth = azimuth[::int(line_count)]
            zenith = zenith[:int(line_count):]
        int_matrix = intensity.reshape(int(len(intensity)/line_count), int(line_count))

        if state_indv == 1:
            for i in range(shape(int_matrix)[0]):
                if fast_phi == 1:
                    out_scan = column_stack((azimuth, int_matrix[i,:]))
                    savetxt(file_name + "_Scan"+str(i+1)+" PSI="+str(round(zenith[i],2))+".txt", out_scan, fmt = '%10.8f')
                else :
                    out_scan = column_stack((zenith, int_matrix[i,:]))
                    savetxt(file_name + "_Scan"+str(i+1)+" PHI="+str(round(azimuth[i],2))+".txt", out_scan, fmt = '%10.8f')

        if state_angmat == 1:
            if fast_phi == 1:
                out_matrix = column_stack((zenith, int_matrix))
            else:
                out_matrix = column_stack((zenith, int_matrix.T))
            out_matrix = row_stack((append([0], azimuth), out_matrix))
            savetxt(file_name + '_ChiPhi_matrix.txt', out_matrix.T, fmt = '%10.8f')

        r, theta = meshgrid(zenith, azimuth*pi/180)
        plt.ion()
        fig, ax = plt.subplots(subplot_kw=dict(projection='polar'))
        if fast_phi == 1:
            ax.contourf(theta, r, log10(int_matrix.T+bkg), 25, cmap='jet')
        else:
            ax.contourf(theta, r, log10(int_matrix+bkg), 25, cmap='jet')
        plt.show()

    return status

def generate_Custom(cleaned, file_name, line_count, state_th, state_tth, state_chi, state_phi, state_x, state_y, state_temp,
                     start, stop):
    line_count = int(line_count)
    start = int(start)
    stop = int(stop)
    temperature = cleaned[:,0] - 273
    chi = cleaned[:,1]
    phi = cleaned[:,2]
    tx = cleaned[:,3]
    ty = cleaned[:,4]
    om = cleaned[:,5]
    tth = cleaned[:,7]
    angle = cleaned[:,8]
    intensity = cleaned[:,9]

    if ((start!=0) or (stop!=0)):
        temperature = crop_data(temperature,line_count, start, stop, 0, 0)
        chi = crop_data(chi,line_count, start, stop, 0, 0)
        phi = crop_data(phi,line_count, start, stop, 0, 0)
        tx = crop_data(tx,line_count, start, stop, 0, 0)
        ty = crop_data(ty,line_count, start, stop, 0, 0)
        om = crop_data(om,line_count, start, stop, 0, 0)
        tth = crop_data(tth,line_count, start, stop, 0, 0)
        angle = crop_data(angle,line_count, start, stop, 0, 0)
        intensity = crop_data(intensity,line_count, start, stop, 0, 0)

        line_count = line_count - start - stop

    temperature = temperature[::int(line_count)]
    chi = chi[::int(line_count)]
    phi = phi[::int(line_count)]
    tx = tx[::int(line_count)]
    ty = ty[::int(line_count)]
    om = om[::int(line_count)]
    tth = tth[::int(line_count)]
    angle = angle[:int(line_count):]
    int_matrix = intensity.reshape(int(len(intensity)/line_count), int(line_count))

    for i in range(shape(int_matrix)[0]):
        out_scan = column_stack((angle, int_matrix[i,:]))
        name = file_name + "_Scan"+str(i)
        if state_temp == 1:
            name += " T= " + str(round(temperature[i],2))
        if state_chi == 1:
            name += " CHI= " + str(round(chi[i],2))
        if state_phi == 1:
            name += " PHI= " + str(round(phi[i],2))
        if state_x == 1:
            name += " X= " + str(round(tx[i],2))
        if state_y == 1:
            name += " Y= " + str(round(ty[i],2))
        if state_th == 1:
            name += " TH= " + str(round(om[i],3))
        if state_tth == 1:
            name += " TTH= " + str(round(tth[i],3))
        savetxt(name+".txt", out_scan, fmt = '%10.8f')

    return 1
