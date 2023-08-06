import requests as http
import json

def RigoMiddleware(hostname,action,options={}):
    def as_parameter(key,value):
        return "%s=%s&" % (key,value)
    action = action.lower()
    if action in ["new-entry","edit-entry"]:
        call_type = "post"
    else:
        call_type = "get"
    if call_type == "get":
        dyna_url = "%s:7737/rigo-remote/%s?" % (hostname,action)
        for key in options:
            dyna_url+=as_parameter(key,options[key])
        dyna_url = dyna_url[:-1]
        try:
            result = http.get(dyna_url).json()
            if "data" in result:
                return result["data"]
            else:
                if action == "join":
                    try:
                        return eval(result["message"].split(' [')[0])
                    except:
                        return result["message"]
                else:
                    return result["message"]
        except:
            return "error"
    if call_type == "post":
        data = json.dumps(options)
        stat_url = "%s:7737/rigo-remote/%s?" % (hostname,action)
        try:
            result = http.post(stat_url,data).json()
            if "data" in result:
                return result["data"]
            else:
                return result["message"]
        except:
            return "error"
