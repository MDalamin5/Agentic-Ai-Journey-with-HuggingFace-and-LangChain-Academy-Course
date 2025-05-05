from typing import TypedDict

class Student(TypedDict):
    name: str
    age: int
    uni: str
    
stu1: Student = {
    'name': "Md Al Amin",
    'age': 26,
    'uni': "NSU"
}

print(stu1)