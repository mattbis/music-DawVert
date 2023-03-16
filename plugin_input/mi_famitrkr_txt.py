# SPDX-FileCopyrightText: 2023 SatyrDiamond
# SPDX-License-Identifier: GPL-3.0-or-later

from functions import data_bytes
from functions import song_tracker
import plugin_input
import json

def hextoint(value):
    return int(value, 16)

keytable_vals = [0,2,4,5,7,9,11]
keytable = ['C','D','E','F','G','A','B']

mt_type_colors = {}
mt_type_colors['Square1'] = [0.97, 0.56, 0.36]
mt_type_colors['Square2'] = [0.97, 0.56, 0.36]
mt_type_colors['Triangle'] = [0.94, 0.33, 0.58]
mt_type_colors['Noise'] = [0.33, 0.74, 0.90]
mt_type_colors['FDS'] = [0.94, 0.94, 0.65]
mt_type_colors['DPCM'] = [0.48, 0.83, 0.49]
mt_type_colors['VRC7FM'] = [1.00, 0.46, 0.44]
mt_type_colors['VRC6Square'] = [0.60, 0.44, 0.93]
mt_type_colors['VRC6Saw'] = [0.46, 0.52, 0.91]
mt_type_colors['S5B'] = [0.58, 0.94, 0.33]
mt_type_colors['N163'] = [0.97, 0.97, 0.36]

chipname = {}
chipname['pulse'] = 'Pulse'
chipname['noise'] = 'Noise'
chipname['triangle'] = 'Triangle'
chipname['pcm'] = 'DPCM'
chipname['saw'] = 'Saw'
chipname['fds'] = 'FDS'
chipname['VRC7FM'] = 'VRC7FM'
chipname['namco'] = 'N163'

def setmacro(cvpj_plugdata, listname, macro_list, famitrkr_instdata_macro_id):
    if famitrkr_instdata_macro_id in macro_list:
        cvpj_plugdata[listname] = macro_list[famitrkr_instdata_macro_id]

def parsecell(celldata):
    cellsplit = celldata.split(' ')

    cellsplit_key = cellsplit[0]
    cellsplit_inst = cellsplit[1]
    cellsplit_vol = cellsplit[2]

    cellsplit_key_note = cellsplit_key[0]
    cellsplit_key_sharp = cellsplit_key[1]
    cellsplit_key_oct = cellsplit_key[2]

    out_cell = [{},[None, None, {}, {}]]

    if cellsplit_key == '---':
        out_cell[1][0] = 'Off'
    elif cellsplit_key == '===':
        out_cell[1][0] = 'Off'
    elif cellsplit_key != '...':
        out_note = 0
        if cellsplit_key_oct != '#':
            out_note += keytable_vals[keytable.index(cellsplit_key_note)]
            out_note += (int(cellsplit_key_oct)-3)*12
            if cellsplit_key_sharp == '#': out_note += 1
            out_cell[1][0] = out_note

    if cellsplit_inst != '..':
        out_cell[1][1] = hextoint(cellsplit_inst)

    if cellsplit_vol != '.':
        out_cell[1][2]['vol'] = hextoint(cellsplit_vol)/15

    return(out_cell)

retroinst_names = ['Square1','Square2','Triangle','Noise']

class input_famitrkr_txt(plugin_input.base):
    def __init__(self): pass
    def is_dawvert_plugin(self): return 'input'
    def getshortname(self): return 'famitrkr_txt'
    def getname(self): return 'famitrkr_txt'
    def gettype(self): return 'mi'
    def supported_autodetect(self): return False
    def parse(self, input_file, extra_param):
        f_smp = open(input_file, 'r')
        lines_smp = f_smp.readlines()

        if 'songnum' in extra_param: selectedsong = int(extra_param['songnum'])
        else: selectedsong = 1

        songnum = 1

        mt_pat = {}
        mt_ord = {}
        mt_ch_insttype = ['Square1','Square2','Triangle','Noise','DPCM']
        mt_ch_names = ['Square1','Square2','Triangle','Noise','DPCM']

        cur_pattern = 1

        i_trackactive = False
        ft_info_main_title = ''
        ft_info_title = ''
        ft_info_author = ''
        ft_info_copyright = ''
        famitrkr_instdata = {}
        t_patterndata = {}

        song_tempo = 150
        song_speed = 3
        song_rows = 64

        macro_vol = {}
        macro_arp = {}
        macro_pitch = {}
        macro_hipitch = {}
        macro_duty = {}

        inst_name = {}

        for line in lines_smp:
            ft_cmd_data = line.strip().split(' ', 1)

            #print(ft_cmd_data)
            if ft_cmd_data[0] == 'TITLE':
                ft_info_main_title = ft_cmd_data[1].split('"')[1::2][0]
                print('[input-famitracker_txt] Title: ' + ft_info_main_title)

            if ft_cmd_data[0] == 'MACRO':
                macrodata = ft_cmd_data[1].split(' : ')
                if len(macrodata) > 1:
                    macrotxt, macroseq = macrodata
                    macroseq = [int(i) for i in macroseq.split()]
                    macrovals = macrotxt.strip().split()
                    microtype = int(macrovals[0])
                    macroid = int(macrovals[1])
                    macroloop = int(macrovals[2])
                    macrorelease = int(macrovals[3])
                    env_data = {}
                    env_data['values'] = macroseq
                    if macrorelease != -1: env_data['release'] = macrorelease
                    if macroloop != -1: env_data['loop'] = macroloop
                    if microtype == 0: macro_vol[macroid] = env_data
                    if microtype == 1: macro_arp[macroid] = env_data
                    if microtype == 2: macro_pitch[macroid] = env_data
                    if microtype == 3: macro_hipitch[macroid] = env_data
                    if microtype == 4: macro_duty[macroid] = env_data

            if ft_cmd_data[0] == 'AUTHOR':
                ft_info_author = ft_cmd_data[1].split('"')[1::2][0]
                print('[input-famitracker_txt] Author: ' + ft_info_author)

            if ft_cmd_data[0] == 'COPYRIGHT':
                ft_info_copyright = ft_cmd_data[1].split('"')[1::2][0]
                print('[input-famitracker_txt] Copyright: ' + ft_info_copyright)

            if ft_cmd_data[0] == 'EXPANSION':
                ft_info_expansion = int(ft_cmd_data[1].split()[0])
                print('[input-famitracker_txt] Expansion: ' + str(ft_info_expansion))
                if ft_info_expansion == 0:
                    mt_ch_insttype = ['Square1','Square2','Triangle','Noise','DPCM']
                    mt_ch_names = ['Square1','Square2','Triangle','Noise','DPCM']
                if ft_info_expansion == 1:
                    mt_ch_insttype = ['Square1','Square2','Triangle','Noise','DPCM','VRC6Square','VRC6Square','VRC6Saw']
                    mt_ch_names = ['Square1','Square2','Triangle','Noise','DPCM','VRC6Square','VRC6Square','VRC6Saw']
                if ft_info_expansion == 2:
                    mt_ch_insttype = ['Square1','Square2','Triangle','Noise','DPCM','VRC7FM','VRC7FM','VRC7FM','VRC7FM','VRC7FM','VRC7FM']
                    mt_ch_names = ['Square1','Square2','Triangle','Noise','DPCM','VRC7FM','VRC7FM','VRC7FM','VRC7FM','VRC7FM','VRC7FM']
                if ft_info_expansion == 4:
                    mt_ch_insttype = ['Square1','Square2','Triangle','Noise','DPCM','FDS']
                    mt_ch_names = ['Square1','Square2','Triangle','Noise','DPCM','FDS']
                if ft_info_expansion == 8:
                    mt_ch_insttype = ['Square1','Square2','Triangle','Noise','DPCM','VRC6Square','VRC6Square']
                    mt_ch_names = ['Square1','Square2','Triangle','Noise','DPCM','VRC6Square','VRC6Square']
                if ft_info_expansion == 16:
                    mt_ch_insttype = ['Square1','Square2','Triangle','Noise','DPCM','N163']
                    mt_ch_names = ['Square1','Square2','Triangle','Noise','DPCM','N163']

                for chnum in range(len(mt_ch_insttype)):
                    mt_ord[chnum] = []
                    mt_pat[chnum] = {}

            if ft_cmd_data[0] == 'INST2A03':
                t_instdata = ft_cmd_data[1].split('"')[:2]
                t_instdata_nums = t_instdata[0].split()
                t_instdata_name = t_instdata[1]

                inst_id = int(t_instdata_nums[0])
                inst_macro_vol = int(t_instdata_nums[1])
                inst_macro_arp = int(t_instdata_nums[2])
                inst_macro_pitch = int(t_instdata_nums[3])
                inst_macro_hipitch = int(t_instdata_nums[4])
                inst_macro_duty = int(t_instdata_nums[5])

                famitrkr_instdata[inst_id] = [t_instdata_name, inst_macro_vol, inst_macro_arp, inst_macro_pitch, inst_macro_hipitch, inst_macro_duty]

                print('[input-famitracker_txt] Inst #' + str(inst_id) + ' (' + t_instdata_name + ')')

            if ft_cmd_data[0] == 'TRACK':
                t_trackdata = ft_cmd_data[1].split('"')[:2]
                ft_info_title = t_trackdata[1]
                print('[input-famitracker_txt] Song #' + str(songnum) + ' (' + ft_info_title + ')')
                if selectedsong == songnum: 
                    i_trackactive = True
                    t_trackdata_nums = t_trackdata[0].split()
                    song_rows = int(t_trackdata_nums[0])
                    song_speed = int(t_trackdata_nums[1])
                    song_tempo = int(t_trackdata_nums[2])
                    print('[input-famitracker_txt]     Tempo: ' + str(song_tempo) + ' | Speed: ' + str(song_speed) + ' | Rows: ' + str(song_rows))
                else: i_trackactive = False
                songnum += 1

            if i_trackactive == True:

                if ft_cmd_data[0] == 'ORDER':
                    t_tracks_order_sep = ft_cmd_data[1].split(':')
                    t_tracks_ordernum = hextoint(t_tracks_order_sep[0])
                    t_tracks_orderdata = t_tracks_order_sep[1].split()
                    for i in range(0, len(t_tracks_orderdata)): t_tracks_orderdata[i] = hextoint(t_tracks_orderdata[i])

                    for chnum in range(len(t_tracks_orderdata)):
                        mt_ord[chnum].append(t_tracks_orderdata[chnum])

                if ft_cmd_data[0] == 'PATTERN':
                    cur_pattern = hextoint(ft_cmd_data[1])
                    print('[input-famitracker_txt]     Pattern #' + str(cur_pattern+1))
                    t_patterndata[cur_pattern] = {}

                if ft_cmd_data[0] == 'ROW':
                    row_tab = ft_cmd_data[1].split(' : ')
                    row_num = hextoint(row_tab[0])+1
                    row_data = row_tab[1:]
                    t_patterndata[cur_pattern][row_num] = row_data

        for patnum in t_patterndata:
            for chnum in range(len(mt_ch_insttype)):
                mt_pat[chnum][patnum] = []
                for _ in range(song_rows): mt_pat[chnum][patnum].append([{},[None, None, {}, {}]])

        for patnum in t_patterndata:
            s_patdata = t_patterndata[patnum]
            #print('-----', patnum)
            for rownum in range(song_rows): 
                if rownum+1 in s_patdata:
                    #print(rownum+1, s_patdata[rownum+1])
                    for chnum in range(len(s_patdata[rownum+1])):
                        mt_pat[chnum][patnum][rownum] = parsecell(s_patdata[rownum+1][chnum])

        cvpj_l = {}
        cvpj_l_instrument_data = {}
        cvpj_l_instrument_order = []

        song_tracker.multi_convert(cvpj_l, song_rows, mt_pat, mt_ord, mt_ch_insttype, mt_ch_names, mt_type_colors)

        total_used_instruments = song_tracker.get_multi_used_instruments()

        for total_used_instrument in total_used_instruments:
            insttype = total_used_instrument[0]
            instid = total_used_instrument[1]

            cvpj_instid = insttype+'_'+instid
            cvpj_inst = {}
            cvpj_inst["pan"] = 0.0
            cvpj_inst["vol"] = 1.0
            cvpj_inst["instdata"] = {}
            if insttype in mt_type_colors:
                cvpj_inst["color"] = mt_type_colors[insttype]
            if int(instid) in famitrkr_instdata:
                cvpj_inst["name"] = insttype+'-'+famitrkr_instdata[int(instid)][0]
                if insttype in retroinst_names:
                    cvpj_inst["instdata"]["plugin"] = 'retro'
                    cvpj_inst["instdata"]["plugindata"] = {}
                    cvpj_plugdata = cvpj_inst["instdata"]["plugindata"]
                    if insttype == 'Square1' or insttype == 'Square2':
                        cvpj_plugdata["wave"] = "square"
                    if insttype == 'Triangle':
                        cvpj_plugdata["wave"] = "triangle"
                    if insttype == 'Noise':
                        cvpj_plugdata["wave"] = "noise"
                    setmacro(cvpj_plugdata, "env_vol", macro_vol, famitrkr_instdata[int(instid)][1]) 
                    setmacro(cvpj_plugdata, "env_arp", macro_arp, famitrkr_instdata[int(instid)][2]) 
                    setmacro(cvpj_plugdata, "env_pitch", macro_pitch, famitrkr_instdata[int(instid)][3]) 
                    setmacro(cvpj_plugdata, "env_hipitch", macro_hipitch, famitrkr_instdata[int(instid)][4])
                    setmacro(cvpj_plugdata, "env_duty", macro_duty, famitrkr_instdata[int(instid)][5]) 
                    print(famitrkr_instdata[int(instid)])
            else:
                cvpj_inst["name"] = insttype+'_'+instid
                cvpj_inst["instdata"]["plugin"] = 'none'
                cvpj_inst["instdata"]["plugindata"] = {}


            cvpj_l_instrument_data[cvpj_instid] = cvpj_inst
            cvpj_l_instrument_order.append(cvpj_instid)

        cvpj_l['do_addwrap'] = True
        cvpj_l['do_lanefit'] = True
        
        cvpj_l['use_instrack'] = False
        cvpj_l['use_fxrack'] = False

        cvpj_l['instruments_data'] = cvpj_l_instrument_data
        cvpj_l['instruments_order'] = cvpj_l_instrument_order
        
        cvpj_l['bpm'] = song_tempo
        return json.dumps(cvpj_l)