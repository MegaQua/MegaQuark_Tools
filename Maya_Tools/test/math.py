ONCE: rad2deg = 180/PI_VALUE
ONCE: deg2rad = PI_VALUE/180


OC11 = TC44 ^ 1  # record 
OC14 = TC45 ^ 1  # reverse 
OC13 = TC46 ^ 1  # advance
OC10 = TC47 ^ 1  # play 
OC16 = TC48 ^ 1  # goto head
OC17 = TC50 ^ 1  # set tail
OC15 = TC52 ^ 1  # set head
OC26 = TC55 ^ 1  # key platform
OC25 = TC58 ^ 1  # toggle platform
OC28 = TC51 ^ 1  # live mode toggle ( streaming )
OC22 = TC56 ^ 1  # Goto Pos
OC21 = TC57 ^ 1  # Save Pos
OC20 = TC59 ^ 1  # zero offsets
OC35 = TC60 ^ 1  # flight mode
OC19 = TC61 ^ 1  # Roll kill
OC34 = TC67 ^ 1  # Roll kill

Matrix m1                     # temporaries
Matrix m2
Vector v1
Vector v2

ONCE: X=0
ONCE: Y=1
ONCE: Z=2


ONCE: NATIVE = 0
ONCE: INTERSENSE = 1
ONCE: STATUS_CHANGE_THRESH = 15

if (mocap_scheme == NATIVE)
   RotationOrder = X + 4*Y + 16*Z     # roll-yaw-pitch
else     # INTERSENSE
   RotationOrder = X + 4*Y + 16*Z     # roll-pitch-yaw
endif

Matrix mr_result
Matrix mr_tmpX
Matrix mr_tmpY
Matrix mr_tmpZ
Function Create_ordered_rotation_matrix[Rx, Ry, Rz, RotationOrder]
   mr_tmpX = create_rotation_matrix_scaled(Rx, 0, 0, deg2rad)
   mr_tmpY = create_rotation_matrix_scaled(0, Ry, 0, deg2rad)
   mr_tmpZ = create_rotation_matrix_scaled(0, 0, Rz, deg2rad)
   first_index = RotationOrder & 3             #  3 ==    011
   second_index = (RotationOrder & 12) ~> 2    # 12 ==  01100
   third_index = (RotationOrder & 48) ~> 4     # 48 ==0110000
  

   if (first_index == X)
      mr_result = mr_tmpX
   endif
   if (first_index == Y)
      mr_result = mr_tmpY
   endif
   if(first_index == Z)
      mr_result = mr_tmpZ
   endif


   if (second_index == X)
      mr_result = mr_tmpX * mr_result
   endif
   if (second_index == Y)
      mr_result = mr_tmpY * mr_result
   endif
   if (second_index == Z)
      mr_result = mr_tmpZ * mr_result
   endif

   if (third_index == X)
      mr_result = mr_tmpX * mr_result
   endif
   if (third_index == Y)
      mr_result = mr_tmpY * mr_result
   endif
   if (third_index == Z)
      mr_result = mr_tmpZ * mr_result
   endif

Return [mr_result]

ONCE: platform_status_old = 0
ONCE: parent_status_old = 0
ONCE: platform_status = 0
ONCE: parent_status = 0
ONCE: platform_change_counter = 0
ONCE: parent_change_counter = 0

if(TC5 != platform_status_old)
	platform_change_counter = platform_change_counter + 1
else
	platform_change_counter = 0
endif

if(platform_change_counter > STATUS_CHANGE_THRESH)
	platform_status_old = platform_status
	platform_status = TC5
	if(platform_status == 1)
		MM_trigger(3)     
	else
                MM_trigger(4)     
	endif

endif

if(TC26 != parent_status_old)
	parent_change_counter = parent_change_counter + 1
else
	parent_change_counter = 0
endif

if(parent_change_counter > STATUS_CHANGE_THRESH)
	parent_status_old = parent_status
	parent_status = TC26                  # toggle
	if(parent_status == 1)
		MM_trigger(5)     
	else
                MM_trigger(6)     
	endif
   	
endif

trans_scale_x = TC20                            # From MoBu
trans_scale_y = TC21
trans_scale_z = TC22

flight_speed_gain = TC6                         # flight multiplier, from MoBu UI
flight_speed_gain = flight_speed_gain * (TC65 - TC65:m) / (TC65:x - TC65:m)

ONCE: VC6 = 0                                   # zero-out joystick accum
ONCE: VC7 = 0
ONCE: VC8 = 0
ONCE: VC9 = 0                                   # zero out the 'zeroed' mocap position
ONCE: VC10 = 0
ONCE: VC11 = 0
ONCE: VC12 = 0                                  # zero out the 'zeroed' mocap orientation
ONCE: VC13 = 0
ONCE: VC14 = 0

if (platform_status == 1)
   if (TC25 & 1)                                # bitfield of MoBu UI checkboxes; bitwise AND
      include_mocap_rotations = 1
   else
      include_mocap_rotations = 0
   endif
   if (TC25 & 2)
      include_mocap_translations = 1
   else
      include_mocap_translations = 0
   endif
   include_setup_offsets = 0                    # setup offsets already included in platform
else
   if (parent_status == 1) 
      if (TC27 & 1)                             # bitfield of MoBu UI checkboxes; bitwise AND
         include_mocap_rotations = 1
      else
         include_mocap_rotations = 0
      endif
      if (TC27 & 2)
         include_mocap_translations = 1
      else
         include_mocap_translations = 0
      endif
      include_setup_offsets = 0
   else
      include_setup_offsets = 1
      include_mocap_translations = 1
      include_mocap_rotations = 1
   endif
endif


Matrix m_identity
m_identity = create_rotation_matrix(0, 0, 0)

Matrix mr_postrotation_offset         # this is mathematically a prerotation, about camera local axes
Matrix mtr_mocap
Matrix mr_setup_rotation_offset
Matrix mt_joystick_accum
Matrix mt_setup_translation_offset
Matrix mtr_final        # = mt_setup * mt_joystick * mr_setup * mtr_mocap * mr_post

Vector v_current_mocap_trans
Vector v_zeroed_mocap_trans   # where camera was in mocap volume when Zero button was pressed
Vector v_delta_mocap_trans    # (scaled) vector camera has traveled in mocap since Zero button was pressed
Vector v_joystick_delta       # amount to move this frame due to joysticks
Vector v_setup_translation_offset
Vector v_flight_speed_gain

if (include_setup_offsets)
   v_setup_translation_offset = create_vector(TC8, TC9, TC10)               # Setup Trans Offset from MoBu UI
   mt_setup_translation_offset = create_translation_matrix(TC8, TC9, TC10)  # same
   mr_setup_rotation_offset = create_rotation_matrix_scaled(TC17, TC18, TC19, deg2rad)   # from MoBu UI
   mr_postrotation_offset = create_rotation_matrix_scaled(TC14, TC15, TC16, deg2rad)     # from MoBu UI
else
   v_setup_translation_offset = create_vector(0, 0, 0)
   mt_setup_translation_offset = m_identity
   mr_setup_rotation_offset = m_identity
   mr_postrotation_offset = m_identity
endif
mt_joystick_accum = create_translation_matrix(VC6, VC7, VC8)             # initially zero

if (mocap_scheme == NATIVE)
   Tx_mocap = TC31                                  # from mocap NetEC - one horizontal axis
   Ty_mocap = TC32                                  # vertical up
   Tz_mocap = TC33                                  # other horizontal axis
else               # INTERSENSE
   Tx_mocap = TC31 * 100                            # one horizontal axis; convert m to cm
   Tz_mocap = TC32 * 100                            # other horizontal axis
   Ty_mocap = -TC33 * 100                           # vertical down
endif
if (include_mocap_translations)
   v_current_mocap_trans = create_vector(Tx_mocap, Ty_mocap, Tz_mocap)   # in MoBu coordinates
   v_zeroed_mocap_trans = create_vector(VC9, VC10, VC11)                 # were stored when zeroed
   v_delta_mocap_trans = v_current_mocap_trans - v_zeroed_mocap_trans
   v_delta_mocap_trans = create_vector(trans_scale_x * get_x(v_delta_mocap_trans), trans_scale_y * get_y(v_delta_mocap_trans), trans_scale_z * get_z(v_delta_mocap_trans))
else
   v_delta_mocap_trans = create_vector(0,0,0)
endif

if (include_mocap_rotations)
   Rx_mocap = TC34                               # from mocap NetEC - camera forward axis
   Ry_mocap = TC35                            
   Rz_mocap = TC36
   [m1] = Create_ordered_rotation_matrix[Rx_mocap, Ry_mocap, Rz_mocap, RotationOrder]
   if (mocap_scheme == INTERSENSE)
      v1 = get_rotation_angles_YZX_from_rotation_matrix(m1)        # roll-yaw-pitch, order create_rotation_matrix() uses          
      Rx = get_x(v1)              # MoBu roll = intersense roll
      Rz = get_y(v1)              # MoBu pitch = intersense pitch
      Ry = -get_z(v1)             # MoBu yaw = intersense yaw
      m1 = create_rotation_matrix(Rx, Ry, Rz)
   endif
else
   m1 = create_rotation_matrix(0, 0, 0)
endif
mtr_mocap = create_translation_matrix_from_vector(v_delta_mocap_trans) * m1

ONCE: zero_request_old = 0
zero_request = (TC24 + OC20)                  # if either MoBu button or h/w button are 1
if ((zero_request == 1) && (zero_request_old != 1 ))
   VC6 = 0                                    # zero out joystick accumulators
   VC7 = 0
   VC8 = 0

   VC9 = Tx_mocap                      # save current mocap location, subtract from mocap from now on
   VC10 = Ty_mocap
   VC11 = Tz_mocap
endif
zero_request_old = zero_request



ONCE: savepos_request_old = 0
savepos_request = TC3 + OC21
if ((savepos_request == 1) && (savepos_request_old != 1))
   VC15 = OC1                                 # use channels, not variables, to store pos
   VC16 = OC2
   VC17 = OC3
endif
savepos_request_old = savepos_request

ONCE: gotopos_request_old = 0
gotopos_request = TC4 + OC22
if ((gotopos_request == 1) && (gotopos_request_old != 1))
   Vector v_final_desired
   Vector v_joy_accum_desired
   v_final_desired = create_vector(VC15, VC16, VC17)     # the saved position
   v1 = mr_setup_rotation_offset * v_delta_mocap_trans

   v_joy_accum_desired = v_final_desired - v_setup_translation_offset - v1
   VC6 = get_x(v_joy_accum_desired)
   VC7 = get_y(v_joy_accum_desired)
   VC8 = get_z(v_joy_accum_desired)
endif
gotopos_request_old = gotopos_request

ONCE: platform_or_parent_status_old = 0
platform_or_parent_status = parent_status + platform_status
platform_or_parent_status_old = parent_status_old + platform_status_old
if ((platform_or_parent_status >= 1) && (platform_or_parent_status_old < 1))
   saved_zeroed_mocap_tx = VC9
   saved_zeroed_mocap_ty = VC10
   saved_zeroed_mocap_tz = VC11
   VC9  = Tx_mocap                         # Store mocap pos as if they had clicked Zero button; now ...
   VC10 = Ty_mocap                         # ... whether Include Translations is on or off, we are ...
   VC11 = Tz_mocap                         # ... sending (0,0,0) for translation

   saved_joy_accum_tx = VC6
   saved_joy_accum_ty = VC7
   saved_joy_accum_tz = VC8
   VC6 = 0                                 # zero out joystick accumulators
   VC7 = 0
   VC8 = 0

   MM_trigger(1)                           # create log message
endif

if ((platform_or_parent_status == 0) && (platform_or_parent_status_old != 0))
   VC9  = saved_zeroed_mocap_tx
   VC10 = saved_zeroed_mocap_ty
   VC11 = saved_zeroed_mocap_tz
   VC6 = VC6 + saved_joy_accum_tx          # include joy motions accumulated since we went on-platform
   VC7 = VC7 + saved_joy_accum_ty
   VC8 = VC8 + saved_joy_accum_tz

   MM_trigger(2)                           # create log message
endif


ONCE: do_hold = 0
ONCE: streaming_status_old = 0
streaming_status = TC28                                # from MoBu
ONCE: hold_button_old = 0
hold_button = TC49 ^ 1                                 # from vcam hardware

if (streaming_status == 0)
   do_hold = 1
else
   if (streaming_status_old == 0)
      do_hold = 0
   else
      if ((hold_button == 1) && (hold_button_old != 1))
         do_hold = 1 - do_hold                          # toggle
      endif
   endif
endif
OC27 = do_hold
streaming_status_old = streaming_status
hold_button_old = hold_button


mtr_final = mt_setup_translation_offset * mt_joystick_accum * mr_setup_rotation_offset * mtr_mocap * mr_postrotation_offset


v1 = get_rotation_angles_from_rotation_matrix(mtr_final)

thetaX_rad = get_x(v1)
thetaY_rad = get_y(v1)
thetaZ_rad = get_z(v1)

roll_kill = TC1                                   # MoBu is single source of truth for status
if (roll_kill == 1)
   m1 = create_rotation_matrix(0, thetaY_rad, thetaZ_rad)
   v1 = m1 * create_vector(0, 1, 0)               # yHat = transformed (local) Y axis
   v2 = m1 * create_vector(0, 0, 1)               # zHat = transformed (local) Z axis
   thetaX_rad = -atan2(-get_y(v2), get_y(v1))
endif

Vector v_trans_final
v_trans_final = get_translation_from_rotation_matrix(mtr_final)

if (! do_hold)
   OC1 = get_x(v_trans_final)
   OC2 = get_y(v_trans_final)
   OC3 = get_z(v_trans_final)

   OC4 = thetaX_rad * rad2deg
   OC5 = thetaY_rad * rad2deg
   OC6 = thetaZ_rad * rad2deg

   OC7 = get_x(v_trans_final) - TC8
   OC8 = get_y(v_trans_final) - TC9
   OC9 = get_z(v_trans_final) - TC10
endif

v_joystick_delta = create_vector(trans_scale_x*VC3*flight_speed_gain, trans_scale_y*VC4*flight_speed_gain, trans_scale_z*VC5*flight_speed_gain)
flight_mode = TC2                                 # 0: XZ planar mode    1: fly along local axes

m1 = create_rotation_matrix(thetaX_rad, thetaY_rad, thetaZ_rad)
if (flight_mode == 0)
   Vector v_camera_axis
   v_camera_axis = m1 * create_vector(1, 0, 0)   # camera axis is transformed (local) X-axis
   azim_rad = -atan2(get_z(v_camera_axis), get_x(v_camera_axis))   

   x_flight = get_x(v_joystick_delta)             # amount we want to travel along camera axis
   z_flight = get_z(v_joystick_delta)             # amount we want to travel perpendicular to camera axis
   x_global =  (x_flight * cos(azim_rad)) + (z_flight * sin(azim_rad))
   z_global = -(x_flight * sin(azim_rad)) + (z_flight * cos(azim_rad))

   v_joystick_delta = create_vector(x_global, get_y(v_joystick_delta), z_global)
else
   v_joystick_delta = m1 * v_joystick_delta
endif

VC6 = VC6 + get_x(v_joystick_delta)
VC7 = VC7 + get_y(v_joystick_delta)
VC8 = VC8 + get_z(v_joystick_delta)




v1 = create_vector(1, 0, 0)
v2 = mtr_final * v1
final_camera_local_x_x = get_x(v2)
final_camera_local_x_y = get_y(v2)
final_camera_local_x_z = get_z(v2)

v1 = create_vector(0, 1, 0)
v2 = mtr_final * v1
final_camera_local_y_x = get_x(v2)
final_camera_local_y_y = get_y(v2)
final_camera_local_y_z = get_z(v2)

v1 = create_vector(0, 0, 1)
v2 = mtr_final * v1
final_camera_local_z_x = get_x(v2)
final_camera_local_z_y = get_y(v2)
final_camera_local_z_z = get_z(v2)
