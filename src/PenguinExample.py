from _ssl import SSLError
import urllib2, urllib, json, time, re, threading, sys

DEBUG_LEVEL = 0  # Set this to 1 to see Headers and Exact content


class DlPenguinClient(object):
    def __init__(self, hostName, userName, password, appID):
        self.baseURL, self.appID, self.eServiceEventHandlers = hostName, appID, []
        self.userName, self.password = userName, password

        self._opener = urllib2.build_opener(urllib2.HTTPSHandler(debuglevel=DEBUG_LEVEL), urllib2.HTTPHandler(debuglevel=DEBUG_LEVEL))

    def login(self):
        fh = self._opener.open(self.baseURL + "/penguin/api/authtokens", urllib.urlencode(
            {"userId": self.userName, "password": self.password, "domain": "DL", "appKey": self.appID}))
        loginMessage = json.loads(fh.read())
        self.authToken = loginMessage["content"]["authToken"]
        self.requestToken = loginMessage["content"]["requestToken"]
        self.gateways = loginMessage["content"]["gateways"]

    def getRelativeURL(self, url, data=None, contentType="application/x-www-form-urlencoded"):
        r = urllib2.Request(re.sub("\\{gatewayGUID}", self.gateways[0]["id"], self.baseURL + url, flags=re.IGNORECASE), headers={'authToken': self.authToken, 'requestToken': self.requestToken, 'appKey': self.appID})
        if data is not None:
            r.data = data
            r.add_header('Content-Type', contentType)
            fh = self._opener.open(r)
        else:
            fh = self._opener.open(r)
        return fh.read()

    def listenToEService(self):
        self.eServiceThread = threading.Thread(target=self.__eServiceHelper)
        self.__eServiceContinue = True
        self.eServiceThread.start()

    def stopEService(self):
        self.__eServiceContinue = False

    def __eServiceHelper(self):
        fh = self._opener.open(self.baseURL + "/messageRelay/pConnection?uuid=" + str(time.time()) + '&app2="""&key=' + self.gateways[0]["id"], timeout=5)

        longerBuffer = ""
        while self.__eServiceContinue:
            try:
                data = fh.read(1)
                if not data:
                    break
                longerBuffer += data
                if longerBuffer.endswith('"""'):
                    longerBuffer = longerBuffer.strip('\n\r\t *"')
                    if len(longerBuffer) > 0:
                        for eventHandler in self.eServiceEventHandlers:
                            eventHandler(longerBuffer)
                            #Custom event handler that sends buffer data to json file for Carl to 
                    longerBuffer = ""
            except SSLError:
                pass  # Caused by read timeout
        print "EService Thread Ending"


def getAttributeValue(deviceJson, attributeName):
    return filter(lambda attrib: attrib["label"] == attributeName, deviceJson["attributes"])[0]["value"]


def hasAttribute(deviceJson, attributeName):
    return len(filter(lambda attrib: attrib["label"] == attributeName, deviceJson["attributes"])) > 0


if __name__ == "__main__":
    APP_ID = "FE_7B1ED62B29D02482_1"
    USERNAME = "553474447"
    PASSWORD = "NO-PASSWD"

    client = DlPenguinClient("https://systest.digitallife.att.com", USERNAME, PASSWORD, APP_ID)
    client.login()
    deviceList = json.loads(client.getRelativeURL("/penguin/api/{gatewayGUID}/inbox"))["content"]
    print  "--- Print inbox messages --"
    print json.dumps(deviceList)
    
    
    
    
