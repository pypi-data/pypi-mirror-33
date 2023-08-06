import requests, random

class SMSAuthorizer:

    def __init__(self, **kwargs):
        self.author = kwargs["author"]
        self.sid = kwargs["sid"]
        self.token = kwargs["token"]

    class FormatException(Exception):
        pass

    def authorize(self, **kwargs):
        code = ""
        for i in range(kwargs["code_length"]):
            code += str(random.randint(0, 9))
        if "message" not in kwargs.keys():
            message = "Your verification code is: " + code
        else:
            message_l = kwargs["message"].split("[]")
            if len(message_l) != 2:
                raise self.FormatException("Format your message with '[]' in place of the verification code.")
            message = message_l[0] + code + message_l[1]
        r = requests.post("https://api.twilio.com/2010-04-01/Accounts/" + self.sid + "/Messages.json", data={"To": kwargs["check"], "From": self.author, "Body": message}, auth=(self.sid, self.token))
        resp = r.json()
        if resp["status"] != "queued":
            raise RuntimeError("Status: " + str(resp["status"]) + "\n" + resp["message"] + "\nMore Info: " + resp["more_info"])
        return code