from requests import Session
from hexicapi import save

from link_information import login_url
from lilypad import yes_or_no


def get_verification_token(S: Session) -> str:
    resp = S.get(login_url)
    html = resp.content.decode('utf-8')
    element = html.split('<input name="__RequestVerificationToken" ')[1].split('>')[0]
    value = element.split('value=')[1].split('"')[1]
    return value


def get_login_data(S: Session, username: str, password: str) -> bool:
    token = get_verification_token(S)
    resp = S.post(login_url, {
        '__RequestVerificationToken': token,
        'UserName': username,
        'Password': password,
        'RememberMe': False,
    }, allow_redirects=False)
    return resp.status_code == 302


def login_to_judge(S: Session) -> None:
    try:
        username, password = save.load('login.sav')
        used_saved = True
    except:
        username, password = input("username: "), input("password: ")
        used_saved = False

    login = get_login_data(S, username, password)
    while not login:
        print("Wrong login!")
        username, password = input("username: "), input("password: ")
        used_saved = False
        login = get_login_data(S, username, password)

    print(f'Authenticated with SoftUni, user {username}.')

    if (not used_saved) and yes_or_no('Save?'):
        save.save('login.sav', username, password)

