from fastapi import APIRouter, HTTPException, status, Depends
from fastapi.responses import JSONResponse

from src.database import get_db

from src.course.crud import *
from src.course.schemas import NewClass, UserEmail, NewCourse, NewEvent


course = APIRouter()


@course.get("/courses", tags=["courses"])
def get_courses(user_email: str, db: Session = Depends(get_db)):
    courses = all_courses(db, user_email)
    return courses


@course.get("/courses/{course_id}", tags=["courses"])
def get_course(course_id: int, db: Session = Depends(get_db)):
    course = get_course_by_id(db, course_id)
    if course is None:
        raise HTTPException(status_code=404, detail="Course not found")
    return course


@course.get("/courses/{course_id}/modules", tags=["courses"])
def get_modules_by_course(course_id: int, db: Session = Depends(get_db)):
    modules = get_modules_by_course_id(db, course_id)
    return modules


@course.get("/courses/{course_id}/modules/{module_id}/classes/{class_id}", tags=["courses"])
def get_class_by_id_course_and_module(course_id: int, module_id: int, class_id: int, db: Session = Depends(get_db)):
    return get_module_class(db, course_id, module_id, class_id)


@course.post("/course/{course_id}/modules/{module_id}/classes", tags=["courses"])
def add_new_class_module(course_id: int, module_id: int, new_class: NewClass, db: Session = Depends(get_db)):
    add_class_to_module(db, course_id, module_id, new_class)


@course.get("/course/class/{class_name}", tags= ["courses"])
def get_class_by_name(class_name: str, db: Session = Depends(get_db)):
    class_instance = get_class_by_name_method(db, class_name)
    if class_instance is None:
        raise HTTPException(status_code=404, detail="Class not found")
    return class_instance


@course.get("/course/name/{course_name}", tags= ["courses"])
def get_course_by_name(course_name: str, db: Session = Depends(get_db)):
    course = get_course_by_name_method(db, course_name)
    if course is None:
        raise HTTPException(status_code=404, detail="Course not found")
    return course


@course.post("/course/{course_name}/modules/{module_id}/classes/{class_id}/completed", tags=['courses'])
def mark_class_complete(class_id: int, user_email: UserEmail, db: Session = Depends(get_db)):
    add_class_as_seen(db, class_id, user_email)
    return JSONResponse(status_code=201, content={'response': 'Class completed'})


@course.get('/course/{course_name}/module/{module_id}/classes/{class_id}/next_class', tags=['courses'])
def get_next_class(module_id: int, class_id: int, db: Session = Depends(get_db)):
    return get_next_class_course(db, class_id, module_id)


@course.get('/course/{course_name}/module/{module_id}/classes/{class_id}/previous_class', tags=['courses'])
def get_next_class(module_id: int, class_id: int, db: Session = Depends(get_db)):
    return get_previous_class_course(db, class_id, module_id)
