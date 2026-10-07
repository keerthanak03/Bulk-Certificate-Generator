from fastapi import FastAPI, Depends, HTTPException, BackgroundTasks
from fastapi.responses import FileResponse
from sqlalchemy.orm import Session
import os

import models
import schemas
from database import engine, get_db
from generator import generate_certificate_image

# Create tables
models.Base.metadata.create_all(bind=engine)

app = FastAPI(title="Bulk Certificate Generator API")

def process_generation_job(job_id: int, db: Session):
    """Background task to generate certificates."""
    job = db.query(models.Job).filter(models.Job.id == job_id).first()
    if not job:
        return

    job.status = "processing"
    db.commit()

    certificates = db.query(models.Certificate).filter(models.Certificate.job_id == job_id).all()
    
    for cert in certificates:
        try:
            # Generate the certificate using the template
            file_path = generate_certificate_image(cert.recipient_name, cert.course_name)
            cert.file_path = file_path
            cert.status = "generated"
        except Exception as e:
            # Handle individual failure without stopping the job
            cert.status = "failed"
            cert.error_message = str(e)
        
        db.commit()

    job.status = "completed"
    db.commit()


@app.post("/api/jobs", response_model=schemas.JobResponse, status_code=202)
def create_bulk_job(job_req: schemas.JobCreate, background_tasks: BackgroundTasks, db: Session = Depends(get_db)):
    """Accepts a certificate generation request for a list of recipients."""
    
    new_job = models.Job(status="pending")
    db.add(new_job)
    db.commit()
    db.refresh(new_job)

    for recipient in job_req.recipients:
        new_cert = models.Certificate(
            job_id=new_job.id,
            recipient_name=recipient.recipient_name,
            course_name=recipient.course_name,
            status="pending"
        )
        db.add(new_cert)
    
    db.commit()
    db.refresh(new_job)

    # Queue background processing
    background_tasks.add_task(process_generation_job, new_job.id, db)

    return new_job


@app.get("/api/jobs/{job_id}", response_model=schemas.JobResponse)
def get_job_status(job_id: int, db: Session = Depends(get_db)):
    """Track the generation status and progress."""
    job = db.query(models.Job).filter(models.Job.id == job_id).first()
    if not job:
        raise HTTPException(status_code=404, detail="Job not found")
    return job


@app.get("/api/certificates/{cert_id}/download")
def download_certificate(cert_id: int, db: Session = Depends(get_db)):
    """Retrieve generated certificates."""
    cert = db.query(models.Certificate).filter(models.Certificate.id == cert_id).first()
    if not cert:
        raise HTTPException(status_code=404, detail="Certificate not found")
    
    if cert.status != "generated" or not cert.file_path or not os.path.exists(cert.file_path):
        raise HTTPException(status_code=400, detail="Certificate file is not available")

    return FileResponse(cert.file_path, media_type="image/png", filename=f"certificate_{cert_id}.png")