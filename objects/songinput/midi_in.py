# SPDX-FileCopyrightText: 2024 SatyrDiamond
# SPDX-License-Identifier: GPL-3.0-or-later 

import numpy as np

from functions import data_values
from functions import colors

from objects import datastore
from objects.data_bytes import structalloc
from objects.convproj import autoticks
from objects.convproj import project as convproj
from objects_midi import sysex

instrument_premake = structalloc.dynarray_premake([
	('track', np.uint8),
	('chan', np.uint8),
	('drum', np.uint8),
	('bank', np.uint8),
	('bank_hi', np.uint8),
	('inst', np.uint8),
	('is_custom', np.uint8),
	('custom_name', np.unicode_, 128),
	('custom_color_used', np.uint8),
	('custom_color', np.uint8, 3)])
timesig_premake = structalloc.dynarray_premake([
	('pos', np.uint32),
	('numerator', np.uint8),
	('denominator', np.uint8)])
bpm_premake = structalloc.dynarray_premake([
	('pos', np.uint32),
	('tempo', np.float32)])
pitchauto_premake = structalloc.dynarray_premake([
	('pos', np.uint32),
	('channel', np.uint8),
	('value', np.int16),
	('mode', np.int16)]
	)
instauto_premake = structalloc.dynarray_premake([
	('pos', np.uint32),
	('channel', np.uint8),
	('type', np.uint8),
	('value', np.uint8)])
chanauto_premake = structalloc.dynarray_premake([
	('pos', np.uint32),
	('channel', np.uint8),
	('control', np.uint8),
	('value', np.uint8)])
midinote_premake = structalloc.dynarray_premake([
	('complete', np.uint8),
	('chan', np.uint8),
	('start', np.int32),
	('end', np.int32),
	('key', np.uint8),
	('vol', np.uint8),
	('i_drum', np.uint8),
	('i_bank_hi', np.uint8),
	('i_bank', np.uint8),
	('i_inst', np.uint8),
	])
otherauto_premake = structalloc.dynarray_premake([
	('pos', np.uint32),
	('value', np.uint8)])

def get_auto(channel, ctrlnum, fxoffset):
	autochannum = str(channel+1+fxoffset)

	addmul = [0, 1]
	defualtval = 0
	autoloc = ['fxmixer', autochannum]
	pname = None

	if ctrlnum in [10, 64, 65, 66, 67, 68]: addmul = [-0.5, 1]

	if ctrlnum == 1: pname = 'modulation'
	if ctrlnum == 7: pname, defualtval = 'vol', 1
	if ctrlnum == 10: pname = 'pan'
	if ctrlnum == 64: pname = 'damper_pedal'
	if ctrlnum == 65: pname = 'portamento'
	if ctrlnum == 66: pname = 'sostenuto'
	if ctrlnum == 67: pname = 'soft_pedal'
	if ctrlnum == 68: pname = 'legato'
				
	if ctrlnum == 91: 
		autoloc, pname, defualtval = ['send', autochannum+'_reverb'], 'amount', 0
	if ctrlnum == 93: 
		autoloc, pname, defualtval = ['plugin', autochannum+'_chorus', 'amount'], 'amount', 0

	return autoloc, pname, addmul, defualtval

class midi_track:
	def __init__(self, numevents, song_obj):
		self.active_notes = [[[] for x in range(128)] for x in range(16)]
		self.notes = midinote_premake.create()
		self.notes.alloc(numevents)
		self.song_obj = song_obj
		self.portnum = 0

		self.track_name = None
		self.track_color = None
		self.used_insts = None
		self.seqspec = []

	def applyinst(self, channel, i_type, posval):
		if len(posval) != 0:
			n_used = self.notes.data['used']
			n_data = self.notes.data['chan']
			n_start = self.notes.data['start']
			filt_chan = np.logical_and(n_used==1, n_data==channel)

			for start, end, val in data_values.rangepos(posval, -1):
				if end == -1:
					filt_l_all = np.logical_and(filt_chan, n_start>=start)
					self.notes.data[i_type][np.where(filt_l_all)] = val
				else:
					filt_l_all = np.logical_and(filt_chan, n_start>=start, end>n_start)
					self.notes.data[i_type][np.where(filt_l_all)] = val


	def applyinst_chan(self, channel, chan_inst):
		n_used = self.notes.data['used']
		n_data = self.notes.data['chan']
		allfilt = np.where(np.logical_and(n_used==1, n_data==channel))
		chanfilt = chan_inst[channel]

		s_inst = chanfilt[np.where(chanfilt['type']==0)][['pos', 'value']]
		s_bank_lo = chanfilt[np.where(chanfilt['type']==1)][['pos', 'value']]
		s_bank_hi = chanfilt[np.where(chanfilt['type']==2)][['pos', 'value']]
		s_drum = chanfilt[np.where(chanfilt['type']==3)][['pos', 'value']]

		self.applyinst(channel, 'i_inst', s_inst)
		self.applyinst(channel, 'i_drum', s_drum)
		self.applyinst(channel, 'i_bank_hi', s_bank_hi)
		self.applyinst(channel, 'i_bank', s_bank_lo)

	def where_chan(self, channel):
		n_used = self.notes.data['used']
		n_data = self.notes.data['chan']
		return np.where(np.logical_and(n_used==1, n_data==channel))

	def filter_chan(self, channel):
		return self.notes.data[self.where_chan(channel)]

	def startpos_chan(self, channel):
		notedata = self.filter_chan(channel)
		return np.min(notedata['start']) if len(notedata) else 2147483647

	def endpos_chan(self, channel):
		notedata = self.filter_chan(channel)
		return np.max(notedata['end']) if len(notedata) else 0

	def note_on(self, curpos, channel, note, velocity):
		self.notes.add()
		self.notes['chan'] = channel
		self.notes['start'] = curpos
		self.notes['key'] = note
		self.notes['vol'] = velocity
		self.active_notes[channel][note].append(self.notes.cursor)

	def note_off(self, curpos, channel, note):
		nd = self.active_notes[channel][note]
		if nd:
			notenum = nd.pop()
			self.notes.data[notenum]['end'] = curpos
			self.notes.data[notenum]['complete'] = 1

	def note_dur(self, curpos, channel, note, velocity, duration):
		self.notes.add()
		self.notes['complete'] = 1
		self.notes['chan'] = channel
		self.notes['start'] = curpos
		self.notes['end'] = curpos+duration
		self.notes['key'] = note
		self.notes['vol'] = velocity

	def track_name(self, text):
		self.track_name = text

	def portnum(self, port):
		self.portnum = port

	def pitchwheel(self, curpos, channel, pitch):
		pitchchan = self.song_obj.auto_pitch
		pitchchan.add()
		pitchchan['pos'] = curpos
		pitchchan['channel'] = channel
		pitchchan['value'] = pitch

	def control_change(self, curpos, channel, controller, value):
		if controller == 0:
			instauto = self.song_obj.insts
			instauto.add()
			instauto['pos'] = curpos
			instauto['channel'] = channel
			instauto['type'] = 1
			instauto['value'] = value
		elif controller == 32:
			instauto = self.song_obj.insts
			instauto.add()
			instauto['pos'] = curpos
			instauto['channel'] = channel
			instauto['type'] = 2
			instauto['value'] = value
		elif controller == 111: self.song_obj.loop_start = curpos
		elif controller == 116: self.song_obj.loop_start = curpos
		elif controller == 117: self.song_obj.loop_end = curpos
		else:
			ctrlchan = self.song_obj.auto_chan
			ctrlchan.add()
			ctrlchan['pos'] = curpos
			ctrlchan['channel'] = channel
			ctrlchan['control'] = controller
			ctrlchan['value'] = value

	def program_change(self, curpos, channel, program):
		instauto = self.song_obj.insts
		instauto.add()
		instauto['pos'] = curpos
		instauto['channel'] = channel
		instauto['type'] = 0
		instauto['value'] = program

	def set_tempo(self, curpos, tempo):
		tempoauto = self.song_obj.auto_bpm
		tempoauto.add()
		tempoauto['pos'] = curpos
		tempoauto['tempo'] = tempo

	def time_signature(self, curpos, numerator, denominator):
		tsauto = self.song_obj.auto_timesig
		tsauto.add()
		tsauto['pos'] = curpos
		tsauto['numerator'] = numerator
		tsauto['denominator'] = denominator

	def text(self, curpos, text):
		self.song_obj.texts.add_point(curpos, text)

	def marker(self, curpos, text):
		if text == 'loopStart': self.song_obj.loop_start = curpos
		if text == 'loopEnd': self.song_obj.loop_end = curpos
		if text == 'Start': 
			self.song_obj.start_pos_est = False
			self.song_obj.start_pos = curpos
		self.song_obj.marker.add_point(curpos, text)

	def copyright(self, copyright):
		self.song_obj.copyright = copyright

	def sequencer_specific(self, data):
		seqspec_obj = sysex.seqspec_obj()
		seqspec_obj.detect(data)
		#seqspec_obj.print()
		color_found = None
		if seqspec_obj.sequencer == 'signal_midi' and seqspec_obj.param == 'color': color_found = seqspec_obj.value
		if seqspec_obj.sequencer == 'anvil_studio' and seqspec_obj.param == 'color': color_found = seqspec_obj.value
		if seqspec_obj.sequencer == 'studio_one' and seqspec_obj.param == 'color': color_found = seqspec_obj.value
		if color_found: self.track_color = [x/255 for x in color_found]
		self.seqspec.append(seqspec_obj)

	def sysex(self, curpos, data):
		sysex_obj = sysex.sysex_obj()
		sysex_obj.detect(data)
		#sysex_obj.print()
		self.song_obj.auto_sysex.add_point(curpos, sysex_obj)

		if sysex_obj.vendor.id == 67:
			if (sysex_obj.param, sysex_obj.value) == ('reset', 'all_params'):
				self.song_obj.device = 'xg'

		if sysex_obj.vendor.id == 65:
			if sysex_obj.param == 'gs_reset':
				self.song_obj.device = 'gs'

			if sysex_obj.model_id == 22:
				self.song_obj.device = 'mt32'

	def lyric(self, curpos, data):
		self.song_obj.lyrics[curpos] = data

class midi_song:
	def __init__(self, numchannels, ppq, tempo, timesig):
		self.miditracks = []

		self.song_channels = numchannels
		self.ppq = ppq
		self.pitch_gm = False

		self.fx_offset = 0

		self.auto_pitch = pitchauto_premake.create()
		self.auto_chan = chanauto_premake.create()
		self.insts = instauto_premake.create()
		self.auto_timesig = timesig_premake.create()
		self.auto_bpm = bpm_premake.create()
		self.copyright = None
		self.lyrics = {}
		self.device = 'gm'

		self.auto_master_vol = otherauto_premake.create()

		self.texts = datastore.auto_multidata()
		self.marker = datastore.auto_multidata()
		self.auto_sysex = datastore.auto_multidata()

		self.loop_start = None
		self.loop_end = None
		self.start_pos = None
		self.start_pos_est = True

		self.start_ctrls = [{} for _ in range(self.song_channels)]
		self.start_pitch = [0 for _ in range(self.song_channels)]
		self.chan_ctrls = [{} for _ in range(self.song_channels)]

		self.instruments = instrument_premake.create()

	def add_port(self, numchannels):
		self.song_channels += numchannels
		self.start_ctrls += [{} for _ in range(numchannels)]
		self.start_pitch += [0 for _ in range(numchannels)]
		self.chan_ctrls += [{} for _ in range(numchannels)]

	def add_instrument(self, i_track, i_chan, i_bank, i_bank_hi, i_patch, i_drum):
		self.instruments.add()
		self.instruments['track'] = i_track
		self.instruments['chan'] = i_chan
		self.instruments['drum'] = i_drum
		self.instruments['bank'] = i_bank
		self.instruments['bank_hi'] = i_bank_hi
		self.instruments['inst'] = i_patch

	def create_track(self, numevents):
		track_obj = midi_track(numevents, self)
		self.miditracks.append(track_obj)
		return track_obj

	def postprocess(self):
		self.auto_pitch.sort(['pos'])
		self.auto_pitch.unique(['pos', 'channel'])

		self.auto_chan.sort(['pos'])

		self.auto_timesig.sort(['pos'])
		self.auto_bpm.sort(['pos'])

		self.auto_sysex.sort()

		self.g_used_fx = []
		self.used_fx = [[] for x in range(self.song_channels)]

		for x in self.miditracks:
			x.notes.clean()

		for x in self.auto_sysex:
			p_pos, p_sysexs = x
			for p_sysex in p_sysexs:
				if p_sysex.model_name == 'sc88':
					if p_sysex.category == 'patch_a' and p_sysex.group == 'block' and p_sysex.param == 'use_rhythm': 
						instauto = self.insts
						instauto.add()
						instauto['pos'] = p_pos
						instauto['channel'] = p_sysex.num if p_sysex.num!=0 else 9
						instauto['type'] = 3
						instauto['value'] = int(p_sysex.value!=0)

				if p_sysex.vendor.id == 127:
					if p_sysex.category == 'device' and p_sysex.param == 'master_volume': 
						mastervol_auto = self.auto_master_vol
						mastervol_auto.add()
						mastervol_auto['pos'] = p_pos
						mastervol_auto['value'] = p_sysex.value

		self.auto_master_vol.sort(['pos'])
		self.insts.sort(['pos'])

		if len(self.insts.data):
			i_used = self.insts.data['used']
			i_data = self.insts.data['channel']
			chan_inst = [self.insts.data[np.where(np.logical_and(i_data==x, i_used==1))] for x in range(self.song_channels)]
		else:
			chan_inst = None

		if len(self.auto_pitch.data):
			pitchdata = self.auto_pitch.data
			for x in self.auto_sysex:
				p_pos, p_sysexs = x
				for p_sysex in p_sysexs:
					if p_sysex.model_name == 'aibo' and p_sysex.param == 'on?': 
						pitchdata['mode'][np.where(pitchdata['pos']>=p_pos)] = 1
					if p_sysex.model_name == 'sc88':
						if p_sysex.param in ['gs_reset', 'sys_mode']: 
							pitchdata['mode'][np.where(pitchdata['pos']>=p_pos)] = 0

		if len(self.auto_pitch.data):
			p_used = self.auto_pitch.data['used']
			p_data = self.auto_pitch.data['channel']
			chan_pitch = [self.auto_pitch.data[np.where(np.logical_and(p_data==x, p_used==1))] for x in range(self.song_channels)]
		else:
			chan_pitch = None

		if len(self.auto_chan.data):
			a_used = self.auto_chan.data['used']
			a_data = self.auto_chan.data['channel']
			chan_auto = [self.auto_chan.data[np.where(np.logical_and(a_used==1, a_data==x))] for x in range(self.song_channels)]
			chan_auto_uni = [np.unique(chan_auto[x]['control']) for x in range(self.song_channels)]
		else:
			chan_auto = None
			chan_auto_uni = None

		s_prepos = np.rot90(np.array([[t.startpos_chan(c) for c in range(self.song_channels)] for t in self.miditracks]))
		self.startpos_chan = [np.min(x) for x in s_prepos][::-1]

		e_prepos = np.rot90(np.array([[t.endpos_chan(c) for c in range(self.song_channels)] for t in self.miditracks]))
		self.endpos_chan = [np.max(x) for x in e_prepos][::-1]

		for num, track in enumerate(self.miditracks):
			drums_where = np.where(track.notes.data['chan']==9)
			track.notes.data['i_inst'] = 255
			track.notes.data['i_drum'][drums_where] = 1
			for channel in range(self.song_channels):
				if chan_inst != None: track.applyinst_chan(channel, chan_inst)
			track.used_insts = np.unique(track.notes.data[['chan','i_drum','i_bank_hi','i_bank','i_inst']])

			for ui in track.used_insts:
				self.add_instrument(num, ui['chan'], ui['i_bank'], ui['i_bank_hi'], ui['i_inst'], ui['i_drum'])

		for chan in range(self.song_channels):
			s_ctrls = chan_auto_uni[chan] if chan_auto_uni else []

			if 91 in s_ctrls: self.used_fx[chan].append('reverb')
			if 93 in s_ctrls: self.used_fx[chan].append('chorus')

			if 'reverb' in self.used_fx[chan] and 'reverb' not in self.g_used_fx: 
				self.g_used_fx.append('reverb')

			for ctrlnum in s_ctrls:
				chanauto = np.unique(chan_auto[chan][np.where(chan_auto[chan]['control']==ctrlnum)][['pos', 'value']])
				self.chan_ctrls[chan][ctrlnum] = chanauto
				acp = np.where(chanauto['pos']<=self.startpos_chan[chan])

				if len(acp[0])!=0: 
					self.start_ctrls[chan][ctrlnum] = chanauto['value'][acp][-1]

			if chan_pitch != None:
				s_pitch = chan_pitch[chan][['pos', 'value']]

				app = np.where(s_pitch['pos']<=self.startpos_chan[chan])
				if len(app[0])!=0: self.start_pitch[chan] = s_pitch['value'][app][-1]

	def to_cvpj(self, convproj_obj):
		convproj_obj.set_timings(self.ppq, True)
		self.instruments.clean()
		self.auto_pitch.clean()
		self.auto_chan.clean()
		self.auto_timesig.clean()
		self.auto_bpm.clean()

		for inst in self.instruments:
			instid = '_'.join([
				str(inst['track']), 
				str(inst['chan']), 
				str(inst['inst']), 
				str(inst['bank']), 
				str(inst['bank_hi']), 
				str(inst['drum'])])
			midiinst = int(inst['inst']) if inst['inst']!=255 else 0

			inst_obj = convproj_obj.add_instrument(instid)

			inst_obj.visual.name = inst['custom_name'] if inst['custom_name'] else None
			if inst['custom_color_used']: 
				inst_obj.visual.color.set_int([x/255 for x in inst['custom_color']])
			inst_obj.visual.from_dset_midi(inst['bank_hi'], inst['bank'], midiinst, inst['drum'], self.device, False)

			plugin_obj = convproj_obj.add_plugin_midi(instid, int(inst['bank_hi']), int(inst['bank']), int(midiinst), int(inst['drum']), self.device)
			plugin_obj.role = 'synth'
			inst_obj.pluginid = instid
			inst_obj.fxrack_channel = int(inst['chan'])+1+self.fx_offset

			if inst['drum']: inst_obj.visual.color.set_float([0.81, 0.80, 0.82])

		if len(self.miditracks)>1:

			single_trackinst = []
			for tracknum in range(len(self.miditracks)):
				sametrknum = np.where(self.instruments.data['track']==tracknum)[0]
				if len(sametrknum)==1:
					i = self.instruments.data[sametrknum[0]]
					single_trackinst.append([str(i['bank_hi']),str(i['bank']),str(i['inst']),str(i['drum']),str(i['chan'])])
				else: single_trackinst.append(None)

			for tracknum, track in enumerate(self.miditracks):
				cvpj_trackid = 'track_'+str(tracknum)

				track_obj = convproj_obj.add_track(cvpj_trackid, 'instruments', 0, False)
				track_obj.visual.name = track.track_name
				track_obj.visual.color.set_int(track.track_color)

				s_tin = single_trackinst[tracknum]
				if s_tin != None:
					if not s_tin[3]:
						track_obj.visual.from_dset('midi', self.device+'_inst', '_'.join([s_tin[0],s_tin[1],s_tin[2]]), False)

				for n in track.notes:
					if n['complete']:
						instid = '_'.join([str(tracknum),str(n['chan']),str(n['i_inst']),str(n['i_bank']),str(n['i_bank_hi']),str(n['i_drum'])])
						track_obj.placements.notelist.add_m(instid, int(n['start']), int(n['end']-n['start']), int(n['key'])-60, float(n['vol'])/127, {})

		if len(self.miditracks)==1:
			track = self.miditracks[0]
			convproj_obj.metadata.name = track.track_name
			wherecomplete = np.where(track.notes.data['complete']==1)
			tracknotes = track.notes.data[wherecomplete]
			usedchans = np.unique(tracknotes['chan'])

			for usedchan in usedchans:
				cvpj_trackid = 'chan_'+str(usedchan)
				chantxt = 'Chan #'+str(usedchan+1)

				track_obj = convproj_obj.add_track(cvpj_trackid, 'instruments', 0, False)

				for n in tracknotes[np.where(tracknotes['chan']==usedchan)]:
					instid = '_'.join(['0',str(n['chan']),str(n['i_inst']),str(n['i_bank']),str(n['i_bank_hi']),str(n['i_drum'])])
					track_obj.placements.notelist.add_m(instid, int(n['start']), int(n['end']-n['start']), int(n['key'])-60, float(n['vol'])/127, {})

				instlist = self.instruments.data[np.where(self.instruments.data['chan']==usedchan)]
				if len(instlist)==1:
					i = instlist[0]

					if not i['drum']: 
						track_obj.visual.from_dset_midi(i['bank_hi'], i['bank'], i['inst'], i['drum'], self.device, False)
						if track_obj.visual.name: track_obj.visual.name += ' ('+str(chantxt)+')'
						else: track_obj.visual.name = chantxt
					else: 
						track_obj.visual.name = 'Drums'
						track_obj.visual.color.set_float([0.81, 0.80, 0.82])

				else:
					track_obj.visual.name = chantxt

		for ts in self.auto_timesig:
			convproj_obj.timesig_auto.add_point(ts['pos'], [ts['numerator'], ts['denominator']**2])

		for point in self.auto_master_vol:
			convproj_obj.automation.add_autotick(['main', 'vol'], 'float', point['pos'], point['value']/127)

		for bpm in self.auto_bpm:
			convproj_obj.automation.add_autotick(['main', 'bpm'], 'float', bpm['pos'], bpm['tempo'])

		fxchannel_obj = convproj_obj.add_fxchan(0)
		fxchannel_obj.visual.name = "Master"
		fxchannel_obj.visual.color.set_float([0.3, 0.3, 0.3])

		if 'reverb' in self.g_used_fx:
			reverb_fxchannel_obj = convproj_obj.add_fxchan(self.song_channels+1+self.fx_offset)
			reverb_fxchannel_obj.visual.name = 'Reverb'
			reverb_fxchannel_obj.visual_ui.other['docked'] = 1
			plugin_obj, reverb_pluginid = convproj_obj.add_plugin_genid('simple', 'reverb')
			plugin_obj.visual.name = 'Reverb'
			plugin_obj.fxdata_add(1, 0.5)
			reverb_fxchannel_obj.fxslots_audio.append(reverb_pluginid)

		for fx_num in range(self.fx_offset):
			fxchannel_obj = convproj_obj.add_fxchan(fx_num+1)

		for ch_num in range(self.song_channels):

			fx_num = ch_num+1+self.fx_offset

			fxchannel_obj = convproj_obj.add_fxchan(ch_num+1+self.fx_offset)
			fxchannel_obj.sends.add(0, None, 1)

			used_fx = self.used_fx[ch_num]
			start_ctrls = self.start_ctrls[ch_num]
			start_pitch = self.start_pitch[ch_num]

			fxchannel_obj.params.add('pitch', start_pitch/8192, 'float')
			if 7 in start_ctrls: fxchannel_obj.params.add('vol', start_ctrls[7]/127, 'float')
			if 10 in start_ctrls: fxchannel_obj.params.add('pan', (start_ctrls[10]/127)-0.5, 'float')

			if 'reverb' in used_fx:
				reverbsend = start_ctrls[91]/127 if 91 in start_ctrls else 0
				reverb_pluginid = str(fx_num+1)+'_reverb'
				fxchannel_obj.sends.add(self.song_channels+1, reverb_pluginid, 0)

			if 'chorus' in used_fx:
				chorus_size = start_ctrls[93]/127 if 93 in start_ctrls else 0
				chorus_pluginid = str(fx_num+1)+'_chorus'
				chorus_plugin_obj = convproj_obj.add_plugin(chorus_pluginid, 'simple', 'chorus')
				chorus_plugin_obj.visual.name = 'Chorus'
				chorus_plugin_obj.params.add('amount', chorus_size, 'float')
				fxchannel_obj.fxslots_audio.append(chorus_pluginid)

			inst_chan = np.where(self.instruments.data['chan']==ch_num)[0]
			if len(inst_chan):
				befsame_chan = self.instruments.data[inst_chan]

				same_track = befsame_chan['track'][0] if np.all(befsame_chan['track']) else None
				if same_track != None:
					track = self.miditracks[same_track]
					fxchannel_obj.visual.add_opt(track.track_name if track.track_name else None, track.track_color)

				same_drum = befsame_chan['drum'][0] if np.all(befsame_chan['drum']) else None
				same_inst = befsame_chan['inst'][0] if np.all(befsame_chan['inst']) else None

				if same_drum == 1: fxchannel_obj.visual.add_opt('Drums', [0.81, 0.80, 0.82])
				elif same_inst != None: 
					b_instchan = befsame_chan[np.where(befsame_chan['inst']==same_inst)][0]
					fxchannel_obj.visual.from_dset('midi', self.device+'_inst', '0_0_'+str(same_inst), False)

			fxchannel_obj.visual.add_opt('Chan #'+str(ch_num+1), [0.1, 0.1, 0.1])


		for ch_num in range(self.song_channels):
			pitch_data = self.auto_pitch.data[np.where(self.auto_pitch.data['channel']==ch_num)]

			prevval = 0
			for pitchpoint in pitch_data:
				value = float(pitchpoint['value'])/(1365 if pitchpoint['mode'] else 8192)
				if prevval != value:
					convproj_obj.automation.add_autotick(['fxmixer', str(ch_num+1), 'pitch'], 'float', pitchpoint['pos'], value)
				prevval = value

			chan_ctrls = self.chan_ctrls[ch_num]
			for ctrlnum, autodata in chan_ctrls.items():
				autoloc, pname, addmul, defualtval = get_auto(ch_num, ctrlnum, self.fx_offset)
				i_add, i_mul = addmul
				if pname and len( np.where(autodata['pos']>=self.startpos_chan[ch_num])[0] ):
					prevval = 0
					for posval in autodata:
						value = ((posval['value']/127)+i_add)*i_mul
						if value != prevval:
							convproj_obj.automation.add_autotick(
								autoloc+[pname], 'float', 
								posval['pos'], 
								value
								)
						prevval = value

		if self.loop_start != None and self.loop_end != None: 
			convproj_obj.loop_active = True
			convproj_obj.loop_start = self.loop_start
			convproj_obj.loop_end = self.loop_end
		elif self.loop_start != None and self.loop_end == None: 
			convproj_obj.loop_active = True
			convproj_obj.loop_start = self.loop_start
			convproj_obj.loop_end = np.max(self.endpos_chan)

		if self.start_pos_est:
			self.start_pos = min(self.startpos_chan)

		if len(self.auto_timesig.data):
			ts_d = self.auto_timesig.data
			timesigm = ts_d[np.where(ts_d['pos']<=self.start_pos)]

			firstts = timesigm[-1]
			convproj_obj.timesig = [int(firstts['numerator']), int(firstts['denominator'])**2]

		if len(self.auto_bpm.data)>0:
			tb_d = self.auto_bpm.data
			tempom = tb_d[np.where(tb_d['pos']<=self.start_pos)]
			if len(tempom): convproj_obj.params.add('bpm', tempom[-1]['tempo'], 'float')
			else: convproj_obj.params.add('bpm', tb_d[0]['tempo'], 'float')
		
		convproj_obj.start_pos = self.start_pos
