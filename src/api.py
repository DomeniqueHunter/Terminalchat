import requests
import json
import time

from httpclient import HTTPClient


async def get_ticket(account:str, password:str, try_nr:int=0, max_trys:int=10) -> str:
    data={'account': account, 'password': password}
    
    try:
        request = await HTTPClient.post('https://www.f-list.net/json/getApiTicket.php', data)
        
        if "error" in request:
            print(request["error"])
            
        if "ticket" in request:
            return request['ticket']
        
        exit(0)
    
    except Exception as e:
        if try_nr <= max_trys:
            time.sleep(1)
            return await get_ticket(account, password, try_nr=try_nr+1)
        else:
            print(f"ERROR: Too many reconnect trys failed ({try_nr})")
            print(f"ERROR: {e} [{type(e).__name__}]")
            exit(0)   

    
def send_friend_request(account:str, ticket:str, from_char:str, to_char:str) -> dict:
    data={'account': account,
          'ticket': ticket,
          'source_name': from_char,
          'dest_name': to_char           
          }
    request = requests.post('https://www.f-list.net/json/request-send.php', data)
    
    if (request.status_code == 200):
        data = json.loads(request.text)
        return data
    else:
        print("ERROR, could not require a ticket")
        exit(1)


def get_character_data(ticket:str, account:str, charactername:str) -> None: 
    data = {'ticket': ticket,
            'account': account,
            'name': charactername
            }
    request = requests.post('https://www.f-list.net/json/api/character-data.php', data)
    if request.status_code == 200:
        data = json.loads(request.text)
    else:
        print("Error, could not get character data")
    