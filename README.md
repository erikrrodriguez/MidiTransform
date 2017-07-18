# Midi Transform
A program to randomly alter various midi note properties. Utilizes the **MIDI Objects for Python Library** - https://github.com/olemb/mido 
Interface created with PyQt5.

![MidiTransform](http://i.imgur.com/klCd4xG.jpg)

**Controls:**
* Import a MIDI file using the **Open** button.
* Mark the check boxes of each property to be altered. The options are **Note(s)**, **Velocity**, **Start Time**, and **End Time**.
* **Note(s)**: One or more midi notes can be entered, separated by commas. Midi notes range from 0 to 127. Pick the minimum and maximum values to be added or subtracted from each note (negative values are accepted).
* **Velocity**: Pick the minimum and maximum values to be added or subtracted from all note velocities (negative values are accepted).
* **Start Time** Pick the minimum and maximum values to be added or subtracted from all note start times (negative values are accepted).
* **End Time** Pick the minimum and maximum values to be added or subtracted from all note end times (negative values are accepted).
* Write the name of the new file in the **New File Name...** dialog box. If no name is provided, the name of the opened file will be used.
* Once all selections are made, press **Run**.

**Caution:**
* Currently, the program only affects midi notes in the 2nd track
* The number of notes in the input must match the number of +/- Note Min and Max inputs


## To Do
* Handle midi files with various tracks.
* Allow note specifications for velocity, start time, and end time
* Implement "Affect all notes except..." check boxes



