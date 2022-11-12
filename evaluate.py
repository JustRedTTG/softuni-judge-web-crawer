import _io
from hexicapi import save

contests_list: list[dict]
exercises_list: list[dict]

try:
    contests_list, exercises_list = save.load('exercises.sav')
except:
    contests_list, exercises_list = [], []
    print("exercises.sav was not found or failed to load")
    quit()

print(f'Totalling at {len(contests_list)} contests and {len(exercises_list)} exercises!')

submissions: list[dict] = []
submissions_count = 0
for exercise in exercises_list:
    submissions.append({
        'submissions': [
            [
                {
                    'time': test['TimeUsed'],
                    'memory': test['MemoryUsed'],
                    'failed': test['ExecutionResult']!=0,
                    'check': test['IsTrialTest']
                } # format a dictionary for the test
                for test in sorted(submission['TestRuns'], key= lambda x: not x['IsTrialTest'])
            ] # get a list of all the tests in this submission
            for submission in exercise['submission_data']['Data']
        ], # get a list of all the submissions in this exercise
        'exercise': {
            'clickable_url': exercise['clickable_url'],
            'number': exercise['number'],
            'name': exercise['name']
        } # note the exercise with these submissions
    })
    submissions_count += len(submissions[-1]['submissions'])

print(f"Scanning {submissions_count} submissions!\n")

# keep track of things

not_complete: list[int] = []
complete: list[int] = []
has_errors: list[int] = []


for i, exercise in enumerate(submissions):
    if len(exercise['submissions']) < 1:
        not_complete.append(i)
    else:
        scores = []
        for submission in exercise['submissions']:
            maximum_score = len(submission)
            score = len([0 for test in submission if not test['failed']]) / maximum_score
            scores.append(int(score * 100))
        scores.sort(reverse=True)
        if scores[0] == 100:
            complete.append(i)
        else:
            has_errors.append(i)




other: int = len(exercises_list)-len(not_complete)

print(f"A total of {len(not_complete)}/{len(exercises_list)} exercises are not even started!")
print(f"A total of {len(complete)}/{other} exercises are 100/100 score!")
print(f"A total of {len(has_errors)}/{other} exercises are not complete!\n")

print("Your report will be saved to report.txt and report.html")


def compile_contests(list_exercise: list[str]) -> list[str]:
    contests: dict = {contest['identifier']: [] for contest in contests_list}
    contests_real: dict = {contest['identifier']: [] for contest in contests_list}
    final = []
    for exercise in list_exercise:
        contests[int(exercise['clickable_url'].split('#')[0].split('/')[-1])].append(exercise)
    for exercise in exercises_list:
        contests_real[int(exercise['clickable_url'].split('#')[0].split('/')[-1])].append(exercise)
    for contest, exercises in contests.items():
        contest_type:str = sorted(contests_list, key=lambda x: x['identifier'] == contest, reverse=True)[0]['type']
        if len(exercises) < len(contests_real[contest]):
            for exercise in exercises:
                final.append(f"{contest_type.upper()} at {exercise['clickable_url']}")
        else:
            final.append(f"EVERYTHING from https://judge.softuni.org/Contests/{contest_type.capitalize()}/Index/{contest}")
    return sorted(final, key= lambda x: {'everything':0,'compete':1, 'practice': 2}[x.split()[0].lower()])


def compile_list(indexes: list[int]) -> list[str]:
    return compile_contests([
        exercise
        for exercise in [
            submissions[i]['exercise']
            for i in indexes
        ]
    ])

def write_for(f: _io.TextIOWrapper, indexes: list[int], msg: str):
    if len(indexes) > 0:
        f.write(f"=== {msg.upper()} ===\n\n")
        f.writelines([x+'\n' for x in compile_list(indexes)])
        f.write('\n')


def html_for(f: _io.TextIOWrapper, indexes: list[int], msg: str, name: str):
    if len(indexes) > 0:
        f.write(f'<h1 class="{name}">=== {msg.upper()} ===</h1>')
        f.write(''.join([f'<p class="{name}{" practice_color" if x.lower().startswith("practice") else " everything_color" if x.lower().startswith("everything") else " compete_color" if x.lower().startswith("compete") else ""}">{" ".join([y for i, y in enumerate(x.split()) if i < 2])} <a href="{x.split()[-1]}">here</a><p>' for x in compile_list(indexes)]))
        f.write('<br/>')


with open('report.txt', 'w') as f:
    write_for(f, has_errors, 'has errors')
    write_for(f, not_complete, 'not started')
    write_for(f, complete, 'complete')
    f.write("Happy coding!")

with open('report.html', 'w') as f:
    f.write("<!DOCTYPE html><html><meta><title>Report</title></meta><body>")
    html_for(f, has_errors, 'has errors', 'has_errors')
    html_for(f, not_complete, 'not started', 'not_started')
    html_for(f, complete, 'complete', 'complete')
    f.write("</body><style> a {color: red;} a:visited {color: green;} .complete {color: gray!important;} p.complete {background-color: #1A1A1A; width: fit-content;;} .practice_color {color: magenta;} .everything_color {color: orange;} .compete_color {color: yellow;} body, html {color: white;font-family: Arial, Helvetica, sans-serif; background-color:#202020}</style></html>")