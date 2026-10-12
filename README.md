KlipperScreen Caselight Addon

addon to KlipperScreen to run a macro when the screen goes to sleep or wakeup. Useful to turn off and on lights automatically

to install, create folder "addons" into KlipperScreen installation folder, navigate into it and download caselight_handler.py into it
```
cd ~/KlipperScreen
mkdir addons && cd addons
wget https://raw.githubusercontent.com/steeveone/KlipperScreen-Caselight-addon/refs/heads/main/addons/caselight_handler.py
```

Now you have to configure the script, with your fav editor change the value of MACRO_WAKE and MACRO_SLEEP to your macros to handle caselight
```
# Configuration
MACRO_WAKE = "CASELIGHT_ON"
MACRO_SLEEP = "CASELIGHT_OFF"
```

At this point you have to create corresponding macros into your configuration (in printer.cfg): here are mine, they handle StealthBurner's leds (defined as sb_leds)  and the Caselight pin (called caselight), adapt macros at your use case.
```
[gcode_macro CASELIGHT_VARIABLES]
# Salviamo i canali separatamente come liste di numeri puri
variable_saved_r: []
variable_saved_g: []
variable_saved_b: []
variable_saved_w: []
variable_saved_caselight_brightness: 0.0
gcode:

[gcode_macro CASELIGHT_ON]
gcode:
	{% set current_brightness = printer["output_pin caselight"].value | float %}
	{% if current_brightness < 0.1 %}
		{% set led_name = "sb_leds" %}
		
		{% set r = printer["gcode_macro CASELIGHT_VARIABLES"].saved_r %}
		{% set g = printer["gcode_macro CASELIGHT_VARIABLES"].saved_g %}
		{% set b = printer["gcode_macro CASELIGHT_VARIABLES"].saved_b %}
		{% set w = printer["gcode_macro CASELIGHT_VARIABLES"].saved_w %}

		{% set target_brightness = printer["gcode_macro CASELIGHT_VARIABLES"].saved_caselight_brightness | float %}

		{% for i in range(r|length) %}
			SET_LED LED={led_name} INDEX={i + 1} RED={r[i]} GREEN={g[i]} BLUE={b[i]} WHITE={w[i]|default(0.0)} TRANSMIT={1 if loop.last else 0}
		{% endfor %}
		
		SET_PIN PIN=caselight VALUE={target_brightness}
	{% endif %}

[gcode_macro CASELIGHT_OFF]
gcode:
	{% if printer.toolhead.homed_axes == "" %}
		{% set current_brightness = printer["output_pin caselight"].value | float %}
		{% if current_brightness > 0 %}
			{% set led_name = "sb_leds" %}
			{% set current_chain = printer["neopixel " ~ led_name].color_data %}
			
			{% set list_r = current_chain | map(attribute=0) | list %}
			{% set list_g = current_chain | map(attribute=1) | list %}
			{% set list_b = current_chain | map(attribute=2) | list %}
			{% set list_w = current_chain | map(attribute=3) | default([0.0, 0.0, 0.0]) | list %}
			
			SET_GCODE_VARIABLE MACRO=CASELIGHT_VARIABLES VARIABLE=saved_r VALUE="{list_r}"
			SET_GCODE_VARIABLE MACRO=CASELIGHT_VARIABLES VARIABLE=saved_g VALUE="{list_g}"
			SET_GCODE_VARIABLE MACRO=CASELIGHT_VARIABLES VARIABLE=saved_b VALUE="{list_b}"
			SET_GCODE_VARIABLE MACRO=CASELIGHT_VARIABLES VARIABLE=saved_w VALUE="{list_w}"

			SET_GCODE_VARIABLE MACRO=CASELIGHT_VARIABLES VARIABLE=saved_caselight_brightness VALUE={current_brightness}
			STATUS_OFF
			SET_PIN PIN=caselight VALUE=0.0
		{% endif %}
	{% endif %}
```

From your screen, enable addons:
```
Settings->KlipperScreen->Enable Add-ons
```
Now issue a firmware restart and a KlipperScreen restart and enjoy!
