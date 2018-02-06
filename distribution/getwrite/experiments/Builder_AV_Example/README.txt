OpenHandWrite Example 2 
------------------------------

Wacom Wintab device required; Surface Pro 3 + not supported yet.

An example PsychoPy Builder project that uses the iohub.wintab device, plays video and audio files.

Please edit the iohub_config.yaml file to set the display device parameters so they are valid for your setup.

Experiment design is in progress, based on the original builder example, and modified to more closely meet issue #194 requirements.

Current experiment flow:

SS: TODO UPDATE BELOW TEXT; IT IS OUT OF DATE

1. Display Experiment Start Screen, wait for button press.

2. Run the iohub wintab validation procudure. This is pure custom code.

3. Run practice trial:
	3a. Display Practice Screen
   	3b. Display pen and pen trace
   	3c. Wait until 'next' button is pressed with tablet pen.

4. Trial Set loop (1 trial for each row in conditions file.) 
     For each trial:

5. Display no writing screen for 2 seconds. Graphics:
   	- pen point
   	- 4 no writing images
   	- grey background

6. Starting playing video clip (T_MOV column of conditions file). Graphics
   	- same as step 5
   	- + video

7. Wait 1 second.

8. Start playing audio clip (T_SND column of conditions file). 

9. After audio and video clips have ended, Wait 1 second

10. Update display; show trial screen: Graphics:
   - white background
   - green point image (T_IMG column of conditions file)
   - pen pos
   - pen trace
   - stop button image

11. When Stop Button is pressed with Pen goto 5; repeating for number trials defined in condions file.
