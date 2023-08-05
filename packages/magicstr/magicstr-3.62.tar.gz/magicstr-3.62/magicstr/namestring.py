#! /usr/bin/env python
# -*- coding: utf-8 -*-

import os
import re
import hashlib
import ast 
import lxml.etree as ET
import xml.sax.saxutils as SAX
 
import gspread_tools as GSTool 
from word import Word

from difflib import SequenceMatcher

ATTRIB_TITLE = ['Upload done.', 'platform', 'alias', 'translatable', 'description']
NONCONTENT_KEY = ['key', 'platform', 'alias', 'translatable', 'description']
CONTENT_KEY = []
TRANSLATE_OR_NOT = {'false':'##### Ignore #####', '':'##### Need Translate #####'}

                    
def calculate_similarity(str1, str2):
    
    if(str1 != None and str2 != None):
        if(isinstance(str1, unicode)):
            str1 = str1.encode('utf-8')
        if(isinstance(str2, unicode)):
            str2 = str2.encode('utf-8')
        return SequenceMatcher(None, str1, str2).ratio()
        
    elif(str1 == None and str2 == None):
        return 1.0
    
    return 0.0
        
    
def escape_check(input_str, platform='android'):

    # 1. single ['] and ["] should be escaped.
    # chr(92) = '\'

    if(platform != 'ios'):
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
    
 
def namestring_to_googlesheet(ws, ns_manager, selected_keys=None, mode=None, title_order=None):

    global TRANSLATE_OR_NOT
    global ATTRIB_TITLE

    selected_keys = ns_manager.order if selected_keys == None else selected_keys
    if(title_order == None):
        content_title = ns_manager.file_id_list
    else:
        content_title = [x for x in title_order if x in ns_manager.file_id_list]

    data = [ATTRIB_TITLE + content_title]
    ns = ns_manager.namestring
    for key in selected_keys:
    
        row_data = [
            key.decode('utf-8') if isinstance(key, str) else key, 
            ns[key]['platform'],
            ns[key]['alias'],
            ns[key]['translatable'],
            ns[key]['description']
        ]

        for file_id in content_title:
            default_str = TRANSLATE_OR_NOT[ns[key]['attrib'].get('translatable')]
            row_data.append(ns[key]['content'].get(file_id, default_str))

        data.append(row_data)
        
    if(mode == None):
        GSTool.upload_to_current_row(ws, data, 1)
    else:
        print '[#] Use mode: %s, to upload data.' % mode
        GSTool.upload_data(ws, data, mode=mode, flag_name='END_FLAG')
        
    return

    
def process_value(type, value):
    
    if(type == 'platform'):
        if(len(value) == 0):
            value = '[]'
        return ast.literal_eval(value)
    
    elif(type == 'alias'):
        if(len(value) == 0):
            value = '{}'
        return ast.literal_eval(value)
    
    elif(type == 'tranlatable'):
        return 'false' if(len(values) != 0) else ''
    
    elif(type == 'description'):
        return value
    
    return value

    
def process_word_data(word_data):

    global TRANSLATE_OR_NOT
    global CONTENT_KEY, NONCONTENT_KEY

    key = word_data['key']
    alias = process_value('alias', word_data.get('alias', ''))
    attrib = { 'platform':process_value('platform', word_data.get('platform', '')),
               'translatable':process_value('translatable', word_data.get('translatable', '')), 
               'description':process_value('description', word_data.get('description', ''))}               
    
    content = {}
    for ckey in CONTENT_KEY:
        if(word_data[ckey] not in [TRANSLATE_OR_NOT['false'], TRANSLATE_OR_NOT['']]):
            content[ckey] = word_data[ckey]

    return Word(key=key, alias=alias, attrib=attrib, content=content)

               
def googlesheet_to_namestring(ws, ns_manager=None):
        
    global ATTRIB_TITLE
    global CONTENT_KEY, NONCONTENT_KEY
 
    all_values = ws.get_all_values()
    if(len(all_values) == 0):
        print('\033[1;33m[#] Worksheet not found or no data.\033[1;m')
        return ns_manager
    else:
        rows = len(all_values)
        cols = len(all_values[0])
        print('[#] Get data from googlesheet...')

    if(ns_manager == None):
        ns_manager = NameStringManager()
    
    # Preprocessing the data
    title = ['key'] + all_values[0][1:]
    all_values = all_values[1:]
    all_word_data = [dict(zip(title, row)) for row in all_values]    
    CONTENT_KEY = [key for key in title if key not in NONCONTENT_KEY]
        
    ns_manager.file_id_list = CONTENT_KEY
    for word_data in all_word_data:    
        if(len(word_data['key']) == 0):
            continue
        ns_manager.order.append(word_data['key'])
        ns_manager.namestring[word_data['key']] = process_word_data(word_data)
    
    ws.update_acell('A1', 'Download done.')
    print('\033[1;32m[+] Get data done!\033[1;m')
    return ns_manager
    
  
class NameStringManager:

    strfile_name = { 'android':'strings.xml',
                     'ios':'Localizable.strings'}
                             
    def __init__(self, order=None, namestring=None):
    
        if(order == None):
            if(namestring != None):
                self.order = namestring.keys()
            else:
                self.order = []
        else:
            self.order = order
            
        if(namestring == None):
            self.namestring = {}
        else:
            self.namestring = namestring
        
        self.xmltemplate_path = None
        self.file_id_list = []   
        self.deleted_ns = None
        self.name_mapping = None
        self.verbose = False
        
    def __eq__(self, other):
        if isinstance(other, self.__class__):
            return self.__dict__ == other.__dict__
    #    return False        
        return NotImplemented

        
    def __ne__(self, other):
        if isinstance(other, self.__class__):
            return not self.__eq__(other)
    #    return not self.__eq__(other)
        return NotImplemented    
      
      
    def size(self):
        return len(self.order)

        
    def __hash__(self):
        # Override the default hash behavior (that returns the id or the object)
    #    return hash(tuple(sorted(self.__dict__.items())))
        return int(self.get_hash(), 16)

    def set_verbose(self):
        self.verbose = True
        return
        
    def get_entry_num(self):
        if(self.namestring == {}):
            return 0
        return sum([len(self.namestring[key]['content'].keys()) for key in self.namestring.keys()])

        
    def get_hash(self):
        
        ns = self.namestring
        m = hashlib.md5()
        file_id_str = ''.join(self.file_id_list)
        key_str = ''.join(ns.keys()).encode('utf-8')
        subkey_str = ''.join([''.join(ns[key]['content'].keys()) for key in ns.keys()]).encode('utf-8')
        entry_str = ''.join([''.join([ns[key]['content'][id].encode('utf-8') for id in ns[key]['content'].keys()]) for key in ns.keys()])
        
        m.update(file_id_str)
        m.update(key_str)
        m.update(subkey_str)
        m.update(entry_str)
        return m.hexdigest()

        
    def get_deleted_ns(self):
        return self.deleted_ns

        
    def set_xmltemplate(self, path):
        self.xmltemplate_path = path
    #    print '[+] xml template file : ' + path
        return

        
    def set_name_mapping(self, name_mapping):
        self.name_mapping = name_mapping
    #    print '[+] set name mapping done.'
        return
    
    
    def dir2lang(self, dir_name):
        if(self.name_mapping == None):
            print '[-] name_mapping not set.'
            return dir_name
        return self.name_mapping['dir_name'].get(dir_name, None)
                
        
    def lang2dir(self, lang_name):
        if(self.name_mapping == None):
            print '[-] name_mapping not set.'
            return lang_name
        return self.name_mapping['lang_name'].get(lang_name, None)
        
        
    def import_namestring(self, param):

        # Check parameters       
        if( param.get('platform', None) == None or
            param.get('target_path', None) == None):
            
            print '[-] Wrong parameters format.'
            return False
        else:
            target_path = param['target_path']
            platform = param['platform']
            
        if(platform not in ['ios', 'android']):
            print '[-] Unknown platform for "%s"' % (platform)
            return False
       
        if(os.path.exists(target_path) == False):
            print "[-] Target path doesn't exist."
            return False
        
        file_id_list = []
        dir_list = os.listdir(target_path)
        for subdir in dir_list:
            
            file_id = self.dir2lang(subdir)
            if(file_id == None):
                if self.verbose:
                    print '[*] language mapping of dir_name: "%s" not found, ignore.\n' % subdir
                continue
            
            ns_file_path = '%s/%s/%s' % (target_path, subdir, self.strfile_name[platform])
            if(os.path.exists(ns_file_path) == False):
                continue
            else:
                print '[#] Find %s : %s' % (self.strfile_name[platform], ns_file_path)
                file_id_list.append(file_id)
        
            if(platform == 'ios'):
                self.localizable_to_namestring(file_id=file_id, file_path=ns_file_path)
            else:
                self.xmlfile_to_namestring(file_id=file_id, file_path=ns_file_path)
        
        self.file_id_list = file_id_list
#        print self.file_id_list
        return True
    

    def delete_namestring_waring(self, param):
    
        old_ns = NameStringManager()
        if self.verbose:
            old_ns.set_verbose()
        old_ns.set_name_mapping(self.name_mapping)
        old_ns.import_namestring(param)
        
        deleted_key = [x for x in old_ns.order if (x not in self.order and self.find_main_key(x, param.get('platform')) == None)]
        
        if(len(deleted_key) != 0):
            print('\033[1;33m\n[#] These strings will be deleted from all the %s files:\n\033[1;m' % 
                  (self.strfile_name[param['platform']]))
                  
            for i, dns in enumerate(deleted_key):
                if(param['platform'] == 'android'):
                    print('    [%d] <string name=\033[1;36m"%s"\033[1;m>' % (i, dns))
                else:
                    print('    [%d] \033[1;36m"%s"\033[1;m' % (i, dns))
            print('\033[1;33m\n[#] Are you sure to do it? (y/n) \033[1;m')
            
            if(raw_input() != 'y'):
                print('\033[1;33m[#] Do nothing.\033[1;m')
                exit()
            else:
                print('\033[1;33m[#] Deleted.\033[1;m')
                deleted_ns = NameStringManager()
                deleted_ns.file_id_list = [x for x in old_ns.file_id_list]
                deleted_ns.order = deleted_key
                
                for i, key in enumerate(deleted_key):
                    deleted_ns.namestring[key] = old_ns.namestring[key].copy()
                return deleted_ns
                
        return NameStringManager()

        
    def export_namestring(self, param=None):
        
        # Check parameters       
        if( param.get('platform', None) == None or
            param.get('target_path', None) == None):
            print '[-] Wrong parameters format.'
            return False
        else:
            target_path = param['target_path']
            platform = param['platform']
            if(platform not in ['ios', 'android']):
                print '[-] Unknown platform type: %s' % (platform)
                return False
            elif(platform == 'android' and self.xmltemplate_path == None):
                print '[-] strings.xml template file not found.'
                return False
        
        if(os.path.exists(target_path) == False):
            os.mkdir(target_path)
            self.deleted_ns = NameStringManager()
        else:
            # Check and warn user if the directory exists.
            self.deleted_ns = self.delete_namestring_waring(param)
        
    #    dir_list = os.listdir(target_path)
        for file_id in self.file_id_list:
          
            subdir = self.lang2dir(file_id)
            if(subdir == None):
                if self.verbose:
                    print '[*] directory mapping of language: "%s" not found, ignore.' % file_id
                continue

            subdir_path = target_path + '/' + subdir
            if(os.path.exists(subdir_path) == False):
                os.mkdir(subdir_path)
            
            ns_file_path = subdir_path + '/' + self.strfile_name[platform]
            if(platform == 'ios'):
                self.namestring_to_localizable(file_id=file_id, file_path=ns_file_path)
            else:
                self.namestring_to_xmlfile(file_id=file_id, file_path=ns_file_path)
        
        return True

        
    def xmlfile_to_namestring(self, file_id, file_path):
        
        tree = ET.parse(file_path)
        root = tree.getroot()
        for child in root:
        
            raw_text = ET.tostring(child, encoding = 'unicode', method = 'html').strip()
            text = raw_text[raw_text.find('>') + 1:].replace('</string>', '') 
        #    text = (raw_text.replace('<string>', '')).replace('</string>', '')
            
            if(child.attrib.get('name') == None):
                continue
                
            key = child.attrib['name']
            if(self.namestring.get(key, None) == None):
                attrib = {'translatable':child.attrib.get('translatable', ''),
                          'description':'',
                          'platform':['android']}
                self.namestring[key] = Word(key=key, attrib=attrib)
                self.order.append(key)
            
            if(self.namestring[key]['content'].get(file_id, None) == None):
                if(text == None):
                    text = ''
                elif(len(text) > 1 and (text[0] == '"' and text[-1] == '"')):
                    text = text[1:-1]
                    
                # xml.sax.saxutils.unescape(string): 
                #     Replace &amp; , &lt; and &gt; with '&', '<' and '>' respectively.
                     
                self.namestring[key]['content'][file_id] = SAX.unescape(text)
            #    self.namestring[key][file_id] = inv_escape_check(text).encode('utf-8')
                
        return
        

    def localizable_to_namestring(self, file_id, file_path):

        with open(file_path, 'r') as f:
            
            for line in f:            
                line = line.strip()
                pat = r'.*?"(.*)"\s*=\s*"(.*)";.*' 
                match = re.search(pat, line)
                
                if(match == None):
                    continue    
                key = match.group(1).decode('utf-8')
                value = match.group(2).decode('utf-8')
                
                if(self.namestring.get(key) == None):
                    attrib = {'translatable':'', 'description':'', 'platform':['ios']}
                    self.namestring[key] = Word(key=key, attrib=attrib)
                    self.order.append(key)
                
                if(self.namestring[key]['content'].get(file_id) == None):
                    self.namestring[key]['content'][file_id] = value
                
        return
            
            
    def namestring_to_xmlfile(self, file_id, file_path):
        
        tree = ET.ElementTree(file=self.xmltemplate_path)
        root = tree.getroot()
        root.text = '\n\n    '
        
        temp_node = None
        for i, key in enumerate(self.order):
        
            attrib = self.namestring[key]['attrib']
            if('android' not in attrib['platform']):
                continue
        
            translatable = attrib.get('translatable', '')
            value = self.namestring[key]['content'].get(file_id, None)
            if(value == None):
                continue
            
            alias_list = self.namestring[key]['alias']['android']
            
            for alias_name in alias_list:
            
                temp_node = ET.SubElement(root, 'string')
                temp_node.text = '"%s"' % (escape_check(value))
            #    temp_node.text = '"' + escape_check(content).decode('utf-8') + '"'
                
            #    temp_node.attrib['name'] = key
                temp_node.attrib['name'] = alias_name
                if(len(translatable) != 0):
                    temp_node.attrib['translatable'] = 'false'
                    
                temp_node.tail = '\n    '
            #    if(i == len(self.order) - 1 and alias_name == alias_list[-1]):
    
        temp_node.tail += '\n\n'
        output = ET.tostring(tree, method = "html", encoding = 'utf-8')
        output = output.replace('&lt;', '<')
        output = output.replace('&gt;', '>')
        with open(file_path, 'w') as f:
            f.write(output)
            
        return
        
        
    def namestring_to_localizable(self, file_id, file_path):

        print '[#] Download data from "%s" column to path: "%s"' % (file_id, file_path)
    
        with open(file_path, 'w') as f:
            for i, key in enumerate(self.order):
            
                attrib = self.namestring[key]['attrib']

                if('comment' in attrib['platform']):
                    f.write('/* {} */\n\n'.format(key))
                    continue

                if('ios' not in attrib['platform']):
                    continue
                    
                value = self.namestring[key]['content'].get(file_id, None)
                if(value == None):
                    continue
                if(isinstance(value, unicode) == True):
                    value = value.encode('utf-8')

                alias_list = self.namestring[key]['alias']['ios']
                for alias_name in alias_list:                                
                    ios_key = alias_name
                    if(isinstance(ios_key, unicode) == True):
                        ios_key = ios_key.encode('utf-8')
                
                    f.write('"%s" = "%s";\n\n' % (
                        escape_check(ios_key, platform='ios'), 
                        escape_check(value, platform='ios')
                    ))
                
        return


    def find_main_key(self, query_key, platform):

        if(query_key in self.namestring.keys()):
            return query_key
        else:
            for key in self.namestring.keys():
                alias_key = self.namestring[key]['alias'].get(platform, [])
                if(query_key in alias_key):
                    return key
        return None

        
    def get_suggestion(self, other_ns, key):
    
        ret_str = ''
        for current_key in self.namestring.keys():
        
            similarity = []
            for file_id in other_ns[key]['content'].keys():
                other_value = other_ns[key]['content'][file_id]
                current_value = self.namestring[current_key]['content'].get(file_id)
                similarity.append(calculate_similarity(current_value, other_value))
            
            avg_sim = sum(similarity) / len(similarity)
            if(avg_sim >= 0.7):
                current_value = self.namestring[current_key]['content'].get('English')
                ret_str += '\n[similar] %s (%.2f): %s' % (current_key, avg_sim, current_value) 
        
        return ret_str
            
    
    def merge_manager(self, other_manager):
    
        if (isinstance(other_manager, self.__class__) == False):
            print '[NameStringManager] merge_manager() fail: "Invalid ns_manager object"'
            return False

        print self.file_id_list 
        print other_manager.file_id_list
        
        for file_id in other_manager.file_id_list:
            if(file_id not in self.file_id_list):
                self.file_id_list.append(file_id)
        
        temp_order = []
        temp_suggestion = []
        other_ns = other_manager.namestring
        for key in other_ns.keys():

            other_platform = other_ns[key]['attrib'].get('platform', [None])[0]
            if(other_platform == None):
                print '[-] Unexpected error: fail to get other platform of key "%s" when merging data.' % key
                exit()
        
            add_key_flag = 0
            main_key = self.find_main_key(key, other_platform)
            if(main_key == None):
                add_key_flag = 1
            else:
                
                current_platform = self.namestring[main_key]['attrib'].get('platform', None)
                # platform exists, add new value if it doesn't exist. Ignore inconsistent value.
                if(other_platform in current_platform):
                    for file_id in other_ns[key]['content'].keys():
                        if( self.namestring[main_key]['content'].get(file_id) == None):
                            self.namestring[main_key]['content'][file_id] = other_ns[key]['content'][file_id]
                            
                # platform doesn't exist, check whether all the values are the same to insert platform.
                else:
                    for file_id in other_ns[key]['content'].keys():
                        other_value = other_ns[key]['content'].get(file_id)
                        current_value = self.namestring[main_key]['content'].get(file_id)
                        if(other_value != current_value):
                            add_key_flag = 1
                            break
                    else:
                        self.namestring[main_key]['attrib']['platform'].append(platform)
            
            if(add_key_flag == 1):
                temp_order.append(key)
                temp_suggestion.append(self.get_suggestion(other_ns, key))
                
        for i, key in enumerate(temp_order):
            self.order.append(key)
            self.namestring[key] = other_ns[key].copy()
            
            des = self.namestring[key]['attrib'].get('description', '')
            self.namestring[key]['attrib']['description'] = des + temp_suggestion[i]

            
