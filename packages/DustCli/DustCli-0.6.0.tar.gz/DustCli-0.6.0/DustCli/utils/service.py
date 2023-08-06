import requests

host = 'http://localhost:5758/api'


class Service:

    @staticmethod
    def groups(platform):
        response = requests.get(host + '/v1/%s/groups' % platform)
        if response.status_code != 200:
            return []

        print(response.json())
        return response.json()['data']['groups']

    @staticmethod
    async def create_repo(name, group):
        response = requests.post('http://localhost:5758/api/v1/new', data={
            'name': name,
            'group': group
        })

        if response.status_code != 200:
            return []

        return response.json()
