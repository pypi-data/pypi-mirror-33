from pythoncom import CoInitialize
from win32com.client import Dispatch
from plover.engine import StenoEngine
class TypedChars:
    def __init__(self,maxCharsToKeep=512):
        self.maxCharsToKeep = maxCharsToKeep
        self.text = ''
        self.unspokenNewText = ''
        self.unspokenRemovedText = ''
        self.haveAddedNewTextSinceRemove = False
        
    def add(self,text):
        isAllSpaces = len(text.strip()) == 0
        if isAllSpaces and not self.haveAddedNewTextSinceRemove:
            self.unspokenNewText = ''
        self.text += text
        self.unspokenNewText += text
        self.unspokenRemovedText = ''
        if not isAllSpaces:
            self.haveAddedNewTextSinceRemove = True
        
    def remove (self,count):
        self.haveAddedNewTextSinceRemove = False
        removed = self.text[-count:]
        self.text = self.text[:-count]
        self.unspokenRemovedText = removed + self.unspokenRemovedText
        self.unspokenNewText = self.unspokenNewText[:-count]
        if not self.unspokenNewText and self.text and not self.text[-1].isspace():
            self.unspokenNewText = self.getLastWord()
        return removed

    def getAndClearUnspokenNewText(self):
        text = self.unspokenNewText
        self.unspokenNewText = ''
        return text
    
    def getAndClearUnspokenRemovedText(self):
        text = self.unspokenRemovedText
        self.unspokenRemovedText = ''
        return text

    def getLastWord(self):
        start = self.text.rfind(' ',0,-1)
        if start == -1:
            return self.text
        return self.text[start+1:]

    def isOnWordBoundary(self):
        return not self.text or self.text[-1].isspace()
    
class PloverJAWS:
    def __init__(self, engine,jawsApi=None):
        super().__init__()
        self.engine = engine
        self.running = False
        CoInitialize()
        self.jaws = jawsApi if jawsApi is not None else Dispatch("freedomsci.jawsapi")
        self.engine.hook_connect('send_string',self.onSendString)
        self.engine.hook_connect('send_backspaces',self.onSendBackspaces)
        self.engine.hook_connect('send_key_combination',self.onSendKeyCombination)
        self.chars = TypedChars()
        self.lastSpoken = ''
        
    def start(self):
        self.running = True
        
    def stop(self):
        self.running = False
        
    def onSendString(self,text):
        if len(text.strip()) == 0:
            self.speakRemovedText()
        self.chars.add(text)
        if self.chars.isOnWordBoundary():
            self.speakNewText()


    def onSendBackspaces(self,count):
        #print('backspace {0}'.format(count))
        self.chars.remove(count)
        if self.chars.isOnWordBoundary():
            self.speakRemovedText()

    def onSendKeyCombination(self,string):
        self.jaws.SayString('keycombo: {0}'.format(string))
    def speak(self,text,alwaysSpeak=True):
        if alwaysSpeak or self.lastSpoken != text:
            self.jaws.SayString(text,False)
        self.lastSpoken = text
        
    def speakNewText(self):
        text = self.chars.getAndClearUnspokenNewText()
        if text and len(text.strip()) > 0:
            self.speak('{0} '.format(text))
    def speakRemovedText(self):
        text = self.chars.getAndClearUnspokenRemovedText()
        if text and len(text.strip()) > 0:
            self.speak('{0} '.format(text))

class MockJawsApi:
    @staticmethod
    def SayString(text,flush=True):
        print(text)

class Tester:
    def hook_connect(self,name,function):
        pass
    
    def load(self,className):
        self.plugin=  className(self,MockJawsApi)
        
    def sendString(self,text):
        self.plugin.onSendString(text)

    def sendBackspaces(self,count):
        self.plugin.onSendBackspaces(count)
        
def test()    :
    engine = Tester()
    engine.load(PloverJAWS)
    engine.sendString("hel")
    engine.sendString("lo ")
    engine.sendString("there")
    engine.sendBackspaces(2)
    engine.sendString("thi")
    engine.sendString("s is a test ")
    engine.sendBackspaces(1)
    engine.sendBackspaces(4)
    engine.sendString('dog ')
    engine.sendString('no ')
    engine.sendBackspaces(1)
    engine.sendString("-no ")
    engine.sendBackspaces(4)
    engine.sendString(' ')
    engine.sendString('another ')
                
if __name__ == "__main__": test()
        

