# SPDX-FileCopyrightText: 2022 Colby Ray
# SPDX-License-Identifier: GPL-3.0-or-later
import json
import base64
import xml.etree.ElementTree as ET
import pathlib
import os
import struct
from functions import audio_wav
from functions import data_bytes
from functions import vst_list
from functions import vst_fx
from functions import vst_inst
from functions import vst_params

# -------------------- VST --------------------
def vst_add_param(paramlist, num, name, value):
	paramlist[str(num)] = {}
	paramlist[str(num)]['name'] = name
	paramlist[str(num)]['value'] = str(value)

# -------------------- Func Instruments --------------------
# magical8bitplug

# grace
def grace_addvalue(xmltag, name, value):
	temp_xml = ET.SubElement(xmltag, name)
	if value != None:
		temp_xml.text = value
def grace_create_main():
	gx_root = ET.Element("root")

	gx_GlobalParameters = ET.SubElement(gx_root, "GlobalParameters")
	grace_addvalue(gx_GlobalParameters, 'VoiceMode', 'Poly')
	grace_addvalue(gx_GlobalParameters, 'VoiceGlide', '0')

	gx_SampleGroup = ET.SubElement(gx_root, "SampleGroup")
	grace_addvalue(gx_SampleGroup, 'Name', 'Group 1')
	gx_VoiceParameters = ET.SubElement(gx_SampleGroup, "VoiceParameters")
	grace_addvalue(gx_VoiceParameters, 'AmpAttack', '0')
	grace_addvalue(gx_VoiceParameters, 'AmpDecay', '0')
	grace_addvalue(gx_VoiceParameters, 'AmpEnvSnap', 'SnapOff')
	grace_addvalue(gx_VoiceParameters, 'AmpHold', '0')
	grace_addvalue(gx_VoiceParameters, 'AmpRelease', '0')
	grace_addvalue(gx_VoiceParameters, 'AmpSustain', '1')
	grace_addvalue(gx_VoiceParameters, 'AmpVelocityDepth', 'Vel80')
	grace_addvalue(gx_VoiceParameters, 'Filter1KeyFollow', '0.5')
	grace_addvalue(gx_VoiceParameters, 'Filter1Par1', '0.5')
	grace_addvalue(gx_VoiceParameters, 'Filter1Par2', '0.5')
	grace_addvalue(gx_VoiceParameters, 'Filter1Par3', '0.5')
	grace_addvalue(gx_VoiceParameters, 'Filter1Par4', '1')
	grace_addvalue(gx_VoiceParameters, 'Filter1Type', 'ftNone')
	grace_addvalue(gx_VoiceParameters, 'Filter2KeyFollow', '0.5')
	grace_addvalue(gx_VoiceParameters, 'Filter2Par1', '0.5')
	grace_addvalue(gx_VoiceParameters, 'Filter2Par2', '0.5')
	grace_addvalue(gx_VoiceParameters, 'Filter2Par3', '0.5')
	grace_addvalue(gx_VoiceParameters, 'Filter2Par4', '1')
	grace_addvalue(gx_VoiceParameters, 'Filter2Type', 'ftNone')
	grace_addvalue(gx_VoiceParameters, 'FilterOutputBlend', '1')
	grace_addvalue(gx_VoiceParameters, 'FilterRouting', 'Serial')
	grace_addvalue(gx_VoiceParameters, 'Lfo1Par1', '0.5')
	grace_addvalue(gx_VoiceParameters, 'Lfo1Par2', '0.5')
	grace_addvalue(gx_VoiceParameters, 'Lfo1Par3', '0.5')
	grace_addvalue(gx_VoiceParameters, 'Lfo2Par1', '0.5')
	grace_addvalue(gx_VoiceParameters, 'Lfo2Par2', '0.5')
	grace_addvalue(gx_VoiceParameters, 'Lfo2Par3', '0.5')
	grace_addvalue(gx_VoiceParameters, 'LfoFreqMode1', 'Fixed100Millisecond')
	grace_addvalue(gx_VoiceParameters, 'LfoFreqMode2', 'Fixed100Millisecond')
	grace_addvalue(gx_VoiceParameters, 'LfoShape1', 'Triangle')
	grace_addvalue(gx_VoiceParameters, 'LfoShape2', 'Triangle')
	grace_addvalue(gx_VoiceParameters, 'LoopEnd', '1')
	grace_addvalue(gx_VoiceParameters, 'LoopStart', '0')
	grace_addvalue(gx_VoiceParameters, 'ModAttack', '0')
	grace_addvalue(gx_VoiceParameters, 'ModDecay', '0.300000011920929')
	grace_addvalue(gx_VoiceParameters, 'ModEnvSnap', 'SnapOff')
	grace_addvalue(gx_VoiceParameters, 'ModHold', '0')
	grace_addvalue(gx_VoiceParameters, 'ModRelease', '0.300000011920929')
	grace_addvalue(gx_VoiceParameters, 'ModSustain', '0.300000011920929')
	grace_addvalue(gx_VoiceParameters, 'ModVelocityDepth', 'Vel80')
	grace_addvalue(gx_VoiceParameters, 'OutputGain', '0.5')
	grace_addvalue(gx_VoiceParameters, 'OutputPan', '0.504999995231628')
	grace_addvalue(gx_VoiceParameters, 'PitchTracking', 'Note')
	grace_addvalue(gx_VoiceParameters, 'SampleEnd', '1')
	grace_addvalue(gx_VoiceParameters, 'SampleReset', 'None')
	grace_addvalue(gx_VoiceParameters, 'SamplerLoopBounds', 'LoopPoints')
	grace_addvalue(gx_VoiceParameters, 'SamplerTriggerMode', 'LoopOff')
	grace_addvalue(gx_VoiceParameters, 'SampleStart', '0')
	grace_addvalue(gx_VoiceParameters, 'Seq1Clock', 'Div_4')
	grace_addvalue(gx_VoiceParameters, 'Seq1Direction', 'Forwards')
	grace_addvalue(gx_VoiceParameters, 'Seq2Clock', 'Div_4')
	grace_addvalue(gx_VoiceParameters, 'Seq2Direction', 'Forwards')
	grace_addvalue(gx_VoiceParameters, 'StepSeq1Length', 'Eight')
	grace_addvalue(gx_VoiceParameters, 'StepSeq2Length', 'Eight')
	grace_addvalue(gx_VoiceParameters, 'VoicePitchOne', '0.5')
	grace_addvalue(gx_VoiceParameters, 'VoicePitchTwo', '0.5')

	grace_addvalue(gx_root, 'PatchFileFormatVersion', '4')
	grace_addvalue(gx_root, 'PatchFileType', 'LucidityPatchFile')

	gx_PresetInfo = ET.SubElement(gx_root, "PresetInfo")
	grace_addvalue(gx_PresetInfo, 'PresetName', 'Defualt')
	grace_addvalue(gx_PresetInfo, 'PresetFileName', None)

	gx_MidiMap = ET.SubElement(gx_root, "MidiMap")

	return gx_root
def grace_create_region(gx_root, regionparams):
	gx_SampleGroup = gx_root.findall('SampleGroup')[0]
	gx_Region = ET.SubElement(gx_SampleGroup, "Region")
	gx_RegionProp = ET.SubElement(gx_Region, "RegionProperties")
	gx_SampleProp = ET.SubElement(gx_Region, "SampleProperties")

	FileName = ''

	if 'file' in regionparams: FileName = regionparams['file']
	grace_addvalue(gx_SampleProp, 'SampleFileName', str(FileName))

	LowNote = 0
	HighNote = 127
	LowVelocity = 0
	HighVelocity = 127
	RootNote = 60
	SampleStart = 0
	SampleEnd = 0
	LoopStart = -1
	LoopEnd = -1
	
	if 'r_key' in regionparams:
		LowNote = regionparams['r_key'][0] + 60
		HighNote = regionparams['r_key'][1] + 60

	if 'r_vol' in regionparams:
		LowVelocity = int(regionparams['vol'][0]*127)
		HighVelocity = int(regionparams['vol'][1]*127)

	if 'loop' in regionparams:
		if regionparams['loop']['enabled'] == 1:
			LoopStart = regionparams['loop']['points'][0]
			LoopEnd = regionparams['loop']['points'][1]

	if 'middlenote' in regionparams: RootNote = regionparams['middlenote'] + 60
	if 'start' in regionparams: SampleStart = regionparams['start']
	if 'end' in regionparams: SampleEnd = regionparams['end'] - 1

	grace_addvalue(gx_RegionProp, 'LowNote', str(LowNote))
	grace_addvalue(gx_RegionProp, 'HighNote', str(HighNote))
	grace_addvalue(gx_RegionProp, 'LowVelocity', str(LowVelocity))
	grace_addvalue(gx_RegionProp, 'HighVelocity', str(HighVelocity))
	grace_addvalue(gx_RegionProp, 'RootNote', str(RootNote))
	grace_addvalue(gx_RegionProp, 'SampleStart', str(SampleStart))
	grace_addvalue(gx_RegionProp, 'SampleEnd', str(SampleEnd))
	grace_addvalue(gx_SampleProp, 'SampleFrames', str(SampleEnd))
	grace_addvalue(gx_RegionProp, 'LoopStart', str(LoopStart))
	grace_addvalue(gx_RegionProp, 'LoopEnd', str(LoopEnd))

	SampleVolume = 0
	SamplePan = 0
	SampleTune = 0
	SampleFine = 0

	grace_addvalue(gx_RegionProp, 'SampleVolume', str(SampleVolume))
	grace_addvalue(gx_RegionProp, 'SamplePan', str(SamplePan))
	grace_addvalue(gx_RegionProp, 'SampleTune', str(SampleTune))
	grace_addvalue(gx_RegionProp, 'SampleFine', str(SampleFine))

	SampleBeats = 4

	grace_addvalue(gx_RegionProp, 'SampleBeats', str(SampleBeats))

	return gx_root

# -------------------- Instruments --------------------
def convplug_inst(instdata, dawname, extra_json, nameid):
	m8bp_shapesupported = ['shape-square', 'shape-triangle', 'retro-noise', 'shape-pulse']
	global supportedplugins
	if 'plugin' in instdata:
		if 'plugindata' in instdata:
			pluginname = instdata['plugin']
			plugindata = instdata['plugindata']

			# ---------------------------------------- 1 ----------------------------------------
			if pluginname == 'native-fl':
				fl_plugdata = base64.b64decode(plugindata['data'])
				fl_plugstr = data_bytes.bytearray2BytesIO(base64.b64decode(plugindata['data']))
				if plugindata['name'].lower() == 'fruity soundfont player':
					flsf_unk = int.from_bytes(fl_plugstr.read(4), "little")
					flsf_patch = int.from_bytes(fl_plugstr.read(4), "little")-1
					flsf_bank = int.from_bytes(fl_plugstr.read(4), "little")
					flsf_reverb_sendlvl = int.from_bytes(fl_plugstr.read(4), "little")
					flsf_chorus_sendlvl = int.from_bytes(fl_plugstr.read(4), "little")
					flsf_mod = int.from_bytes(fl_plugstr.read(4), "little")
					flsf_asdf_A = int.from_bytes(fl_plugstr.read(4), "little") # max 5940
					flsf_asdf_D = int.from_bytes(fl_plugstr.read(4), "little") # max 5940
					flsf_asdf_S = int.from_bytes(fl_plugstr.read(4), "little") # max 127
					flsf_asdf_R = int.from_bytes(fl_plugstr.read(4), "little") # max 5940
					flsf_lfo_predelay = int.from_bytes(fl_plugstr.read(4), "little") # max 5900
					flsf_lfo_amount = int.from_bytes(fl_plugstr.read(4), "little") # max 127
					flsf_lfo_speed = int.from_bytes(fl_plugstr.read(4), "little") # max 127
					flsf_cutoff = int.from_bytes(fl_plugstr.read(4), "little") # max 127

					flsf_filelen = int.from_bytes(fl_plugstr.read(1), "little")
					flsf_filename = fl_plugstr.read(flsf_filelen).decode('utf-8')

					flsf_reverb_sendto = int.from_bytes(fl_plugstr.read(4), "little", signed="True")+1
					flsf_reverb_builtin = int.from_bytes(fl_plugstr.read(1), "little")
					flsf_chorus_sendto = int.from_bytes(fl_plugstr.read(4), "little", signed="True")+1
					flsf_reverb_builtin = int.from_bytes(fl_plugstr.read(1), "little")
					flsf_hqrender = int.from_bytes(fl_plugstr.read(1), "little")

					instdata['plugin'] = "soundfont2"
					instdata['plugindata'] = {}
					instdata['plugindata']['file'] = flsf_filename
					if flsf_patch > 127:
						instdata['plugindata']['bank'] = 128
						instdata['plugindata']['patch'] = flsf_patch-128
					else:
						instdata['plugindata']['bank'] = flsf_bank
						instdata['plugindata']['patch'] = flsf_patch
				elif plugindata['name'].lower() == 'fruity dx10':
					int.from_bytes(fl_plugstr.read(4), "little")
					fldx_amp_att = int.from_bytes(fl_plugstr.read(4), "little")/65536
					fldx_amp_dec = int.from_bytes(fl_plugstr.read(4), "little")/65536
					fldx_amp_rel = int.from_bytes(fl_plugstr.read(4), "little")/65536
					fldx_mod_course = int.from_bytes(fl_plugstr.read(4), "little")/65536
					fldx_mod_fine = int.from_bytes(fl_plugstr.read(4), "little")/65536
					fldx_mod_init = int.from_bytes(fl_plugstr.read(4), "little")/65536
					fldx_mod_time = int.from_bytes(fl_plugstr.read(4), "little")/65536
					fldx_mod_sus = int.from_bytes(fl_plugstr.read(4), "little")/65536
					fldx_mod_rel = int.from_bytes(fl_plugstr.read(4), "little")/65536
					fldx_mod_velsen = int.from_bytes(fl_plugstr.read(4), "little")/65536
					fldx_vibrato = int.from_bytes(fl_plugstr.read(4), "little")/65536
					fldx_waveform = int.from_bytes(fl_plugstr.read(4), "little")/65536
					fldx_mod_thru = int.from_bytes(fl_plugstr.read(4), "little")/65536
					fldx_lforate = int.from_bytes(fl_plugstr.read(4), "little")/65536
					fldx_mod2_course = int.from_bytes(fl_plugstr.read(4), "little")/65536
					fldx_mod2_fine = int.from_bytes(fl_plugstr.read(4), "little")/65536
					fldx_mod2_init = int.from_bytes(fl_plugstr.read(4), "little")/65536
					fldx_mod2_time = int.from_bytes(fl_plugstr.read(4), "little")/65536
					fldx_mod2_sus = int.from_bytes(fl_plugstr.read(4), "little")/65536
					fldx_mod2_rel = int.from_bytes(fl_plugstr.read(4), "little")/65536
					fldx_mod2_velsen = int.from_bytes(fl_plugstr.read(4), "little")/65536
					fldx_octave = (int.from_bytes(fl_plugstr.read(4), "little", signed="True")/6)+0.5

					vstdxparams = {}
					vstdxparams[0] = {"name": "Attack  ","value": fldx_amp_att}
					vstdxparams[1] = {"name": "Decay   ","value": fldx_amp_dec}
					vstdxparams[2] = {"name": "Release ","value": fldx_amp_rel}
					vstdxparams[3] = {"name": "Coarse  ","value": fldx_mod_course}
					vstdxparams[4] = {"name": "Fine    ","value": fldx_mod_fine}
					vstdxparams[5] = {"name": "Mod Init","value": fldx_mod_init}
					vstdxparams[6] = {"name": "Mod Dec ","value": fldx_mod_time}
					vstdxparams[7] = {"name": "Mod Sus ","value": fldx_mod_sus}
					vstdxparams[8] = {"name": "Mod Rel ","value": fldx_mod_rel}
					vstdxparams[9] = { "name": "Mod Vel ","value": fldx_mod_velsen}
					vstdxparams[10] = {"name": "Vibrato ","value": fldx_vibrato}
					vstdxparams[11] = {"name": "Octave  ","value": fldx_octave}
					vstdxparams[12] = {"name": "FineTune","value": 0.5}
					vstdxparams[13] = {"name": "Waveform","value": fldx_waveform}
					vstdxparams[14] = {"name": "Mod Thru","value": fldx_mod_thru}
					vstdxparams[15] = {"name": "LFO Rate","value": fldx_lforate}
					vst_list.replace_params(instdata, 'DX10', 16, vstdxparams)

			# ---------- from general-midi
			elif pluginname == 'general-midi':
				if 'soundfont' in extra_json:
					sffile = extra_json['soundfont']
					gmdata = instdata['plugindata']
					instdata['plugin'] = "soundfont2"
					instdata['plugindata'] = {}
					instdata['plugindata']['bank'] = gmdata['bank']
					instdata['plugindata']['patch'] = gmdata['inst']
					instdata['plugindata']['file'] = sffile
					print('[plug-conv] GM MIDI > soundfont2')
				else:
					print('[plug-conv] Soundfont argument not defined.')

			# ---------------------------------------- 2 ----------------------------------------
			pluginname = instdata['plugin']
			plugindata = instdata['plugindata']

			# -------------------- sampler > vst2 (Grace) --------------------
			if pluginname == 'sampler' and dawname not in supportedplugins['sampler']:
				sampler_data = instdata
				sampler_file_data = instdata['plugindata']
				wireturn = audio_wav.complete_wav_info(sampler_file_data)
				if vst_list.vst2path_loaded == True:
					if vst_list.ifexists_vst2('Grace') == True:
						if 'file' in sampler_file_data and wireturn != None and wireturn == 1:
							file_extension = pathlib.Path(sampler_file_data['file']).suffix
							if file_extension == '.wav':
								gx_root = grace_create_main()
								regionparams = {}
								regionparams['file'] = sampler_file_data['file']
								regionparams['length'] = sampler_file_data['length']
								regionparams['start'] = 0
								regionparams['loop'] = sampler_file_data['loop']
								regionparams['end'] = sampler_file_data['length']
								grace_create_region(gx_root, regionparams)
								xmlout = ET.tostring(gx_root, encoding='utf-8')
								vst_list.replace_data(instdata, 'Grace', xmlout)
						else:
							print("[plug-conv] Unchanged, Grace (VST2) only supports Format 1 .WAV")
					else:
						print('[plug-conv] Unchanged, Plugin Grace not Found')
				else:
					print('[plug-conv] Unchanged, VST2 list not found')

			# -------------------- sampler-multi > vst2 (Grace) --------------------

			elif pluginname == 'sampler-multi' and dawname not in supportedplugins['sampler-multi']:
				msmpl_data = instdata
				msmpl_p_data = instdata['plugindata']
				if vst_list.vst2path_loaded == True:
					if vst_list.ifexists_vst2('Grace') == True:
						regions = msmpl_p_data['regions']
						gx_root = grace_create_main()
						for regionparams in regions:
							grace_create_region(gx_root, regionparams)
						xmlout = ET.tostring(gx_root, encoding='utf-8')
						vst_list.replace_data(instdata, 'Grace', xmlout)
					else:
						print('[plug-conv] Unchanged, Plugin Grace not Found')
				else:
					print('[plug-conv] Unchanged, VST2 list not found')

			# -------------------- vst2 (juicysfplugin) --------------------

			# ---------- from native soundfont2
			elif pluginname == 'soundfont2' and dawname not in supportedplugins['sf2']:
				sf2data = instdata['plugindata']
				if 'bank' in sf2data: sf2_bank = sf2data['bank']
				else: sf2_bank = 0
				if 'patch' in sf2data: sf2_patch = sf2data['patch']
				else: sf2_params = 0
				if 'file' in sf2data: sf2_filename = sf2data['file']
				else: sf2_filename = 0
				jsfp_xml = vst_inst.juicysfplugin_create(sf2_bank, sf2_patch, sf2_filename)
				vst_list.replace_data(instdata, 'juicysfplugin', vst_params.make_vc2_xml(jsfp_xml))

			# -------------------- vst2 (magical8bitplug) --------------------

			# ---------- famistudio
			elif pluginname == 'famistudio':
				fsd_data = instdata['plugindata']
				m8p_root = ET.Element("root")
				m8p_params = ET.SubElement(m8p_root, "Params")
				vst_inst.m8bp_addvalue(m8p_params, "arpeggioDirection", 0.0)
				vst_inst.m8bp_addvalue(m8p_params, "arpeggioTime", 0.02999999932944775)
				vst_inst.m8bp_addvalue(m8p_params, "attack", 0.0)
				vst_inst.m8bp_addvalue(m8p_params, "bendRange", 12.0)
				vst_inst.m8bp_addvalue(m8p_params, "colorScheme", 1.0)
				vst_inst.m8bp_addvalue(m8p_params, "decay", 0.0)
				vst_inst.m8bp_addvalue(m8p_params, "duty", 0.0)
				vst_inst.m8bp_addvalue(m8p_params, "gain", 0.5)
				vst_inst.m8bp_addvalue(m8p_params, "isAdvancedPanelOpen_raw", 1.0)
				vst_inst.m8bp_addvalue(m8p_params, "isArpeggioEnabled_raw", 0.0)
				m8p_dutyEnv = ET.SubElement(m8p_root, "dutyEnv")
				m8p_pitchEnv = ET.SubElement(m8p_root, "pitchEnv")
				m8p_volumeEnv = ET.SubElement(m8p_root, "volumeEnv")
				for Envelope in fsd_data['Envelopes']:
					if Envelope == "DutyCycle":
						vst_inst.m8bp_addvalue(m8p_params, "isDutySequenceEnabled_raw", 1.0)
						m8p_dutyEnv.text = fsd_data['Envelopes'][Envelope]['Values']
					else: vst_inst.m8bp_addvalue(m8p_params, "isDutySequenceEnabled_raw", 0.0)
					if Envelope == "Volume":
						vst_inst.m8bp_addvalue(m8p_params, "isVolumeSequenceEnabled_raw", 1.0)
						m8p_volumeEnv.text = fsd_data['Envelopes'][Envelope]['Values']
					else: vst_inst.m8bp_addvalue(m8p_params, "isVolumeSequenceEnabled_raw", 0.0)
				vst_inst.m8bp_addvalue(m8p_params, "maxPoly", 8.0)
				vst_inst.m8bp_addvalue(m8p_params, "noiseAlgorithm_raw", 0.0)
				if fsd_data['wave'] == 'Square': vst_inst.m8bp_addvalue(m8p_params, "osc", 0.0)
				if fsd_data['wave'] == 'Triangle': vst_inst.m8bp_addvalue(m8p_params, "osc", 1.0)
				if fsd_data['wave'] == 'Noise': vst_inst.m8bp_addvalue(m8p_params, "osc", 2.0)
				vst_inst.m8bp_addvalue(m8p_params, "pitchSequenceMode_raw", 0.0)
				vst_inst.m8bp_addvalue(m8p_params, "release", 0.0)
				vst_inst.m8bp_addvalue(m8p_params, "restrictsToNESFrequency_raw", 0.0)
				vst_inst.m8bp_addvalue(m8p_params, "suslevel", 1.0)
				vst_inst.m8bp_addvalue(m8p_params, "sweepInitialPitch", 0.0)
				vst_inst.m8bp_addvalue(m8p_params, "sweepTime", 0.1000000014901161)
				vst_inst.m8bp_addvalue(m8p_params, "vibratoDelay", 0.2999999821186066)
				vst_inst.m8bp_addvalue(m8p_params, "vibratoDepth", 0.0)
				vst_inst.m8bp_addvalue(m8p_params, "vibratoIgnoresWheel_raw", 1.0)
				vst_inst.m8bp_addvalue(m8p_params, "vibratoRate", 0.1500000059604645)
				vst_list.replace_data(instdata, 'Magical 8bit Plug 2', vst_params.make_vc2_xml(m8p_root))

			# ---------- retro shapes
			elif pluginname in m8bp_shapesupported :
				m8p_root = vst_inst.shape_m8bp(pluginname, plugindata)
				vst_list.replace_data(instdata, 'Magical 8bit Plug 2', vst_params.make_vc2_xml(m8p_root))

			# -------------------- zynaddsubfx > vst2 (Zyn-Fusion) - from lmms --------------------
			elif pluginname == 'zynaddsubfx-lmms' and dawname != 'lmms':
				zasfxdata = instdata['plugindata']['data']
				zasfxdatastart = '<?xml version="1.0" encoding="UTF-8"?><!DOCTYPE ZynAddSubFX-data>' 
				zasfxdatafixed = zasfxdatastart.encode('utf-8') + base64.b64decode(zasfxdata)
				vst_list.replace_data(instdata, 'ZynAddSubFX', zasfxdatafixed)
			else:
				print('[plug-conv] Unchanged')

# -------------------- FX --------------------
def convplug_fx(fxdata, dawname, extra_json, nameid):
	global supportedplugins
	if 'plugin' in fxdata:
		if 'plugindata' in fxdata:
			pluginname = fxdata['plugin']
			plugindata = fxdata['plugindata']
			if pluginname == 'native-lmms':
				mmp_plugname = plugindata['name']
				mmp_plugdata = plugindata['data']
				# -------------------- waveshaper > vst2 (Wolf Shaper) - from lmms --------------------
				if mmp_plugname == 'waveshaper':
					waveshapebytes = base64.b64decode(plugindata['data']['waveShape'])
					waveshapepoints = [struct.unpack('f', waveshapebytes[i:i+4]) for i in range(0, len(waveshapebytes), 4)]
					vst_fx.wolfshaper_init()
					for pointnum in range(50):
						pointdata = waveshapepoints[pointnum*4][0]
						vst_fx.wolfshaper_addpoint(pointnum/49,pointdata,0.5,0)
					vst_fx.wolfshaper_get()
					vst_list.replace_data(fxdata, 'Wolf Shaper', vst_params.make_nullbytegroup(vst_fx.wolfshaper_get()))
			else:
				print('[plug-conv] Unchanged')

# -------------------- convproj --------------------
def do_fxchain(fxchain, dawname, extra_json, nameid):
	for fxslot in fxchain:
		convplug_fx(fxslot, dawname, extra_json, nameid)

def convproj(cvpjdata, in_type, out_type, dawname, extra_json):
	global supportedplugins
	vst_list.listinit('windows')
	supportedplugins = {}
	supportedplugins['sf2'] = ['cvpj', 'cvpj_r', 'cvpj_s', 'cvpj_m', 'cvpj_mi', 'lmms', 'flp']
	supportedplugins['sampler'] = ['cvpj', 'cvpj_r', 'cvpj_s', 'cvpj_m', 'cvpj_mi', 'lmms', 'flp']
	supportedplugins['sampler-multi'] = ['cvpj', 'cvpj_r', 'cvpj_s', 'cvpj_m', 'cvpj_mi', 'ableton']
	cvpj_l = json.loads(cvpjdata)
	if out_type != 'debug':
		if in_type == 'r':
			if 'trackdata' in cvpj_l:
				for track in cvpj_l['trackdata']:
					trackdata = cvpj_l['trackdata'][track]
					if 'type' in trackdata:
						if trackdata['type'] == 'instrument':
							if 'instdata' in trackdata:
								instdata = trackdata['instdata']
								print('[plug-conv] --- Inst: '+track)
								convplug_inst(instdata, dawname, extra_json, track)
		if in_type == 'm' or in_type == 'mi':
			if 'instruments' in cvpj_l:
				for track in cvpj_l['instruments']:
					trackdata = cvpj_l['instruments'][track]
					if 'instdata' in trackdata:
						instdata = trackdata['instdata']
						print('[plug-conv] --- Inst: '+track)
						convplug_inst(instdata, dawname, extra_json, track)
		if 'fxrack' in cvpj_l:
			for fxid in cvpj_l['fxrack']:
				fxiddata = cvpj_l['fxrack'][fxid]
				if 'fxchain' in fxiddata:
					fxchain = fxiddata['fxchain']
					print('[plug-conv] --- FX: '+fxid)
					do_fxchain(fxchain, dawname, extra_json, fxid)
		return json.dumps(cvpj_l, indent=2)