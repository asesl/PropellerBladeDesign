# Import all the necessary libraries
import Part
import numpy as np
import math
import FreeCAD
import pathlib
import propeller_generator.wingtools as wt

class PropellerBlade(object):
    def __init__(self, foil_type, geo_file_name, span_length, left_or_right, doc):
        self.foil_type = foil_type
        self.geo_file_name = geo_file_name
        self.span_length = span_length
        self.left_or_right = left_or_right
	
    def make_PropellerBlade(self):
        
        # This is the function that needs to be ran from FreeCAD in order to generate Mavic Pro compatible blades.
  
        pathName = str(pathlib.Path(__file__).parent.absolute())
        
        # Get the foil shape from the foil folder
        Air_foil_raw = wt.get_foil(self.foil_type)
        # This file contains pertinant geometric data for creating the 3-D CAD
        export_data = np.genfromtxt(self.geo_file_name, delimiter=',')

        # Orient the foil for either a left or right hand blade
        Air_foil = np.zeros([len(Air_foil_raw),2])
        Air_foil[:,0] = Air_foil_raw[:,0]*self.left_or_right
        Air_foil[:,1] = Air_foil_raw[:,1]*-1
        
        # Create local versions of geometric data
        # This code also orients it for either left or right hand blades
        z_array = export_data[:,0]*self.span_length # Span array
        chord = export_data[:,1]
        twist_array =   export_data[:,2]*self.left_or_right
        x_trans_array = export_data[:,3]*self.left_or_right # Sweep array
        y_trans_array = export_data[:,4] # Dihedral array
        
        PlaneObj = wt.add_planes(len(z_array),self.span_length) # Create the planes within the open FreeCAD part.
        sketch_list = [] # Create empty array of sketches that will eventually get lofted
        
        # This for loop is where the magic happens... it creates the correct foil, orients it and puts it in the right position
        for i in range(len(twist_array)):
            
            foilforSketch = wt.orient_foil(Air_foil,chord[i],x_trans_array[i],y_trans_array[i],twist_array[i],x_trans_array[i],y_trans_array[i])
        
            sketch = wt.add_foil_sketch(PlaneObj[i],foilforSketch,1)
            z_dist = PlaneObj[i].Placement.Base.z
            sketch.Placement.Base.z = z_array[i]
            sketch_list.append(sketch)   
            
            sketch.ViewObject.Visibility = 0
            
        # Loft all the sketches together into a solid blade
        My_Loft = wt.add_loft(sketch_list) 

        FreeCAD.activeDocument().recompute()

    def __getstate__(self):
        return None

    def __setstate__(self, state):
        return None
