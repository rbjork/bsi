import arcpy
import os
from Tkinter import Tk
from tkFileDialog import askdirectory

def addTransitAccess(transitdir,countydir,transitdata,geoDataBaseName, addfield, transitstops_lyr):
    countypath = dataPath + countydir + "\\"
    arcpy.FeatureClassToGeodatabase_conversion(transitdir + "\\" + countydir + "\\" + transitdata, countypath + geoDataBaseName)
    if addfield:
        arcpy.AddField_management(countypath + geoDataBaseName + "\\" + transitdata, "access", "TEXT")
    expression = "getJobAccessScore(!X_Coord!)"
    codeblock = """def getJobAccessScore(lng):
    v = int(lng)
    if v <= 5975000:
        return '1'
    if v > 5975000 and v <= 5979000:
        return '2'
    if v > 5979000:
        return '3'"""

    featureclass= transitdata.split(".")[0]
    arcpy.CalculateField_management(countypath + "\\" + geoDataBaseName + "\\" + featureclass, "access", expression,"PYTHON_9.3",codeblock)
    arcpy.MakeFeatureLayer_management(countypath + "\\" + geoDataBaseName + "\\" + featureclass, transitstops_lyr)

def addTransitPotential(countydir,countyparcelnames,geoDataBaseName):
    countyPath = dataPath + countydir + "\\"
    expression = "setDefaultScore()"
    codeblock = """def setDefaultScore():
    return '0'"""
    for parcels in countyparcelnames:
        arcpy.AddField_management(countyPath + geoDataBaseName + "\\" + parcels, "potential", "TEXT")
        arcpy.CalculateField_management(countyPath + geoDataBaseName + "\\" + parcels, "potential", expression,"PYTHON_9.3",codeblock)

def features2gdb(countyfoldersList,outdir,geodbname):
    print "features2gdb"
    outWorkspace = outdir + "\\" + geodbname
    newfilelist = []
    n = 0
    for countyfolder in countyfoldersList:
        arcpy.env.workspace = homedir + "\\data\\" + str(countyfolder)
        for fc in arcpy.ListFeatureClasses():
            if str(fc) == "Parcels.shp":
                arcpy.FeatureClassToGeodatabase_conversion(fc, outWorkspace)
                if n > 0:
                    filename = fc.split('.')[0]
                    typ = fc.split('.')[1]
                    newfilelist.append(filename + "_" + str(n) + "." + typ)
                else:
                    newfilelist.append(fc)
        n = n + 1
    return newfilelist

# Alternative approach which may not be needed - creates seperate features for each set of transit stops distinquished by access
def splitTransitStopsData(transitdata,transitDataLayer,countyDir):
    featureclass= transitdata.split(".")[0]
    countypath = dataPath + countydir + "\\"

    arcpy.MakeFeatureLayer_management(countypath + "\\" + geoDataBaseName + "\\" + featureclass, transitDataLayer)
    arcpy.SelectLayerByAttribute_management(transitDataLayer, "NEW_SELECTION", "access > 0")
    arcpy.CopyFeatures_management(transitDataLayer, dataPath + countyDir + "\\" + geoDataBaseName + "\\transitStopsAccessLow")
    arcpy.SelectLayerByAttribute_management(transitDataLayer, "NEW_SELECTION", "access > 1")
    arcpy.CopyFeatures_management(transitDataLayer, dataPath + countyDir + "\\" + geoDataBaseName + "\\transitStopsAccessMedium")
    arcpy.SelectLayerByAttribute_management(transitDataLayer, "NEW_SELECTION", "access > 2")
    arcpy.CopyFeatures_management(transitDataLayer, dataPath + countyDir + "\\" + geoDataBaseName + "\\transitStopsAccessHigh")


def bufferTransitStops_QUARTER(transitstops, bufferedName, geoDataBaseName):
    print "bufferDestinations"
    countypath = dataPath +  countydir + "\\"
    arcpy.Buffer_analysis( countypath  + geoDataBaseName + "\\" + transitstops, transitdir + "\\" + geoDataBaseName + "\\" + bufferedName, "2640 Feet")

def bufferTransitStops_HALF(transitstops, bufferedName, geoDataBaseName):
    print "bufferDestinations"
    countypath = dataPath +  countydir + "\\"
    arcpy.Buffer_analysis( countypath  + geoDataBaseName + "\\" + transitstops, transitdir + "\\" + geoDataBaseName + "\\" + bufferedName, "2640 Feet")

def scoreparcels(targetFeature,bufferedTransitStop,geoDataBaseName, quarterMile, access):
    fcnear = bufferedTransitStop + "_shp" #'c:/data/base.gdb/well'
    fctarget = targetFeature + "_shp"
    arcpy.env.workspace = homedir + "\\" + geoDataBaseName
    arcpy.MakeFeatureLayer_management(targetFeature, 'parcels_lyr')
    #arcpy.SelectLayerByAttribute_management(fcnear, "SUBSET_SELECTION", "access > 10000")
    arcpy.SelectLayerByLocation_management(fcnear, 'intersect', fctarget)
    expression = "setScore("+str(access)+")"
    if quarterMile:     # Quarter Mile
        codeblock = """def setScore(access):
        if access == 'LOW':
            return '1'
        if access == 'MEDIUM':
            return '2'
        if access == 'HIGH':
            return '3'"""
    else:               # Half Mile
        codeblock = """def getScore(access):
        if access == 'LOW':
            return '4'
        if access == 'MEDIUM':
            return '5'
        if access == 'HIGH':
            return '6'"""
    arcpy.CalculateField_management(transitdir + "\\" + geoDataBaseName + "\\transitsStops", "access", expression,"PYTHON_9.3",codeblock)


# No Split required
def scoreparcels2(targetFeature,bufferedTransitStop,geoDataBaseName, quarterMile, access):
    fcnear = bufferedTransitStop + "_shp" #'c:/data/base.gdb/well'
    fctarget = targetFeature + "_shp"
    arcpy.env.workspace = homedir + "\\" + geoDataBaseName
    arcpy.MakeFeatureLayer_management(targetFeature, 'parcels_lyr')
    arcpy.SelectLayerByAttribute_management(fcnear, "NEW_SELECTION", "access > " + str(access))
    arcpy.SelectLayerByLocation_management(fcnear, 'intersect', fctarget)
    expression = "setScore("+str(access)+")"
    if quarterMile:     # Quarter Mile
        codeblock = """def setScore(access):
        if access == 'LOW':
            return '1'
        if access == 'MEDIUM':
            return '2'
        if access == 'HIGH':
            return '3'"""
    else:               # Half Mile
        codeblock = """def getScore(access):
        if access == 'LOW':
            return '4'
        if access == 'MEDIUM':
            return '5'
        if access == 'HIGH':
            return '6'"""
    arcpy.CalculateField_management(transitdir + "\\" + geoDataBaseName + "\\transitsStops", "access", expression,"PYTHON_9.3",codeblock)


'''
There are two groups of datasets: Parcels and TransitStops.
Within TransitStops datasets there are three smaller datasets: transitStopsAccessLow,transitStopsAccessMedium and transitStopsAccessHigh

'''

def promptForFoldersForMetro():
    print("Please select the directory containing the metro .ZIP files to be processed:")
    Tk().withdraw() #prevents Tk window from showing up unnecessarily
    file_directory = askdirectory() #opens directory selection dialog
    os.chdir(homedir)
    arcpy.env.workspace = homedir
    metro_counties = os.listdir(file_directory)
    return metro_counties

if __name__ == '__main__':
    homedir =  os.getcwd()
    homePath = homedir + "\\"
    dataPath = homePath + "data\\"
    countyFolderList = promptForFoldersForMetro()
    countydir = "06041" #countyFolderList[0] # single county test

    transitdir = homedir + "\\transit"
    transitdata = "GGBRIDGE_transit_stop.shp"
    transitLayer = "transitstops_lyr"

    geoDataBaseName = "transitdb.gdb"
    '''
    arcpy.CreateFileGDB_management(dataPath + countydir, geoDataBaseName)

    # addTransitAccess(transitdir,countydir,transitdata,geoDataBaseName, addfield, transitstops_lyr):
    addTransitAccess(transitdir,countydir,transitdata,geoDataBaseName,False,transitLayer)
    newgdbfiles = features2gdb(countyFolderList, dataPath + countydir, geoDataBaseName)
    addTransitPotential(countydir,newgdbfiles,geoDataBaseName) # sets all parcel TransitPotential values to default value of 0
    '''
    method1 = True
    if method1:
        splitTransitStopsData(transitdata,transitLayer,countydir)

    '''
    # Access Low
    bufferTransitStops_HALF("transitStopsAccessLow","transitbuffered", geoDataBaseName)
    scoreparcels("parcels","transitbuffered", "transitPotential", geoDataBaseName,False,0) # Give overlaps parcels score 1
    bufferTransitStops_QUARTER("transitStopsAccessLow","transitbuffered", geoDataBaseName)
    scoreparcels("parcels","transitbuffered", "transitPotential", geoDataBaseName,True,0) # Give overlaps parcels score 2
    # Access Medium
    bufferTransitStops_HALF("transitStopsAccessMedium","transitbuffered", geoDataBaseName)
    scoreparcels("parcels","transitbuffered", "transitPotential", geoDataBaseName,False,1) # Give overlaps parcels score 3
    bufferTransitStops_QUARTER("transitStopsAccessMedium","transitbuffered", geoDataBaseName)
    scoreparcels("parcels","transitbuffered", "transitPotential", geoDataBaseName,True,1) # Give overlaps parcels score 4
    # Access High
    bufferTransitStops_HALF("transitStopsAccessHigh","transitbuffered", geoDataBaseName)
    scoreparcels("parcels","transitbuffered", "transitPotential", geoDataBaseName,False,2) # Give overlaps parcels score 5
    bufferTransitStops_QUARTER("transitStopsAccessHigh","transitbuffered", geoDataBaseName)
    scoreparcels("parcels","transitbuffered", "transitPotential", geoDataBaseName,True,2) # Give overlaps parcels score 6
    '''

