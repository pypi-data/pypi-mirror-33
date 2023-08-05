#!/usr/bin/env python
# -*- coding: utf-8 -*-

import time
import string
import gspread

from datetime import datetime, timedelta
from oauth2client.service_account import ServiceAccountCredentials

def get_spreadsheet(ws_url, credential_file):

    ######## Get Google Sheet Imformation ######### 
    scope = ['https://spreadsheets.google.com/feeds']                                            
#    credentials = ServiceAccountCredentials.from_json_keyfile_name('AutoNameString-2322f16ec2d9.json', scope)
    credentials = ServiceAccountCredentials.from_json_keyfile_name(credential_file, scope)
    gc = gspread.authorize(credentials)
    try:
        sh = gc.open_by_url(ws_url)
    except:
        print('\033[1;31merror: Cannot open the google sheet.')
        print('\033[1;33m       Please make sure:')
        print('       (1) The url is valid.')
        print('       (2) The google sheet is shared with "autonamestring@appspot.gserviceaccount.com".')
        print('           (with permission to edit the given google sheet)\n\033[1;m')
        raise
    return sh

    
def get_worksheet(sh, ws_name):

    sh_list = sh.worksheets()
    title_list = []
    for name in sh_list:
        title_list.append(name.title)

    if((ws_name in title_list) == False):
        ws = sh.add_worksheet(title = ws_name, rows= "1000", cols = "26")
        return ws,'new'
    else:
        ws = sh.worksheet(ws_name)
    return ws, 'old'
    
    
def get_range(a1, a2, b1, b2):

	parts = ['', '', '', '']	
	if(a1 > 26):
		parts[0] = string.letters[25 + ((a1-1)/26)] + string.letters[25 + ((a1-1)%26+1)]
	else:
		parts[0] = string.letters[25 + a1]
	parts[1] = str(a2)
	
	if(b1 > 26):
		parts[2] = string.letters[25 + ((b1-1)/26)] + string.letters[25 + ((b1-1)%26+1)]
	else:
		parts[2] = string.letters[25 + b1]
	parts[3] = str(b2)
	
	return '%s%s:%s%s' % (parts[0], parts[1], parts[2], parts[3])


def make_arg_elem(name, type, shift, END_FLAG=None, default=None):
	
	shift = [1,0] if shift == 'col' else [0, 1]	
	elem = {'name':name, 'type':type, 'shift':shift, 'END_FLAG':END_FLAG, 'default':default}
	return elem	
	
	
def get_arguments(ws, arg_inf):	

	#	arg_inf = [{arg_elem_1}, {arg_elem_2}, ... {arg_elem_N}]
	#	arg_elem = {'name':'the_fist_arg',
	#				'type':'list' or 'cell'
	#				'shift':[row, col]
	#				'END_FLAG':a name to indicate the end of that argument.}
	
	args = {}
	all_value = ws.get_all_values()	
	for arg_elem in arg_inf:
	
		args[arg_elem['name']] = None
		try:
			flag = ws.find(arg_elem['name'])	
		except:
			continue
				
		if(arg_elem['type'] == 'cell'):
			row = flag.row + arg_elem['shift'][0]
			col = flag.col + arg_elem['shift'][1]			
			args[arg_elem['name']] = ws.cell(row, col).value
			
		elif(arg_elem['type'] == 'list'):
			
			if(arg_elem['shift'][0] == 1):
				raw_data = ws.col_values(flag.col)				
			elif(arg_elem['shift'][1] == 1):
				raw_data = ws.row_values(flag.row)
			
			data = [d for d in raw_data if len(d) != 0]
			try:
				data[:data.index(arg_elem['name'])+1] = []
				if(arg_elem['END_FLAG'] != None):
					data[data.index(arg_elem['END_FLAG']):] = []
			except:
				print '[-] Parsing argument error when getting "%s"' % arg_elem['name']

			args[arg_elem['name']] = data
			if(args[arg_elem['name']] == None):
				args[arg_elem['name']] = args[arg_elem['default']]
			
	return args

	
def get_cell_list_2D(ws, base, row_size, col_size):

	cell_list_2D = [['' for col in range(col_size)] for row in range(row_size)]	
	range_str = get_range(base[0], base[1], base[0] + col_size-1, base[1] + row_size-1)	
	print range_str

	cell_list_1D = ws.range(range_str)		
	for cell in cell_list_1D:
		cell_list_2D[cell.row - base[1]][cell.col - base[0]] = cell
	
	return cell_list_2D
	
		
def upload_to_current_row(ws, data, current_row):

	t1 = time.time()

	all_cell_list = []
	max_size = max([len(d) for d in data])	
	cell_list_2D = get_cell_list_2D(ws, [1, current_row], len(data), max_size)
	
	for i, chunk in enumerate(data):
	
		padding_chunk = chunk + [''] * (max_size - len(chunk))		
		for cell, value in zip(cell_list_2D[i], padding_chunk):
			
			try:
				if(len(value) == 0):
					cell.value = ''
				else:
					cell.value = "'" + value
			except TypeError:
				cell.value = "'" + str(value)
			except:
				cell.value = "# ERROR #"
			
		all_cell_list += cell_list_2D[i]
		current_row += 1
		
		if(len(all_cell_list) > 2000):
			ws.update_cells(all_cell_list)
			all_cell_list = []
	
	ws.update_cells(all_cell_list)
	
	t2 = time.time()
	print 'Time spent: ', t2 - t1
	
	return current_row

    
def	upload_data(ws, data, mode='append', flag_name='END_FLAG', tail_space=1, extra_attrs=None):
	
	if(extra_attrs == None):
		extra_attrs = {}
		
	update_time = (datetime.utcnow() + timedelta(hours=8)).strftime('%Y/%m/%d, %H:%M:%S')
	if(mode == 'override'):
		current_row = ws.find(flag_name).row
		padding = [[flag_name, '', update_time]]			
		upload_to_current_row(ws, padding + data, current_row)
		
	elif(mode == 'append'):
		padding = [['']] * tail_space
		padding += [[flag_name, '', update_time]]
	
		current_row = ws.find(flag_name).row
		upload_to_current_row(ws, data + padding, current_row)
	
	elif(mode == 'prepend'):
		
		start_row = extra_attrs.get('start_row', 3)
		# Has some problem to be fixed.
		
		exist_data = ws.get_all_values()
		if(len(exist_data) != 0):
		
			for i, d in enumerate(exist_data):
				if(d[0] == flag_name):
					exist_data[:i] = []
					break
			
			# Remove the oldest data block according maximum block number.
			count = 0
			for i, d in enumerate(exist_data):
				if(d[0] == exist_data[0][0]):
					count += 1
				if(count >= extra_attrs.get('max_size', 5)):
					exist_data[i] = ['']
			
		data = [[flag_name, '', update_time]] + data +[['']] * tail_space + exist_data
		upload_to_current_row(ws, data, start_row)
	
	return
    