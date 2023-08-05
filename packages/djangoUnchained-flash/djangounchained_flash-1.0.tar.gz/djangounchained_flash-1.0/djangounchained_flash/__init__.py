class ErrorManager:
    def __init__(self):
        self.messages=[]
    def addMessage(self, message, tag='X9583SSSS2###d'):
        toAdd=ErrorMessage(message, tag)
        self.messages.append(toAdd)
        return self
    def getMessages(self, tag='X9583SSSS2###d'):
        if tag=='X9583SSSS2###d':
            return self.messages
        else:
            output=[]
            for message in self.messages:
                if(message.tag==tag):
                    output.append(message)
            return output

class ErrorMessage:
    def __init__(self, message, tag):
        self.message=message
        self.tag=tag