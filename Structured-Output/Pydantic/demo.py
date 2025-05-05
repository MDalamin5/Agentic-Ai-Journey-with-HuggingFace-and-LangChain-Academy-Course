from pydantic import BaseModel, EmailStr, Field
from typing import Optional

class Student(BaseModel):
    name: str
    age: Optional[int] = None
    email: EmailStr
    cgpa: float = Field(gt=0, lt=4, default=2.0, description="A decimal value representation the cgpa of the student") # for applying the condition use Field 
    

new_student = {
    "name": "Alamin",
    "age": "26",  # pydantic do the type conva
    'email': "hello@gmail.com",
    'cgpa': 3.15
}

student = Student(**new_student)
print(student)

stu_dict = dict(student)

print(stu_dict['email'])