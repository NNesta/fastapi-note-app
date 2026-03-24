from fastapi import APIRouter, status, HTTPException
from schemas import NoteResponse, NoteCreate, NoteUpdate
from models import Note
from sqlalchemy.orm import Session
from database import get_db
from typing import Annotated
from fastapi import Depends
from sqlalchemy import select

router = APIRouter()

@router.get("/", response_model=list[NoteResponse])
def get_notes(db:Annotated[Session, Depends(get_db)]):
    result = db.execute(select(Note))
    notes = result.scalars().all()
    return notes

@router.post("/",response_model=NoteResponse, status_code=status.HTTP_201_CREATED)
def create_note(note: NoteCreate, db: Annotated[Session, Depends(get_db)]):
    existing_note = db.execute(select(Note).where(Note.title == note.title)).scalar_one_or_none
    if existing_note:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST,detail="Note with this title already exists")
    new_note = Note(title=note.title, content=note.content)
    db.add(new_note)
    db.commit()
    db.refresh(new_note)
    return new_note

@router.put("/{note_id}", response_model=NoteResponse)
def update_note(note_id: int, note_data:NoteCreate, db: Annotated[Session, Depends(get_db)]):
    note = db.execute(select(Note).where(Note.id == note_id)).scalar_one_or_none()
    if not note:
        raise HTTPException(status_code= status.HTTP_400_BAD_REQUEST, detail="Note does not exist")
    note.title = note_data.title
    note.content = note_data.content
    db.commit()
    db.refresh(note)
    return note

@router.patch("/{note_id}", response_model=NoteResponse)
def update_note(note_id: int, note_data:NoteUpdate, db: Annotated[Session, Depends(get_db)]):
    note = db.execute(select(Note).where(Note.id == note_id)).scalar_one_or_none()
    if not note:
        raise HTTPException(status_code= status.HTTP_400_BAD_REQUEST, detail="Note does not exist")
    updated_note = note_data.model_dump(exclude_unset=True) # To remove those that are set by pydantic as default
    for field, value in updated_note.items():
        setattr(note, field, value)
    db.commit()
    db.refresh(note)
    return note

@router.delete("/",status_code=status.HTTP_204_NO_CONTENT)
def delete_note(note_id, db: Annotated[Session, Depends(get_db)]):
    note = db.execute(select(Note).where(Note.id == note_id)).scalar_one_or_none()
    if not note:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Note not found")
    db.delete(note)
    db.commit()
    return None

@router.get("/{note_id}", response_model=NoteResponse)
def get_note(note_id:int, db:Annotated[Session, Depends(get_db)]):
    note = db.execute(select(Note).where(Note.id == note_id)).scalar_one_or_none()
    if not note:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Note not found")
    return note