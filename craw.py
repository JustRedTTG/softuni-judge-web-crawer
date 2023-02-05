import threading, time
import requests, ast
from typing import *
from hexicapi import save

from lilypad import fix_names
from authenticate import login_to_judge
from link_information import get_contest_url, judge_url

# Load completed exercises
try: complete_exercises = save.load('completed_exercises.sav')[0]
except TypeError: complete_exercises = []

# Variables
contests_category_url = get_contest_url() # Get contest url
exercise_result_page_size = 10 # Page limit
S = requests.session() # Requests session
craw_time = 0 # Measurement of craw time
exercise_list: list[dict] = [] # Empty list for exercises

# Authenticate
login_to_judge(S)


def get_contests(category_url: str) -> Tuple[list[dict], list[int], int]:
    global craw_time
    contests: list[dict] = []
    contests_identifiers: list[int] = []

    for i in range(1,21): # This is the amount of pages to try and scrape!
        resp = S.get(judge_url+f'Contests/List/ByCategory/{category_url}?page={i}')
        if 'The selected category is empty.' in resp.text: break
        lines = resp.text.splitlines(False)
        for index, line in enumerate(lines):
            start_time = time.time()
            if line.startswith('<a href="    /Contests/'):
                identifier, url_name = line.split('Contests/')[1].split('/')
                name = lines[index+1].split('>')[1].rstrip('</a')
                contests.append({
                    'identifier': int(identifier),
                    'name': name,
                    'url_name': url_name,
                    'type': 'compete' if lines[index+4] != '</td>' else 'practice'
                })
                contests_identifiers.append(int(identifier))
                threading.Thread(target=get_exercises, args=(contests[-1],), daemon=True).start()
            craw_time += time.time()-start_time
    print(f"Got {len(contests)} contests!\n")
    # noinspection PyUnboundLocalVariable
    return contests, contests_identifiers, i-1


def get_exercise_information(exercise_url: str, contest_identifier: int, clickable_url: str, number: int):
    exercise_dictionary = {
        'url': exercise_url,
        'contest_identifier': contest_identifier,
        'clickable_url': clickable_url,
        'full_name': '',
        'name': '',
        'number': 0,
    }

    resp = S.get(judge_url+exercise_url.lstrip('/'))
    exercise_dictionary['full_name'] = fix_names(resp.text.split('\n<h2>\n')[1].split('\n')[0])

    if '.' in exercise_dictionary['full_name']:
        _, name = exercise_dictionary['full_name'].split(maxsplit=1)
        exercise_dictionary['name'] = name
    else: exercise_dictionary['name'] = exercise_dictionary['full_name']
    exercise_dictionary['number'] = number

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
        exercise_dictionary['submission_data'] = ast.literal_eval(dict_text)
    except:
        print(f"Can't text to dict the following: \n{dict_text}\n")


    return exercise_dictionary


def get_exercises(contest: dict):
    global craw_time
    resp = S.get(judge_url+f'Contests/{contest["type"].capitalize()}/Index/{contest["identifier"]}#0')
    exercises: list[dict] = []
    #print(resp.text)
    exercise_urls: list[str] = resp.text.split('"contentUrls":[')[1].split(']')[0].split(',')
    for i, exercise_url in enumerate(exercise_urls):

        exercise_url = exercise_url.strip('"')
        # Get the completed urls, continue if it's in them
        if exercise_url in [exercise_dictionary['url'] for exercise_dictionary in complete_exercises]: continue
        exercises.append(get_exercise_information(exercise_url, contest["identifier"],
                        judge_url+f'Contests/{contest["type"].capitalize()}/Index/{contest["identifier"]}#{i}', i))
    contest['exercises'] = exercises


# Get all the contests
contests_list, identifiers, number_of_pages = get_contests(contests_category_url)


# CHECK FOR CONTEST IDENTIFIER
for exercise in complete_exercises:
    try:
        if exercise['contest_identifier'] in identifiers: exercise_list.append(exercise)
    except KeyError: print('Detected old complete exercise version, will be updated upon evaluation')


for contest_dict in contests_list:
    start = time.time()
    while 'exercises' not in contest_dict.keys(): pass
    exercise_list.extend(contest_dict['exercises'])
    print(f"Scanned contest \"{contest_dict['name']}\"")
    craw_time += time.time() - start

print(f"\nGot {len(exercise_list)} exercises!")

# Remove unknown
contests_list = [contest for contest in contests_list if contest['type'] != 'unknown']

# Save exercises
save.save('exercises.sav', contests_list, exercise_list)

print(f"Total time for crawling: {time.strftime('%M:%S', time.gmtime(craw_time))}\n")

# noinspection PyUnresolvedReferences
import evaluate

input("Press enter to exit ")
