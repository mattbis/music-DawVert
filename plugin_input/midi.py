# SPDX-FileCopyrightText: 2022 Colby Ray
# SPDX-License-Identifier: GPL-3.0-or-later

import plugin_input
import os.path
import json
import mido
from mido import MidiFile
from functions import note_convert

MIDIInstNames = ["Acoustic Grand Piano", "Bright Acoustic Piano", "Electric Grand Piano", "Honky-tonk Piano", "Electric Piano 1", "Electric Piano 2", "Harpsichord", "Clavi", "Celesta", "Glockenspiel", "Music Box", "Vibraphone", "Marimba", "Xylophone", "Tubular Bells", "Dulcimer", "Drawbar Organ", "Percussive Organ", "Rock Organ", "Church Organ", "Reed Organ", "Accordion", "Harmonica", "Tango Accordion", "Acoustic Guitar (nylon)", "Acoustic Guitar (steel)", "Electric Guitar (jazz)", "Electric Guitar (clean)", "Electric Guitar (muted)", "Overdriven Guitar", "Distortion Guitar", "Guitar harmonics", "Acoustic Bass", "Electric Bass (finger)", "Electric Bass (pick)", "Fretless Bass", "Slap Bass 1", "Slap Bass 2", "Synth Bass 1", "Synth Bass 2", "Violin", "Viola", "Cello", "Contrabass", "Tremolo Strings", "Pizzicato Strings", "Orchestral Harp", "Timpani", "String Ensemble 1", "String Ensemble 2", "SynthStrings 1", "SynthStrings 2", "Choir Aahs", "Voice Oohs", "Synth Voice", "Orchestra Hit", "Trumpet", "Trombone", "Tuba", "Muted Trumpet", "French Horn", "Brass Section", "SynthBrass 1", "SynthBrass 2", "Soprano Sax", "Alto Sax", "Tenor Sax", "Baritone Sax", "Oboe", "English Horn", "Bassoon", "Clarinet", "Piccolo", "Flute", "Recorder", "Pan Flute", "Blown Bottle", "Shakuhachi", "Whistle", "Ocarina", "Lead 1 (square)", "Lead 2 (sawtooth)", "Lead 3 (calliope)", "Lead 4 (chiff)", "Lead 5 (charang)", "Lead 6 (voice)", "Lead 7 (fifths)", "Lead 8 (bass + lead)", "Pad 1 (new age)", "Pad 2 (warm)", "Pad 3 (polysynth)", "Pad 4 (choir)", "Pad 5 (bowed)", "Pad 6 (metallic)", "Pad 7 (halo)", "Pad 8 (sweep)", "FX 1 (rain)", "FX 2 (soundtrack)", "FX 3 (crystal)", "FX 4 (atmosphere)", "FX 5 (brightness)", "FX 6 (goblins)", "FX 7 (echoes)", "FX 8 (sci-fi)", "Sitar", "Banjo", "Shamisen", "Koto", "Kalimba", "Bag pipe", "Fiddle", "Shanai", "Tinkle Bell", "Agogo", "Steel Drums", "Woodblock", "Taiko Drum", "Melodic Tom", "Synth Drum", "Reverse Cymbal", "Guitar Fret Noise", "Breath Noise", "Seashore", "Bird Tweet", "Telephone Ring", "Helicopter", "Applause", "Gunshot"]
MIDIDrumNames = {0:'Drums', 8:'Room Drums', 16:'Power Drums', 24:'Elec Drums', 25:'TR808 Drums', 32:'Jazz Drums', 40:'Brush Drums', 48:'Orchestra Drums', 56:'Sound FX', 127:'MT-32 Drums'}

MIDIInstColors = [[0.10, 0.11, 0.11], #Acoustic Grand Piano
 [0.10, 0.11, 0.11], #Bright Acoustic Piano
 [0.10, 0.11, 0.11], #Electric Grand Piano
 [0.60, 0.19, 0.07], #Honky-tonk Piano
 [0.29, 0.28, 0.28], #Electric Piano 1
 [0.29, 0.28, 0.28], #Electric Piano 2
 [0.57, 0.31, 0.17], #Harpsichord
 [0.59, 0.44, 0.35], #Clavi
 [0.84, 0.68, 0.48], #Celesta
 [0.84, 0.85, 0.87], #Glockenspiel
 [0.60, 0.58, 0.55], #Music Box
 [0.76, 0.78, 0.82], #Vibraphone
 [0.82, 0.32, 0.18], #Marimba
 [0.42, 0.19, 0.13], #Xylophone
 [0.53, 0.58, 0.64], #Tubular Bells
 [0.69, 0.34, 0.08], #Dulcimer
 [0.76, 0.44, 0.15], #Drawbar Organ
 [0.76, 0.44, 0.15], #Percussive Organ
 [0.76, 0.44, 0.15], #Rock Organ
 [0.55, 0.24, 0.08], #Church Organ
 [0.44, 0.15, 0.04], #Reed Organ
 [0.27, 0.25, 0.23], #Accordion
 [0.70, 0.70, 0.66], #Harmonica
 [0.27, 0.25, 0.23], #Tango Accordion
 [0.84, 0.35, 0.00], #Acoustic Guitar (nylon)
 [0.90, 0.62, 0.35], #Acoustic Guitar (steel)
 [0.00, 0.11, 0.33], #Electric Guitar (jazz)
 [0.00, 0.11, 0.33], #Electric Guitar (clean)
 [0.00, 0.11, 0.33], #Electric Guitar (muted)
 [0.90, 0.62, 0.35], #Overdriven Guitar
 [0.90, 0.62, 0.35], #Distortion Guitar
 [0.90, 0.62, 0.35], #Guitar harmonics
 [0.15, 0.15, 0.15], #Acoustic Bass
 [0.09, 0.09, 0.09], #Electric Bass (finger)
 [0.09, 0.09, 0.09], #Electric Bass (pick)
 [0.89, 0.71, 0.53], #Fretless Bass
 [0.89, 0.71, 0.53], #Slap Bass 1
 [0.89, 0.71, 0.53], #Slap Bass 2
 [0.17, 0.16, 0.19], #Synth Bass 1
 [0.17, 0.16, 0.19], #Synth Bass 2
 [0.58, 0.32, 0.14], #Violin
 [0.75, 0.29, 0.00], #Viola
 [0.69, 0.24, 0.01], #Cello
 [0.63, 0.20, 0.08], #Contrabass
 [0.41, 0.06, 0.02], #Tremolo Strings
 [0.41, 0.06, 0.02], #Pizzicato Strings
 [0.58, 0.20, 0.12], #Orchestral Harp
 [0.81, 0.78, 0.71], #Timpani
 [0.41, 0.06, 0.02], #String Ensemble 1
 [0.41, 0.06, 0.02], #String Ensemble 2
 [0.42, 0.23, 0.11], #SynthStrings 1
 [0.42, 0.23, 0.11], #SynthStrings 2
 [0.94, 0.76, 0.70], #Choir Aahs
 [0.94, 0.76, 0.70], #Voice Oohs
 [0.23, 0.23, 0.24], #Synth Voice
 [0.60, 0.18, 0.07], #Orchestra Hit
 [0.75, 0.59, 0.27], #Trumpet
 [0.94, 0.87, 0.47], #Trombone
 [0.85, 0.68, 0.35], #Tuba
 [0.75, 0.59, 0.27], #Muted Trumpet
 [0.85, 0.65, 0.29],  #French Horn
 [0.38, 0.22, 0.06], #Brass Section
 [0.42, 0.23, 0.11], #SynthBrass 1
 [0.42, 0.23, 0.11], #SynthBrass 2
 [0.84, 0.69, 0.41], #Soprano Sax
 [0.71, 0.55, 0.22], #Alto Sax
 [0.74, 0.55, 0.20], #Tenor Sax
 [0.88, 0.68, 0.36], #Baritone Sax
 [0.19, 0.19, 0.20], #Oboe
 [0.10, 0.09, 0.11], #English Horn
 [0.76, 0.15, 0.04], #Bassoon
 [0.27, 0.27, 0.27], #Clarinet
 [0.07, 0.07, 0.10], #Piccolo
 [0.73, 0.72, 0.72], #Flute
 [0.87, 0.71, 0.60], #Recorder
 [0.68, 0.54, 0.30], #Pan Flute
 [0.45, 0.41, 0.01], #Blown Bottle
 [0.61, 0.50, 0.35], #Shakuhachi
 [0.84, 0.25, 0.07], #Whistle
 [0.10, 0.32, 0.74], #Ocarina
 [0.70, 0.70, 0.70], #Lead 1 (square)
 [0.70, 0.70, 0.70], #Lead 2 (sawtooth)
 [0.70, 0.70, 0.70], #Lead 3 (calliope)
 [0.70, 0.70, 0.70], #Lead 4 (chiff)
 [0.70, 0.70, 0.70], #Lead 5 (charang)
 [0.70, 0.70, 0.70], #Lead 6 (voice)
 [0.70, 0.70, 0.70], #Lead 7 (fifths)
 [0.70, 0.70, 0.70], #Lead 8 (bass + lead)
 [0.70, 0.70, 0.70], #Pad 1 (new age)
 [0.70, 0.70, 0.70], #Pad 2 (warm)
 [0.70, 0.70, 0.70], #Pad 3 (polysynth)
 [0.70, 0.70, 0.70], #Pad 4 (choir)
 [0.70, 0.70, 0.70], #Pad 5 (bowed)
 [0.70, 0.70, 0.70], #Pad 6 (metallic)
 [0.70, 0.70, 0.70], #Pad 7 (halo)
 [0.70, 0.70, 0.70], #Pad 8 (sweep)
 [0.70, 0.70, 0.70], #FX 1 (rain)
 [0.70, 0.70, 0.70], #FX 2 (soundtrack)
 [0.70, 0.70, 0.70], #FX 3 (crystal)
 [0.70, 0.70, 0.70], #FX 4 (atmosphere)
 [0.70, 0.70, 0.70], #FX 5 (brightness)
 [0.70, 0.70, 0.70], #FX 6 (goblins)
 [0.70, 0.70, 0.70], #FX 7 (echoes)
 [0.70, 0.70, 0.70], #FX 8 (sci-fi)
 [0.40, 0.20, 0.12], #Sitar
 [0.50, 0.32, 0.20], #Banjo
 [0.45, 0.18, 0.15], #Shamisen
 [0.45, 0.16, 0.11], #Koto
 [0.69, 0.27, 0.16], #Kalimba
 [0.71, 0.15, 0.15], #Bag pipe
 [0.76, 0.30, 0.01], #Fiddle
 [0.66, 0.16, 0.12], #Shanai
 [0.67, 0.45, 0.15], #Tinkle Bell
 [0.10, 0.10, 0.05], #Agogo
 [0.56, 0.57, 0.57], #Steel Drums
 [0.88, 0.68, 0.44], #Woodblock
 [0.36, 0.07, 0.00], #Taiko Drum
 [0.84, 0.77, 0.71], #Melodic Tom
 [0.77, 0.04, 0.03], #Synth Drum
 [0.71, 0.61, 0.36], #Reverse Cymbal
 [0.90, 0.62, 0.35], #Guitar Fret Noise
 [0.94, 0.76, 0.70], #Breath Noise
 [0.23, 0.55, 0.53], #Seashore
 [0.89, 0.81, 0.18], #Bird Tweet
 [0.21, 0.19, 0.15], #Telephone Ring
 [0.18, 0.26, 0.67], #Helicopter
 [0.94, 0.76, 0.70], #Applause
 [0.32, 0.30, 0.27] #Gunshot
 ]





def addtoalltables(contents):
    global t_tn_ch
    for TimedNoteChannel in t_tn_ch:
        TimedNoteChannel.append(contents)

class input_midi(plugin_input.base):
    def __init__(self): pass
    def getshortname(self): return 'midi'
    def getname(self): return 'MIDI'
    def gettype(self): return 'm'
    def supported_autodetect(self): return True
    def detect(self, input_file):
        bytestream = open(input_file, 'rb')
        bytestream.seek(0)
        bytesdata = bytestream.read(4)
        if bytesdata == b'MThd': return True
        else: return False
        bytestream.seek(0)

    def parse(self, input_file, extra_param):
        midifile = MidiFile(input_file, clip=True)
        ppq = midifile.ticks_per_beat
        print("[input-midi] PPQ: " + str(ppq))
        midi_bpm = 120
        midi_numerator = 4
        midi_denominator = 4
        num_tracks = len(midifile.tracks)

        cvpj_songname = None
        cvpj_copyright = None

        t_tracknum = 0
        t_playlistnum = 0

        cvpj_l = {}
        cvpj_l_playlist = {}
        cvpj_l_instruments = {}
        cvpj_l_instrumentsorder = []
        cvpj_l_fxrack = {}

        global t_tn_ch

        for track in midifile.tracks:
            midi_trackname = None

            t_tracknum += 1
            cmd_before_note = True

            t_tn_ch = []
            for _ in range(16): t_tn_ch.append([])

            t_ch_inst = []
            for _ in range(16): t_ch_inst.append([])

            t_def_ch = []
            for _ in range(16): t_def_ch.append(0)

            t_ch_auto = []
            for _ in range(16): t_ch_auto.append([])

            for midi_channum in range(16):
                t_tn_ch[midi_channum].append('instrument;' + str(0))

            for msg in track:
                if msg.type == 'track_name' and cmd_before_note == 1:
                    if num_tracks != 1: midi_trackname = msg.name.rstrip().rstrip('\x00')
                    else: cvpj_songname = msg.name.rstrip().rstrip('\x00')

                if msg.type == 'copyright' and cmd_before_note == 1:
                    cvpj_copyright = msg.text.rstrip()

                if msg.type == 'set_tempo' and cmd_before_note == 1:
                    midi_bpm = mido.tempo2bpm(msg.tempo)

                if msg.type == 'time_signature' and cmd_before_note == 1:
                    midi_numerator = msg.numerator
                    midi_denominator = msg.denominator

                if msg.time != 0:
                    addtoalltables('break;' + str((msg.time/ppq)*4))

                if msg.type == 'note_on':
                    cmd_before_note = 0
                    t_def_ch[msg.channel] = 1
                    if msg.velocity == 0: t_tn_ch[msg.channel].append('note_off;' + str(msg.note-60))
                    else: t_tn_ch[msg.channel].append('note_on;' + str(msg.note-60) + ',' + str(msg.velocity/127))

                if msg.type == 'note_off':
                    t_def_ch[msg.channel] = 1
                    t_tn_ch[msg.channel].append('note_off;' + str(msg.note-60))

                if msg.type == 'program_change':
                    if msg.program+1 not in t_ch_inst[msg.channel]: t_ch_inst[msg.channel].append(msg.program)
                    t_tn_ch[msg.channel].append('instrument;' + str(msg.program))

            for midi_channum in range(16):
                t_instlist = t_ch_inst[midi_channum]
                if t_def_ch[midi_channum] == 1:
                    print("[input-midi] Track " + str(t_tracknum) + ", Channel " + str(midi_channum+1))
                    note_convert.timednotes2notelistplacement_track_start()

                    t_playlistnum += 1
                    playlistrowdata = {}
                    placements = note_convert.timednotes2notelistplacement_parse_timednotes(t_tn_ch[midi_channum], 't'+str(t_tracknum)+'_c'+str(midi_channum+1)+'_i')

                    if midi_trackname != None:
                        playlistrowdata['name'] = str(midi_trackname)+' [Ch'+str(midi_channum+1)+']'
                    else:
                        playlistrowdata['name'] = '[Ch'+str(midi_channum+1)+']'
                    playlistrowdata['color'] = [0.3, 0.3, 0.3]
                    playlistrowdata['placements'] = placements
                    cvpj_l_playlist[str(t_playlistnum)] = playlistrowdata

                for inst in t_instlist:
                    cvpj_trackid = 't'+str(t_tracknum)+'_c'+str(midi_channum+1)+'_i'+str(inst)
                    cvpj_l_instruments[cvpj_trackid] = {}
                    cvpj_trackdata = cvpj_l_instruments[cvpj_trackid]
                    cvpj_trackdata["instdata"] = {}
                    cvpj_trackdata["vol"] = 1.0
                    cvpj_trackdata['fxrack_channel'] = midi_channum+1
                    cvpj_instdata = cvpj_trackdata["instdata"]
                    cvpj_instdata['plugin'] = 'general-midi'
                    if midi_channum != 9:
                        cvpj_instdata['plugindata'] = {'bank':0, 'inst':inst}
                        cvpj_trackdata["name"] = MIDIInstNames[inst]+' [Trk'+str(t_tracknum)+' Ch'+str(midi_channum+1)+']'
                        #cvpj_trackdata["color"] = MIDIInstColors[inst]
                    else:
                        cvpj_instdata['plugindata'] = {'bank':128, 'inst':inst}
                        if inst in MIDIDrumNames:
                            cvpj_trackdata["name"] = MIDIDrumNames[inst]+' [Trk'+str(t_tracknum)+']'
                        else:
                            cvpj_trackdata["name"] = 'Drums [Trk'+str(t_tracknum)+']'
                    cvpj_l_instruments[cvpj_trackid] = cvpj_trackdata
                    cvpj_l_instrumentsorder.append(cvpj_trackid)

        cvpj_l_fxrack["0"] = {}
        cvpj_l_fxrack["0"]["name"] = "Master"

        for midi_channum in range(16):
            cvpj_l_fxrack[str(midi_channum+1)] = {}
            fxdata = cvpj_l_fxrack[str(midi_channum+1)]
            fxdata["fxenabled"] = 1
            fxdata['color'] = [0.3, 0.3, 0.3]
            fxdata["name"] = "Channel "+str(midi_channum+1)

        cvpj_l['fxrack'] = cvpj_l_fxrack
        cvpj_l['instruments'] = cvpj_l_instruments
        cvpj_l['instrumentsorder'] = cvpj_l_instrumentsorder
        cvpj_l['playlist'] = cvpj_l_playlist
        cvpj_l['bpm'] = midi_bpm

        return json.dumps(cvpj_l)