import numpy as np
import math as math
import datetime as datetime
'''TODO:
Z raise depends on layer hight
Z calc depends on tube dia
'''


'''
========DESCRIPTION========
# setting rotation of the z-axis
# setting the y-axis angle = alpha
# winding to full length
# setting the y-axis angle = 0
# rotation of z-axis with calculated offset
# rounding off the offset + calculation of the number of offsets for 1 layer
# setting the y-axis angle = -alpha
# move to home position
'''

#========input_start========
E_base_speed = 16000 #base winding speed
E_slow_speed = 4500 #slow wnding speed
fast_speed = 20000 #fast wnding speed
x0 = 1780 # tube length 1780 mm
flag = 1 # stop after each layer | 0 for disable
array = np.array([75,70,65,60,55,50,45,40,45,80,80,80,80,80,80],int) # winding angles massive in deg
all_time = 0
array2 = np.radians(array)  # winding angles massive in radians
w = 6 # width of rowing
d0 = 60 # tube dia
y0 = 83 # axis 4(y) zero angle
Z = 38 # Z for dia
Ztmp = Z # for time calculation
wall_thickness = 3 #thinkness in mm
fiber_thickness = 0.2
E_steps_for_360 = 400 				
#========input_end========

#========precalc_start========
#l = np.pi*d0 # length of perimeter  #!!! Check was uncommented
# deg_l = l/360 # length of 1 deg 	 #!!! Check was uncommented

layers = int(np.round(wall_thickness/fiber_thickness)) # # of layers calc
#layers = len(array) #length of layres array
#========precalc_end========

#========funcs_start========
def axis3(Z,V):							#!!! Check (was deleted)
	my_file.write("G1 Z"+str(Z)+" F"+str(V)+" ;set axis 3(z) to specified angle"+"\n") 	#!!! Check (was deleted)

def axis2_and_axis1(X,E,V):
	my_file.write("G1 X"+str(X)+" E"+str(E)+" F"+str(V)+"\n")

def axis4(axis4_angle,V):
	my_file.write("G1 Y"+str(axis4_angle)+" F"+str(V)+" ;set axis 4(Y) to specified angle"+"\n")

def axis1(axis1_angle,V):
	my_file.write("G1 E"+str(axis1_angle)+" F"+str(V)+" ;set axis 1(E) to specified angle"+"\n")

def axis4_and_axis1(axis4_angle,axis1_angle,V):
	my_file.write("G1 Y"+str(axis4_angle)+" E"+str(axis1_angle)+" F"+str(V)+" ;set axis 4(Y) and axis 1(E) to specified angle"+"\n")

def reset_axis1():
	my_file.write("G92 E0 ;set axis1(E) to zero"+"\n")

def initial_gcode():
	my_file.write(";Initial gcode\n")
	my_file.write("G92 E0"+"\n")#set axis1(E) to zero
	my_file.write("G28 ;Home all axes\n")
	my_file.write("G1 Y"+str(y0)+" F20000"+"\n") #set axis 4(y) to calibrated zero
	my_file.write("G1 Z"+str(Z)+" F10000"+"\n") #set axis 3(z) to calibrated zero
	my_file.write("G1 E"+str(E_steps_for_360)+" F8000"+"\n") #full revolve axis 1(E)
	my_file.write("G92 E0"+"\n")#set axis1(E) to zero
	my_file.write(";Initial gcode\n")

def final_gcode():
	my_file.write(";Final gcode\n")
	my_file.write("G28 ;Home all axes\n")
	my_file.write(";Final gcode\n")	

def full_layer(layer, curr_dia, fiber_thickness, alpha_rad, x_base, alpha_deg):
	y_positive = y0 + (90-alpha_deg) # calculating positive angle of axis 4(y)
	y_negative = y0 - (90-alpha_deg) # calculating negative angle of axis 4(y)

	perimeter = np.pi*(curr_dia+(2*fiber_thickness*(layer-1))) # length of current layer perimeter
	

	E_step_length = perimeter/E_steps_for_360 #instead if degree calculation -> Estep to avoid an accumulation of computational error 

	E = x_base / E_step_length * math.tan(alpha_rad) # degrees to receive length |degrees calculated here|

	E_ceil = math.ceil(E) # return degrees for E axis for full length

	
	# Recalculating length
	x_pre_recalc = E_ceil*E_step_length/math.tan(alpha_rad) # precalc

	x_recalc = int(np.round(x_pre_recalc,0)) # return mm for x axis

	##### ERRROR FIXED #####
	fibers = int(np.round(perimeter/(w/math.cos(alpha_rad)))) # perimeter/width of fiber at 'alpha' angle
	##### ERRROR FIXED #####
	#ceil_fibers = fibers
	floor_fibers = fibers
	
	#avoid fractional E steps caused by devision 400 to # of fibers 
	#while E_steps_for_360 % ceil_fibers != 0:
	#	ceil_fibers += 1

	print("floor_fibers before: %.2f" % floor_fibers)

	# TODO:Sieve of Eratosthenes, Factorization | 
	# 1. List of prime numbers
	# 2. Filter prime numbers which is a divisor of E_steps_for_360
	# 3. powers up 1 to n in for and check if they a divisor of E_steps_for_360
	# 4. multiply in pairs, filter them
	while E_steps_for_360 % floor_fibers != 0:  # floor_fibers this number must be a divisor of the E_steps_for_360 = 400 steps 
		floor_fibers -= 1

	# calculating number of fibers #
	print("floor_fibers: %.2f" % floor_fibers)

	E_offset = (E_ceil * 2 + 200) % E_steps_for_360 # offset between start E angle(0deg) and final winding angle after x = xmax -> x = x0 
	E_TMP = E_steps_for_360 - E_offset # diff between start & end E position + full revolve cause i can not rotate backwards
	offset = int((E_steps_for_360/floor_fibers+E_TMP)%(E_steps_for_360)) # calculating [offset] for next fiber #
	
	#E_ceil+200+E_ceil

	#'question: why layer 2 is doubled in width?'
	print("perimeter:    %.2fmm" % perimeter)
	print("E:            %.2f" % E)
	print("E_ceil:       %d" % E_ceil)
	print("x_pre_recalc: %f" % x_pre_recalc)
	print("x_recalc:     %d" % x_recalc)
	print("Fibers:       %d" % fibers)
	print('E_ceil:       %d' % E_ceil)
	print('E_offset:     %d' % E_offset)
	print('E_TMP:        %d' % E_TMP)
	print("Offset:       %d" % offset)
	
	my_file.write(";layer"+str(layer)+"\n")

	# axis X speed recalс to not exceed E max_speed
	adapted_speed = math.floor(np.around(E_base_speed/np.tan(array2[layer-1]),-2))
	if adapted_speed > 14000:
		adapted_speed = 14000

	if adapted_speed > 6000:
			sides_speed = 6000
	else:
		sides_speed = adapted_speed
	global all_time
	all_time = all_time + layers*2*x0/adapted_speed

	axis4(y_positive,fast_speed)
	for counter in range(1,floor_fibers+1):
		#first spiral
		my_file.write(";fiber"+str(counter)+"\n")
		my_file.write("M117 Layer: "+str(layer)+" Fiber: "+str(counter)+"\n")
		axis2_and_axis1(x_recalc,E_ceil,adapted_speed)
		reset_axis1()

		# axis4(y0,fast_speed)
		# axis1(180,E_base_speed)
		# #backward spiral
		# axis4(y_negative,fast_speed)
		axis4_and_axis1(y_negative,200,sides_speed)

		reset_axis1()
		axis2_and_axis1(0,E_ceil,adapted_speed)
		reset_axis1()

		# axis4(y0,fast_speed)
		# axis1(offset,E_base_speed)
		# axis4(y_positive,fast_speed)
		tmpf = int(math.floor(np.around(0.5*E_steps_for_360/offset*sides_speed,-2)))
		if tmpf>6000:
			tmpf=6000
		axis4_and_axis1(y_positive,offset,tmpf)

		reset_axis1() 
#========funcs_end========

#check if calculated layers = array.length
if layers != len(array):
	print("Array length %d not equal array of angles length %d" % (len(array), layers))
else:
	my_file = open("winding.gcode", "w")
	
	initial_gcode()
	
	for counter2 in range(1,layers+1):
		full_layer(counter2, d0, fiber_thickness, array2[counter2-1], x0, array[counter2-1])
		Ztmp=Ztmp-(fiber_thickness) ## !!! Check (was deleted)
		axis3(np.round(Ztmp,1),fast_speed) ## !!! Check (was deleted)
		if flag:
			my_file.write("M0 ;wait for click after each layer\n")
		print("=== LAYER: %d \n=== Angle %d deg" % (counter2, array[counter2-1]))
	
	
	final_gcode() 
	
	my_file.close()
	
	print("done")
	print("# of generated layers = %d" % layers)
	
	# time calculation for each layer
	# time calculation
	print("Easy time calculaltion:")
	print(datetime.timedelta(hours=all_time/60))
	print("time: {:.0f} min".format(all_time))	
	print("time: {:.1f} h \n".format(all_time/60))
	
	print("E axis speed:")
	for i in range(0,layers):
		recalc_true_speed=E_base_speed/np.tan(array2[i])
		print("{:.0f} on layer %d".format(E_base_speed/np.tan(array2[i])) % i)
		all_time = all_time + 20*2*x0/recalc_true_speed
	
	print("\nTime recalculaltion based on recalc_true_speed:")
	all_time_h = all_time/60
	print("time: %d min" % all_time)
	print("time: {:.1f}".format(all_time_h))
