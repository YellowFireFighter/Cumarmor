import tornado.ioloop
import tornado.web
import os.path
import mysql.connector
import requests
import datetime
import random
import string
import threading
import time

# Connect to the MySQL database
conn = mysql.connector.connect(
  host="localhost",
  user="root",
  password="root",
  auth_plugin='mysql_native_password',
  pool_name = "sqlpool",
  pool_size = 3
)
c = conn.cursor(buffered=True)

c.execute("use main;")

# Create invites table if not exists
create_table_query = '''CREATE TABLE IF NOT EXISTS invites (
                        id VARCHAR(255) PRIMARY KEY,
                        hwid VARCHAR(255) NOT NULL,
                        ip VARCHAR(255) NOT NULL,
                        invite VARCHAR(255) NOT NULL,
                        hwidresets INT NOT NULL,
                        lastreset VARCHAR(255) NOT NULL,
                        oldhwid VARCHAR(255) NOT NULL,
                        oldip VARCHAR(255) NOT NULL,
                        executions INT NOT NULL,
                        version INT NOT NULL
                    )'''
c.execute(create_table_query)

# Ping Database
def ping():
    while True:
        c.execute("SELECT 1")
        print("Pinged DB")
        time.sleep(3600)

query_thread = threading.Thread(target=ping, daemon=True)
query_thread.start()

def GetKeys():
    query = "SELECT invite FROM invites"
    c.execute(query)

    rows = c.fetchall()
    table = []

    for row in rows:
        table.append(list(row))

    return table

class MainHandler(tornado.web.RequestHandler):
    def get(self):
        return self.render("index.html")

class BaseHandler(tornado.web.RequestHandler):
    def get_current_user(self):
        user_id = self.get_secure_cookie("user")
        if not user_id:
            return None
        return int(user_id)

# whitelist
crack_table = {
    "1": "isfunctionhooked",
    "2": "os.time",
    "3": "request",
    "4": "gethwid",
    "5": "wait",
    "6": "os.time",
    "7": "os.date",
    "8": "spawn"
}

# Add own encoding (Removed for security reasons)
def encode_string(string):
    return string

def decode_string(string):
    return string

def generate_random_string(length):
  characters = string.ascii_letters

  result = ''.join(random.choice(characters) for i in range(length))
  return result

execution_webhook = "Webhook_Here"
execution_failed_webhook = "Webhook_Here"
crack_webhook = "Webhook_Here"

def mask_with_spoiler(value):
    """Masks a value using Discord's spoiler feature."""
    return f"||{value}||"

def send_embed(hwid, executor, executions, discord_id, key, script_id, roblox, ip, oldhwid, oldip, webhook):
    masked_ip = mask_with_spoiler(ip)
    masked_roblox_username = mask_with_spoiler(roblox)
    masked_key = mask_with_spoiler(key)
    masked_hwid = mask_with_spoiler(hwid)
    masked_oldhwid = mask_with_spoiler(oldhwid)
    masked_oldip = mask_with_spoiler(oldip)

    embed = {
        "title": "User executed!",
        "description": f"This user has executed the script **{executions}** times in total successfully.",
        "color": 0x00FF00,  # Green color for the embed
        "fields": [
            {"name": "HWID:", "value": masked_hwid, "inline": False},
            {"name": "Executor:", "value": executor, "inline": True},
            {"name": "Discord ID:", "value": f"<@{discord_id}>", "inline": True},
            {"name": "Roblox Username:", "value": masked_roblox_username, "inline": True},
            {"name": "IP Address:", "value": masked_ip, "inline": True},
            {"name": "Key:", "value": masked_key, "inline": False},
            {"name": "Old HWID:", "value": masked_oldhwid, "inline": True},
            {"name": "Old IP:", "value": masked_oldip, "inline": True},
            {"name": "Script:", "value": f"V6\n(ID: {script_id})", "inline": False}
        ],
        "footer": {
            "text": "Crumbleware V6 Whitelist"
        }
    }

    data = {
        "embeds": [embed]  # Send the embed inside an array
    }

    # Send the POST request to the Discord Webhook URL
    result = requests.post(webhook, json=data)

    # Check if the request was successful
    if 200 <= result.status_code < 300:
        print(f"Embed sent successfully: {result.status_code}")
    else:
        print(f"Failed to send embed: {result.status_code}, {result.text}")

def send_embed2(hwid, executor, ip, discord_id, key, webhook, method):
    masked_ip = mask_with_spoiler(ip)
    masked_key = mask_with_spoiler(key)
    masked_hwid = mask_with_spoiler(hwid)
    embed = {
        "title": "Tampering Detected",
        "description": "User Has Possibly Tampered With The Script.",
        "color": 0xFF0000,  # Red color for the embed
        "fields": [
            {"name": "HWID:", "value": masked_hwid, "inline": False},
            {"name": "Executor:", "value": executor, "inline": True},
            {"name": "IP:", "value": masked_ip, "inline": True},
            {"name": "Discord ID:", "value": f"<@{discord_id}>", "inline": True},
            {"name": "Key:", "value": masked_key, "inline": True},
            {"name": "Detection:", "value": method, "inline": True}
        ],
        "footer": {
            "text": "Crumbleware V6 Whitelist"
        }
    }

    data = {
        "embeds": [embed]  # Embed inside an array
    }

    # Send the POST request to the Discord Webhook URL
    result = requests.post(webhook, json=data)

    # Check if the request was successful
    if 200 <= result.status_code < 300:
        print(f"Embed sent successfully: {result.status_code}")
    else:
        print(f"Failed to send embed: {result.status_code}, {result.text}")

def send_embed3(hwid, executor, ip, discord_id, key, webhook, method):
    masked_ip = mask_with_spoiler(ip)
    masked_key = mask_with_spoiler(key)
    masked_hwid = mask_with_spoiler(hwid)
    embed = {
        "title": "Script Execution Failed",
        "description": "User Execution Failed",
        "color": 0xFF0000,  # Red color for the embed
        "fields": [
            {"name": "HWID:", "value": masked_hwid, "inline": False},
            {"name": "Executor:", "value": executor, "inline": True},
            {"name": "IP:", "value": masked_ip, "inline": True},
            {"name": "Discord ID:", "value": f"<@{discord_id}>", "inline": True},
            {"name": "Key:", "value": masked_key, "inline": True},
            {"name": "Error:", "value": method, "inline": True}
        ],
        "footer": {
            "text": "Crumbleware V6 Whitelist"
        }
    }

    data = {
        "embeds": [embed]  # Embed inside an array
    }

    # Send the POST request to the Discord Webhook URL
    result = requests.post(webhook, json=data)

    # Check if the request was successful
    if 200 <= result.status_code < 300:
        print(f"Embed sent successfully: {result.status_code}")
    else:
        print(f"Failed to send embed: {result.status_code}, {result.text}")

class DataHandler(BaseHandler):
    def get(self):
        remote_ip = self.request.headers.get("X-Real-IP") or \
            self.request.headers.get("X-Forwarded-For") or \
            self.request.remote_ip
        return self.write(encode_string(str(remote_ip)))

class SanityCheckHandler(BaseHandler):
    def post(self):
        try:
            decoded = decode_string(self.get_argument("data"))
            raw = decoded.split(":")

            # Implement custom math checks here (Removed for security reasons)
            check1 = int(raw[0])
            check2 = int(raw[1])
            check3 = int(raw[2])
            check4 = int(raw[3])

            raw = "sanity_check:" + str(check1) + ":" + str(check2) + ":" + str(check3) + ":" + str(check4)
            raw_encoded = encode_string(raw)

            print(raw)
            print(raw_encoded)
            return self.write(raw_encoded)
        except:
            print("sanity check exception")

class AuthHandler(BaseHandler):
    def post(self):
        try:
            string = decode_string(self.get_argument("data"))
            raw = string.split(":")
            offset = int(raw[len(raw) - 2])
            valid = False
            error = "request"
            if raw[0 + offset] == "key": # check if decoding worked
                #if raw[1 + offset] == datetime.datetime.now().strftime("%x"): #check day 
                    test = int(time.time()) - int(raw[2 + offset])
                    if test < 10: #check minute                  # raw[2 + offset] == datetime.datetime.now().strftime("%M")
                        select_query = '''SELECT * FROM invites WHERE LOWER(invite) = LOWER(%s)'''
                        c.execute(select_query, (raw[3 + offset],))
                        user = c.fetchone()
                        if user: # check key
                            if raw[4 + offset]: # check username
                                select_query = '''SELECT * FROM invites WHERE LOWER(invite) = %s AND LOWER(hwid) = %s'''
                                c.execute(select_query, (raw[3 + offset], raw[5 + offset],))
                                hwid = c.fetchone()
                                if hwid: # check hwid
                                    valid = True
                                else:
                                    select_query = '''SELECT * FROM invites WHERE LOWER(invite) = %s AND LOWER(hwid) = %s'''
                                    c.execute(select_query, (raw[3 + offset], "",))
                                    hwid = c.fetchone()
                                    if hwid:
                                        #set new hwid
                                        update_query = '''UPDATE invites SET hwid = LOWER(%s) WHERE LOWER(invite) = LOWER(%s)'''
                                        c.execute(update_query, (raw[5 + offset], raw[3 + offset]))
                                        conn.commit()
                                        valid = True
                                    else:
                                        error = "hwid"
                        else:
                            error = "key"

                    #if raw[3 + offset] == "free_day": # free day for next weekend
                    #    valid = True
            else: 
                if raw[0 + offset] == "test":
                    crack = int(raw[0])
                    method = crack_table.get(str(crack), "Unknown")
                    select_query = '''SELECT id, oldhwid FROM invites WHERE LOWER(invite) = %s'''
                    c.execute(select_query, (raw[3 + offset],))
                    if c.fetchone() == None:
                        id, oldhwid = c.fetchone()
                    else:
                        id = "Unknown"
                    send_embed2(hwid = raw[2 + offset], executor="Wave", ip=raw[4 + offset], discord_id=id, key=raw[3 + offset], webhook=crack_webhook, method=method)
                    raw = generate_random_string(54) + ":" + "etwtgfffewgwegweg:" + "69" + ":" + "9/1/1" + ":" + "wrong key idiot" + ":" + "wpw" + ":" + "eat my ass" + ":" + "faggot" + ":" + "1" + ":" + generate_random_string(32) #send back invalid data
                    raw_encoded = encode_string(raw)
                    return self.write(raw_encoded)

            if valid:
                update_query = '''UPDATE invites SET executions = executions + 1 WHERE LOWER(invite) = %s'''
                c.execute(update_query, (raw[3 + offset],))
                conn.commit()

                # check ip
                select_query = '''SELECT * FROM invites WHERE LOWER(invite) = %s AND ip = %s'''
                c.execute(select_query, (raw[3 + offset], raw[6 + offset],))
                ip = c.fetchone()
                if not ip:
                    update_query = '''UPDATE invites SET ip = %s WHERE LOWER(invite) = %s'''
                    c.execute(update_query, (raw[6 + offset], raw[3 + offset]))
                    conn.commit()
                    
                    #if not ip == "": # sends even if new for now keep out
                        # send sharing webhook
                    #    print("Sharing?")
                else:
                    update_query = '''UPDATE invites SET oldip = %s WHERE LOWER(invite) = %s'''
                    c.execute(update_query, (ip[2], raw[3 + offset]))
                    conn.commit()

                select_query = '''SELECT executions, id, oldhwid, oldip, version FROM invites WHERE LOWER(invite) = %s'''
                c.execute(select_query, (raw[3 + offset],))
                executions, id, oldhwid, oldip, version = c.fetchone()
                #if c.fetchone() != None:
                #    executions, id, oldhwid, oldip = c.fetchone()
                #else:
                #    executions = "Unknown"
                #    id = "Unknown"
                #    oldhwid = "Unknown"
                #    oldip = "Unknown"
                
                print("Exeuction") #webhook
                send_embed(oldhwid=oldhwid, oldip=oldip, hwid = raw[5 + offset], executor="Wave", discord_id=id, executions=executions, script_id=84532198209467459264, key=raw[3 + offset], roblox=raw[4 + offset], ip=raw[6 + offset], webhook=execution_webhook)
                raw = generate_random_string(43) + ":" + str(time.time()) + ":" + "valid:" + raw[6 + offset] + ":" + raw[3 + offset] + ":" + raw[4 + offset] + ":" + raw[5 + offset] + ":" + datetime.datetime.now().strftime("%x") + ":" + "1" + ":" + generate_random_string(25) + ":" + str(version) #send back valid data
                raw_encoded = encode_string(raw)
                print(raw_encoded)
                return self.write(raw_encoded)
            else:
                method = crack_table.get(str(error), "Unknown")
                select_query = '''SELECT id, oldhwid FROM invites WHERE LOWER(invite) = %s'''
                c.execute(select_query, (raw[3 + offset],))
                #if c.fetchone():
                #    id, oldhwid = c.fetchone()
                #else:
                id = "Unknown"
                send_embed3(hwid = raw[5 + offset], executor="Wave", ip=raw[6 + offset], discord_id=id, key=raw[3 + offset], webhook=execution_failed_webhook, method=error)
                raw = generate_random_string(54) + ":" + "etwtgfffewgwegweg:" + error + ":" + "9/1/1" + ":" + "wrong key idiot" + ":" + "wpw" + ":" + "eat my ass" + ":" + "faggot" + ":" + "1" + ":" + generate_random_string(32) #send back invalid data
                raw_encoded = encode_string(raw)
                return self.write(raw_encoded)
        except:
          print("caught exception")

def make_app():
    settings = {
        "cookie_secret": "cookie_secret_here",
        "login_url": "/login",
        "static_path": os.path.join(os.path.dirname(__file__), "static"),
    }
    return tornado.web.Application([
        (r"/", MainHandler),
        (r"/auth", AuthHandler),
        (r"/hyperion", SanityCheckHandler),
        (r"/data", DataHandler),
        (r"/static/(.*)", tornado.web.StaticFileHandler, {"path": settings["static_path"]})
    ], **settings)

if __name__ == "__main__":
    app = make_app()
    app.listen(3000)
    tornado.ioloop.IOLoop.current().start()

def on_shutdown():
    conn.close()

tornado.ioloop.IOLoop.current().add_callback(on_shutdown)
