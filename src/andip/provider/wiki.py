# -*- coding: utf-8 -*-
'''
Created on Apr 27, 2012

@author: Bartosz Alchimowicz
'''

import urllib
import re

from andip import DataProvider
from andip.provider import Conjugation


class WikiProvider(DataProvider):
    def __init__(self, url):
        self.__url = url
        
    def _get_word(self, conf):
        assert isinstance(conf, tuple)
        assert len(conf) == 3
        assert isinstance(conf[0], basestring)
        assert isinstance(conf[1], basestring)
        assert isinstance(conf[2], dict)
        #

    def _get_conf(self, word):
        assert isinstance(word, str)
        
        return urllib.urlopen(self.__url + 'w/api.php?format=xml&action=query&prop=revisions&rvprop=content&titles=' + word).read()
        
    def _get_dump(self, word=None, conf=None):
        """
        Dump data of a specified word in a string recognazible by FileProvider.
        @param word: a word to dump
        @param conf: restric dump to a specified configuration
        @return: string in a JSON format
        """
        pass

    
class PlWikiProvider(WikiProvider):
    
    def __init__(self):
        WikiProvider.__init__(self, "http://pl.wiktionary.org/")
        self.__schema_adjective = None
    
    def _load(self, data_set):
        return eval(open(data_set + ".txt").read())
    
    def __get_conf_verb(self, base_word, data):
        if len(data) == 0:
            raise Exception("verb error")
        
        conf = data[0]
        config = dict()
        conf = conf.replace("| ", "").split("\n")
        for element in filter(None, conf):  # filter removes empty elements
            tmp = element.split("=")
            config[tmp[0]] = tmp[1]
            
        if config['dokonany'] == 'tak':
            done = 'dokonane' 
        else:
            done = 'niedokonane'
        
        configuration = {}
        configuration[base_word] = {}
        configuration[base_word]['aspekt'] = {}
        configuration[base_word]['aspekt'][done] = {}
        for forma in ['czas terazniejszy', 'czas przeszly']:
            configuration[base_word]['aspekt'][done][forma] = {}
            configuration[base_word]['aspekt'][done][forma]['liczba'] = {}
            for liczba in ['pojedyncza', 'mnoga']:
                configuration[base_word]['aspekt'][done][forma]['liczba'][liczba] = {}
                configuration[base_word]['aspekt'][done][forma]['liczba'][liczba]['osoba'] = {}
                for osoba in ['pierwsza', 'druga', 'trzecia']:
                    configuration[base_word]['aspekt'][done][forma]['liczba'][liczba]['osoba'][osoba] = {}
                    conj = Conjugation.Conjugation()
                    if forma == 'czas przeszly':
                        for rodzaj in ['meski', 'zenski', 'nijaki']:
                            configuration[base_word]['aspekt'][done][forma]['liczba'][liczba]['osoba'][osoba][rodzaj] = conj.get_word_past(config['koniugacja'], forma, liczba, rodzaj, osoba, base_word)
                    else:
                        configuration[base_word]['aspekt'][done][forma]['liczba'][liczba]['osoba'][osoba] =  conj.get_word_present(config['koniugacja'],forma, liczba, osoba, base_word)
        
        return configuration[base_word]
                    
    def __get_conf_noun(self, base_word, data):
        print 'noun'
            
    def __get_conf_adjective(self, base_word, data):
        if len(data) == 0:
            raise Exception("adjective error")
        words = data[0].replace("|", "").split("\n")
        
        assert len(words) > 0
        word = words[0]
        
        # generowanie stopniowania
        if word == '' or word == 'brak':
            # brak stopniowania?
            return
        else:
#            print word # stopniowanie na podstawie podanego drugiego stopnia
            pass
    
        # generowanie odmian
        if self.__schema_adjective is None:
            self.__schema_adjective = self._load("../data/adjective_schema")

        last_letter = base_word[len(base_word) - 1]
        if last_letter == 'y' or last_letter == 'i':
            retval = self.__schema_adjective[last_letter]
            for przyp in retval['przypadek']:
                for licz in retval['przypadek'][przyp]['liczba']:
                    for rodz in retval['przypadek'][przyp]['liczba'][licz]['rodzaj']:
                        print base_word[0:len(base_word) - 2], retval['przypadek'][przyp]['liczba'][licz]['rodzaj'][rodz] 
                        
                        retval['przypadek'][przyp]['liczba'][licz]['rodzaj'][rodz] = base_word[0:len(base_word) - 1] + retval['przypadek'][przyp]['liczba'][licz]['rodzaj'][rodz] 
                    
        return retval
#        print self.__schema_adjective['y']
        
#        retval = self.conf_cache.get(word, None)


    def get_conf(self, word):
        data = self._get_conf(word)

        type = re.findall("-([^-]*)-polski", data)
        if len(type) == 0:
            raise Exception("word not found")
        return {
            'przymiotnik': self.__get_conf_adjective,
            'czasownik': self.__get_conf_verb,
            # (re.findall("\{\{odmiana-czasownik-polski([^\}]*)}}", data)),
            'rzeczownik': self.__get_conf_noun  #
        }.get(type[0])(word, re.findall("\{\{odmiana-" + type[0] + "-polski([^\}]*)}}", data));

    def get_word(self, conf):
        '''
            Conf is a configuration that user chose to get information about word.
            It's a touple, that first element determines type of word, second is the word alone,
            and the third is a dictionary that contains details about form of word we want to have
        
        '''
        word_about = self._get_conf(conf[1])
        
        print conf[2]
        
        try:
            if conf[0] == 'przymiotnik':
                tmp = self.__get_conf_adjective(word_about),  #
            elif conf[0] == 'czasownik':
                return self.__get_conf_verb(conf[1], re.findall("\{\{odmiana-czasownik-polski([^\}]*)}}", word_about))['aspekt'][conf[2]['aspekt']][conf[2]['forma']]['liczba'][conf[2]['liczba']]['osoba'][conf[2]['osoba']]
            elif conf[0] == 'rzeczownik': 
                tmp = self.__get_conf_noun  #
        except KeyError:
            return 'No information about this form'
            
        
        

    def get_dump(self, word=None, conf=None):
        return self._get_dump(word, conf)







