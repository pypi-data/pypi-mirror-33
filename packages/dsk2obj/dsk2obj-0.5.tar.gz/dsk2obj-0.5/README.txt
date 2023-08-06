----------------------------------------     dsk2obj     ----------------------------------------

this package (alpha version) consists on three files:

   - objloader2, first generates the .obj file to be displayed later from a .bds (dsk kernel)
	         the input filename.bds and output filename.obj have to be introduced.
		 At the end of the script you can find glColor4f to select the color of the
		 vertex composing the mesh. Note that to achieved improved efficiency when 
		 displaying the .obj generated file, a wireframe model is displayed.

   - objloader2axis, similarly to the first script, it loads the XYZ axis to be displayed
		     together with the generated .obj model. The inputs of this function are:
		     
			- filename; xaxis.obj (yaxis.obj for Y axis and zaxis.obj for zaxis)
			- R, G, B; the RGB color code in percentaje for the axis (example: 1.0, 0.0, 0.0)
			- X0, Y0, Z0; the position of the origin of coordinates for the displayed ref frame
			- factor, factor multiplying the size of the displayed ref frame accounting fot model size 

   - objloadercall2, this is the main function, the visualization control variables are set at
		     at the beginning using OpenGL package modules. Then the Object and the set 
		     of Axis are loaded calling to the previous two scripts. Finally the scene
		     loop is created with the camara control options and the scene rendering. 