help_dict = dict()

# Basic help
#---------------------------------------------------------------------------
help_dict['LBP'] = "Low Battery Protection [V]\n\n \
This is the voltage at which the controller will stop the motor to keep your\n \
battery safe from over-discharge. It should be set by the manufacturer\n \
properly and you don’t need to change it.\n\n \
Example:\n \
   For 13S battery packs, 41V is the default."

help_dict['LC'] = "Current Limit [A]\n\n \
This is the maximum current allowed the flow through the motor. If your motor\n \
is rated at 25A for example, you can set it to 20A to keep it safe. It is not\n \
recommended to set higher current than the nominal. Even set at 25A the peak \n \
current will be higher so better not set more than that."

help_dict['ALC0-9'] = "Assist 0 ÷ Assist 9\n\n \
Those are all possible assist settings (both for pedal assist and throttle\n \
handle using one of those). It is important to mention the Assist 0 current\n \
and speed limits must be set to 1 if you want to be able to use your\n \
throttle handle with PAS0 selected on your LCD. Usually Assist 0 is set\n \
to 0 so you can use your bicycle without assistance if you want. Be careful\n \
setting these levels. If you set the current too low the motor won’t be able\n \
to move the bicycle and it might suffer damage. If you set the first assist\n \
level current too high then the acceleration at start will be significant.\n \
This might damage the internal gears or make you fall of your bicycle.\n\n\
The speed limit sets which speed (% of the maximum speed, set from your LCD)\n \
the motor will reduce its power and just keep that speed instead of\n \
accelerating more."

help_dict['WD'] = "Wheel Diameter [inch] x 2\n\n \
The wheel diameter should match the size of your drive wheel (hence your\n \
bicycle could have two different sized wheels). Setting the diameter to a\n \
smaller size than it really is will increase your speed but also can easily\n \
lead to motor damage.\n\n \
Example:\n \
   If your wheel is 28\" then this should be set to 56."

help_dict['SM'] = "Speed Meter Type\n\n \
This one selects the speed meter used on your bicycle. For BBS kits it is\n \
\"External\". This parameter is set by the manufacturer and if your setup\n \
is not custom then you don’t need to change it.\n\n \
Speed Meter Signals\n\n \
Set how many signals per revolution your sensor generates. If you use the\n \
external sensor with magnet it generates one signal per wheel revolution.\n \
This parameter is set by the manufacturer and if your setup is not custom\n \
then you don’t need to change it. SM is normally set to 1.\n\n \
Example:\n \
   For External and 1 signal per revolution, this should be set to 1"

# Pedal Assist help
#---------------------------------------------------------------------------
help_dict['PT'] = "Pedal Sensor Type\n\n \
This parameter selects the pedal rotation sensor type. It is set by the\n \
manufacturer and should not be changed.\n\n \
Values are:\n \
   0x00=None, 0x01=DH-Sensor-12, 0x02=BB-Sensor-32, 0x03=DoubleSignal-24"

help_dict['DA-PAS'] = "Designated Assist Level\n\n \
You have two type of operation selected with this parameter. First is\n \
“By Display’s Command”. This means that the assist level (the one from\n \
the Basic settings tab) will be selected from your LCD. The second option\n \
is to choose a specific assist level which will be fixed and you will not\n \
be able to change that from the LCD. For this you can select any level\n \
from 0 to 9."

help_dict['SL-PAS'] = "Speed Limit\n\n \
This is the maximum speed at which the motor will provide additional\n \
acceleration. When the speed is reached it will only keep it but won’t\n \
accelerate more. If you set this parameter to \“By Display’s Command\"\n \
you will be able to set the speed from your LCD. Keep in mind that some\n \
LCDs allow you to set speed of 99km/h which is not possible at least with\n \
the current BBS kits. As far as I have tested the maximum speed without\n \
pedaling is 40km/h (when the wheel size is set correctly). This setting\n \
is used for all assist levels the Basic settings. If you set this to \n \
40km/h (in this program or from your LCD) and your Assist 5 level is set\n \
to 50% speed then you will be able to reach 20km/h at that assist level."

help_dict['SC-PAS'] = "Start Current [%]\n\n \
This is the startup current when you start rotating the pedals. It is good\n \
to set this to at least 10% to make sure the bicycle will start moving and\n \
the motor won’t be stalled. Setting this to very high value will make the\n \
bicycle accelerate very fast at start which might damage its internal gears\n \
and or the motor. Recommended value is one between 10% and 30%. You should\n \
also make sure you don’t start pedaling at a too high gear which will load\n \
the motor too much."

help_dict['SSM'] = "Slow-start Mode (1-8)\n\n \
This setting controls how quickly the start current is reached. You can make\n \
your bicycle accelerate smoothly and make it respond quickly. A value of\n \
around 4 usually works well for normal cycling. If you are mountain-biker then\n \
setting to  a low value will make the acceleration faster which might be useful\n \
but you should be careful not to fry your controller and motor."

help_dict['SDN'] = "Start Degree (Signal No.)\n\n \
This parameter sets how many pulses from the pedal sensor are needed before the\n \
motor starts. Full pedal revolution on BBS kits generates 24 pulses. Setting\n \
this to 0 or 1 will not work. A value around 4 works well as it doesn’t start\n \
with just a small move and also doesn’t require too much rotation."

help_dict['WM'] = "Work Mode (Angular Pedal Speed / Wheel * 10)\n\n \
This parameter’s purpose is not very clear. It is supposed to control the\n \
power according to pedal rotation speed. The value set by manufacturer seems\n \
to work just fine so you don’t need to change it.\n\n \
Default Value:\n \
   255 which is an undetermined mode"

help_dict['SD'] = "Stop Delay [x10ms]\n\n \
This is the delay after you stop pedaling before the motor stops. Keep in mind\n \
the x10. If you set it to 100 this will lead to 1 second delay. A value of 25\n \
(250ms) works well."

help_dict['CD'] = "Current Decay (1-8)\n\n \
This parameter sets how fast the current drops when you are pedaling fasted and\n \
are reaching the maximum speed at the selected assist level. Lower value means\n \
the current will start to drop at lower speed."

help_dict['TS'] = "Stop Decay [x10ms]\n\n \
The amount of time it takes the motor to stop."

help_dict['KC'] = "Keep Current [%]\n\n \
This setting controls the percentage of the maximum current at the selected\n \
assist level which will be flowing through the motor when you reach the\n \
maximum speed and keep pedaling. So if your maximum current is 25A and you\n \
use PAS5 set to 50% current then you will have maximum current of 12.5A for\n \
this assist level. Then if Keep Current is set to 50% when the maximum speed\n \
is reached and you continue pedaling the current will be kept at 6.25A. This\n \
ensures smooth transition to assist power when you reduce the pedaling speed\n \
and the moving speed drops below the maximum."

# Throttle help
#----------------------------------------------------------------------------
help_dict['SV'] = "Start Voltage [x100mV]\n\n \
This is the throttle handle voltage at which the motor will start. The\n \
minimum at which the controller responds is 1.1V so you should set this\n \
parameter to 11 (11x100mV=1.1V).\n \
Best Values:\n \
   Between 10 and 15, default 11"

help_dict['EV'] = "End Voltage [x100mV]\n\n \
This is the throttle handle voltage at which the motor will reach its\n \
maximum power (limited by other settings). The maximum accepted from the\n \
controller is 4.2V (42x100mV=4.2V). You need to play a little with this\n \
parameter as the throttle handle maximum can be different depending on\n \
model. If you set this parameter too low you will get almost no response\n \
from the throttle handle. When you set it to the maximum that the handle\n \
can produce you will get the widest possible range of control over motor\n \
power.\n \
Best Values:\n \
   Between 35 and 42, default 36"

help_dict['MODE'] = "Mode\n\n \
This is the operation mode of the throttle handle. You have two options:\n \
speed and current. When set to speed it the controller uses the moving\n \
speed to set the motor power according to the position of the throttle\n \
handle. Unfortunately there is significant delay because of the way the speed\n \
is measured and the response is pretty bad in this mode. When set to current,\n \
the handle controls the motor current according to its position. This mode\n \
works better and similar to a car operation.\n \
Values:\n \
    Mode: Speed -- 0x00=\"speed\" or 0x01=\"current\""

help_dict['DA-THR'] = "Designated Assist Level\n\n \
You can set this to “By Display’s Command” or select a fixed level. The first\n \
option uses the PAS setting from your LCD. This means that the maximum power\n \
output and speed depend on the PAS level selected and the position of the\n \
throttle handle. So if a low PAS is selected the maximum current and speed will\n \
be low too, even if you push the throttle to maximum. If a fixed assist level is\n \
selected for this parameter the throttle handle will use its maximum current and\n \
speed. Be careful if you set this to level 9 not to push the throttle to max\n \
when stopped as the high current and the power could damage your controller\n \
and motor."

help_dict['SL-THR'] = "Speed Limit\n\n \
Cuts power when the road speed from the mag sensor hits the number set here.\n \
If set to By Display’s Command then it uses the Display’s set speed limit.\n \
However this setting can sometimes cause severe Throttle lag in PAS0 so if you\n \
set it to 40km/hr the 2-3 second throttle lag should disappear.\n\n \
The speed limit only applies to the PAS and is ignored by throttle input, so\n \
in other words, if you want to go past the speed limit, just use the throttle.\n \
This is a setting that allows the rider to set a pace or cadence when using\n \
pedal assist for a comfortable steady pace. Almost like cruise control, when you\n \
begin to go past the speed, the motor cuts out to maintain a lower speed.  It is\n \
a useful way to extend range. The max speed limit of the display is 45 mph."

help_dict['SC-THR'] = "Start Current [%]\n\n \
This is the percentage of maximum current applied to the motor when the throttle\n \
handle generates the minimum accepted voltage. Usually a value of 10% or 20% works\n \
well. If your maximum current at the Basic tab is set to 25A and Start Current\n \
is set to 10% you will get 2.5A start current. This will lead to smooth start\n \
and will not load the internal gears too much. If you set this parameter to very\n \
high value you can damage the internal gears and the motor.\n \
Common Values:\n \
   10 to 20, default 10"



