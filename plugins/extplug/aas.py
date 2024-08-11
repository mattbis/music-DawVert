# SPDX-FileCopyrightText: 2024 SatyrDiamond
# SPDX-License-Identifier: GPL-3.0-or-later

import plugins
import lxml.etree as ET
from objects import globalstore
from functions import data_xml
from functions_plugin_ext import data_vc2xml
from functions_plugin_ext import plugin_vst2

class extplugin(plugins.base):
	def __init__(self): 
		self.plugin_data = None
		self.plugin_type = None

	def is_dawvert_plugin(self): return 'extplugin'
	def getshortname(self): return 'tunefish4'
	def getextpluginfo(self, plugconv_obj): 
		plugconv_obj.ext_formats = ['vst2', 'vst3']
		plugconv_obj.type = 'brain_control'
		plugconv_obj.subtype = 'tunefish4'

	def check_exists(inplugname):
		outlist = []
		if plugin_vst2.check_exists('id', 1416000308): outlist.append('vst2')
		return outlist

	def check_plug(plugin_obj): 
		if plugin_obj.check_wildmatch('vst2', None):
			if plugin_obj.datavals.match('fourid', 1416000308): return 'vst2'
		return None

	def decode_data(self, plugintype, plugin_obj):
		if plugintype in ['vst2', 'vst3']:
			chunkdata = plugin_obj.rawdata_get('chunk')
			self.plugin_data = data_vc2xml.get(chunkdata)
			self.plugin_type = chunkdata

	def encode_data(self, plugintype, convproj_obj, plugin_obj, extplat):
		if not (self.plugin_data is None):
			chunkdata = data_vc2xml.make(self.plugin_data)
			if plugintype == 'vst2':
				plugin_vst2.replace_data(convproj_obj, plugin_obj, 'id', extplat, 1416000308, 'chunk', chunkdata, None)
			if plugintype == 'vst3':
				plugin_vst3.replace_data(convproj_obj, plugin_obj, 'id', extplat, '5653545466733474756E656669736834', chunkdata)

	def params_from_plugin(self, convproj_obj, plugin_obj, pluginid, plugintype):
		globalstore.paramremap.load('tunefish4', '.\\data_ext\\remap\\tunefish4.csv')
		manu_obj = plugin_obj.create_manu_obj(convproj_obj, pluginid)
		if not (self.plugin_data is None):
			for valuepack, extparamid, paramnum in manu_obj.remap_ext_to_cvpj__pre('tunefish4', plugintype):
				if extparamid in self.plugin_data.attrib: valuepack.value = float(self.plugin_data.attrib[extparamid])
			plugin_obj.replace('brain_control', 'tunefish4')
			manu_obj.remap_ext_to_cvpj__post('tunefish4', plugintype)
			return True
		return False

	def params_to_plugin(self, convproj_obj, plugin_obj, pluginid, plugintype):
		globalstore.paramremap.load('tunefish4', '.\\data_ext\\remap\\tunefish4.csv')
		manu_obj = plugin_obj.create_manu_obj(convproj_obj, pluginid)
		tf4_root = ET.Element("TF4SETTINGS")
		for valuepack, extparamid, paramnum in manu_obj.remap_cvpj_to_ext__pre('tunefish4', plugintype):
			tf4_root.set(extparamid, str(valuepack.value))
		plugin_obj.replace('vst2', None)
		manu_obj.remap_cvpj_to_ext__post('tunefish4', plugintype)
		self.plugin_data = tf4_root
		return True