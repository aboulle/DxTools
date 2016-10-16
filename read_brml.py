# -*- coding: utf-8 -*-
import zipfile
import os
import sys
import glob
import xml.etree.ElementTree as ET


def file_nb(path):
    number = int(path.split("RawData")[-1].split(".xml")[0])
    return number
    

def brml_reader(file_name):
    #Extracts all RawData*.xml files in the brml to temporary unzip file
    extract_path = os.path.join(os.getcwd(),"unzip")
    with zipfile.ZipFile(file_name,"r") as brml:
        for info in brml.infolist():
            if "RawData" in info.filename:
                brml.extract(info.filename, extract_path)
                if "xperiment1" in info.filename: # Returns an error if there are multiple exp files in brml
                    return "exp error", 0, 0

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
            if "PSD" in scan_type:
                scan_type = "PSDFIXED"
            if "Coupled" in scan_type:
                scan_type = "COUPLED"

        for chain in root.findall("./FixedInformation/Instrument/PrimaryTracks/TrackInfoData/MountedOptics/InfoData/Tube/WaveLengthAlpha1"):
            wl = chain.get("Value")
        for chain in root.findall("./DataRoutes/DataRoute/ScanInformation/ScanAxes/ScanAxisInfo"):
            if new_file == 0:
                step = chain.find("Increment").text
                start = chain.find("Start").text
                new_file += 1

        for chain in root.findall("./DataRoutes/DataRoute/ScanInformation/ScanAxes/ScanAxisInfo"):
            if chain.get("AxisName") == "TwoTheta":
                tth = chain.find("Start").text
                #print("tth", tth)
            if chain.get("AxisName") == "Theta":
                om = chain.find("Start").text
                #print("om", om)
            if chain.get("AxisName") == "Chi":
                chi = chain.find("Start").text
                #print("chi", chi)
            if chain.get("AxisName") == "Phi":
                phi = chain.find("Start").text
                #print("phi", phi)
            if chain.get("AxisName") == "X":
                tx = chain.find("Start").text
                #print("tx", tx)
            if chain.get("AxisName") == "Y":
                ty = chain.find("Start").text
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
        #print("offset",offset)

        if "PSDFIXED" in scan_type:
            if check_temperature == 0:
                for chain in root.findall("./DataRoutes/DataRoute"):
                    intensity = (chain.find("Datum").text).split(',')
                line_count = 0
                for i in range(len(intensity)-2): #first 2 digits are time and abs. factor
                    if i == 0:
                        scanning = float(start)
                    else:
                        scanning += float(step)
                    line_count += 1
                    outfile.write("25" + " " + (chi) + " " + (phi)
                                  + " " + (tx) + " " + (ty) + " " + (om)
                                  + " " + (offset) + " " + (tth) + " " + str(scanning)
                                  + " "  + intensity[i+2] +'\n')
        
        if "COUPLED" in scan_type:
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

file_name = "./Examples/RSmap/002map.brml"
#file_name = "./Examples/Temperature/TiO2(001)-40-100.brml"
#file_name = "./Examples/Xmap/th2th392-419-001-01-1D-scanY-10-10 UP.brml"
a,b,c = brml_reader(file_name)
print(a,b,c)