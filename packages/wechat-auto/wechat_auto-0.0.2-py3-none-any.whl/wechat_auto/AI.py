import requests
import json

post_data = {
        'perception':{
            'inputText':{
                'Text': '你好'
            }
        },
        'userInfo': {
            'apiKey': '83c333a444aa4f4f9e25e434236e0fb9',
            'userId': 'qinluo1023'
        }
    }

def get_msg_by_AI(msg):
    #UNDO, 自己实现更加个性化AI回复
    post_data['perception']['inputText']['Text'] = msg
    r = requests.post('http://openapi.tuling123.com/openapi/api/v2',json.dumps(post_data))
    result = json.loads(r.text)
    return result['results'][0]['values']['text']
