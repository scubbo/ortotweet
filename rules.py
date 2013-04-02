import time
import threading

class Rule:
    def __init__(self, api, parentApp, tca):
        '''tca will be a list of [triggers, conditions, actions], with the following substructures:
        triggers := [[triggerType, triggerArgs], [triggerType, triggerArgs], ... ] where args is particular to the triggerType
        conditions := tbc
        actions := tbc
        '''
        self.api = api
        self.parentApp = parentApp
        triggers, conditions, actions = tca
        #Make conditions and actions
        for trigger in triggers:
            triggerThread = Trigger(self, trigger[0], list(trigger[1]))
        
    def activate(self, trigger, args):
        '''args will be a list of parameters passed from the Trigger object.
        In the case of mention triggerTypes, it will be a singleton list of the triggering tweet object
        '''
        #Replace this with a more general 'carry out defined action' statement
        if trigger.triggerType == 'mention':
            self.api.PostUpdate('@' + args[0].user.screen_name + ' you talkin\' to me?')
            print 'Replied to ' + repr(args[0].user.screen_name)
        elif trigger.triggerType == 'searchTerm':
            print 'I found a matching tweet: \n' + args[0].text
            
    
        
class Trigger:
    def __init__(self, parentRule, triggerType, args):
        self.triggerType = triggerType
        self.parentRule = parentRule
        self.triggerTypes = {
            'mention': threading.Thread(None, self.mentionTrigger, args=[self, self.parentRule.api]+args), 
            'searchTerm': threading.Thread(None, self.searchTermTrigger, args=[self, self.parentRule.api]+args)
        }
        if self.triggerType not in self.triggerTypes.keys():
            raise ValueError('Invalid Trigger Type - ' + self.triggerType)
        self.triggerThread = self.triggerTypes[self.triggerType]
        self.triggerThread.daemon = True
        self.triggerThread.start()
        
    def triggered(self, *args):
        self.parentRule.activate(self, args)
      
    def mentionTrigger(self, *args):
        '''
        args is a list of arguments, of the form [parentTrigger, api, [args1]], where args1 is [delay, latest=None]
        '''
        threadName = threading.currentThread().name
        parentTrigger = args[0]
        api=args[1]
        delay=args[2]
        if len(args) > 3:
            latest = args[3]
        else:
            latest = api.GetPublicTimeline()[0].id
        while True:
            mentions=api.GetMentions(latest)
            if mentions != []:
                latest = mentions[0].id
                for tweet in mentions:
                    parentTrigger.triggered(tweet)
            time.sleep(float(delay))
            
    def searchTermTrigger(self, *args):
        '''
        args is a list of arguments, of the form [parentTrigger, api, [args1]], where args1 is [searchTerm, delay, latest=None]
        '''
        threadName = threading.currentThread().name
        print args
        parentTrigger = args[0]
        api=args[1]
        searchTerm=args[2]
        delay=args[3]
        if len(args) > 4:
            latest = args[4]
        else:
            latest = api.GetPublicTimeline()[0].id
        while True:
            print 'latest is ' + repr(latest)
            results=api.GetSearch(searchTerm, since_id=latest)
            if results != []:
                latest = results[0].id
                for tweet in results:
                    parentTrigger.triggered(tweet)
            time.sleep(float(delay))  
