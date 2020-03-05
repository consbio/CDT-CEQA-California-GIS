########################################################################################################################
# File name: arc_objects_get_symbology_from_lyr.py
# Author: Mike Gough
# Date created: 09/28/2018
# Date last modified: 10/17/2018
# Python Version: 2.7
# Description:
# Uses ArcObjects to extract the symbology out of a .lyr file for the following symbology types:
# Vector: Single symbol, unique values, or graduated colors
# Raster: Unique values, classified, stretched, or discrete.
# Returns results in JSON format.
########################################################################################################################

from comtypes.client import CreateObject
import comtypes.gen.esriCarto as esriCarto
import comtypes.gen.esriDisplay as esriDisplay
import json
import glob
import os

# Test: Points
# inputFile = "../lyr/populated_places_single_symbol.lyr"
# inputFile = "../lyr/populated_places_unique_values.lyr"
# inputFile = "../lyr/populated_places_graduated_colors.lyr"
# inputFile = "../lyr/populated_places_graduated_symbols.lyr"

# Test: Lines
# inputFile = "../lyr/roads_single_symbol.lyr"
# inputFile = "../lyr/roads_unique_values.lyr"
# inputFile = "../lyr/roads_graduated_colors.lyr"

# Test: Polygons
# inputFile = "../lyr/counties_single_symbol.lyr"
# inputFile = "../lyr/counties_unique_values.lyr"
# inputFile = "../lyr/counties_graduated_colors.lyr"

# Test: Raster
# inputFile = "../lyr/raster_unique_values.lyr"
# inputFile = "../lyr/raster_classified.lyr"
# inputFile = "../lyr/raster_stretched.lyr"
# inputFile = "../lyr/raster_discrete_color.lyr"

inputDir = r"P:\Projects3\CDT-CEQA_California_2019_mike_gough\Tasks\CEQA_Parcel_Exemptions\Data\Layer_files\For_Tile_Packages"
outputDir = r"P:\Projects3\CDT-CEQA_California_2019_mike_gough\Tasks\CEQA_Parcel_Exemptions\Data\Tile_Packages\Legends"

def main(lyrFile, outputFile):

    # Create a new comtypes POINTER object where LayerFile is the CoClass to be instantiated and
    # ILayerFile is the interface that is assigned.
    layerFile = CreateObject(esriCarto.LayerFile, interface=esriCarto.ILayerFile)

    # Open the .lyr file passed in to the main function.
    layerFile.Open(lyrFile)

    # Create a layer object by subclassing the Layer Abstract class of the LayerFile object.
    # ILayer is the interface that is assigned.
    layer = layerFile.Layer

    # Cast the layer object to the ILayerEffects interface of the DisplayLayer Abstract class.
    layerEffects = CType(layer, interface=esriCarto.ILayerEffects)

    symbology = dict()
    symbology["transparency"] = layerEffects.Transparency

    # Identify Vector by casting the layer object with the ILayer interface to the IGeoFeature interface
    if CType(layer, interface=esriCarto.IGeoFeatureLayer):

        layerObject = CType(layer, interface=esriCarto.IGeoFeatureLayer)
        renderObject = CType(layerObject.Renderer, interface=esriCarto.IFeatureRenderer)

        # Vector Renderers
        if CType(renderObject, interface=esriCarto.ISimpleRenderer):
            symbology["type"] = "Single Symbol"
            renderer = CType(renderObject, esriCarto.ISimpleRenderer)
            # Determine SymbolType (Point, Line, or Polygon)
            symbolType = getSymbolType(renderer.Symbol)
            symbol = CType(renderer.Symbol, symbolType)
            color = CType(symbol.Color, esriDisplay.IRgbColor)
            symbology["rgb"] = [color.Red, color.Green, color.Blue]

        elif CType(renderObject, interface=esriCarto.IUniqueValueRenderer):
            symbology["type"] = "Unique Values"
            symbology["values"] = []
            renderer = CType(renderObject, interface=esriCarto.IUniqueValueRenderer)
            # Determine SymbolType (Point, Line, or Polygon)
            defaultLabel = renderer.DefaultLabel
            symbolType = getSymbolType(renderer.DefaultSymbol)
            symbol = CType(renderer.DefaultSymbol, symbolType)
            color = CType(symbol.Color, esriDisplay.IColor)
            rgbColor = CreateObject(esriDisplay.RgbColor, interface=esriDisplay.IRgbColor)
            rgbColor.RGB = color.RGB
            rgb = [rgbColor.Red, rgbColor.Green, rgbColor.Blue]
            # Field used for Symbology:
            symbology["field"] = renderer.Field(0)
            # If <all other values> is being used.
            if renderer.UseDefaultSymbol:
                symbology["values"].append({"value": defaultLabel, "rgb": rgb})

            for i in range(renderer.valueCount):
                sVal = renderer.Value(i)
                label = renderer.Label(sVal)
                symbol = CType(renderer.Symbol(sVal), symbolType)
                color = CType(symbol.Color, esriDisplay.IColor)
                rgbColor = CreateObject(esriDisplay.RgbColor, interface=esriDisplay.IRgbColor)
                rgbColor.RGB = color.RGB
                rgb = [rgbColor.Red, rgbColor.Green, rgbColor.Blue]
                symbology["values"].append({"value": sVal, "label": label, "rgb": rgb})

        elif CType(renderObject, interface=esriCarto.IClassBreaksRenderer):
            symbology["type"] = "Classified"
            symbology["classes"] = []
            renderer = CType(renderObject, interface=esriCarto.IClassBreaksRenderer)
            # Field used for Symbology:
            symbology["field"] = renderer.Field
            # Determine SymbolType (Point, Line, or Polygon)
            symbolType = getSymbolType(renderer.Symbol(0))
            minBreak = renderer.MinimumBreak

            for i in range(renderer.BreakCount):
                symbol = CType(renderer.Symbol(i), symbolType)
                color = CType(symbol.Color, esriDisplay.IColor)
                rgbColor = CreateObject(esriDisplay.RgbColor, interface=esriDisplay.IRgbColor)
                rgbColor.RGB = color.RGB
                rgb = [rgbColor.Red, rgbColor.Green, rgbColor.Blue]
                if hasattr(symbol, "Size"):
                    symbology["classes"].append({"min": minBreak, "max": renderer.Break(i), "size": symbol.Size, "rgb": rgb})
                else:
                    symbology["classes"].append({"min": minBreak, "max": renderer.Break(i), "rgb": rgb})
                minBreak = renderer.Break(i)
        else:
            raise Exception("Not a valid render type")

    # Identify Raster by casting the layer object with the ILayer interface to the IRasterLayer interface
    elif CType(layer, interface=esriCarto.IRasterLayer):
        layerObject = CType(layer, interface=esriCarto.IRasterLayer)
        renderObject = CType(layerObject.Renderer, interface=esriCarto.IRasterRenderer)

        # Raster Renderers
        if CType(renderObject, interface=esriCarto.IRasterUniqueValueRenderer):
            symbology["type"] = "Raster Unique Values"
            symbology["values"] = []
            renderer = CType(renderObject, interface=esriCarto.IRasterUniqueValueRenderer)
            # Field used for Symbology:
            symbology["field"] = renderer.Field
            defaultLabel = renderer.DefaultLabel
            symbolType = getSymbolType(renderer.DefaultSymbol)
            symbol = CType(renderer.DefaultSymbol, symbolType)
            color = CType(symbol.Color, esriDisplay.IColor)
            rgbColor = CreateObject(esriDisplay.RgbColor, interface=esriDisplay.IRgbColor)
            rgbColor.RGB = color.RGB
            rgb = [rgbColor.Red, rgbColor.Green, rgbColor.Blue]
            if renderer.UseDefaultSymbol:
                symbology["values"].append({"value": defaultLabel, "rgb": rgb})
            numberOfClasses = renderer.ClassCount(0)

            for i in range(numberOfClasses):
                # Value at class index i
                # Remove int cast
                sVal = renderer.Value(0, i, 0)
                label = renderer.Label(0, i)
                symbol = CType(renderer.Symbol(0, i), symbolType)
                color = CType(symbol.Color, esriDisplay.IColor)
                rgbColor = CreateObject(esriDisplay.RgbColor, interface=esriDisplay.IRgbColor)
                rgbColor.RGB = color.RGB
                rgb = [rgbColor.Red, rgbColor.Green, rgbColor.Blue]
                symbology["values"].append({"value": sVal, "label": label, "rgb": rgb})

        elif CType(renderObject, interface=esriCarto.IRasterClassifyColorRampRenderer):
            symbology["type"] = "Raster Classified"
            symbology["classes"] = []
            renderer = CType(renderObject, interface=esriCarto.IRasterClassifyColorRampRenderer)
            # Field used for Symbology:
            symbology["field"] = renderer.ClassField
            symbolType = getSymbolType(renderer.Symbol(0))

            for i in range(renderer.ClassCount):
                symbol = CType(renderer.Symbol(i), symbolType)
                color = CType(symbol.Color, esriDisplay.IColor)
                rgbColor = CreateObject(esriDisplay.RgbColor, interface=esriDisplay.IRgbColor)
                rgbColor.RGB = color.RGB
                rgb = [rgbColor.Red, rgbColor.Green, rgbColor.Blue]
                symbology["classes"].append({"min": renderer.Break(i), "max": renderer.Break(i + 1), "rgb": rgb})

        elif CType(renderObject, interface=esriCarto.IRasterStretchColorRampRenderer):
            symbology["type"] = "Raster Stretched"
            symbology["rgb"] = []
            renderer = CType(renderObject, interface=esriCarto.IRasterStretchColorRampRenderer)
            colorRamp = renderer.ColorRamp
            colorRamp.Size = 20
            colorRamp.CreateRamp()
            # Option for fetching color scheme name
            # print renderer.ColorScheme
            symbology["labels"] = [renderer.LabelLow, renderer.LabelMedium, renderer.LabelHigh]

            for i in range(colorRamp.Size):
                color = CType(colorRamp.Color(i), esriDisplay.IColor)
                rgbColor = CreateObject(esriDisplay.RgbColor, interface=esriDisplay.IRgbColor)
                rgbColor.RGB = color.RGB
                rgb = [rgbColor.Red, rgbColor.Green, rgbColor.Blue]
                symbology["rgb"].append(rgb)

        elif CType(renderObject, interface=esriCarto.IRasterDiscreteColorRenderer):
            # Note: Doesn't seem to work with the color schemes having the boxes.
            symbology["type"] = "Raster Discrete Color"
            symbology["rgb"] = []
            renderer = CType(renderObject, interface=esriCarto.IRasterDiscreteColorRenderer)
            numColors = renderer.NumColors
            rendererColorRamp = CType(renderObject, interface=esriCarto.IRasterRendererColorRamp)
            colorRamp = rendererColorRamp.ColorRamp
            colorRamp.Size = numColors
            colorRamp.CreateRamp()

            for i in range(numColors):
                color = CType(colorRamp.Color(i), esriDisplay.IColor)
                rgbColor = CreateObject(esriDisplay.RgbColor, interface=esriDisplay.IRgbColor)
                rgbColor.RGB = color.RGB
                rgb = [rgbColor.Red, rgbColor.Green, rgbColor.Blue]
                symbology["rgb"].append(rgb)

        else:
            raise Exception("Not a valid render type")

    else:
        raise Exception("Not a valid layer type")

    jsonDump = json.dumps(symbology, sort_keys=False, indent=2)
    print(jsonDump)

    with open(outputFile, 'w') as output:
        output.write(jsonDump)


def CType(obj, interface):
    """Casts obj to interface and returns comtypes POINTER or None if the interface is not supported"""
    try:
        newobj = obj.QueryInterface(interface)
        return newobj
    except:
        return None


def getSymbolType(mySymbol):

    if CType(mySymbol, esriDisplay.ILineSymbol):
        mySymbolType = esriDisplay.ILineSymbol

    elif CType(mySymbol, esriDisplay.IFillSymbol):
        mySymbolType = esriDisplay.IFillSymbol

    elif CType(mySymbol, esriDisplay.IMarkerSymbol):
        mySymbolType = esriDisplay.IMarkerSymbol

    else:
        raise Exception("Not a valid symbol type")

    return mySymbolType


if __name__ == "__main__":

    for inputLyrFile in glob.glob(inputDir + "/*2107*lyr"):
        inputLyrBasename = os.path.basename(inputLyrFile).split(".")[0]
        outputJSONfile = outputDir + os.sep + inputLyrBasename + ".json"
        main(inputLyrFile, outputJSONfile)
