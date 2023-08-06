import requests
import json

class RPC:
    version = "2.0"
    id = 0
    url="http://127.0.0.1:8820/rpc/v2"

    def __init__(self, method):
        self.method = method
        self.__class__.id += 1
        self.id = self.__class__.id

    def __to_data(self, positional, optional):
        # filter the None value in the end of positional

        params = filter(lambda x: x != None, positional)

        params.append({})
        for key in optional:
            if optional[key] != None:
                params[-1][key] = optional[key]

        ret = {
            'method' : self.method,
            'id' : self.id,
            'jsonrpc' : self.version,
            "params": params}
        return json.dumps( ret )

    def post(self, positional, optional):
        rpc_rsp = requests.post(self.url, data=self.__to_data(positional, optional))
        assert (rpc_rsp.json()['id'] == self.id)

        return rpc_rsp

def mvs_api_v2(func):
    def wrapper(*args, **kwargs):
        cmd, positional, optional = func(*args, **kwargs)
        rpc_cmd = RPC(cmd)
        rpc_rsp = rpc_cmd.post(positional, optional)
        if "error" in rpc_rsp.json():
            #return rpc_rsp.json()['error']['code'], rpc_rsp.json()['error']['message']
            return rpc_rsp.json()['error']['message'], None
        #return 0, rpc_rsp.json()['result']
        return None, rpc_rsp.json()['result']
    return wrapper
