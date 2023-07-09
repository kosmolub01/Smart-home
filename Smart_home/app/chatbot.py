from pydoc_data import topics
import nltk
from nltk.chat.util import Chat, reflections
import re

class Chatbot:
    # Initializes Chatbot with the devices and their locations. 
    # devices - list of tuples, where device is the first element of a tuple, 
    # and its location is the second element.
    def __init__(self, devices) -> None:
        self.devices = devices

         # Define the chatbot's responses to user input
        self.pairs = [
        ['my name is (.*)', ['introduction %1']],
        ['hi|hello|hey', ['Hi there!', 'Hello!']],
        ['what is your name?', ['My name is Bot.']],
        ['how are you?', ['I am doing well, thank you!']],
        ['bye|goodbye', ['Goodbye!', 'Bye!']],
        ['(.*)value(.*)', ['value']],
        ['(.*)turn on(.*)', ['turn on']],
        ['(.*)turn off(.*)', ['turn off']],
        ['(.*)switch on(.*)', ['switch on']],
        ['(.*)switch off(.*)', ['switch off']],
        ['(.*)set to(.*)', ['set to']],
        ['.*', ['I am not sure what you are trying to say.']]
        ]

        # Create a Chat instance
        self.chat = Chat(self.pairs, reflections)

    # Sends message to the Chatbot. Chatbot processes the message and returns the answer.
    # If user uses smart-home functions, then returns list [<command type>, <device>, <location>]
    # or [<command type>, <device>, <location>, <value>] in case of 'set to' command.
    def send_message(self, message):
        response = self.chat.respond(message)

        # Needed to extract value to be set with 'set to' command.
        numeric_const_pattern = '[-+]? (?: (?: \d* \. \d+ ) | (?: \d+ \.? ) )(?: [Ee] [+-]? \d+ ) ?'
        rx = re.compile(numeric_const_pattern, re.VERBOSE)

        # Check if user uses smart-home functions, then react accordingly.
        if response == 'value':
            for device, location in self.devices:
                if message.find(device) != -1 and message.find(location) != -1:
                    return ['value', device, location]
                else:
                    response = "I am not sure what you are trying to say."

        elif response == 'turn on':
            for device, location in self.devices:
                if message.find(device) != -1 and message.find(location) != -1:
                    return ['turn on', device, location]
                else:
                    response = "I am not sure what you are trying to say."

        elif response == 'turn off':
            for device, location in self.devices:
                if message.find(device) != -1 and message.find(location) != -1:
                    return ['turn off', device, location]
                else:
                    response = "I am not sure what you are trying to say."

        elif response == 'switch on':
            for device, location in self.devices:
                if message.find(device) != -1 and message.find(location) != -1:
                    return ['switch on', device, location]
                else:
                    response = "I am not sure what you are trying to say."

        elif response == 'switch off':
            for device, location in self.devices:
                if message.find(device) != -1 and message.find(location) != -1:
                    return ['switch off', device, location]
                else:
                    response = "I am not sure what you are trying to say."

        elif response == 'set to':
            for device, location in self.devices:
                if message.find(device) != -1 and message.find(location) != -1:
                    value = rx.findall(message, message.find('set to') + 7)
                    return ['set to', device, location, str(value[0])]
                else:
                    response = "I am not sure what you are trying to say."

        # If user introduced himself, then take additional action to start his name 
        # with a capital letter (for some reason NLTK chat response is with small letter).
        elif response.find('introduction') != -1:
            name = response.replace('introduction ', '')
            capitalized_name = name.capitalize()
            response = 'Hello ' + capitalized_name + '!'

        return response
