from fastapi import HTTPException
from sqlalchemy import desc
from sqlalchemy.orm import Session, joinedload

from src.models import *
from src.course.schemas import NewClass


def all_courses(db: Session, user_email: str):
    from src.users.crud import calculate_progress

    # Obtener el usuario por correo electrónico
    user = db.query(User).filter_by(email=user_email).first()

    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    # Obtener los cursos y las clases tomadas por el usuario en una sola consulta
    user_courses = db.query(Course).options(joinedload(Course.modules).joinedload(Module.classes)).join(
        UserCourse, UserCourse.course_id == Course.id).filter(UserCourse.user_id == user.id).all()

    user_classes = db.query(UserClass).filter_by(
        user_id=user.id).order_by(desc(UserClass.id)).all()
    user_class_ids = {uc.class_id: uc.id for uc in user_classes}

    result = []

    for course in user_courses:
        progress = calculate_progress(
            db=db, user_email=user_email, course_id=course.id)

        last_user_class_id = None
        last_class_name = None

        for module in course.modules:
            for classObj in module.classes:
                classObj.taken = classObj.id in user_class_ids

                if classObj.taken and (last_user_class_id is None or user_class_ids[classObj.id] > last_user_class_id):
                    last_user_class_id = user_class_ids[classObj.id]
                    last_class_name = classObj.title

        result.append({
            'course': course,
            'progress': progress,
            'last_class_name': last_class_name,
        })

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
    user_db = db.query(User).filter(User.email == user_email).options(
        joinedload(User.classes)).first()
    class_db = db.query(Class).filter(Class.id == class_id).first()

    if user_db is None:
        raise HTTPException('User not found')

    if class_db not in user_db.classes:
        user_db.classes.append(class_db)
    else:
        raise HTTPException(
            status_code=400, detail='Class already seen by user')

    db.commit()
    db.refresh(user_db)


def get_next_class_course(db: Session, class_id: int, module_id: int):
    current_class = db.query(Class).filter(Class.id == class_id).first()

    if current_class.next_id is None:
        current_module = db.query(Module).filter(
            Module.id == module_id).first()

        if current_module.next_id is None:
            return None
        else:
            next_module = db.query(Module).filter(
                Module.id == current_module.next_id).options(joinedload(Module.classes)).first()

            if next_module is None or len(next_module.classes) == 0:
                return None

            next_class = next_module.classes[0]

    else:
        next_class = db.query(Class).filter(
            Class.id == current_class.next_id).first()

    return next_class


def get_previous_class_course(db: Session, class_id: int, module_id: int):
    current_class = db.query(Class).filter(Class.id == class_id).first()

    if current_class.previous_id is None:
        current_module = db.query(Module).filter(
            Module.id == module_id).first()

        if current_module.previous_id is None:
            return None
        else:
            previous_module = db.query(Module).filter(
                Module.id == current_module.previous_id).options(joinedload(Module.classes)).first()

            if previous_module is None or len(previous_module.classes) == 0:
                return None

            previous_class = previous_module.classes[-1]

    else:
        previous_class = db.query(Class).filter(
            Class.id == current_class.previous_id).first()
    return previous_class
