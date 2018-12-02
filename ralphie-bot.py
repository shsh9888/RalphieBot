import os
import time
import re
from slackclient import SlackClient
from pymongo import MongoClient
from bson.json_util import dumps
from collections import Counter
import string
import math
import json

import nltk

# Please download once
#nltk.download('averaged_perceptron_tagger')
from nltk.tag import pos_tag

# instantiate Slack client
slack_client = SlackClient(os.environ.get('SLACK_BOT_TOKEN'))
# starterbot's user ID in Slack: value is assigned after the bot starts up
starterbot_id = None

# constants
RTM_READ_DELAY = 1 # 1 second delay between reading from RTM
EXAMPLE_COMMAND = "do"
MENTION_REGEX = "^<@(|[WU].+?)>(.*)"

def parse_bot_commands(slack_events):
    """
        Parses a list of events coming from the Slack RTM API to find bot commands.
        If a bot command is found, this function returns a tuple of command and channel.
        If its not found, then this function returns None, None.
    """
    for event in slack_events:
        if event["type"] == "message" and not "subtype" in event:
            user_id, message = parse_direct_mention(event["text"])
            if user_id == starterbot_id:
                return message, event["channel"]
    return None, None

def parse_direct_mention(message_text):
    """
        Finds a direct mention (a mention that is at the beginning) in message text
        and returns the user ID which was mentioned. If there is no direct mention, returns None
    """
    matches = re.search(MENTION_REGEX, message_text)
    # the first group contains the username, the second group contains the remaining message
    return (matches.group(1), matches.group(2).strip()) if matches else (None, None)

def handle_command(command, channel, channel_name):
    """
        Executes bot command if the command is known
    """
    # Default response is help text for the user
    default_response = "IDK.".format(EXAMPLE_COMMAND)

    # Finds and executes the given command, filling in response
    response = None
    # This is where you start to implement more commands!
    result_dict = parse_query(command)
    #result_dict["category"] = channel_name
    #if command.startswith(EXAMPLE_COMMAND):
        #response = "Sure...write some more code then I can do that!"
    result = fetch_from_db(result_dict)
    response = []



    for document in result: 
        response.append(dumps(document))
    # Sends the response back to the channel
    slack_client.api_call(
        "chat.postMessage",
        channel=channel,
        text=dumps(response) or default_response
    )


def fetch_from_db(result_dict):
    # connect to MongoDB, change the << MONGODB URL >> to reflect your own connection string
    client = MongoClient("127.0.0.1", username='student', password='student', authSource='ralphiedb')
    db=client.ralphiedb
    responses = []
    allRes = []
    flag = 0

    for key, val in result_dict.items():
        
        # response = db.ralphiebot.find({key : {"$in": val}})
        responseOld = db.ralphiebot.find({key : {"$in": val}})
        response = {}

        for rr in responseOld:
            for key, val in rr.items():
                key = str(key)
                val = str(val)
                udata=key.decode("utf-8")
                keyA=udata.encode("ascii","ignore")

                udata=val.decode("utf-8")
                valA=udata.encode("ascii","ignore")
                response[keyA] = valA

        if bool(response):
            responses.append(response)

    idL = []
    ans_d={}

    # try:
    print (responses)

    if len(responses) == 1:
        if "_id" not in responses[0]:
            return ans_d.values()
        ans_d[responses[0]['_id']] = responses[0]
        print ("len=1: ",responses[0])
        # return responses[0]
        return ans_d.values()

    for res in responses:
        print ("A response:", res)
        if bool(res):
            if res['_id'] not in idL:
                idL.append(res['_id'])
            else:
                ans_d[res['_id']] = res

    return ans_d.values()
    # except Exception as e:
    #     return ["Please contact Rajshree!"]


def parse_query(questionString):
    script_dir = os.path.dirname(__file__)
    wb = "wordbag.json"
    wb = os.path.join(script_dir, wb)
    wb = open(wb, "r")

    courseKW = []
    housingKW = []

    wordBag1 = json.loads(wb.read())
    wordBag = {}

    for key, val in wordBag1.items():
        udata=key.decode("utf-8")
        keyA=udata.encode("ascii","ignore")

        udata=val.decode("utf-8")
        valA=udata.encode("ascii","ignore")
        wordBag[keyA] = valA
        
    # questionString = "what are the subjects offered by instructor James Martin is taking"
    # questionString = "When is the subject CSCI112 CS12 taken by instructor ABC XYS"
    # questionString = "When is the deadline for transcript submission"
    #questionString = "what are the subjects of CSCI offered in fall 2018"
    # questionString = "who are the instructors teaching in fall 2018"

    words1 = questionString.split(" ")
    words = []
    for w in words1:
        udata=w.decode("utf-8")
        asciidata=udata.encode("ascii","ignore")
        words.append(asciidata)

    tagged_sent = pos_tag(words)
    print (tagged_sent)
    columns = {}

    for iw, word in enumerate(words):
        if word in wordBag.keys():
            pn = []
            aPN = ""
            for ip in tagged_sent[iw+1:]:
                if ip[1] == 'NNP' or ip[1] == 'NN' or ip[1] == 'CD':
                    if aPN == "":
                        aPN = ip[0]
                    else:
                        aPN += " "+ip[0]
                elif ip[1] == 'IN':
                    continue
                else:
                    break
            pn.append(aPN)
            columns[wordBag[word]] = [word]+pn

    # propernouns = [word for word,pos in tagged_sent if pos == 'NNP']

    # if len(propernouns) != 0:
    #   columns["PN"] = propernouns
    print (columns)
    return columns
if __name__ == "__main__":
    if slack_client.rtm_connect(with_team_state=False):
        print("Starter Bot connected and running!")
        # Read bot's user ID by calling Web API method `auth.test`
        starterbot_id = slack_client.api_call("auth.test")["user_id"]
        while True:
            command, channel = parse_bot_commands(slack_client.rtm_read())
            if command:
                channel_info=slack_client.api_call("channels.info",channel=channel)
                handle_command(command, channel, channel_info["channel"]["name"])
            time.sleep(RTM_READ_DELAY)
    else:
        print("Connection failed. Exception traceback printed above.")