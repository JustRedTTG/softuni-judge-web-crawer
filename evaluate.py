from hexicapi import save

try:
    contests_list, exercises_list = save.load('exercises.sav')
except:
    print("exercises.sav was not found or failed to load")
    quit()

print(f'Totalling at {len(contests_list)} contests and {len(exercises_list)} exercises!')

