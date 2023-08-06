#!/usr/bin/python3

import re
from steemax import axverify
from steemax import axdb
from steemax import default
from steemax import sec

class Web:


    def __init__ (self):
        self.verify = axverify.AXverify()
        self.db = axdb.AXdb(default.dbuser, 
                        default.dbpass, 
                        default.dbname)


    def template (self, templatefile="", **kwargs):
        ''' opens a template file and fills in the 
        template with the key value pairs
        '''
        fh = open(templatefile, 'r')
        template = fh.read()
        regobj = re.compile(
            r"^(.+)(?:\n|\r\n?)((?:(?:\n|\r\n?).+)+)", 
            re.MULTILINE)
        newtemplate = regobj.sub('', template)
        for key, value in kwargs.items():
            newtemplate = re.sub(str(key), 
                                str(value), 
                                newtemplate)
        return newtemplate


    def login (self, token):
        ''' logs a user in using SteemConnect
        adds the user to the database if it's
        their first time.
        '''
        if self.verifytoken(token):
            if self.db.get_user_token(self.username):
                self.db.update_token(self.username, 
                            self.verify.steem.accesstoken, 
                            self.verify.steem.refreshtoken)
            else:
                self.db.add_user(self.username, 
                            self.verify.steem.privatekey, 
                            self.verify.steem.refreshtoken, 
                            self.verify.steem.accesstoken)
            return ("\r\n" + self.template("index.html", 
                                ACCOUNT1=self.username))
        else:
            return self.auth()


    def invite (self, token, account2, per, ratio, dur):
        ''' Creates an invite
        '''
        if self.verifytoken(sec.filter_token(token)):
            account2 = sec.filter_account(account2)
            if self.verify.steem.check_balances(account2):
                memoid = self.db.add_invite(self.username, 
                                    account2,  
                                    sec.filter_number(per), 
                                    sec.filter_number(ratio), 
                                    sec.filter_number(dur))
                return "\r\n <h1>Memo created</h1><br><h4>" + memoid + ":accept</h4>"
            else:
                return self.error("Invalid account name.")
        else:
            return self.auth()


    def verifytoken (self, token):
        ''' cleans and verifies a SteemConnect
        refresh token, then attains the user's 
        Steemit account name.
        '''
        token = sec.filter_token(token)
        if (token is not None
                    and self.verify.steem.verify_key (
                    acctname="", tokenkey=token)):
            self.username = self.verify.steem.username
            return True
        else:
            return False


    def auth (self):
        ''' Returns the SteemConnect authorization
        URL for SteemAX
        '''
        url = self.verify.steem.connect.auth_url()
        return ("Location: " + url + "\r\n")


    def error (self, msg):
        ''' Rutrns the HTML page with the
        given error message
        '''
        return ("\r\n" + self.template("error.html", 
                                ERRORMSG=msg))


# EOF
