# -*- coding: utf-8 -*-
# -*- coding: utf-8 -*-
import zipfile
import os
import io
import sys
import glob
import xml.etree.ElementTree as ET


def uxd_reader(file_name):
    """
    Scans the uxd file, for every intensity value, saves all relevant motor coordinates and sensor values.
    All values are save in temporary SPEC-style tmp file.
    """
    #Check encoding: utf8 or latin1
    try:
        infile = io.open(file_name, "r", encoding="utf8")
        data = infile.read()
        infile.close()
        coding="utf8"
    except:
        data = io.open(file_name, "r", encoding="latin1")
        data = infile.read()
        infile.close()
        coding="latin1"
    try:
        infile = io.open(file_name, "r", encoding=coding)
    except:
        return "encoding error", 0, 0
    #sys.stdout.write("Reading raw data file...\n")
    i = 0.
    outfile = open("tmp", "w", encoding='utf8')
    outfile.write("#temperature   khi   phi   x   y   theta   offset   2theta   scanning motor   intensity\n")
    for line in infile:
        i += 1.
        #sys.stdout.write("\r%d %% complete" %(100*i/Nlignes))
        #sys.stdout.flush()
        if line.startswith("_DRIVE") or line.startswith("_TYPE"):
            scantype = line.split("=")[1]
        elif line.startswith("_WL1"):
            wl = float(line.split("=")[1])
        elif line.startswith("_STEPSIZE") or line.startswith("_STEP_SIZE"):
            if not line.startswith("_STEP_SIZE_B"):
                step = float(line.split("=")[1])
                line_count= 0.
        elif line.startswith("_STEP_SIZE_B"):
            stepb = float(line.split("=")[1])
        elif line.startswith("_START"):
            start = float(line.split("=")[1])
        elif line.startswith("_THETA") or line.startswith("_OMEGA"):
            om = float(line.split("=")[1])
        elif line.startswith("_2THETA") or line.startswith("_TWOTHETA"):
            if not line.startswith("_2THETAC"):
                tth = float(line.split("=")[1])
                offset = om - tth/2
        elif line.startswith("_KHI"):
            khi = float(line.split("=")[1])
        elif line.startswith("_PHI"):
            phi = float(line.split("=")[1])
        elif line.startswith("_X"):
            tx = float(line.split("=")[1])
        elif line.startswith("_Y"):
            ty = float(line.split("=")[1])
        elif line.startswith("_V4_TEMPERATURE"):
            temperature = float(line.split("=")[1]) - 273.
        elif not line.startswith(";"):
            if not line.startswith("_"):
                if line.strip():
                    try:
                        temperature = temperature
                    except:
                        temperature = 25
                    try:
                        scanning, intensity = line.split()
                        line_count +=1
                        outfile.write(str(temperature) + " " + str(khi) + " " + str(phi) + " " + str(tx) + " " + str(ty) + " " + str(om) + " " + str(offset) + " " + str(tth) + " " + scanning + " "  + intensity +'\n')
                    except:
                        if line_count==0:
                            scanning = start
                        else:
                            scanning += step
                        line_count +=1
                        intensity = line.split()[0]
                        outfile.write(str(temperature) + " " + str(khi) + " " + str(phi) + " " + str(tx) + " " + str(ty) + " " + str(om) + " " + str(offset) + " " + str(tth) + " " + str(scanning) + " "  + intensity +'\n')
    #sys.stdout.write("\n")
    #sys.stdout.write("Done !\n")
    infile.close()
    outfile.close()
    return scantype, line_count, wl

def file_nb(path):
    number = int(path.split("RawData")[-1].split(".xml")[0])
    return number

def brml_reader(file_name):
    """
    Extracts brml into a temporary unzip file, and parses all xml files.
    For every intensity value, saves all relevant motor coordinates and sensor values.
    All values are save in temporary SPEC-style tmp file.
    """
    extract_path = os.path.join(os.getcwd(),"unzip")
    if sys.platform == "win32":
        os.system("RMDIR "+ extract_path +" /s /q")
    elif sys.platform == "darwin":
        os.system("rm -rf "+ extract_path)
    elif sys.platform == "linux" or sys.platform == "linux2":
        os.system("rm -rf "+ extract_path)
    #Extracts all RawData*.xml files in the brml to temporary unzip file
    with zipfile.ZipFile(file_name,"r") as brml:
        for info in brml.infolist():
            if "RawData" in info.filename:
                brml.extract(info.filename, extract_path)

    outfile = open("tmp", "w", encoding='utf8') # Create output data file
    outfile.write("#temperature   khi   phi   x   y   theta   offset   2theta   scanning motor   intensity\n")

    data_path = os.path.join(extract_path, "*0","*.xml") #reading files in Experiment0 folder
    for file in sorted(glob.glob(data_path), key=file_nb):
        new_file = 0
        check_temperature = 0
        #parsing XML file
        tree = ET.parse(file) 
        root = tree.getroot()
        for chain in root.findall("./DataRoutes/DataRoute/ScanInformation"):
            scan_type = chain.get("VisibleName")
            if ("PSD" in scan_type) or ("Psd" in scan_type):
                scan_type = "PSDFIXED"
            if ("Coupled" in scan_type) or ("coupled" in scan_type) or ("2Theta-Omega" in scan_type):
                scan_type = "COUPLED"
            if ("Rocking" in scan_type) or ("rocking" in scan_type):
                scan_type = "THETA"

        for chain in root.findall("./FixedInformation/Instrument/PrimaryTracks/TrackInfoData/MountedOptics/InfoData/Tube/WaveLengthAlpha1"):
            wl = chain.get("Value")
        for chain in root.findall("./DataRoutes/DataRoute/ScanInformation/ScanAxes/ScanAxisInfo"):
            if new_file == 0:
                step = chain.find("Increment").text
                start = chain.find("Start").text
                if chain.find("Reference").text != "0":
                    ref = chain.find("Reference").text
                    start = str(float(ref)+float(start))
                new_file += 1

        for chain in root.findall("./DataRoutes/DataRoute/ScanInformation/ScanAxes/ScanAxisInfo"):
            if chain.get("AxisName") == "TwoTheta":
                tth = chain.find("Start").text
                if chain.find("Reference").text != "0":
                    ref = chain.find("Reference").text
                    tth = str(float(ref)+float(tth))
                #print("tth", tth)
            if chain.get("AxisName") == "Theta":
                om = chain.find("Start").text
                if chain.find("Reference").text != "0":
                    ref = chain.find("Reference").text
                    om = str(float(ref)+float(om))
                #print("om", om)
            if chain.get("AxisName") == "Chi":
                chi = chain.find("Start").text
                if chain.find("Reference").text != "0":
                    ref = chain.find("Reference").text
                    chi = str(float(ref)+float(chi))
                #print("chi", chi)
            if chain.get("AxisName") == "Phi":
                phi = chain.find("Start").text
                if chain.find("Reference").text != "0":
                    ref = chain.find("Reference").text
                    phi = str(float(ref)+float(phi))
                #print("phi", phi)
            if chain.get("AxisName") == "X":
                tx = chain.find("Start").text
                if chain.find("Reference").text != "0":
                    ref = chain.find("Reference").text
                    tx = str(float(ref)+float(tx))
                #print("tx", tx)
            if chain.get("AxisName") == "Y":
                ty = chain.find("Start").text
                if chain.find("Reference").text != "0":
                    ref = chain.find("Reference").text
                    ty = str(float(ref)+float(ty))
                #print("ty", ty)

        for chain in root.findall("./DataRoutes/DataRoute/DataViews/RawDataView/Recording"):
            if "Temperature" in chain.get("LogicName"):
                check_temperature = 1

        for chain in root.findall("./FixedInformation/Drives/InfoData"):
            if chain.get("LogicName") == "TwoTheta":
                tth = chain.find("Position").attrib["Value"]
                #print("tth", tth)
            if chain.get("LogicName") == "Theta":
                om = chain.find("Position").attrib["Value"]
                #print("om", om)
            if chain.get("LogicName") == "Chi":
                chi = chain.find("Position").attrib["Value"]
                #print("chi", chi)
            if chain.get("LogicName") == "Phi":
                phi = chain.find("Position").attrib["Value"]
                #print("phi", phi)
            if chain.get("LogicName") == "X":
                tx = chain.find("Position").attrib["Value"]
                #print("tx", tx)
            if chain.get("LogicName") == "Y":
                ty = chain.find("Position").attrib["Value"]
                #print("ty", ty)

        offset = str(float(om) - float(tth)/2.)

        if "PSDFIXED" in scan_type:
            if check_temperature == 0:
                for chain in root.findall("./DataRoutes/DataRoute"):
                    intensity = (chain.find("Datum").text).split(',')

                for chain in root.findall("./DataRoutes/DataRoute/DataViews/RawDataView/Recording"):
                    if chain.get("LogicName") == "Counter1D":
                        n_channels = int(chain.find("Size/X").text)

                line_count = 0
                int_shift = len(intensity) - n_channels
                for i in range(n_channels): #the intensity values are shifted to the right by int_shift
                    if i == 0:
                        scanning = float(start)
                    else:
                        scanning += float(step)
                    line_count += 1
                    outfile.write("25" + " " + (chi) + " " + (phi)
                                  + " " + (tx) + " " + (ty) + " " + (om)
                                  + " " + (offset) + " " + (tth) + " " + str(scanning)
                                  + " "  + intensity[i+int_shift] +'\n')
            else:
                return implementation_warning, 0, 0
        
        #if "COUPLED" in scan_type:
        # to do check in brml that all scans (except psd fixed) share the same data structure (wrt temperature)
        else:
            if check_temperature == 0:
                line_count = 0
                for chain in root.findall("./DataRoutes/DataRoute/Datum"):
                    if line_count == 0:
                        scanning = float(start)
                    else:
                        scanning += float(step)
                    line_count += 1
                    intensity = (chain.text).split(',')[-1]
                    outfile.write("25" + " " + (chi) + " " + (phi)
                                  + " " + (tx) + " " + (ty) + " " + (om)
                                  + " " + (offset) + " " + (tth) + " " + str(round(scanning, 4))
                                  + " "  + intensity +'\n')
            else:
                line_count = 0
                for chain in root.findall("./DataRoutes/DataRoute/Datum"):
                    if line_count == 0:
                        scanning = float(start)
                    else:
                        scanning += float(step)
                    line_count += 1
                    intensity = (chain.text).split(',')[-2]
                    temperature = (chain.text).split(',')[-1]
                    outfile.write(temperature + " " + (chi) + " " + (phi)
                                  + " " + (tx) + " " + (ty) + " " + (om)
                                  + " " + (offset) + " " + (tth) + " " + str(round(scanning, 4))
                                  + " "  + intensity +'\n')


    outfile.close()
    if sys.platform == "win32":
        os.system("RMDIR "+ extract_path +" /s /q")
    elif sys.platform == "darwin":
        os.system("rm -rf "+ extract_path)
    elif sys.platform == "linux" or sys.platform == "linux2":
        os.system("rm -rf "+ extract_path)
    return scan_type, line_count, wl
