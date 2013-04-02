import twitter
import urllib, urllib2
from random import choice
from base64 import b64encode
from itertools import repeat
from hashlib import sha1
import string
import time
import hmac
from binascii import b2a_base64
from webbrowser import open as wb_open
import pickle
import os

import rules
import interface

class OrtoTweet:
    def __init__(self):
        '''
        self.users is a dictionary of the required information to post as a user.
        It is of the form access_token_key, access_token_secret
        
        self.responses is a dictionary of the potential responses.
        It is of the form {name: [response1, response2, ...]}, where responseN is a string (possibly with some custom syntax
        
        '''
        
        self.load()
        self.save()
        
        self.commands = {
            'help': self.help,
            'addUser': self.addUser, 
            'deleteUser': self.deleteUser,
            'view_users': self.view_users, 
            'post': self.post, 
            'makeRule': self.makeRule, 
            'save': self.save, 
            'load': self.load
        }
            
    def requestPIN(self):
        #Start the sign-in process. Returns the oauth_token
        http_method = 'POST'
        url = 'https://api.twitter.com/oauth/request_token'
        nonce = self.makeNonce()
        
        ##
        values = {
            'oauth_callback':urllib.quote('oob', ''),
            'oauth_consumer_key':'BGCXJGj3E24xIPXC3Vq1dA',
            'oauth_nonce':nonce,
            'oauth_signature_method':'HMAC-SHA1',
            'oauth_timestamp':str(int(time.time())),
            'oauth_version':'1.0'
        }
        #Generate signature
        oauth_signature = self.signRequest(url, http_method, values)
        #Generated all values, generate the header
        values['oauth_signature'] = oauth_signature
        DST = self.makeDST(values)
        #Got all the required values - send it off!
        req = urllib2.Request(url, {}, headers={'Authorization': DST})
        response = urllib2.urlopen(req)
        #This is the request token
        data = dict([tuple(i.split('=')) for i in response.read().split('&')])
        if data['oauth_callback_confirmed'] != 'true':
            raise ValueError('callback not confirmed')
        wb_open('https://api.twitter.com/oauth/authenticate?oauth_token=' + data['oauth_token'], 2)
        return data['oauth_token']
        
    def validateUser(self, PIN, oauthToken):
        #Now we request an access token
        http_method = 'POST'
        url = 'https://api.twitter.com/oauth/access_token'
        nonce = self.makeNonce()
        values = {
            'oauth_consumer_key':'BGCXJGj3E24xIPXC3Vq1dA',
            'oauth_nonce':nonce,
            'oauth_signature_method':"HMAC-SHA1",
            'oauth_timestamp':str(int(time.time())),
            'oauth_token':oauthToken,
            'oauth_verifier':PIN,
            'oauth_version':'1.0'
        }
        oauth_signature = self.signRequest(url, http_method, values)
        values['oauth_signature'] = oauth_signature
        DST = self.makeDST(values)
        req = urllib2.Request(url, {}, headers={'Authorization': DST})
        response = urllib2.urlopen(req)
        data = dict([tuple(i.split('=')) for i in response.read().split('&')])
        self.users[data['screen_name']] = twitter.Api('BGCXJGj3E24xIPXC3Vq1dA', 'wdn5ozSjfLRXmCWN0ObOqB0Hnb2K5rHSitYu6EpoBA', data['oauth_token'], data['oauth_token_secret'])
        self.save()
            
    def signRequest(self, url, http_method, values):
        temp_signature = ''
        ordered_list = values.keys()
        ordered_list.sort()
        for i in ordered_list:
            temp_signature += i + '=' + urllib.quote(values[i], '') + '&'
        temp_signature = temp_signature[:-1]
        base_string = http_method.upper()+'&' + urllib.quote(url, '') + '&' + urllib.quote(temp_signature, '')
        signing_key = urllib.quote('wdn5ozSjfLRXmCWN0ObOqB0Hnb2K5rHSitYu6EpoBA', '') + '&'
        hashed = hmac.new(signing_key, base_string, sha1)
        oauth_signature = b2a_base64(hashed.digest())[:-1]
        return oauth_signature
        
    def makeDST(self, values):
        DST = 'OAuth '
        ordered_list = values.keys()
        ordered_list.sort()
        for i in ordered_list:
            DST += urllib.quote(i, '') + '="' + urllib.quote(values[i], '') + '", '
        DST = DST[:-2]
        return DST
        
    def makeNonce(self):
        nonce = ''
        for i in repeat(None, 32*8):
            nonce += str(choice(range(10)))
        nonce = b64encode(nonce)
        nonce = ''.join(c for c in nonce if c in string.lowercase+string.uppercase+string.digits)
        return nonce
        
    def triggered(self, triggering_thread_name, *args):
        if triggering_thread_name in self.rules.keys():
            print 'Rule was triggered - taking action ' + self.rules[triggering_thread_name]
        
    ######
    #Interaction commands here
    ######
    
    def help(self, *items):
        print self.commands.keys()
    
    def addUser(self, args=[]):
        oauth_token = self.requestPIN()
        self.validateUser(raw_input('Please enter the PIN from the web page'), oauth_token)
    
    def deleteUser(self, args=[]):
        if args==[]:
            username = raw_input('Delete which user? ')
        else:
            username = args[0]
        if username not in self.users.keys():
            raise ValueError('User not recognised')
        self.users.__delitem__(username)
    
    def view_users(self, args):
        print ''
        for i in self.users.keys(): print i
        print ''
        
    def post(self, args=[]):
        if args==[]:
            user = raw_input('What username? ')
        if len(args) > 1:
            status = args[1]
        else:
            status = raw_input('What do you want to post? ')
        if self.users.has_key(user):
            self.users[user].PostUpdate(status)
        else:
            raise ValueError('No such registered user - ' + user)
            
    def makeRule(self, args=[]):
        '''Args as [username, triggerType, conditions, action, ...]'''
        username, triggerType, conditions, action = args[:4]
        additionalargs = args[4:]
        if username not in self.users.keys():
            raise ValueError('User not registered')
        rules.Rule(self.users[username], self, [[[triggerType, additionalargs]], None, None])
        
    def save(self, args=[]):
        for api in self.users.values():
            api._urllib = 'POINTER TO URLLIB2'
        with file('saved_users.pkl', 'w') as f:
            pickle.dump(self.users, f)
        for api in self.users.values():
            api._urllib = urllib2
        with file('saved_rules.pkl', 'w') as f:
            pickle.dump(self.rules, f)
        with file('saved_responses.pkl', 'w') as f:
            pickle.dump(self.responses, f)
            
    def load(self, args=[]):
        if os.path.exists('saved_users.pkl'):
            self.users = pickle.load(file('saved_users.pkl', 'r'))
            for api in self.users.values():
                if api._urllib == 'POINTER TO URLLIB2':
                    api._urllib = urllib2
        else:
            self.users = {}
        if os.path.exists('saved_rules.pkl'):
            self.rules = pickle.load(file('saved_rules.pkl', 'r'))
        else:
            self.rules = {}
        if os.path.exists('saved_responses.pkl'):
            self.responses = pickle.load(file('saved_responses.pkl', 'r'))
        else:
            self.responses = {}
        
    #####
    #main interation
    #####
    
        
    def main(self):
        while True:
            command = raw_input('What would you like to do? ')
            split_command=command.split(' ')
            if split_command[0] == 'exit':
                break
            if self.commands.has_key(split_command[0]):
                self.commands[split_command[0]](split_command[1:])
            else:
                print 'Sorry, that\'s not a recognized command. '
        
if __name__ == '__main__':
    ot = OrtoTweet()
    interface.launch(ot)
    
otApi = twitter.Api('BGCXJGj3E24xIPXC3Vq1dA', 'wdn5ozSjfLRXmCWN0ObOqB0Hnb2K5rHSitYu6EpoBA', '19688598-0ArsW160fmWQ3GBiutXaDVK7R6O2MRLQPS8erLmV4', '6VtJKcxi1PXA3yUH0Dl2WuOk4Sdeo668QW4sLvclGII')
