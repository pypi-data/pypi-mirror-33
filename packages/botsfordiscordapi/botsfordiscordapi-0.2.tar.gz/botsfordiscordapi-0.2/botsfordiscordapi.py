import requests

server_count = 0 # Type: int
token = '' # Note: Your Botfordiscord api token
api_version = '' # Note: 'v1' (As of current update) 

class login:
    def __init__(self, token, api_version):
        self.token = token
        self.url = f"https://botsfordiscord.com/api/{api_version}"

    def push(self, server_count):
        if self.token == '':
            raise Exception('No token given!')
        if isinstance(server_count):
            response = requests.post(self.url, data={
                'server_count': server_count
            }, headers={
                'Authorization': self.token
            })
            return response
        else:
            raise Exception('Server count must be an integer')

    def get(self, bot_id):
        try:
            result = requests.get(f'{self.url}/bots/{bot_id}')
            return result.json()
        except Exception as e:
            raise Exception(e)
    


