import json


class JsonSerialize:
    
    def serialize(self, data):
        if isinstance(data, dict):
            if self.data_wrap:
                return json.dumps({'data': data})
            
            return json.dumps(data)
        else:
            if self.data_wrap:
                return json.dumps({'data': json.loads(data.to_json())})
            
            return data.to_json()
        

