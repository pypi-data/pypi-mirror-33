import asyncio, aiohttp, requests, random

class SMSAuthorizer:

    def __init__(self, *, author: str, sid: str, token: str, session=None):
        self.author = author
        self.sid = sid
        self.token = token
        self.session = session or aiohttp.ClientSession()

    class FormatException(Exception):
        pass

    def authorize(self, *, check: str, message: str=None, code_length: int):
        code = ""
        for i in range(code_length):
            code += str(random.randint(0, 9))
        if not message:
            message = f"Your verification code is: {code}"
        else:
            message_l = message.split("[]")
            if len(message_l) != 2:
                raise self.FormatException("Format your message with '[]' in place of the verification code.")
            message = f"{message_l[0]}{code}{message_l[1]}"
        r = requests.post(f"https://api.twilio.com/2010-04-01/Accounts/{self.sid}/Messages.json", data={"To": check, "From": self.author, "Body": message}, auth=(self.sid, self.token))
        resp = r.json()
        if resp["status"] != "queued":
            raise RuntimeError("Status: " + str(resp["status"]) + "\n" + resp["message"] + "\nMore Info: " + resp["more_info"])
        return code

    async def authorize_async(self, *, check: str, message: str=None, code_length: int):
        code = ""
        for i in range(code_length):
            code += str(random.randint(0, 9))
        if not message:
            message = f"Your verification code is: {code}"
        else:
            message_l = message.split("[]")
            if len(message_l) != 2:
                raise self.FormatException("Format your message with '[]' in place of the verification code.")
            message = f"{message_l[0]}{code}{message_l[1]}"
        auth = aiohttp.BasicAuth(login=self.sid, password=self.token)
        async with self.session.post(f"https://api.twilio.com/2010-04-01/Accounts/{self.sid}/Messages.json", data={"To": check, "From": self.author, "Body": message}, auth=auth) as resp:
            r_json = await resp.json()
        if r_json["status"] != "queued":
            raise RuntimeError("Status: " + str(r_json["status"]) + "\n" + r_json["message"] + "\nMore Info: " + r_json["more_info"])
        return code