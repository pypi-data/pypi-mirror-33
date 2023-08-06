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
        if self.verify_token(token):
            if self.db.get_user_token(self.verify.steem.username):
                self.db.update_token(self.verify.steem.username, 
                            self.verify.steem.accesstoken, 
                            self.verify.steem.refreshtoken)
            else:
                self.db.add_user(self.verify.steem.username, 
                            self.verify.steem.privatekey, 
                            self.verify.steem.refreshtoken, 
                            self.verify.steem.accesstoken)
            return ("\r\n" 
                    + self.template("index.html", 
                    ACCOUNT1=self.verify.steem.username,
                    REFRESHTOKEN=self.verify.steem.refreshtoken))
        else:
            return self.auth_url()


    def invite (self, token, account2, per, ratio, dur, response, ip):
        ''' Creates an invite
        '''
        if not verify_recaptcha(response, ip):
            return self.error_page("Invalid captcha.")
        if self.verify_token(sec.filter_token(token)):
            account2 = sec.filter_account(account2)
            if self.verify.steem.check_balances(account2):
                memoid = self.db.add_invite(self.verify.steem.username, 
                                    account2,  
                                    sec.filter_number(per), 
                                    sec.filter_number(ratio), 
                                    sec.filter_number(dur))
                return "\r\n <h1>Memo created</h1><br><h4>" + str(memoid) + ":accept</h4>"
            else:
                return self.error_page("Invalid account name.")
        else:
            return self.auth_url()


    def verify_token (self, token):
        ''' cleans and verifies a SteemConnect
        refresh token
        '''
        token = sec.filter_token(token)
        if (token is not None
                    and self.verify.steem.verify_key (
                    acctname="", tokenkey=token)):
            return True
        else:
            return False


    def auth_url (self):
        ''' Returns the SteemConnect authorization
        URL for SteemAX
        '''
        url = self.verify.steem.connect.auth_url()
        return ("Location: " + url + "\r\n")


    def error_page (self, msg):
        ''' Rutrns the HTML page with the
        given error message
        '''
        return ("\r\n" + self.template("error.html", 
                                ERRORMSG=msg))


    def verify_recaptcha(response, remoteip):
        data = {
            'secret': default.recaptcha_secret,
            'response': response
            'remoreip': remoteip
        }
        encoded = parse.urlencode(data).encode()
        req = request.Request(default.recaptcha_url, data=encoded)
        with request.urlopen(req) as resp:
            self.json_resp = json.loads(resp.read().decode('utf-8'))
            if self.json_resp['success']:
                return True
            else:
                return False


# EOF
