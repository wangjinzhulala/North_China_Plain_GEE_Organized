# ---------------------------------------------------------------------------
# export_netCDF_slice.py
# Created on: 2011-06-02 10:18:49.00000
# Description: This scipt will create a TIFF raster from a NetCDF layer, and
# save each band of that TIFF as a seperate TIF raster (for each time slcie in a netcdf file) 
# ---------------------------------------------------------------------------

# Import modules
import arcpy, os

#Inputs
Input_NetCDF_layer = arcpy.GetParameterAsText(0)
Output_Folder = arcpy.GetParameterAsText(1)

Input_Name = Input_NetCDF_layer
Output_Raster = Output_Folder + os.sep + "NetCDF_Raster.tif"

#Copy the NetCDF layer as a TIF file. 
arcpy.CopyRaster_management(Input_Name, Output_Raster)
arcpy.AddMessage(Output_Raster + " " + "created from NetCDF layer")

#Reading number of band information from saved TIF
bandcount = arcpy.GetRasterProperties_management (Output_Raster, "BANDCOUNT") 
resultValue = bandcount.getOutput(0)

count = 1
arcpy.AddMessage("Exporting individual bands from" + Output_Raster)

#Loop through the bands and copy bands as a seperate TIF file.
while count <= int(resultValue):
    Input_Raster_Name = Output_Raster + os.sep+ "Band_" + str(count)
    Output_Band = Output_Folder + os.sep + "Band_" + str(count) +".tif"
    arcpy.CopyRaster_management(Input_Raster_Name, Output_Band)
    arcpy.AddMessage("Band_" + str(count).zfill(2) +".tif" + " " "exported" + " " + "successfully")
    count +=1

# The following will delete the TIFF file that was created by CopyRaster tool.  
arcpy.Delete_management(Output_Raster,"#")
    
arcpy.AddMessage("Tool Executed Successfully")