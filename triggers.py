import time
import threading

def createTrigger(api=None, parentApp=None, triggerType=None, *args):
	if triggerType == None:
		triggerType = raw_input('What type of trigger? ')
	if triggerType=="time":
		pass
	elif triggerType=="mention":
		t=threading.Thread(None, mentionTrigger, args=[api, parentApp]+list(args))
		t.daemon = True
		t.start()
	elif triggerType=="keyword":
		pass
	else:
		raise ValueError('No trigger of that type recognised')
		
def mentionTrigger(*args):
    '''
    args is a list of arguments, of the form [api, parentApp, [args1]], where args1 is [delay, latest=None]
    '''
    threadName = threading.currentThread().name
    api=args[0]
    parentApp=args[1]
    delay=args[2][0]
    parentApp.rules[threadName] = 'replyFromList'
    if len(args[2]) > 1:
        latest = args[2][1]
    else:
        latest = None
    while True:
        print 'Loop begin - latest is ' + repr(latest)
        if latest != None:
            mentions=api.GetMentions(latest)
        else:
            mentions=api.GetMentions()
        if mentions != []:
            latest = mentions[0].id
            for tweet in mentions:
                parentApp.triggered(threadName, api, tweet)
        time.sleep(float(delay))
	
		
