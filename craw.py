import threading
import time

import requests
import ast
from hexicapi import save
from typing import *
from link_information import get_contest_url, login_url, judge_url


try:
    complete_exercises = save.load('completed_exercises.sav')[0]
except: complete_exercises = []


contests_category_url = get_contest_url()

exercise_result_page_size = 10

S = requests.session()
craw_time = 0

def get_verification_token() -> str:
    resp = S.get(login_url)
    html = resp.content.decode('utf-8')
    element = html.split('<input name="__RequestVerificationToken" ')[1].split('>')[0]
    value = element.split('value=')[1].split('"')[1]
    return value


def get_login_data(username: str, password: str) -> bool:
    token = get_verification_token()
    resp = S.post(login_url, {
        '__RequestVerificationToken': token,
        'UserName': username,
        'Password': password,
        'RememberMe': False,
    }, allow_redirects=False)
    return resp.status_code == 302


def yes_or_no(msg: str) -> bool:
    return input(f'{msg} [Y/n]').lower() != 'n' or False


def get_contests(category_url: str) -> Tuple[list[dict], int]:
    global craw_time
    contests: list[dict] = []
    for i in range(1,21): # This is the amount of pages to try and scrape!
        resp = S.get(judge_url+f'Contests/List/ByCategory/{category_url}?page={i}')
        if 'The selected category is empty.' in resp.text: break
        lines = resp.text.splitlines(False)
        for i, line in enumerate(lines):
            start = time.time()
            if line.startswith('<a href="    /Contests/'):
                identifier, url_name = line.split('Contests/')[1].split('/')
                name = lines[i+1].split('>')[1].rstrip('</a')
                contests.append({
                    'identifier': int(identifier),
                    'name': name,
                    'url_name': url_name,
                    'type': 'compete' if lines[i+4] != '</td>' else 'practice'
                })
                threading.Thread(target=get_exercises, args=(contests[-1],), daemon=True).start()
            craw_time += time.time()-start
    return contests, i-1


def fix_names(name):
    name = name.replace('\t', ' ')
    return name


def get_exercise_information(exercise_url: str, contest_identifier: int, clickable_url: str, number: int):
    exercise = {
        'url': exercise_url,
        'contest_identifier': contest_identifier,
        'clickable_url': clickable_url
    }

    resp = S.get(judge_url+exercise_url.lstrip('/'))
    exercise['full_name'] = fix_names(resp.text.split('\n<h2>\n')[1].split('\n')[0])

    if '.' in exercise['full_name']:
        _, name = exercise['full_name'].split(maxsplit=1)
        exercise['name'] = name
    else: exercise['name'] = exercise['full_name']
    exercise['number'] = number

    resp = S.post(judge_url + exercise_url.lstrip('/').replace('Problem','ReadSubmissionResults'), {
        'sort': "SubmissionDate-desc",
        'page': 1,
        'pageSize': exercise_result_page_size,
        'group': '',
        'filter': ''
    })
    dict_text: str = resp.text
    dict_text = dict_text.replace('null','None')
    dict_text = dict_text.replace('true','True')
    dict_text = dict_text.replace('false','False')
    try:
        exercise['submission_data'] = ast.literal_eval(dict_text)
    except:
        print(f"Can't text to dict the following: \n{dict_text}\n")


    return exercise


def get_exercises(contest: dict):
    global craw_time
    resp = S.get(judge_url+f'Contests/{contest["type"].capitalize()}/Index/{contest["identifier"]}#0')
    exercises: list[dict] = []
    #print(resp.text)
    exercise_urls: list[str] = resp.text.split('"contentUrls":[')[1].split(']')[0].split(',')
    for i, exercise_url in enumerate(exercise_urls):

        exercise_url = exercise_url.strip('"')
        # Get the completed urls, continue if it's in them
        if exercise_url in [exercise['url'] for exercise in complete_exercises]: continue
        exercises.append(get_exercise_information(exercise_url, contest["identifier"],
                        judge_url+f'Contests/{contest["type"].capitalize()}/Index/{contest["identifier"]}#{i}', i))
    contest['exercises'] = exercises


def login_to_judge() -> None:
    try:
        username, password = save.load('login.sav')
        used_saved = True
    except:
        username, password = input("username: "), input("password: ")
        used_saved = False

    login = get_login_data(username, password)
    while not login:
        print("Wrong login!")
        username, password = input("username: "), input("password: ")
        used_saved = False
        login = get_login_data(username, password)

    if (not used_saved) and yes_or_no('Save?'):
        save.save('login.sav', username, password)


login_to_judge()
contests_list, number_of_pages = get_contests(contests_category_url)

print(f"Got {len(contests_list)} contests!")
exercise_list: list[dict] = []

identifiers = [contest['identifier'] for contest in contests_list]


# CHECK FOR CONTEST IDENTIFIER
for exercise in complete_exercises:
    try:
        if exercise['contest_identifier'] in identifiers:
            exercise_list.append(exercise)
    except KeyError: print('Detected old complete exercise version, will be updated upon evaluation')


for contest_dict in contests_list:
    start = time.time()
    while 'exercises' not in contest_dict.keys(): pass
    exercise_list.extend(contest_dict['exercises'])
    print(f"Scanned contest \"{contest_dict['name']}\"")
    craw_time += time.time() - start

print(f"Got {len(exercise_list)} exercises!")

contests_list = [contest for contest in contests_list if contest['type'] != 'unknown']

save.save('exercises.sav', contests_list, exercise_list)

print(f"Total time for crawing: {time.strftime('%M:%S', time.gmtime(craw_time))}")

# print("Please use the evaluate.py to get your evaluation")

import evaluate

input("Press enter to exit ")
