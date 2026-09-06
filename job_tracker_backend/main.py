from fastapi import FastAPI, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List
from fastapi import UploadFile, File

from job_tracker_backend.database import engine, get_db
from job_tracker_backend import models, schemas, crud, auth
from job_tracker_backend.auth import get_current_user
models.Base.metadata.create_all(bind=engine)

app = FastAPI(title="Job Tracker API")

from fastapi.middleware.cors import CORSMiddleware

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/")
def root():
    return {"message": "Job Tracker API is running"}


@app.post("/register", response_model=schemas.UserOut)
def register(user: schemas.UserCreate, db: Session = Depends(get_db)):
    existing_user = crud.get_user_by_email(db, user.email)
    if existing_user:
        raise HTTPException(status_code=400, detail="Email already registered")
    return crud.create_user(db, user)


@app.post("/login", response_model=schemas.Token)
def login(credentials: schemas.UserLogin, db: Session = Depends(get_db)):
    user = crud.authenticate_user(db, credentials.email, credentials.password)
    if not user:
        raise HTTPException(status_code=401, detail="Invalid email or password")

    access_token = auth.create_access_token(data={"sub": user.email})
    return schemas.Token(access_token=access_token)


@app.post("/applications", response_model=schemas.ApplicationOut)
def create_application(
    application: schemas.ApplicationCreate,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_user),
):
    return crud.create_application(db, application, current_user.id)


@app.get("/applications", response_model=List[schemas.ApplicationOut])
def list_applications(
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_user),
):
    return crud.get_applications(db, current_user.id)


@app.get("/applications/{application_id}", response_model=schemas.ApplicationOut)
def get_application(
    application_id: int,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_user),
):
    app_obj = crud.get_application(db, application_id, current_user.id)
    if not app_obj:
        raise HTTPException(status_code=404, detail="Application not found")
    return app_obj


@app.put("/applications/{application_id}", response_model=schemas.ApplicationOut)
def update_application(
    application_id: int,
    updates: schemas.ApplicationUpdate,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_user),
):
    app_obj = crud.update_application(db, application_id, current_user.id, updates)
    if not app_obj:
        raise HTTPException(status_code=404, detail="Application not found")
    return app_obj


@app.delete("/applications/{application_id}")
def delete_application(
    application_id: int,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_user),
):
    app_obj = crud.delete_application(db, application_id, current_user.id)
    if not app_obj:
        raise HTTPException(status_code=404, detail="Application not found")
    return {"detail": "Application deleted successfully"}


@app.get("/analytics", response_model=schemas.AnalyticsOut)
def get_analytics(
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_user),
):
    return crud.get_analytics(db, current_user.id)


from job_tracker_backend import ml


@app.post("/applications/{application_id}/match-score", response_model=schemas.ApplicationOut)
def compute_match_score_route(
    application_id: int,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_user),
):
    app_obj = crud.get_application(db, application_id, current_user.id)
    if not app_obj:
        raise HTTPException(status_code=404, detail="Application not found")

    if not current_user.resume_text:
        raise HTTPException(status_code=400, detail="Please add your resume text to your profile first")

    if not app_obj.job_description:
        raise HTTPException(status_code=400, detail="This application has no job description to match against")

    score = ml.compute_match_score(current_user.resume_text, app_obj.job_description)
    app_obj.match_score = score
    db.commit()
    db.refresh(app_obj)

    return app_obj


@app.put("/me/resume")
def update_resume(
    payload: schemas.ResumeUpdate,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_user),
):
    current_user.resume_text = payload.resume_text
    db.commit()
    return {"detail": "Resume updated successfully"}

@app.post("/applications/{application_id}/classify-role", response_model=schemas.ApplicationOut)
def classify_role_route(
    application_id: int,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_user),
):
    app_obj = crud.get_application(db, application_id, current_user.id)
    if not app_obj:
        raise HTTPException(status_code=404, detail="Application not found")

    predicted = ml.predict_role_type(app_obj.role_title, app_obj.job_description)
    app_obj.predicted_role_type = predicted
    db.commit()
    db.refresh(app_obj)

    return app_obj
@app.post("/me/resume/upload")
async def upload_resume(
    file: UploadFile = File(...),
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_user),
):
    file_bytes = await file.read()

    try:
        extracted_text = ml.extract_text_from_file(file.filename, file_bytes)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))

    if not extracted_text:
        raise HTTPException(status_code=400, detail="Could not extract any text from the file")

    current_user.resume_text = extracted_text
    db.commit()

    return {
        "detail": "Resume uploaded and parsed successfully",
        "extracted_preview": extracted_text[:300],  # show a preview so the user can sanity-check
    }

from job_tracker_backend import skills


@app.get("/applications/{application_id}/skill-gap", response_model=schemas.SkillGapOut)
def skill_gap_route(
    application_id: int,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_user),
):
    app_obj = crud.get_application(db, application_id, current_user.id)
    if not app_obj:
        raise HTTPException(status_code=404, detail="Application not found")

    if not current_user.resume_text:
        raise HTTPException(status_code=400, detail="Please add your resume first")

    if not app_obj.job_description:
        raise HTTPException(status_code=400, detail="This application has no job description")

    result = skills.compute_skill_gap(
        current_user.resume_text,
        app_obj.job_description,
        current_user.years_of_experience,
    )
    return result

@app.put("/me/experience")
def update_experience(
    payload: schemas.ExperienceUpdate,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_user),
):
    current_user.years_of_experience = payload.years_of_experience
    db.commit()
    return {"detail": "Experience updated successfully"}