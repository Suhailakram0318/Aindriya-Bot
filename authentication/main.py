# main.py

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from routes import router as auth_router

app = FastAPI(
    title="Authentication API",
    description="An API for register, login and forgot password."
)

# --- CORS Middleware ---
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include authentication routes
app.include_router(auth_router)

# Health Check
@app.get("/")
def read_root():
    return {"message": "Chatbot Authentication API is running ✅"}
