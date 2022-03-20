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

    # blade_generator.py is a module that allows a user to automatically generate propeller geometries (currently only for the Mavic Pro blade)
	
    def make_MavicPro(self):
        
        # This is the function that needs to be ran from FreeCAD in order to generate Mavic Pro compatible blades.
        # Here are instructions for running this function:
        # 1. Open FreeCAD and go to Macros -> Macros... in the navigation bar
        # 2. Under User Macros, select the elipses (...) and navigate to CAD_generation/Macros
        # 3. Run blade_generator_import.py
        # 4. Copy a reference geometry file from the CAD_Templates folder to a location of your choosing and rename it
        # 5. Open the newly renamed FreeCAD file
        # 6. Import the blade generator tool by typing the following code into the Python console in FreeCAD:
        #    import blade_generator
        # 7. Run the function by typing:
        #    blade_generator.make_MavicPro('MH114','blade_geometry_retwist')
        # Note, the foil type (MH114 in the above example) can be any foil saved in the Air_Foils folder and the
        # geometry file (blade_geometry_retwist in the above example) can be the name of any file in the Blade_Geometry file.
        
        # This value is  specific to the Mavic Pro blade
        # span_length = 105 #mm
        #for i in range(2):
            
            # if i == 0:
            # # Change this value depending on which type of blade you want to spit out
            #     self.left_or_right = -1 # Left = -1, Right = 1
            # else:
        #self.left_or_right = 1
            
        pathName = str(pathlib.Path(__file__).parent.absolute())
        
        # Get the foil shape from the foil folder
        #Air_foil_raw = np.genfromtxt(pathName+'/Air_Foils/' + foil_type + '.csv', delimiter=',')
        Air_foil_raw = wt.get_foil(self.foil_type)
        # This file contains pertinant geometric data for creating the 3-D CAD
        #export_data = np.genfromtxt(pathName+'/Blade_Geometry/' +self.geo_file_name + '.csv', delimiter=',')
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
        y_trans_array = export_data[:,6] # Dihedral array
        chord_rotation_perc = export_data[:,5] 
        
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

        # # Make all the cuts for either left or right hand blades    
        # if self.left_or_right == -1: # Left Side
            
        #     # Loft all the sketches together into a solid blade
        #     Loft_L = wt.add_loft(sketch_list)   
            
            
            
        # else: # Right Side
            
        #     # Loft all the sketches together into a solid blade
        My_Loft = wt.add_loft(sketch_list) 

        FreeCAD.activeDocument().recompute()

    def __getstate__(self):
        return None

    def __setstate__(self, state):
        return None
