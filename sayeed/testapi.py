import requests

url = "http://10.20.15.16:5005/validate_triple"
data = {'subject': 'Doctors', 'predicate': 'recommend', 'object': 'Aspirin'}
response = requests.post(url, json=data)
print(response.json())