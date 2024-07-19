from fastapi import APIRouter, HTTPException, status, Depends
from fastapi.responses import JSONResponse

from src.database import get_db

from src.course.crud import *
from src.course.schemas import NewClass, NewEvent


course = APIRouter()


@course.get("/courses", tags=["courses"])
def get_courses(db: Session = Depends(get_db)):
    courses = all_courses(db)
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

