STEP 1) In terminal, run the command:

pip install jsonpickle

STEP 2) In views.py:
from djangounchained_flash import ErrorManager, ErrorMessage, getFromSession

******INCLUDED FUNCTIONS******

ErrorManager.addMessage(message, tag=optional)
    --pass in a string and a tag parameter for easy access
ErrorManager.getMessages(tag=optional)
    --get all messages, or only the messages with the passed in tag
    --Will return a list of strings
    --Messages will be shown once then removed

******IMPORTANT NOTES********

*Adding to request.session
    request.session['flash']=<instance of ErrorManager>.addToSession()

*Getting from request.session
    e=getFromSession(request.session['flash'])