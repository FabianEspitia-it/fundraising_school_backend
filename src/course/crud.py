from fastapi import HTTPException
from sqlalchemy import desc
from sqlalchemy.orm import Session, joinedload

from src.models import *
from src.course.schemas import NewClass, UserEmail, NewCourse


def all_courses(db: Session, user_email: str):
    from src.users.crud import calculate_progress
    user = db.query(User).filter(User.email == user_email).first()

    courses = db.query(Course).options(joinedload(Course.modules)).join(UserCourse).filter(
        UserCourse.user_id == user.id).all()

    result = []

    for course in courses:
        progress = calculate_progress(
            db=db, user_email=user_email, course_id=course.id)

        last_user_class = db.query(UserClass).filter(
            UserClass.user_id == user.id).order_by(desc(UserClass.id)).first()

        for module in course.modules:
            for classObj in module.classes:
                take_class = db.query(UserClass).filter(
                    UserClass.user_id == user.id, UserClass.class_id == classObj.id).first()

                if take_class:
                    classObj.taken = True
                else:
                    classObj.taken = False

        course_with_progress = {
            'course': course,
            'progress': progress,
            'last_class_name': None,
        }

        if last_user_class:
            last_class_name = db.query(Class).filter(
                Class.id == last_user_class.class_id).first().title

            course_with_progress['last_class_name'] = last_class_name

        result.append(course_with_progress)

    return result



def get_course_by_id(db: Session, course_id: int):
    return db.query(Course).filter(Course.id == course_id).first()


def get_modules_by_course_id(db: Session, course_id: int):
    return db.query(Module).filter(Module.course_id == course_id).options(joinedload(Module.classes)).all()


def get_module_by_id(db: Session, course_id: int, module_id: int) -> Class:
    module = db.query(Module).filter(Module.course_id == course_id and Module.id ==
                                     module_id).options(joinedload(Module.classes)).first()
    if module is None:
        raise HTTPException(status_code=404, detail="Module not found")
    return module


def get_module_class(db: Session, course_id: int, module_id: int, class_id: int):
    module: Module = get_module_by_id(db, course_id, module_id)
    classes: list[Class] = module.classes
    searched_class = list(filter(lambda c: c.id == class_id, classes))
    if len(searched_class) == 0:
        raise HTTPException(status_code=404, detail="Class not found")
    return searched_class[0]


def add_class_to_module(db: Session, course_id: int, module_id: int, new_class: NewClass):
    class_module = get_module_by_id(db, course_id, module_id)
    class_instance = Class(
        title=new_class.title,
        video_link=new_class.video_link,
        description=new_class.description,
        previous_id=new_class.previous_id,
        next_id=new_class.next_id,
        module_id=new_class.module_id,
        module=class_module
    )

    db.add(class_instance)
    db.commit()

    return class_instance


def get_class_by_name_method(db: Session, class_name: str):
    return db.query(Class).filter(Class.title == class_name).first()


def get_course_by_name_method(db: Session, course_name: str):
    return db.query(Course).filter(Course.title == course_name).first()


def add_class_as_seen(db: Session, class_id: int, user_email: str):
    user_db = db.query(User).filter(User.email == user_email).options(joinedload(User.classes)).first()
    class_db = db.query(Class).filter(Class.id == class_id).first()

    if user_db is None:
        raise HTTPException('User not found')

    if class_db not in user_db.classes:
        user_db.classes.append(class_db)
    else:
        raise HTTPException(status_code=400, detail='Class already seen by user')

    db.commit()
    db.refresh(user_db)


def get_next_class_course(db: Session, class_id: int, module_id: int):
    current_class = db.query(Class).filter(Class.id == class_id).first()
    
    if current_class.next_id is None:
        current_module = db.query(Module).filter(Module.id == module_id).first()
        
        if current_module.next_id is None:
            return None
        else:
            next_module = db.query(Module).filter(Module.id == current_module.next_id).options(joinedload(Module.classes)).first()
            
            if next_module is None or len(next_module.classes) == 0:
                return None
            
            next_class = next_module.classes[0]

    else:
        next_class = db.query(Class).filter(Class.id == current_class.next_id).first()
    
    return next_class


def get_previous_class_course(db: Session, class_id: int, module_id: int):
    current_class = db.query(Class).filter(Class.id == class_id).first()
    
    if current_class.previous_id is None:
        current_module = db.query(Module).filter(Module.id == module_id).first()
        
        if current_module.previous_id is None:
            return None
        else:
            previous_module = db.query(Module).filter(Module.id == current_module.previous_id).options(joinedload(Module.classes)).first()
            
            if previous_module is None or len(previous_module.classes) == 0:
                return None
            
            previous_class = previous_module.classes[0]

    else:
        previous_class = db.query(Class).filter(Class.id == current_class.previous_id).first()
    return previous_class
