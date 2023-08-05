#! /usr/bin/env python
# -*- coding: utf-8 -*-

import os, sys, shutil
import re, string

#import xml.etree.cElementTree as ET
import lxml.etree as ET
import xml.sax.saxutils as SAX

from pkg_resources import resource_filename

# for gspread
import gspread
from oauth2client.service_account import ServiceAccountCredentials

# my own package
import gspread_tools as GST
import namestring as NS


#### CONFIG INFORMATION ####
CONFIG = {}
CONFIG['arg_name'] = ['input', 'output', 'system', 'ws_name', 'ws_url', 'lang_map']
CONFIG['arg_display'] = ['input_path', 'output_path', 'system', 'worksheet_name', 'worksheet_url', 'language_name_mapping']

LANG_MAP = []


#### SOME GOOGLESHEET RELATED STRING ####
prefix = "'"
TRANSLATE_OR_NOT = {'false':'##### Ignore #####', '':'##### Need Translate #####'}


#### RUNTIME OPTINI ####

verbose = False

def print_usage():

    print('\n[#] usage: \n')
    print('\033[1;32m' + '    $ magicstr ' + '\033[1;31m' + 'upload   '+ '\033[1;33m' +'[-i input_dir] [-u worksheet_url] [-n worksheet_name]' + '\033[1;m'+ '\n')
    print('    -> Upload the string contents of all the strings.xml files in given directory')
    print('    -> to a given google worksheet.\n')

    print('\033[1;32m' + '    $ magicstr ' + '\033[1;31m' + 'download '+ '\033[1;33m' +'[-o output_dir] [-u worksheet_url] [-n worksheet_name]' + '\033[1;m'+ '\n')
    print('    -> Download and update all the strings.xmls files in the given directroy with ')
    print('    -> contents on the given google worksheet.\n')  
 
    print('\033[1;32m' + '    $ magicstr ' + '\033[1;31m' + 'config ' + '\033[1;m'+ '\n')
    print('    -> Edit config file in the current directory.' )
    print('    -> And of course, you can also edit it with your own text editor directly.\n')

    print('\033[1;32m' + '    $ magicstr ' + '\033[1;31m' + 'init [credential file name]' + '\033[1;m'+ '\n')
    print('    -> Initial files required for execution,' + '\033[1;36m "sudo"\033[1;m' + ' is required.\n')
 
    exit()
    return


def parse_config():
    
    global LANG_MAP
    global CONFIG

    if(os.path.exists('./config') == True):
        f = open('./config', 'r')
    else:
        return False

    mapping = {}
    for i, name in enumerate(CONFIG['arg_name']):
        mapping[CONFIG['arg_display'][i]] = name

    for line in f:
        pair = line.split(': ')
        CONFIG[mapping.get(pair[0], 'unknown')] = pair[1].strip()
    f.close()

    # Remove '/' at the end of path
    if(len(CONFIG['input']) != 0 and CONFIG['input'][-1] == '/' ):
        CONFIG['input'] = CONFIG['input'][:-1]
    if(len(CONFIG['output']) != 0 and CONFIG['output'][-1] == '/' ):
        CONFIG['output'] = CONFIG['output'][:-1]

    # Check system 
    if(CONFIG['system'] not in ['android', 'ios']):
        CONFIG['system'] = 'android'        
        
    # Parse language mapping
    default_dir = {'android':'values', 'ios':'en.lproj'}
    fmt_str = {'android':'values-%s', 'ios':'%s.lproj'}

    name_mapping = {'dir_name':{}, 'lang_name':{}}
    lang_slice = CONFIG['lang_map'][1:-1].split(',')
    lang_order = []
    for pair in lang_slice:
        pair = pair.replace('"', '').strip().split(':')
        
        if(pair[1] == 'default'):
            pair[1] = default_dir[CONFIG['system']]
        else:
            pair[1] = fmt_str[CONFIG['system']] % pair[1]

        lang_order.append(pair[0])
        name_mapping['dir_name'][pair[1]] = pair[0]
        name_mapping['lang_name'][pair[0]] = pair[1]
    
    CONFIG['name_mapping'] = name_mapping
    CONFIG['lang_order'] = lang_order
    
    # Add template path and credential path.
    if('debug' in sys.argv):
        CONFIG['template_path'] = '../magicstr_test/template_strings.xml'
        CONFIG['credential_path'] = '../magicstr_test/AutoNameString-2322f16ec2d9.json'
    else:    
        CONFIG['template_path'] = os.path.abspath(resource_filename('magicstr', 'template_strings.xml'))
        CONFIG['credential_path'] = os.path.abspath(resource_filename('magicstr', 'AutoNameString-2322f16ec2d9.json'))
 
    return True


def parse_command_args():

    global CONFIG, verbose
    
    if(parse_config() == True):
        print('[#] Local config file found.')
    else:
        print('\033[1;31m[-] Local config file not found.\033[1;m')
        print('[#] Please type "magicstr config" to finish the setting."')
        exit()     

    for i in range(len(sys.argv)):
        if(sys.argv[i].find('-') == 0):
            if(i+1 < len(sys.argv) and sys.argv[i+1].find('-') != 0):

                if(sys.argv[i] in ['-i', '-o']):
                   if(sys.argv[i+1][-1] == '/'):
                        sys.argv[i+1] = sys.argv[i+1][:-1]

                if(sys.argv[i] == '-i'):
                    CONFIG['input'] = sys.argv[i+1]
                elif(sys.argv[i] == '-o'):
                    CONFIG['output'] = sys.argv[i+1]
                elif(sys.argv[i] == '-u'):
                    CONFIG['ws_url'] = sys.argv[i+1]
                elif(sys.argv[i] == '-n'):
                    CONFIG['ws_name'] = sys.argv[i+1]
                else:
                    print('[-] Error: unknown specified flag "%s"' % sys.argv[i])
            elif(sys.argv[i] in ['-d']):
                continue
            elif(sys.argv[i] in ['-v', '--verbose']):
                verbose = True
            else:
                print_usage()

    if(len(CONFIG.get('ws_url', '')) == 0):
        print('\033[1;31m[-] Error: Give me the worksheet url plz... QAQ\033[1;m')
        exit()
    if(len(CONFIG.get('ws_name', '')) == 0):
        print('\033[1;31m[-] Error: Give me the worksheet name plz... QAQ\033[1;m')
        exit()
    if(sys.argv[1] == 'download' and len(CONFIG.get('output', '')) == 0):
        print('\033[1;31m[-] Error: Give me the output path plz... QAQ\033[1;m')
        exit()    
    if(sys.argv[1] == 'upload' and len(CONFIG.get('input', '')) == 0):
        print('\033[1;31m[-] Error: Give me the input path plz... QAQ\033[1;m')
        exit()
    else:
        try:
            x = []
            if(os.path.exists(CONFIG['input'])):
                dir_list = os.listdir(CONFIG['input'])
                CONFIG['dir_list'] = sorted([name for name in dir_list if name.find('values') != -1])
            else:
                CONFIG['dir_list'] = []
            
        except:
            raise
    
    if('-d' in sys.argv):
        print(CONFIG)

    return


def escape_check(input_str):

    ### 0. 'true' and 'false' will transform into 'TRUE' and 'FALSE' automatically in google sheet.    
    if(input_str == '-true-'):
        return 'true'
    elif(input_str == '-false-'):
        return 'false'

    ### 1. single ['] and ["] should be escaped.
    ### chr(92) = '\'
    block = input_str.split("'")
    input_str = block[0]
    for i in range(1, len(block)):
        if(len(input_str) == 0 or input_str[-1] != chr(92)):
            input_str += chr(92)
        input_str += "'" + block[i]
    
    block = input_str.split('"')
    input_str = block[0]
    for i in range(1, len(block)):
        if(len(input_str) == 0 or input_str[-1] != chr(92)):
            input_str += chr(92)
        input_str += '"' + block[i]
    
    return input_str

'''
def inv_escape_check(input_str):

    global prefix

    if(input_str == 'true' or input_str == 'false'):
        input_str =  '-' + input_str + '-'
    
    ### xml.sax.saxutils.unescape(string): 
    ###     Replace &amp; , &lt; and &gt; with '&', '<' and '>' respectively.
    return SAX.unescape(input_str)
#    return input_str
'''

# ----- REPLACE BEGIN ----- #

# ----- REPLACE END ----- # 


def ANS_merge_data(ws, ns_manager):

    ##### Merger old content into to-be-upload contents #####
    old_ns_manager = NS.googlesheet_to_namestring(ws)
    if(old_ns_manager == None):
        print('\033[1;32m[+] No old data, no need to merge\033[1;m')
        return ns_manager
    else:
        print('[#] Merging old data with new data.')
    
    old_ns_manager.merge_manager(ns_manager)
    print('\033[1;32m[+] Merge done!\033[1;m')
    return old_ns_manager


def ANS_deleted_ns_backup(sh, ns_manager):

    global CONFIG

    deleted_ns = ns_manager.get_deleted_ns()
    if(deleted_ns.size() == 0):
        return
    else:
        
        res = raw_input('\n\033[1;33m[#] Do you want to backup deleted strings? (y/n)\033[1;m\n: ')
        if(res != 'y'):
            print('\033[1;33m[#] You choose no backup.\033[1;m')
            return
        
        print('\033[1;33m[#] Doing deleted namestring backup.\033[1;m')
    #    print deleted_ns.namestring
        
        ws, flag = GST.get_worksheet(sh, CONFIG['ws_name'] + '_trash_can')
        NS.namestring_to_googlesheet(ws, deleted_ns, mode='prepend', title_order=CONFIG['lang_order'])
        print('\033[1;32m[+] backup done.\033[1;m')
    
    return
        
    
def ANS_upload():

    global CONFIG, verbose

    sh = GST.get_spreadsheet(CONFIG['ws_url'], CONFIG['credential_path'])
    ws, flag = GST.get_worksheet(sh, CONFIG['ws_name'])
    
    # Description:
    #   Get name string contents from strings.xml or localizable.strings. 
    #   Add new data to old data on the googlesheet.
    
    print('[#] Start uploading, please wait...')
    ns_manager = NS.NameStringManager()
    if verbose:
        ns_manager.set_verbose()

    ns_manager.set_xmltemplate(CONFIG['template_path'])
    ns_manager.set_name_mapping(CONFIG['name_mapping'])
    
    param = {'platform':CONFIG['system'], 'target_path':CONFIG['input']}
    ns_manager.import_namestring(param)
    ns_manager = ANS_merge_data(ws, ns_manager)
    NS.namestring_to_googlesheet(ws=ws, ns_manager=ns_manager, title_order=CONFIG['lang_order'])
    return 
    

def ANS_download():

    global CONFIG, verbose

    sh = GST.get_spreadsheet(CONFIG['ws_url'], CONFIG['credential_path'])
    ws, flag = GST.get_worksheet(sh, CONFIG['ws_name'])
    if(flag == 'new'):
        print('\033[1;31m\n[-] Error: The worksheet doesn\'t exsit... QAQ\033[1;m')
        print('\033[1;31m[-]        Please make sure you set the right worksheet name and url.\033[1;m\n')
        sh.del_worksheet(ws)
        return
    else:
        print('[#] Downloading the content...')
    
    ns_manager = NS.googlesheet_to_namestring(ws)
    if verbose:
        ns_manager.set_verbose()
    ns_manager.set_xmltemplate(CONFIG['template_path'])
    ns_manager.set_name_mapping(CONFIG['name_mapping'])
    
    if(ns_manager == None):
        print('\033[1;31m\n[-] Error: Download fail: "No data"\033[1;m')
        print('\033[1;31m[-]        Please check the worksheet.\033[1;m\n')
        return
    else:
        print('\033[1;32m[+] Download done.\033[1;m')
    
    param = {'platform':CONFIG['system'], 'target_path':CONFIG['output']}
    if(ns_manager.export_namestring(param)):
        ANS_deleted_ns_backup(sh, ns_manager)
        print('\033[1;32m[+] Update success.\033[1;m\n')
    else:
        print('\033[1;31m[-] Update fail.\033[1;m\n')
    return

    
# ----- CONFIGURE FUNCTIONS BEGIN ----- #    
    
def init_default_config():

    global CONFIG

    lang_mapping_list = [   '"English":"default"',
                            '"Chinese":"zh-rTW"',
                            '"Chinese2":"zh-Hant"',
                            '"Japanese":"ja"',
                            '"Simplified Chinese":"zh-rCN"',
                            '"Simplified Chinese2":"zh-Hans"',
                            '"Hong Kong":"zh-rHK"',
                            '"German":"de"',
                            '"Turkish":"tr"',
                            '"French":"fr"',
                            '"Spanish":"es"',
                            '"Portuguese":"pt"',
                            '"Italian":"it"',
                            '"Thai":"th"',
                            '"Dutch":"nl"',
                            '"Korean":"ko"',
                            '"Russian":"ru"',
                            '"Arabic":"ar"',
                            '"Indonesian":"id"',
                            '"Pilipino":"tl"']

    CONFIG['input'] = './app/src/main/res'
    CONFIG['output'] = './app/src/main/res'
    CONFIG['system'] = 'android'
    CONFIG['ws_name'] = 'Default Worksheet'
    CONFIG['ws_url'] = 'https://docs.google.com/spreadsheets/d/THE_KEY_OF_YOUR_GOOGLESHEET/edit#gid=0'
    CONFIG['lang_map'] = '{' + ', '.join(lang_mapping_list) + '}'
    return


def show_config():
    
    global CONFIG    
    CLFR = '\033[1;33m'
    CLBC = '\033[1;m'

    print(CLFR + '\n########## [config] ##########' + CLBC)
    for i, name in enumerate(CONFIG['arg_name']):
        print(CLFR + '[%d] %s: ' % (i+1, CONFIG['arg_display'][i]) + CLBC + CONFIG.get(name, ''))
    return


def save_config():

    global CONFIG

    f = open('./config', 'w')
    for i, name in enumerate(CONFIG['arg_name']):
        f.write(CONFIG['arg_display'][i] + ': ' + CONFIG.get(name, '') + '\n')

    f.close()
    print('[#] Save success!')
    return


def ANS_configure():

    global CONFIG

    if(parse_config() == True):
        print('\n[#] Read local config file.')
    else:
        init_default_config()
        print('\n\033[1;33m[#] Local config file not found, create a new config file.\033[1;m')
        raw_input('[#] Press anything...')

    change = 0
    stop_flag = False
    valid_choose = [str(i+1) for i, name in enumerate(CONFIG['arg_name'])]

    show_config()
    while(stop_flag == False):
        
        print('\n[#] Select the number of setting to be changed, press "s" to save or "q" to leave.')        
        while(1):
            cmd = raw_input('$ ')
            if(cmd == 's'):
                save_config()
                change = 0
            elif(cmd == 'q'):
                stop_flag = True
                if(change == 1):
                    stop_flag = (raw_input('[#] Leave without saving? (y/n)\n$ ').strip() == 'y')
                
            elif(cmd not in valid_choose):
                print('what? (please input number 1 ~ %d only)' % (len(CONFIG['arg_name'])))
                continue
            else:
                CONFIG[CONFIG['arg_name'][int(cmd)-1]] = raw_input('New setting: ').strip()
                change = 1
                show_config()
            break
    return

    
# ----- CONFIGURE FUNCTIONS END----- #
    
    
def ANS_init():

    # Description:
    #   Copy credential file under the package dir.
    path = os.path.abspath(resource_filename('magicstr', ''))
    shutil.copy(sys.argv[2], path)

    print('[#] Initial done!')

    return


def do_run():

    global verbose

    '''
    if('debug' in sys.argv):
        
        # Put some test functions here.
        init_default_config()
        exit()
    '''
    
    if "-v" in sys.argv or "--verbose" in sys.argv:
        verbose = True

    if(len(sys.argv) > 1 and (sys.argv[1] in ['init', 'upload', 'download', 'config'])):

        if(sys.argv[1] == 'init'):
            ANS_init()
            exit()
        elif(sys.argv[1] == 'config'):
            ANS_configure()
            exit()

        parse_command_args()
        if(sys.argv[1] == 'upload'):
            ANS_upload()
        elif(sys.argv[1] == 'download'):
            ANS_download()
        exit()

    else:
        print_usage()


if __name__ == '__main__':

    do_run()
