#  Government Scheme Recommendation System (AI + RAG)

##  Overview
An AI-powered backend system that recommends relevant government schemes based on user eligibility. It uses FastAPI and Retrieval-Augmented Generation (RAG) to provide accurate, personalized responses.


##  Features
-  User authentication (Signup/Login)
-  Government scheme management (CRUD APIs)
-  AI chatbot for scheme queries (RAG)
-  Eligibility-based scheme matching
-  Guided chat for personalized recommendations


##  Tech Stack
- Python, FastAPI  
- Supabase (PostgreSQL)  
- SQLAlchemy  
- RAG (Retrieval-Augmented Generation)  
- Docker, Railway  



##  Project Structure
services/ → AI logic (RAG, matching)
routers/ → API routes
main.py → FastAPI entry point
database.py → DB connection
models.py → DB models


## ▶ Run the Project
```bash
pip install -r requirements.txt
uvicorn main:app --reload