import requests
import traceback
import ast
from hexicapi import save
from typing import *

judge_url: str = "https://judge.softuni.org/"
login_url: str = "https://judge.softuni.org/Account/Login"
list_of_content_groups = {
    "Programming Basics": {
        "C# Basics": "245/CSharp-Basics",
        "Java Basics": "246/Java-Basics",
        "JS Basics": "247/JS-Basics",
        "Python Basics": "248/Python-Basics",
        "PB - More Exercises": "193/PB-More-Exercises",
        "PB - Exams": "38/PB-Exams",
        "C++ Basics": "100/CPlusPlus-Basics",
        "Go Basics": "338/Go-Basics",
    },
    "Fundamentals": {
        "C# Fundamentals": "149/CSharp-Fundamentals",
        "Java Fundamentals": "145/Java-Fundamentals",
        "JS Fundamentals": "147/JS-Fundamentals",
        "Python Fundamentals": "191/Python-Fundamentals",
        "PHP Fundamentals": "148/PHP-Fundamentals",
        "Fundamentals - Common": "154/Fundamentals-Common", # It's one lab LMAO
        "Fundamentals - Exams": "153/Fundamentals-Exams",
    },
    "Pick my own using <number>/<name> format from url": {}
}
contests_category_url: str = None
try:
    contests_category_url = save.load('url_backup.sav')[0]
    contests_category_url_was_loaded = True
    print('Loaded url_backup.sav url data.')
except TypeError: contests_category_url_was_loaded = False
finally: i = 2 if contests_category_url_was_loaded else 'g'

while type(i) != int:
    print(*[f"[{i}] {key}" for i, key in enumerate(list_of_content_groups.keys())], sep="\n")
    i = input("Pick: ")
    try:
        i = int(i)
    except ValueError:
        print('\n\nTry again')

group = list_of_content_groups[list(list_of_content_groups.keys())[i]]
if len(group.keys()) > 0:
    i = 'g'
    while type(i) != int:
        print(*[f"[{i}] {key}" for i, key in enumerate(group.keys())], sep="\n")
        i = input("Pick: ")
        try:
            i = int(i)
        except ValueError:
            print('\n\nTry again')
    contests_category_url = group[list(group.keys())[i]]

if not contests_category_url:
    contests_category_url: str = input("url: ")
if not contests_category_url_was_loaded:
    if input('save url? [y/N] ').lower() == 'y':
        save.save('url_backup.sav', contests_category_url)
        print('Saved.\n')
    else:
        print('Skipped.\n')

exercise_result_page_size = 10


def get_verification_token() -> Tuple[str, dict]:
    resp = requests.get(login_url)
    html = resp.content.decode('utf-8')
    element = html.split('<input name="__RequestVerificationToken" ')[1].split('>')[0]
    value = element.split('value=')[1].split('"')[1]
    return value, resp.cookies


def get_login_data(username: str, password: str) -> dict:
    verification_token, cookies = get_verification_token()
    resp = requests.post(login_url, {
        '__RequestVerificationToken': verification_token,
        'UserName': username,
        'Password': password,
        'RememberMe': False,
    },cookies=cookies, allow_redirects=False)
    if resp.status_code == 302:
        login = dict(resp.cookies)
        login['__RequestVerificationToken'] = verification_token
        return login
    else: return None


def yes_or_no(msg: str) -> bool:
    return input(f'{msg} [Y/n]').lower() != 'n' or False


def get_contest_type(ending_words: str) -> str:
    ending_words = ending_words.lower()
    if ending_words[0] == 'l': return 'practice'
    elif ending_words.endswith('es'): return 'practice'
    elif ending_words.startswith('ex'): return 'compete'
    return 'unknown'


def get_contests(login: dict, category_url: str) -> Tuple[list[dict], int]:
    contests: list[dict] = []
    for i in range(1,21):
        resp = requests.get(judge_url+f'Contests/List/ByCategory/{category_url}?page={i}', cookies=login)
        if 'The selected category is empty.' in resp.text: break
        for line in resp.text.splitlines(False):
            if line.startswith('<a href="    /Contests/'):
                identifier, url_name = line.split('Contests/')[1].split('/')
                name = resp.text.split(f'<a href="    /Contests/{identifier}/{url_name}\r\n">')[1].split('</a>')[0]
                contests.append({
                    'identifier': int(identifier),
                    'name': name,
                    'url_name': url_name,
                    'type': get_contest_type(url_name.split('-')[-1])
                })
    return contests, i-1


def get_exercise_information(login: dict, exercise_url: str, clickable_url: str):
    exercise = {
        'url': exercise_url,
        'clickable_url': clickable_url
    }

    resp = requests.get(judge_url+exercise_url.lstrip('/'), cookies=login)
    exercise['full_name'] = resp.text.split('\n<h2>\n')[1].split('\n')[0]
    number, name = exercise['full_name'].split(maxsplit=1)
    exercise['number'] = int(''.join([n for n in number if n.isdecimal()]))
    exercise['name'] = name
    # TODO: get results
    resp = requests.post(judge_url + exercise_url.lstrip('/').replace('Problem','ReadSubmissionResults'), {
        'sort': "SubmissionDate-desc",
        'page': 1,
        'pageSize': exercise_result_page_size,
        'group': '',
        'filter': ''
    }, cookies=login,)
    dict_text: str = resp.text
    dict_text = dict_text.replace('null','None')
    dict_text = dict_text.replace('true','True')
    dict_text = dict_text.replace('false','False')
    try:
        exercise['submission_data'] = ast.literal_eval(dict_text)
    except:
        print(f"Can't text to dict the following: \n{dict_text}\n")


    return exercise


def get_exercises(login: dict, contest: dict):
    resp = requests.get(judge_url+f'Contests/{contest["type"].capitalize()}/Index/{contest["identifier"]}#0', cookies=login)
    exercises: list[dict] = []
    #print(resp.text)
    exercise_urls: list[str] = resp.text.split('"contentUrls":[')[1].split(']')[0].split(',')
    for i, exercise_url in enumerate(exercise_urls):
        exercises.append(get_exercise_information(login, exercise_url.strip('"'),
                        judge_url+f'Contests/{contest["type"].capitalize()}/Index/{contest["identifier"]}#{i}'))
    return exercises



def login_to_judge() -> dict:
    try:
        username, password = save.load('login.sav')
        used_saved = True
    except:
        username, password = input("username: "), input("password: ")
        used_saved = False

    login = get_login_data(username, password)
    while login is None:
        print("Wrong login!")
        username, password = input("username: "), input("password: ")
        used_saved = False
        login = get_login_data(username, password)

    if (not used_saved) and yes_or_no('Save?'):
        save.save('login.sav', username, password)
    return login


login_details: dict = login_to_judge()

# TODO: list[dict] : int
contests_list, number_of_pages = get_contests(login_details.copy(), contests_category_url)
#print("Got contests!\n", *[contest['name'] for contest in contests_list], sep='\n')
print(f"Got {len(contests_list)} contests!")
exercise_list: list[dict] = []
for contest_dict in contests_list:
    if contest_dict['type'] == 'unknown': continue
    try:
        exercise_list += get_exercises(login_details.copy(), contest_dict)
    except:
        exercise_list += get_exercises(login_details.copy(), contest_dict)
    print(f"Scanned contest \"{contest_dict['name']}\"")
print(f"Got {len(exercise_list)} exercises!")
#print("Got exercises!\n", *[exercise['name'] for exercise in exercise_list], sep='\n')

contests_list = [contest for contest in contests_list if contest['type'] != 'unknown']

save.save('exercises.sav', contests_list, exercise_list)

# print("Please use the evaluate.py to get your evaluation")

import evaluate

input("Press enter to exit ")
