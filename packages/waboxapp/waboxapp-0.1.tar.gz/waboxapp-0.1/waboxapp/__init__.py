
import os
import urllib 
import urllib2 
import uuid

class Waboxapp(object):
    def __init__(self, api_key=None, source_number=None):
        self.api_key = api_key or os.environ.get("WABOX_KEY")
        self.source_number = source_number or os.environ.get("WABOX_SRCNUMBER")

    def send_message(self, to, text, msgid=None):
        msgid = msgid or str(uuid.uuid4())
        data = urllib.urlencode({"token":self.api_key,
                                 "uid":self.source_number,
                                 "to":to,
                                 "custom_uid":msgid,
                                 "text":text}) 
        req = urllib2.Request('https://www.waboxapp.com/api/send/chat', data) 
        response = urllib2.urlopen(req) 
        result = response.read()
        return result


if __name__ == "__main__":
    wbox = Waboxapp()
    wbox.send_message(os.environ.get("WABOX_DSTNUMBER"), "this is a pywabox test")


