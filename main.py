from mido import MidiFile, MidiTrack, Message
from random import randint
from functools import partial

import sys
from gui import Ui_Window
from PyQt5.QtWidgets import QApplication, QDialog, QFileDialog
from PyQt5.QtCore import Qt

class AppWindow(QDialog):
	def __init__(self):
		super().__init__()
		self.ui = Ui_Window()
		self.ui.setupUi(self)

		#vars
		self.mid = None
		self.shortName = ''
		self.length = 0
		self.keep_file = False

		# self.noteFlag = False
		# self.noteExceptFlag = False
		# self.noteTargets = [0]
		# self.noteMin = [0]
		# self.noteMax = [0]

		# self.velFlag = False
		# self.velExceptFlag = False
		# self.velTargets = [0]
		# self.velMin = [0]
		# self.velMax = [0]

		# self.startTimeFlag = False
		# self.startExceptFlag = False
		# self.startTimeTargets = [0]
		# self.startTimeMin = [0]
		# self.startTimeMax = [0]

		# self.endTimeFlag = False
		# self.endExceptFlag = False
		# self.endTimeTargets = [0]
		# self.endTimeMin = [0]
		# self.endTimeMax = [0]

		self.midi_props = ['Note', 'Velocity', 'Start Time', 'End Time']
		self.enable_flags = dict(zip(self.midi_props, [False, False, False, False]))
		self.except_flags = dict(zip(self.midi_props, [False, False, False, False]))
		self.note_targets = dict(zip(self.midi_props, [[0], [0], [0], [0]]))
		self.min_vals = dict(zip(self.midi_props, [[0], [0], [0], [0]]))
		self.max_vals = dict(zip(self.midi_props, [[0], [0], [0], [0]]))

		#connect buttons
		self.ui.openFile.clicked.connect(self.open_file)
		self.ui.run.clicked.connect(self.run)
		
		#checkboxes. partial lets you throw in extra params with a callback function
		self.ui.noteCheckBox.stateChanged.connect(partial(self.set_enable_flag, 'Note'))
		self.ui.velCheckBox.stateChanged.connect(partial(self.set_enable_flag, 'Velocity'))
		self.ui.startTimeCheckBox.stateChanged.connect(partial(self.set_enable_flag, 'Start Time'))
		self.ui.endTimeCheckBox.stateChanged.connect(partial(self.set_enable_flag, 'End Time'))

		self.ui.noteExcept.stateChanged.connect(partial(self.set_except_flag, 'Note'))
		self.ui.velExcept.stateChanged.connect(partial(self.set_except_flag, 'Velocity'))
		self.ui.startTimeExcept.stateChanged.connect(partial(self.set_except_flag, 'Start Time'))
		self.ui.endTimeExcept.stateChanged.connect(partial(self.set_except_flag, 'End Time'))

		self.ui.keepFileCheckBox.stateChanged.connect(self.keep_file_mem)
		
		#Text boxes
		self.ui.notePitchBox.editingFinished.connect(partial(self.set_notes, 'Note'))
		self.ui.velNotes.editingFinished.connect(partial(self.set_notes, 'Velocity'))
		self.ui.startTimeNotes.editingFinished.connect(partial(self.set_notes, 'Start Time'))
		self.ui.endTimeNotes.editingFinished.connect(partial(self.set_notes, 'End Time'))

		self.ui.noteMin.editingFinished.connect(partial(self.set_min, 'Note'))
		self.ui.velMin.editingFinished.connect(partial(self.set_min, 'Velocity'))
		self.ui.startTimeMin.editingFinished.connect(partial(self.set_min, 'Start Time'))
		self.ui.endTimeMin.editingFinished.connect(partial(self.set_min, 'End Time'))

		self.ui.noteMax.editingFinished.connect(partial(self.set_max, 'Note'))
		self.ui.velMax.editingFinished.connect(partial(self.set_max, 'Velocity'))
		self.ui.startTimeMax.editingFinished.connect(partial(self.set_max, 'Start Time'))
		self.ui.endTimeMax.editingFinished.connect(partial(self.set_max, 'End Time'))

		self.show()

	def open_file(self):
		name = QFileDialog.getOpenFileName(self, 'Open File','','Midi (*.mid)')
		if name[0]:
			self.shortName = name[0].rsplit('/',1)[-1]
			self.mid = MidiFile(filename=name[0])
			self.length = len(self.mid.tracks[1])
			self.ui.fileName.setText(self.shortName)

	def run(self):
		if not self.mid is None and len(self.noteTargets) == len(self.noteMin) and len(self.noteMin) == len(self.noteMax):
			#make dict of note pitch, min, max
			noteRange = list(zip(self.noteMin, self.noteMax)) #[(a,b), (c,d)]
			noteMinMax = dict(zip(self.noteTargets, noteRange)) #{note : (min, max), note : (min, max)}

			track = MidiTrack()
			for i, msg in enumerate(self.mid.tracks[1]):
				self.ui.progressBar.setValue(int(100*(i+1)/self.length))
				if msg.is_meta:
					track.append(msg)
				if msg.type == 'note_on':
					if msg.note in noteMinMax:
						new_note = self.clamp(0, msg.note + randint(noteMinMax[msg.note][0], noteMinMax[msg.note][1]), 127)
					else:
						new_note = msg.note
					new_vel = self.clamp(0, msg.velocity + randint(self.velMin,self.velMax), 127)
					new_start_time = self.clamp(0, msg.time + randint(self.startTimeMin,self.startTimeMax), 127)
					new_end_time = new_start_time + 50
					track.append(Message('note_on', note=new_note, velocity=new_vel, time=new_start_time))
					#Search for old note off time
					for j in range(i, len(self.mid.tracks[1])):
						test_msg = self.mid.tracks[1][j]
						if test_msg.type == 'note_off' and test_msg.note == msg.note:
							new_end_time = self.clamp(msg.time, test_msg.time + randint(self.endTimeMin,self.endTimeMax), 127)
							break
					track.append(Message('note_off', note=new_note, velocity=new_vel, time=new_end_time))

			# track.sort(key=lambda message: message.time)
			new_mid = MidiFile()
			new_mid.tracks.append(self.mid.tracks[0])
			new_mid.tracks.append(track)
			if self.ui.newFileName.text():
				new_file_name = self.ui.newFileName.text()
				if new_file_name[-4:] is '.mid':
					new_file_name = new_file_name[:-4]
			else:
				new_file_name = self.shortName
			new_mid.save(new_file_name)
			if keep_file:
				#keep new midi file in memory
				self.mid = new_mid
				self.ui.fileName.setText(newFileName)
				self.shortName = newFileName
				self.length = len(self.mid.tracks[1])
			else:
				#Clear midi file from memory
				self.mid = None
				self.ui.fileName.setText('Select File')
				self.ui.newFileName.setText('')		

	def set_enable_flag(self, midiprop, state):
		if state == Qt.Checked:
			self.enable_flags[midiprop] = True
		else:
			self.enable_flags[midiprop] = False
		print(self.enable_flags)

	def set_except_flag(self, midiprop, state):
		if state == Qt.Checked:
			self.except_flags[midiprop] = True
		else:
			self.except_flags[midiprop] = False
		print(self.except_flags)

	def keep_file_mem(self, state):
		if state == Qt.Checked:
			self.keep_file = True
		else:
			self.keep_file = False

	def set_notes(self, midiprop):
		get_text_funcs = [self.ui.notePitchBox.text(), self.ui.velNotes.text(), self.ui.startTimeNotes.text(), self.ui.endTimeNotes.text()]
		prop_funcs = dict(zip(self.midi_props, get_text_funcs))
		notes = prop_funcs[midiprop] #return get text function for property
		notes = ''.join([c for c in notes if c in '0123456789,'])
		if notes is '':
			notes = '0'
		# self.ui.notePitchBox.setText(notes)
		notes = notes.split(',')
		notes = [int(x) for x in notes]
		self.note_targets[midiprop] = notes
		print(self.note_targets)

	def set_min(self, midiprop):
		get_text_funcs = [self.ui.noteMin.text(), self.ui.velMin.text(), self.ui.startTimeMin.text(), self.ui.endTimeMin.text()]
		prop_funcs = dict(zip(self.midi_props, get_text_funcs))
		mins = prop_funcs[midiprop] #return get text function for property
		mins = ''.join([c for c in mins if c in '0123456789,-'])
		# self.ui.notePitchBox.setText(notes)
		mins = mins.split(',')
		mins = [int(x) for x in mins]
		self.min_vals[midiprop] = mins
		print(self.min_vals)

	def set_max(self, midiprop):
		get_text_funcs = [self.ui.noteMax.text(), self.ui.velMax.text(), self.ui.startTimeMax.text(), self.ui.endTimeMax.text()]
		prop_funcs = dict(zip(self.midi_props, get_text_funcs))
		maxs = prop_funcs[midiprop] #return get text function for property
		maxs = ''.join([c for c in maxs if c in '0123456789,-'])
		# self.ui.notePitchBox.setText(notes)
		maxs = maxs.split(',')
		maxs = [int(x) for x in maxs]
		self.max_vals[midiprop] = maxs
		print(self.max_vals)

	# def set_note_min(self):
	# 	vals = self.ui.noteMin.text()
	# 	vals = ''.join([c for c in vals if c in '0123456789,-'])
	# 	self.ui.noteMin.setText(vals)
	# 	vals = vals.split(',')
	# 	vals = [int(x) for x in vals]
	# 	self.noteMin = vals

	# def set_note_max(self):
	# 	vals = self.ui.noteMax.text()
	# 	vals = ''.join([c for c in vals if c in '0123456789,-'])
	# 	self.ui.noteMax.setText(vals)
	# 	vals = vals.split(',')
	# 	vals = [int(x) for x in vals]
	# 	self.noteMax = vals

	# def set_vel_min(self):
	# 	self.velMin = self.ui.velMin.value()

	# def set_vel_max(self):
	# 	self.velMax = self.ui.velMax.value()

	# def set_start_time_min(self):
	# 	self.startTimeMin = self.ui.startTimeMin.value()

	# def set_start_time_max(self):
	# 	self.startTimeMax = self.ui.startTimeMax.value()

	# def set_end_time_min(self):
	# 	self.endTimeMin = self.ui.endTimeMin.value()

	# def set_end_time_max(self):
	# 	self.endTimeMax = self.ui.endTimeMax.value()

	# def note_flag(self, state):
	# 	if state == Qt.Checked:
	# 		self.noteFlag = True
	# 	else:
	# 		self.noteFlag = False

	# def vel_flag(self, state):
	# 	if state == Qt.Checked:
	# 		self.velFlag = True
	# 	else:
	# 		self.velFlag = False

	# def start_time_flag(self, state):
	# 	if state == Qt.Checked:
	# 		self.startTimeFlag = True
	# 	else:
	# 		self.startTimeFlag = False

	# def end_time_flag(self, state):
	# 	if state == Qt.Checked:
	# 		self.endTimeFlag = True
	# 	else:
	# 		self.endTimeFlag = False

	def clamp(self, minimum, x, maximum):
		return max(minimum, min(x, maximum))


app = QApplication(sys.argv)
ui = AppWindow()
sys.exit(app.exec_())

