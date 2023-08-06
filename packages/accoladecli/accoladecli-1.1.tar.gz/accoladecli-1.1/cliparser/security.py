
import requests
import json
import getpass

token_url = "https://login-test3.myaccolade.com/token"

test_api_url = "api url should be here"


#Resource owner's credentials
username = input('Username: ' )
password = getpass.getpass('Passcode: ')
print(username)
print(password)
print('\n')

#client's credentials
client_id = 'etp-admin'
client_secret = 'AJ8t1jknpgd2flqM2-JAs3cIi3EV3Y02jk_WPeMl1LfGRSbZyoIiXx50rCPYbfHKTNgXDTOaE0xCpMwZpexbmIY'

# Single call with resource owner credentials in variable "data" and then client credentials in the "auth"
# Should return the access_token
data = {'grant_type': 'password', 'username': username, 'password': password}


# May have to include if not working:verify=False,
access_token_response = requests.post(token_url, data=data, allow_redirects=False, auth=(client_id, client_secret))

print("Lets now print the type of the access_token_response:")
print(type(access_token_response))
print('\n')
print("Here are the headers of the access_token_response:")
print(access_token_response.headers)
print('\n')
print("Now printing the type of the headers:")
print(type(access_token_response.headers))
print('\n')

print("Here are the text of the access_token_reponse:")
print(access_token_response.text)
print('\n')

tokens = json.loads(access_token_response.text)
print("let's now print the type of the tokens:")
print(type(tokens))
print('\n')
print("I am now printing the access token: " + "\n" + tokens['access_token'])
print('\n')



# Use access token to interact with grant
# print("Now starting to interact with the grant!")
# api_call_headers = {'Authorization': 'Bearer ' + tokens['access_token']}
# print(api_call_headers)
# api_call_response = requests.get(test_api_url, headers=api_call_headers, verify=False)
#
# print(api_call_response.text)