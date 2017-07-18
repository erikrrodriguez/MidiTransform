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
		if not self.mid is None:
			#make dict of note_targets, min_vals, max_vals
			# notes_mins_maxs = list(zip(self.note_targets.values(), self.min_vals.values(), self.max_vals.values()))
			# prop_nmm = dict(zip(self.midi_props, notes_mins_maxs)) #{'Note' : [([notes], [mins], [maxs])]}

			track = MidiTrack()
			for i, msg in enumerate(self.mid.tracks[1]):
				self.ui.progressBar.setValue(int(100*(i+1)/self.length))
				if msg.is_meta:
					track.append(msg)
				if msg.type == 'note_on':
					new_note = msg.note
					new_vel = msg.velocity
					new_start = msg.time
					new_end = msg.time + 1
					#Search for msg note off time
					for j in range(i, len(self.mid.tracks[1])):
						test_msg = self.mid.tracks[1][j]
						if test_msg.type == 'note_off' and test_msg.note == msg.note:
							new_end = test_msg.time
							break

					if self.enable_flags['Note']:
						if self.except_flags['Note']:
							if msg.note not in note_targets['Note']:
								new_note = self.clamp(0, msg.note + randint(min_vals['Note'][0], max_vals['Note'][:-1]), 127)
						else:
							if msg.note in note_targets['Note']:
								nindex = note_targets['Note'].index(msg.note)
								new_note = self.clamp(0, msg.note + randint(min_vals['Note'][nindex], max_vals['Note'][nindex]), 127)
					if self.enable_flags['Velocity']:
						if self.except_flags['Velocity']:
							if msg.note not in note_targets['Velocity']:
								new_vel = self.clamp(0, msg.vel + randint(min_vals['Velocity'][0], max_vals['Velocity'][:-1]), 127)
						else:
							if msg.note in note_targets['Velocity']:
								nindex = note_targets['Velocity'].index(msg.note)
								new_vel = self.clamp(0, msg.vel + randint(min_vals['Velocity'][nindex], max_vals['Velocity'][nindex]), 127)
					if self.enable_flags['Start Time']:
						if self.except_flags['Start Time']:
							if msg.note not in note_targets['Start Time']:
								new_start = self.clamp(0, msg.note + randint(min_vals['Start Time'][0], max_vals['Start Time'][:-1]), 127)
						else:
							if msg.note in note_targets['Start Time']:
								nindex = note_targets['Start Time'].index(msg.note)
								new_start = self.clamp(0, msg.time + randint(min_vals['Start Time'][nindex], max_vals['Start Time'][nindex]), 127)
					if self.enable_flags['End Time']:
						if self.except_flags['End Time']:
							if msg.note not in note_targets['End Time']:
								new_end = self.clamp(msg.time, new_end + randint(min_vals['End Time'][0], max_vals['End Time'][:-1]), 127)
						else:
							if msg.note in note_targets['End Time']:
								nindex = note_targets['End Time'].index(msg.note)
								new_end = self.clamp(msg.time, new_end + randint(min_vals['End Time'][nindex], max_vals['End Time'][nindex]), 127)

					track.append(Message('note_on', note=new_note, velocity=new_vel, time=new_start))
					track.append(Message('note_off', note=new_note, velocity=new_vel, time=new_end))
			# track.sort(key=lambda message: message.time)
			self.create_new_mid(track)	

	def create_new_mid(self, track):
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
		if self.keep_file:
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
		# print(self.note_targets)

	def set_min(self, midiprop):
		get_text_funcs = [self.ui.noteMin.text(), self.ui.velMin.text(), self.ui.startTimeMin.text(), self.ui.endTimeMin.text()]
		prop_funcs = dict(zip(self.midi_props, get_text_funcs))
		mins = prop_funcs[midiprop] #return get text function for property
		mins = ''.join([c for c in mins if c in '0123456789,-'])
		if mins is '':
			mins = '0'
		# self.ui.notePitchBox.setText(notes)
		mins = mins.split(',')
		mins = [int(x) for x in mins]
		self.min_vals[midiprop] = mins
		# print(self.min_vals)

	def set_max(self, midiprop):
		get_text_funcs = [self.ui.noteMax.text(), self.ui.velMax.text(), self.ui.startTimeMax.text(), self.ui.endTimeMax.text()]
		prop_funcs = dict(zip(self.midi_props, get_text_funcs))
		maxs = prop_funcs[midiprop] #return get text function for property
		maxs = ''.join([c for c in maxs if c in '0123456789,-'])
		if maxs is '':
			maxs = '0'
		# self.ui.notePitchBox.setText(notes)
		maxs = maxs.split(',')
		maxs = [int(x) for x in maxs]
		self.max_vals[midiprop] = maxs
		# print(self.max_vals)

	def clamp(self, minimum, x, maximum):
		return max(minimum, min(x, maximum))

app = QApplication(sys.argv)
ui = AppWindow()
sys.exit(app.exec_())

