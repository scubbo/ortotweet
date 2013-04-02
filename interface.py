from Tkinter import *

class Interface:
    def __init__(self, master, ot):
        self.master = master
        self.ot = ot
        
        mainFrame = Frame(master, bg='black')
        mainFrame.grid()
        
        self.mainFrame = mainFrame
        
        leftColumn = Frame(mainFrame, bg=mainFrame['bg'])
        leftColumn.grid(row=0, column=0)
        
        middleColumn = Frame(mainFrame, bg=mainFrame['bg'])
        middleColumn.grid(row=0, column=1, padx=1)
        
        rightColumn = Frame(mainFrame, bg=mainFrame['bg'])
        rightColumn.grid(row=0, column=2)
        
        accountsFrame = Frame(leftColumn)
        accountsFrame.grid(row=0, pady=[0, 1])
        
        responseFrame = Frame(leftColumn)
        responseFrame.grid(row=1, rowspan=2)
        
        rulesFrame = Frame(middleColumn)
        rulesFrame.grid(row=0, rowspan=2, pady=[0, 1], sticky=NS)
        
        quickTweetFrame = Frame(middleColumn)
        quickTweetFrame.grid(row=3, sticky=S)
        
        timelineFrame = Frame(rightColumn)
        timelineFrame.grid(row=0, rowspan=3, sticky=NS)
        
        self.populateAccountsFrame(accountsFrame)
        self.populateResponseFrame(responseFrame)
        self.populateRulesFrame(rulesFrame)
        self.populateQuickTweetFrame(quickTweetFrame)
        self.populateTimelineFrame(timelineFrame)
        
    def populateAccountsFrame(self, accountsFrame):
        accountsTitle = Label(accountsFrame, text='Accounts')
        accountsTitle.grid(row=0, columnspan=2)
        
        accountList = Listbox(accountsFrame)
        for user in self.ot.users.keys():
            accountList.insert(END, user)
        accountList.grid(row=1, columnspan=2)
        self.accountList = accountList
        
        accountAdd = Button(accountsFrame, text='ADD', command=lambda: self.addAccount(accountList))
        accountAdd.grid(row=2, column=0, sticky=W)
        
        accountDel = Button(accountsFrame, text='DEL', command=lambda: self.delAccount(accountList))
        accountDel.grid(row=2, column=1, sticky=E)
        
    def populateResponseFrame(self, responseFrame):
        responseTitle = Label(responseFrame, text='Response Lists')
        responseTitle.grid(row=0, columnspan=3)
        
        responseList = Listbox(responseFrame)
        responseList.grid(row=1, columnspan=3)
        self.responseList = responseList
        
        responseAdd = Button(responseFrame, text='Add', command=self.addResponse)
        responseAdd.grid(row=2, column=0)
        
        responseEdit = Button(responseFrame, text='Edit - not yet active', command=lambda: self.editReponse(responseList))
        responseEdit.grid(row=2, column=1)
        
        responseDelete = Button(responseFrame, text='Del', command=lambda: self.deleteResponse(responseList))
        responseDelete.grid(row=2, column=2)
        self.populateResponseList(responseList)
        
    def populateRulesFrame(self, rulesFrame):
        rulesTitle = Label(rulesFrame, text='Rules')
        rulesTitle.grid()
        
    def populateQuickTweetFrame(self, quickTweetFrame):
        quickTweetTitle = Label(quickTweetFrame, text='Quick Tweet:')
        quickTweetTitle.grid(column=0, sticky=S)
        
        self.quickTweetUserVariable = StringVar(self.master)
        users = self.master.
        quickTweetDropDown = OptionMenu(quickTweetFrame, self.quickTweetUserVariable, 'one', 'two', 'three')
        quickTweetDropDown.grid(column=1)
        
        quickTweetEntry = Entry(quickTweetFrame)
        quickTweetEntry.grid(column=2, sticky=S)
        
        quickTweetSubmit = Button(quickTweetFrame, command=lambda: self.quickTweetSubmitButton(quickTweetDropDown, quickTweetEntry))
        quickTweetSubmit.grid(column=3)
        
    def populateTimelineFrame(self, timelineFrame):
        timelineTitle = Label(timelineFrame, text='Timeline')
        timelineTitle.grid()
    
    #End of gridding and layout functions
        
    def addAccount(self, accountList):
        oauth_token = self.ot.requestPIN()
        
        newUserRoot=Tk()
        newUserLabel = Label(newUserRoot, text='Please enter the pin from the web page')
        newUserLabel.grid()
        newUserPINInput = Entry(newUserRoot)
        newUserPINInput.grid(row=1)
        newUserButton = Button(newUserRoot, text='OK', command=lambda: self.addAccountButton(newUserPINInput, oauth_token, accountList))
        newUserButton.grid()
        newUserRoot.mainloop()
        
    def addAccountButton(self, theInput, oauth_token, accountList):
        self.ot.validateUser(theInput.get(), oauth_token)
        accountList.delete(0, END)
        for user in self.ot.users:
            accountList.insert(END, user)
        theInput.master.destroy()
        
    def delAccount(self, theAccountList):
        theAccount = theAccountList.get(ACTIVE)
        self.ot.users.__delitem__(theAccount)
        theAccountList.delete(ACTIVE)
        self.ot.save()
        
    def populateResponseList(self, responseList):
        for responses in self.ot.responses.keys():
            responseList.insert(END, responses)
        
    def addResponse(self):
        newResponseRoot=Tk()
        
        newResponseTitleLabel = Label(newResponseRoot, text='Please name the response list:')
        newResponseTitleLabel.grid(row=0, column=0)
        
        newResponseTitleEntry = Entry(newResponseRoot)
        newResponseTitleEntry.grid(row=0, column=1)
        
        newResponseMemberLabel = Label(newResponseRoot, text='Enter a response:')
        newResponseMemberLabel.grid(row=1, column=0)
        
        newResponseMemberEntry = Entry(newResponseRoot)
        newResponseMemberEntry.grid(row=1, column=1)
        
        newResponseList = Listbox(newResponseRoot)
        newResponseList.grid(row=2, column=0, columnspan=3)
        
        newResponseMemberAdd = Button(newResponseRoot, text='Add', command=lambda:self.newResponseMemberAddButton(newResponseMemberEntry, newResponseList))
        newResponseMemberAdd.grid(row=1, column=2)
        
        newResponseDelete = Button(newResponseRoot, text='Delete', command=lambda:self.newResponseDeleteButton(newResponseList))
        newResponseDelete.grid(row=3, column=0)
        
        newResponseDone = Button(newResponseRoot, text='Done', command=lambda:self.newResponseDoneButton(newResponseTitleEntry, newResponseList))
        newResponseDone.grid(row=3, column=1)
        
    def newResponseMemberAddButton(self, newResponseMemberEntry, newResponseList):
        newResponseList.insert(END, newResponseMemberEntry.get())
        newResponseMemberEntry.delete(0, END)
    
    def newResponseDeleteButton(self, newResponseList):
        newResponseList.delete(ACTIVE)
        
    def newResponseDoneButton(self, newResponseTitleEntry, newResponseList):
        responseList = [response for response in newResponseList.get(0, END)]
        self.ot.responses[newResponseTitleEntry.get()] = responseList
        self.responseList.insert(END, newResponseTitleEntry.get())
        newResponseTitleEntry.master.destroy()
        self.ot.save()
        
    def quickTweetSubmitButton(self, quickTweetDropDown, quickTweetEntry):
        pass
        
    def deleteResponse(self, responseList):
        responseList.delete(ACTIVE)
    
def launch(ot):
    root=Tk()
    app = Interface(root, ot)
    root.mainloop()
