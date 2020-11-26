import json
import requests
from pymongo import MongoClient

client = MongoClient('localhost', 27017)
db = client['ParserVkAPI']
collection = db['VkUsers']


def get_token():
    with open("APP_token.txt", "r") as file:
        line = file.readline()
    return line

def check_in_db(user_id, data):
    dict2 = {'user_id': user_id}
    data1 = collection.find_one(dict2)
    if data1:
        print('Пользователь есть в базе данных')
    else:
        collection.insert_one(data)
        print('Пользователь добавлен в БД')

def get_user_data(user_id):
    res = requests.get(BASE_URL + f'users.get?user_ids={user_id}&fields=city,  universities&v=5.52&access_token={token}')
    if res.status_code == 200:
        try:
            resp = res.json()
            if 'response' in resp:
                for i in range(len(resp['response'])):
                    data = {}
                    res = resp['response'][i]
                    data.update(
                        {'user_id': res['id'],
                        'first_name': res['first_name'],
                        'last_name': res['last_name']}
                    )

                    if 'city' in res:
                        if len(res['city']) > 0:
                            data.update({'city': res['city']['title']})
                        else:
                            data.update({'city': '-'})
                    
                    if 'universities' in res:
                        if len(res['universities']) > 0:
                            data.update({'universities': res['universities'][0]['name']})
                        else:
                            data.update({'universities': '-'})

                    friends_id, count_friends = get_user_friends(f"{res['id']}")
                    data.update({'friends': friends_id})
                    check_in_db(user_id, data) 
                return friends_id, count_friends
            else:
                print('\n', resp['error']['error_msg'])
        except Exception as exc:
            print(exc, '\n')


def get_user_friends(user_id):
    friends_id = []
    count_friends = 0
    res = requests.get(BASE_URL + f'friends.get?user_id={user_id}&v=5.52&access_token={token}')
    if res.status_code == 200:
        try:
            if 'response' in res.json():
                res = res.json()['response']
                count_friends = res['count']
                for friend in res['items']:
                    friends_id.append(friend)
            return friends_id, count_friends
        except Exception as exc:
            print(exc, '\n')


if __name__ == "__main__":
    try:
        BASE_URL = 'https://api.vk.com/method/'
        token = get_token()
        user_id = str(input('Введите id пользователя:\n'))
        friends, count_friends = get_user_data(user_id)
        friends_id = ''
        for i in range (count_friends):
            friends_id += str(friends[i]) + ','
        get_user_data(friends_id)
    except Exception:
        pass