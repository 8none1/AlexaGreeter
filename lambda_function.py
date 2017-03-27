#!/usr/bin/python

import requests

def build_speechlet_response(title, output, reprompt_text, should_end_session):
    return {
        'outputSpeech': {
            'type': 'PlainText',
            'text': output
        },
        'card': {
            'type': 'Simple',
            'title': "Greeter",
            'content': output
        },
        'reprompt': {
            'outputSpeech': {
                'type': 'PlainText',
                'text': reprompt_text
            }
        },
        'shouldEndSession': should_end_session
    }


def build_response(session_attributes, speechlet_response):
    return {
        'version': '1.0',
        'sessionAttributes': session_attributes,
        'response': speechlet_response
    }
    

def get_user_info(access_token):
    #print access_token
    amazonProfileURL = 'https://api.amazon.com/user/profile?access_token='
    r = requests.get(url=amazonProfileURL+access_token)
    if r.status_code == 200:
        return r.json()
    else:
        return False

def handle_end():
    return build_response({}, build_speechlet_response("Session ended", "Goodbye!", "", True))

def launch_request(access_token):
    session_attributes = {}
    card_title = "Welcome"
    if access_token is None:
        speech_output = "Your user details are not available at this time.  Have you completed account linking via the Alexa app?"
        reprompt_text = ""
        should_end_session = True
    else:
        user_details = get_user_info(access_token)
        if user_details is None:
            speech_output = "There was a problem getting your user details."
            should_end_sesion = True
        else:
            print user_details
            speech_output = "Hello "+user_details['name'].split(" ")[0]+"!  I know all about you now.  We can be friends!"
            reprompt_text = "What can I tell you about your user information?  First name, last name, email address or postcode?"
            should_end_session = False
    return build_response(session_attributes, build_speechlet_response(
        card_title, speech_output, reprompt_text, should_end_session))

def intent_request(intent_request, access_token):
    intent = intent_request['intent']
    intent_name = intent['name']
    
    if intent_name == "GreetIntent":           
        if access_token is not None:
            user_details = get_user_info(access_token)
            if user_details is None:
                query_type = False
            else:
                query_type = intent['slots']['Options']['value']
        else:
            return handle_end()
        
        if query_type == "post code":
            speech_output = "Your post code is "+user_details['postal_code']+"."
        elif query_type == "first name":
            speech_output = "Your first name is "+user_details['name'].split(" ")[0]+"."
        elif query_type == "last name":
            speech_output = "Your last name is "+user_details['name'].split(" ")[1]+"."
        elif query_type == "email address":
            speech_output = "Your email address is "+user_details['email']+"."
        elif query_type == "user id":
            speech_output = "Your user id is "+user_details['user_id']+"."
        else:
            speech_output = "Something went wrong.  Goodbye."
        card_title = "What I know about you"
        return build_response({}, build_speechlet_response(card_title, speech_output, None, True))
        
    if intent_name == "AMAZON.HelpIntent":
        print "Help intent"
        card_title = "No help available!"
        speech_output = "Sorry, I can't help you."
        return build_response({}, build_speechlet_response(card_title, speech_output, None, True))
        
    if intent_name == "AMAZON.CancelIntent" or intent_name == "AMAZON.StopIntent":
        card_title = "Session Ended"
        speech_output = "Good bye!"
        return build_response({}, build_speechlet_response(card_title, speech_output, None, True))
    


def lambda_handler(event, context):
    print event
    try:
        access_token = event['context']['System']['user']['accessToken']
    except:
        access_token = None
    if event['request']['type'] == "LaunchRequest":
        return launch_request(access_token)
    elif event['request']['type'] == "IntentRequest":
        return intent_request(event['request'],access_token)

