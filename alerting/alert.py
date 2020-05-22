import schedule
import time
import json
import requests
import urllib3

def notify(specification, body):
    if specification["type"] != "twilio":
        raise "notification type not implemented"
    from_phone = specification["from_phone"]
    to_phone = specification["to_phone"]
    token = specification["token"]
    account = specification["account"]
    headers = {"Authorization": "Basic {}".format(token), "Content-Type": "application/x-www-form-urlencoded"}
    url = "https://api.twilio.com/2010-04-01/Accounts/{}/Messages.json".format(account)
    body_dict = {"To":to_phone, "From":from_phone, "Body":body}
    r = requests.post(url, headers=headers, data=body_dict)

def job(notification):
    url = config["renderer_url"] + notification["params"]
    body = ""
    r = requests.get(url)

    if r.status_code == 200:
        data = r.json()
        if data["state"] != notification.get("state", None):
            send_notification = True
            if ("state" not in notification) and data["state"] == "ok":
                send_notification = False
            if send_notification:
                body = "{} had change from {} to {}".format(notification["name"], notification.get("state", "(unknown)"), data["state"])
                notify(notification["alert_specification"], body)
            notification["state"] = data["state"]

f = open('config.json')
config = json.load(f)
for notification in config["notifications"]:
    schedule.every(notification["interval"]).seconds.do(job, notification)

while True:
    schedule.run_pending()
    time.sleep(5)