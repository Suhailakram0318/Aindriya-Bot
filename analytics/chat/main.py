# main.py
from fastapi import FastAPI, UploadFile, File, Form, Depends
from fastapi.responses import JSONResponse
from fastapi.middleware.cors import CORSMiddleware
from typing import List, Optional
from models import QuestionPayload, ChatHistory, Session
from docs_to_chunks import process_uploaded_files, process_plain_text
from web_scraper import process_url_content
from faiss_index import create_index, load_index_and_chunks
from gemini_flash import get_llm_response
from sqlalchemy.orm import Session as DBSession
from database import get_db
from chat_history import store_document  # Services to store chat history & documents
from datetime import datetime
from typing import Optional

app = FastAPI(
    title="Document Intelligence API",
    description="An API to upload documents, text, URLs, create vector index, and ask questions using Gemini Flash model."
)

# Memory store (for now simple, in RAM)
chat_memory = []

# --- CORS Middleware ---
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.post("/upload_all")
async def upload_all(
    files: Optional[List[UploadFile]] = File(None),
    plain_text: Optional[str] = Form(None),
    website_url: Optional[str] = Form(None),
    user_id: int = Form(...),  # Assuming user_id is passed in the form data
    username: str = Form(...),  # Assuming username is passed in the form data
    db: Session = Depends(get_db)
):
    try:
        responses = []

        if files:
            file_message = await process_uploaded_files(files)
            # Store the documents in the database
            for file in files:
                content = await file.read()
                doc_type = 'file'  # You can adjust this depending on the file type (text, pdf, etc.)
                store_document(db, user_id, username, doc_type, content.decode())
            responses.append(file_message)

        if plain_text:
            text_message = process_plain_text(plain_text)
            # Store the document in the database
            store_document(db, user_id, username, 'text', plain_text)
            responses.append(text_message)

        if website_url:
            url_message = process_url_content(website_url)
            # Store the URL content in the database
            store_document(db, user_id, username, 'url', website_url)
            responses.append(url_message)

        if not responses:
            return JSONResponse(content={"error": "No input provided."}, status_code=400)

        return {"message": " | ".join(responses)}

    except Exception as e:
        return JSONResponse(content={"error": str(e)}, status_code=500)


@app.post("/create_index")
async def create_faiss_index():
    try:
        message = create_index()
        return {"message": message}
    except Exception as e:
        return JSONResponse(content={"error": str(e)}, status_code=500)


@app.post("/ask")
async def ask_question(payload: QuestionPayload, db: DBSession = Depends(get_db)):
    try:
        question = payload.question
        user_id = payload.user_id
        username = payload.username
        session_id = payload.session_id

        # Load index and chunks
        index, chunks = load_index_and_chunks()

        # Get LLM response
        answer = get_llm_response(index, chunks, question, history=chat_memory)

        # Append to in-memory chat history
        chat_memory.append({
            "user": question,
            "assistant": answer
        })

        # Get or create a session
        if session_id:
            session = db.query(Session).filter_by(id=session_id, user_id=user_id).first()
            if not session:
                return JSONResponse(content={"error": "Invalid session ID for this user."}, status_code=404)
        else:
            session = Session(user_id=user_id)
            db.add(session)
            db.commit()
            db.refresh(session)

        # Save chat to DB
        chat_record = ChatHistory(
            user_id=user_id,
            username=username,
            session_id=session.id,
            message=f"User: {question}\nAssistant: {answer}",
            timestamp=datetime.utcnow()
        )
        db.add(chat_record)
        db.commit()
        db.refresh(chat_record)

        return {"answer": answer, "session_id": session.id}

    except Exception as e:
        return JSONResponse(content={"error": str(e)}, status_code=500)


@app.post("/clear_memory")
async def clear_memory():
    try:
        chat_memory.clear()
        return {"message": "✅ Chat memory has been cleared successfully."}
    except Exception as e:
        return JSONResponse(content={"error": str(e)}, status_code=500)
    
@app.get("/session/{session_id}/chats")
def get_session_chats(session_id: int, db: DBSession = Depends(get_db)):
    # Query the chats for a specific session_id
    chats = db.query(ChatHistory).filter_by(session_id=session_id).all()

    # Return the chat history as a list of dictionaries
    return [
        {
            "id": c.id,  # Chat entry ID
            "user_id": c.user_id,  # User ID
            "username": c.username,  # Username
            "message": c.message,  # The message exchanged between user and assistant
            "timestamp": c.timestamp  # Timestamp when the chat entry was created
        }
        for c in chats
    ]

