# Bulk Certificate Generator API

## Overview
A backend API built with FastAPI that accepts bulk certificate generation requests, processes them asynchronously, and provides endpoints to track status and download the certificates.

## Setup Instructions
1. Ensure you have Python 3.9+ installed.
2. Clone the repository and navigate to the project root.
3. Create a virtual environment:
   `python -m venv venv`
4. Activate the virtual environment:
   - Mac/Linux: `source venv/bin/activate`
   - Windows: `venv\Scripts\activate`
5. Install dependencies:
   `pip install -r requirements.txt`

## Running the Application
Start the FastAPI server using Uvicorn:
`uvicorn main:app --reload`
The API will be available at `http://127.0.0.1:8000`. You can view the interactive Swagger UI at `http://127.0.0.1:8000/docs`.

## Running Tests
Run the test suite using pytest:
`pytest test_main.py -v`

## API Usage Guide

### 1. Submit a Certificate Generation Request
**POST** `/api/jobs`
```json
{
  "recipients": [
    {
      "recipient_name": "John Doe",
      "course_name": "Backend Engineering"
    },
    {
      "recipient_name": "Jane Smith",
      "course_name": "Backend Engineering"
    }
  ]
}