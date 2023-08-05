#! /usr/bin/env python
# -*- coding: utf-8 -*-

import hashlib

class Word:
    
    def __init__(self, key=None, alias=None, attrib=None, content=None):
        
        key = 'default key' if key == None else key
        alias = {} if alias == None else alias
        attrib = {} if attrib == None else attrib
        content = {} if content == None else content
        
        self.key = {'main':key, 'alias':alias}
        self.attrib = { 'translatable': attrib.get('translatable', ''), 
                        'description':attrib.get('description', ''), 
                        'platform':attrib.get('platform', [])} 
        self.content = content

        # Auto fill alias
        for p in self.attrib['platform']:
            self.key['alias'][p] = self.key['alias'].get(p, [self.key['main']])
    
    def __str__(self):
        return str(self.__dict__)

    
    def __eq__(self, other):
        if isinstance(other, self.__class__):
            return self.__dict__ == other.__dict__
        return NotImplemented

        
    def __ne__(self, other):
        if isinstance(other, self.__class__):
            return not self.__eq__(other)
        return NotImplemented

        
    def __hash__(self):
        return int(self.get_hash(), 16)

        
    def get_hash(self):
        
        m = hashlib.md5()
        print '[-] Not Implemented.'
        exit()
        return 

    def __getitem__(self, key):
        if not isinstance(key, str):
            raise TypeError('Index must be str, not {}'.format(type(key).__name__))
        else:
            return self.get_item(key)
            
    
    def get_item(self, key):
        if(key == 'key'):
            return self.key['main']
        elif(key == 'alias'):
            return self.key['alias']
        elif(key == 'attrib'):
            return self.attrib
        elif(key == 'content'):
            return self.content
        elif(key in self.attrib.keys()):
            return self.attrib[key]
        # elif(key in self.content.keys()):
            # return self.content[key]
        else:
            raise KeyError('%s' % key)

            
    def __setitem__(self, key, value):
    
        print key, value
    
        if key == 'key' and not isinstance(value, str):
            raise TypeError('value of index: "{}" must be str, not {}'.format(key, type(value).__name__))
        elif key in ['alias', 'attrib', 'content'] and not isinstance(value, dict):
            raise TypeError('value of index: "{}" must be dict, not {}'.format(key, type(value).__name__))
        elif not isinstance(key, str):
            raise TypeError('Index must be str, not {}'.format(type(key).__name__))
        else:
            return self.set_item(key, value)

            
    def set_item(self, key, value):
    
        if(key == 'key'):
            self.key['main'] = value
        elif(key == 'alias'):
            self.key['alias'] = value
        elif(key == 'attrib'):
            self.attrib = value
        elif(key == 'content'):
            self.content = value
        elif(key in self.attrib.keys()):
            self.attrib[key] = value
        # elif(key in self.content.keys()):
            # self.content[key] = value
        else:
            raise KeyError('%s' % key)

    def copy(self):        
        return Word(key=self.key['main'], alias=self.key['alias'],
                    attrib=self.attrib, content=self.content)
        
            