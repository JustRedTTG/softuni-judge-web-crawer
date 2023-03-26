import _io
import os.path

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
            maximum_score = len(checked_tests := [test for test in submission if not test['check']])
            tests = [0 for test in checked_tests if not test['failed']]
            success_tests = len(tests)
            score = (success_tests / maximum_score) if success_tests > 0 else 0
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

if os.path.isfile('completed_exercises.sav'):
    if (prev_len := len(save.load('completed_exercises.sav')[0])) < len(complete):
        print(f"Well done, you've completed {len(complete)-prev_len} exercises since the last report!")
save.save('completed_exercises.sav', [exercises_list[index] for index in complete])
print('Completed exercises will be saved to "completed_exercises.sav" to improve future craw time.\n')

print("Your report will be saved to report.txt and report.html ;)")

space = ' '
space_html = '%20'


def compile_contests(list_exercise: list[str], html: bool = False) -> list[str]:
    contests: dict = {contest['identifier']: [] for contest in contests_list}
    contests_real: dict = {contest['identifier']: [] for contest in contests_list}
    final = []
    for exercise in list_exercise:
        contests[int(exercise['clickable_url'].split('#')[0].split('/')[-1])].append(exercise)
    for exercise in exercises_list:
        contests_real[int(exercise['clickable_url'].split('#')[0].split('/')[-1])].append(exercise)
    for contest, exercises in contests.items():
        contest_dict:dict = sorted(contests_list, key=lambda x: x['identifier'] == contest, reverse=True)[0]
        contest_type:str = contest_dict['type']
        contest_name:str = contest_dict['name']

        if len(exercises) < len(contests_real[contest]):
            for exercise in exercises:
                exercise_name: str = exercise['name']
                final.append(f"{contest_type.upper()} at {exercise['clickable_url']}{f' {exercise_name.replace(space, space_html)}' if html else ''}")
        else:
            final.append(f"{contest_type.upper()} everything from https://judge.softuni.org/Contests/{contest_type.capitalize()}/Index/{contest}{f' {contest_name.replace(space, space_html)}' if html else ''}")
    return sorted(final, key= lambda x: {'compete everything':0,'compete at':1, 'practice everything':2, 'practice at': 3}[' '.join(x.split()[0:2]).lower()])


def compile_list(indexes: list[int], html: bool = False) -> list[str]:
    return compile_contests([
        exercise
        for exercise in [
            submissions[i]['exercise']
            for i in indexes
        ]
    ], html)


def write_for(f: _io.TextIOWrapper, indexes: list[int], msg: str):
    if len(indexes) > 0:
        f.write(f"=== {msg.upper()} ===\n\n")
        f.writelines([' '.join([y+"D" if i == 0 and msg=="complete" else y for i, y in enumerate(x.split())])+'\n' for x in compile_list(indexes)])
        f.write('\n')


def html_for(f: _io.TextIOWrapper, indexes: list[int], msg: str, name: str):
    if len(indexes) > 0:
        f.write(f'<h1 class="{name}">=== {msg.upper()} ===</h1>')
        f.write(''.join([f'<p class="{name}{" practice_color" if x.lower().startswith("practice") else " compete_color" if x.lower().startswith("compete") else ""}">{" ".join([y+"D" if i == 0 and name=="complete" else y for i, y in enumerate(x.split()) if i < 2 or y in ["from", "at"]])} <a href="{x.split()[-2]}" target="_blank">{x.split()[-1].replace(space_html, space)}</a><p>' for x in compile_list(indexes, True)]))
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
    f.write("</body><style> a {color: red;} a:visited {color: green;} .complete {color: gray!important;} p.complete {background-color: #1A1A1A; width: fit-content;;} .practice_color {color: magenta;} .compete_color {color: yellow;} body, html {color: white;font-family: Arial, Helvetica, sans-serif; background-color:#202020}</style></html>")


if __name__ == '__main__': input("Press enter to exit ")
