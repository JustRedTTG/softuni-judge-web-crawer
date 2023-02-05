from hexicapi import save
from lilypad import dictionary_selector

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
    "Advanced": {
    	"C# Advanced": "182/CSharp-Advanced-Exercises",
    	"Java Advanced": "175/Java-Advanced-Exercises",
    	"Javascript Advanced": "306/JS-Advanced-Exercises",
    	"Python Advanced": "209/Python-Advanced-Exercises"
    },
    "OOP": {
    	"C# OOP": "184/CSharp-OOP-Exercises",
    	"Java OOP": "187/Java-OOP-Exercises",
    	"Javascript Applications": "308/JS-Applications-Exercises",
    	"Python OOP": "210/Python-OOP-Exercises"
    },
    "DB Fundamentals": {
    	"MS-SQL": "62/CSharp-Databases-Basics-Exercises",
    	"MySQL": "66/Java-Databases-Basics-Exercises",
    	"Entity Framework Core": "68/CSharp-Databases-Advanced-Exercises",
    	"Spring Data": "71/Java-Databases-Advanced-Exercises"
    },
    "Web Exams": {
    	"C# Web Exams": "90/CSharp-Web-Development-Basics-Exams",
    	"Java Web Exams": "91/Java-Web-Development-Basics-Exams",
    	"ExpressJS Exams": "119/ExpressJS-Exams",
    	"ReactJS Exams": "120/ReactJS-Exams",
        "Python Web Exams": "290/Python-Web-Basics-Exams"
    },
    "Front-End": {
    	"JS Front-End": "380/JS-Front-End-Exercise",
        "HTML & CSS": "134/HTML-and-CSS-Exercises"
    },
     "Open Courses": {
    	"MongoDB Exams": "243/MongoDB",
        "HTML & CSS": "134/HTML-and-CSS-Exercises",
        "C# Algorithms Fundamentals": "280/Algorithms-Fundamentals-Exercises",
        "C# Algorithms Advanced": "282/Algorithms-Advanced-Exercises",
        "Java Algorithms Fundamentals": "255/Algorithms-Fundamentals-Exercises",
        "Java Algorithms Advanced": "257/Algorithms-Advanced-Exercises",
        "Python Algorithms Fundamentals": "351/Algorithms-Fundamentals-Exercises",
        "C# Data Structures Fundamentals": "261/Data-Structures-Fundamentals-Exercises",
        "C# Data Structures Advanced": "265/Data-Structures-Advanced-Exercises",
        "Java Data Structures Fundamentals": "215/Data-Structures-Fundamentals-Exercises",
        "Java Data Structures Advanced": "217/Data-Structures-Advanced-Exercises"
    },
    "Pick my own using <number>/<name> format from url": {}
}


def input_contest_url():
    i = dictionary_selector(list_of_content_groups)
    group = list_of_content_groups[list(list_of_content_groups.keys())[i]]

    if len(group.keys()) > 0:
        i = dictionary_selector(group)
        contests_category_url = group[list(group.keys())[i]]
    else:
        contests_category_url = input("url: ")

    return contests_category_url


def get_contest_url():
    try:
        contests_category_url = save.load('url_backup.sav')[0]
    except TypeError:
        contests_category_url = input_contest_url()
        if input('Save url? [y/N] ').lower() == 'y':
            save.save('url_backup.sav', contests_category_url)
            print('Saved.\n')
        else: print('Skipped.\n')

    return contests_category_url
