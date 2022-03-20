# wingtools.py
# This module contains functions that leverage the FreeCAD API to do some
# fundamental design work related to creating wings or propeller blades.
# These should be leveraged in order to create macros, scripts and functions
# that generate parameterized designs specific to a use case.
#
# Author: Austin Eslinger

import Part
import numpy as np
import math
import FreeCAD
import pathlib
import Draft

def add_planes(num_planes,seperation):

    # Generate evenly spaced planes in the span wise direction
    # Note, all code needs to based on a fundamental assumption
    # that the spanwise direction is in the positive Z axis
	
	plane_list = []
	
	for i in range(num_planes):
	
		plane_dist = (i)*seperation		
		PlaneCurr = Part.makePlane(100,100,FreeCAD.Base.Vector(-50,-50,plane_dist),FreeCAD.Base.Vector(0,0,1))
		plane_list.append(PlaneCurr)
		
	return plane_list

def orient_foil(foil_array, chord, x_disp, y_disp, twist_deg, x_center, y_center):

    # Calculate 2-D foil positions for a shape. This function 
    # determines rotational and translational position on an
    # airfoil.

    foil_sized = foil_array*chord

    foil_twisted = np.zeros((len(foil_array),2))
    foil_twisted[:,0] = foil_sized[:,0]+ x_disp
    foil_twisted[:,1] = foil_sized[:,1]+ y_disp
		
    theta_delta = math.radians(twist_deg)

    x_final = np.cos(theta_delta)*(foil_twisted[:,0] -x_center)-math.sin(theta_delta)*(foil_twisted[:,1] -y_center)+x_center
    y_final = np.sin(theta_delta)*(foil_twisted[:,0] -x_center)+math.cos(theta_delta)*(foil_twisted[:,1] -y_center)+y_center
    foil_return = np.zeros((len(x_final),2))
    foil_return[:,0] = x_final
    foil_return[:,1] = y_final
		
    return foil_return

def add_foil_sketch(PlaneObj,foil_array,chord):

    # This function places the the foil geometry into FreeCAD

    SketchCurr = FreeCAD.ActiveDocument.addObject('Sketcher::SketchObject','foil_section')
    for i in range(len(foil_array)):
			
        if i == len(foil_array)-1:
            ii = -1	
        else:
            ii = i	

        V1 = FreeCAD.Vector(chord*foil_array[i][0],chord*foil_array[i][1],0)  
        V2 = FreeCAD.Vector(chord*foil_array[ii+1][0],chord*foil_array[ii+1][1],0)
        SketchCurr.addGeometry(Part.LineSegment(V1,V2),False)
        
    return SketchCurr

def add_loft(sketch_list):

    # Loft all spanwise foil sketches together to create a solid
    
    loft_obj = FreeCAD.ActiveDocument.addObject('Part::Loft','Loft')
    loft_obj.Sections = sketch_list
    loft_obj.Solid = True
    loft_obj.Ruled = True
    loft_obj.Closed = False
    
    return loft_obj

def get_foil(foil_type):

    # Pull airfoils from the database based on its name

    pathName = str(pathlib.Path(__file__).parent.absolute())
    raw_foil = np.genfromtxt(pathName+'/Air_Foils/' + foil_type + '.csv', delimiter=',')

    return raw_foil