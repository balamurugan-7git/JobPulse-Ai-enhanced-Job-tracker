from sqlalchemy.orm import Session
import models, schemas, auth

def get_user_by_email(db: Session, email: str):
    return db.query(models.User).filter(models.User.email == email).first()


def create_user(db: Session, user: schemas.UserCreate):
    hashed_pw = auth.hash_password(user.password)
    new_user = models.User(
        email=user.email,
        hashed_password=hashed_pw,
        full_name=user.full_name,
    )
    db.add(new_user)
    db.commit()
    db.refresh(new_user)
    return new_user


def authenticate_user(db: Session, email: str, password: str):
    user = get_user_by_email(db, email)
    if not user:
        return None
    if not auth.verify_password(password, user.hashed_password):
        return None
    return user
def create_application(db: Session, application: schemas.ApplicationCreate, user_id: int):
    new_app = models.Application(
        **application.dict(),
        user_id=user_id,
    )
    db.add(new_app)
    db.commit()
    db.refresh(new_app)

    # log the initial status into history too
    history_entry = models.StatusHistory(
        application_id=new_app.id,
        status=new_app.status,
    )
    db.add(history_entry)
    db.commit()

    return new_app


def get_applications(db: Session, user_id: int):
    return db.query(models.Application).filter(models.Application.user_id == user_id).all()


def get_application(db: Session, application_id: int, user_id: int):
    return (
        db.query(models.Application)
        .filter(models.Application.id == application_id, models.Application.user_id == user_id)
        .first()
    )


def update_application(db: Session, application_id: int, user_id: int, updates: schemas.ApplicationUpdate):
    app_obj = get_application(db, application_id, user_id)
    if not app_obj:
        return None

    update_data = updates.dict(exclude_unset=True)
    status_changed = "status" in update_data and update_data["status"] != app_obj.status

    for key, value in update_data.items():
        setattr(app_obj, key, value)

    db.commit()
    db.refresh(app_obj)

    if status_changed:
        history_entry = models.StatusHistory(
            application_id=app_obj.id,
            status=app_obj.status,
        )
        db.add(history_entry)
        db.commit()

    return app_obj


def delete_application(db: Session, application_id: int, user_id: int):
    app_obj = get_application(db, application_id, user_id)
    if not app_obj:
        return None
    db.delete(app_obj)
    db.commit()
    return app_obj

from sqlalchemy import func


def get_analytics(db: Session, user_id: int):
    # --- Count by status ---
    status_rows = (
        db.query(models.Application.status, func.count(models.Application.id))
        .filter(models.Application.user_id == user_id)
        .group_by(models.Application.status)
        .all()
    )
    by_status = {status.value: count for status, count in status_rows}

    # --- Count by month (based on applied_date) ---
    month_rows = (
        db.query(
            func.date_format(models.Application.applied_date, "%Y-%m").label("month"),
            func.count(models.Application.id),
        )
        .filter(models.Application.user_id == user_id)
        .group_by("month")
        .order_by("month")
        .all()
    )
    by_month = [{"month": month, "count": count} for month, count in month_rows]

    return {"by_status": by_status, "by_month": by_month}
