#!/usr/bin/env python

from __future__ import print_function
from future.standard_library import install_aliases
install_aliases()

from urllib.parse import urlparse, urlencode
from urllib.request import urlopen, Request
from urllib.error import HTTPError

import json
import os
import re

from flask import Flask
from flask import request
from flask import make_response

# Flask app should start in global layout
app = Flask(__name__)

#dictionary for translation
en_vi = {
'0':'vòi rồng',
'1':'bão nhiệt đới',
'2':'bão lớn',
'3':'dông lớn kèm sấm sét',
'4':'dông kèm sấm sét',
'5':'mưa kèm với tuyết',
'6':'mưa và mưa tuyết',
'7':'tuyết và mưa tuyết',
'8':'mưa phùn kèm theo hơi lạnh',
'9':'mưa phùn',
'10':'mưa kèm theo hơi lạnh',
'11':'có mưa',
'12':'có mưa',
'13':'tuyết phủ',
'14':'tuyết rơi nhẹ',
'15':'nhiều tuyết ',
'16':'có tuyết',
'17':'mưa đá',
'18':'mưa tuyết',
'19':'bụi mù',
'20':'có sương',
'21':'bao bọc sương mù',
'22':'sương mù',
'23':'gió thổi mạnh',
'24':'có gió',
'25':'trời lạnh',
'26':'có mây',
'27':'nhiều mây',
'28':'nhiều mây',
'29':'có mây bao phủ',
'30':'có mây bao phủ',
'31':'trời trong',
'32':'trời nắng đẹp',
'33':'trời đẹp',
'34':'trời đẹp',
'35':'mưa kèm mưa đá',
'36':'trời nóng',
'37':'có thể có dông',
'38':'có thể có dông bao phủ',
'39':'có thể có dông bao phủ',
'40':'có thể có mưa',
'41':'tuyết lớn',
'42':'có thể có tuyết rơi xuống',
'43':'tuyết lớn',
'44':'trời có mây nhẹ',
'45':'mưa kèm sớm chớp',
'46':'tuyết rơi nhiều',
'47':'có thể có mưa kèm sớm chớp',
'3200':'thời tiết chưa cập nhật',
'Hanoi':'Hà Nội',
'hanoi':'Hà Nội',
'Ho Chi Minh':'Hồ Chí Minh',
}

vi_en = {


}
pattern = re.compile(r'\b(' + '|'.join(en_vi.keys()) + r')\b')
# end of dictionary

@app.route('/webhook', methods=['POST'])
def webhook():
    req = request.get_json(silent=True, force=True)

    #print("Request:")
    #print(json.dumps(req, indent=4))

    res = processRequest(req)

    res = json.dumps(res, indent=4)
    # print(res)
    r = make_response(res)
    r.headers['Content-Type'] = 'application/json'
    return r


def processRequest(req):
    if req.get("result").get("action") != "yahooWeatherForecast":
        return {}
    baseurl = "https://query.yahooapis.com/v1/public/yql?&u=c"
    yql_query = makeYqlQuery(req)
    if yql_query is None:
        return {}
    yql_url = baseurl + urlencode({'q': yql_query}) + "&format=json"
    result = urlopen(yql_url).read()
    data = json.loads(result)
    res = makeWebhookResult(data)
    return res


def makeYqlQuery(req):
    result = req.get("result")
    parameters = result.get("parameters")
    city = parameters.get("geo-city")
    if city is None:
        return None

    return "select * from weather.forecast where woeid in (select woeid from geo.places(1) where text='" + city + "')"


def makeWebhookResult(data):
    query = data.get('query')
    if query is None:
        return {}
    
	
    result = query.get('results')
    if result is None:
        return {}
    
	
    channel = result.get('channel')
    if channel is None:
        return {}
    
	
    item = channel.get('item')
    location = channel.get('location')
    units = channel.get('units')
    if (location is None) or (item is None) or (units is None):
        return {}
    
	
    condition = item.get('condition')
    if condition is None:
        return {}
    
	    
    # print(json.dumps(item, indent=4))
    code = condition.get('code')
    print('code la :' + code)
    text_weather = pattern.sub(lambda x: en_vi[x.group()], code)  
    
    print(text_weather)
    speech = "Hôm nay ở " + location.get('city') + ": " +  text_weather +\
             ", nhiệt độ trung bình là " + condition.get('temp') + " độ" 

    print("Response:")
    print(speech)

    return {
        "speech": speech,
        "displayText": speech,
        # "data": data,
        # "contextOut": [],
        "source": "apiai-weather-webhook-sample"
    }


if __name__ == '__main__':
    port = int(os.getenv('PORT', 5000))
	
    print("Starting app on port %d" % port)

    app.run(debug=False, port=port, host='0.0.0.0')
