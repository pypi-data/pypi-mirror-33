import requests

def upload_to_zenodo():
    ACCESS_TOKEN = 'MkqBPkeMAHeudWiiX5Jr4yAoeeqID40RFhge8OcH4kuALEwDmbJlggZUhq5B'

    # r = requests.get('https://zenodo.org/api/deposit/depositions',
    #                  params={'access_token': ACCESS_TOKEN})

    headers = {"Content-Type": "application/json"}

    r = requests.post('https://zenodo.org/api/deposit/depositions',
                      params={'access_token': ACCESS_TOKEN}, json={},
                      headers=headers)

    deposition_id = r.json()['id']

    data = {'filename': 'myfirstfile.csv'}
    files = {'file': open('/path/to/myfirstfile.csv', 'rb')}

    r = requests.post('https://zenodo.org/api/deposit/depositions/%s/files' % deposition_id,
                      params={'access_token': ACCESS_TOKEN}, data=data,
                      files=files)

    # data = {
    #     'metadata':
    #         {
    #             'title': 'My first upload',
    #             'upload_type': 'poster',
    #             'description': 'This is my first upload',
    #             'creators': [{'name': 'Doe, John',
    #                           'affiliation': 'Zenodo'}]
    #         }
    # }
    #
    # r = requests.put('https://zenodo.org/api/deposit/depositions/%s' % deposition_id,
    #                  params={'access_token': ACCESS_TOKEN}, data=json.dumps(data),
    #                  headers=headers)

if __name__ == '__main__':
    upload_to_zenodo()