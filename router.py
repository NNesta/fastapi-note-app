from fastapi import APIRouter, status, HTTPException
from schemas import NoteResponse, NoteCreate, NoteUpdate
from models import Note
from sqlalchemy.ext.asyncio import AsyncSession
from database import get_db
from typing import Annotated
from fastapi import Depends
from sqlalchemy import select

router = APIRouter()

@router.get("/", response_model=list[NoteResponse])
async def get_notes(db:Annotated[AsyncSession, Depends(get_db)]):
    result = await db.execute(select(Note))
    notes = result.scalars()
    return notes

@router.post("/",response_model=NoteResponse, status_code=status.HTTP_201_CREATED)
async def create_note(note: NoteCreate, db: Annotated[AsyncSession, Depends(get_db)]):
    result = await db.execute(select(Note).where(Note.title == note.title))
    existing_note = result.scalar_one_or_none()
    if existing_note:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST,detail="Note with this title already exists")
    new_note = Note(title=note.title, content=note.content)
    db.add(new_note)
    await db.commit()
    await db.refresh(new_note)
    return new_note

@router.put("/{note_id}", response_model=NoteResponse)
async def update_note(note_id: int, note_data:NoteCreate, db: Annotated[AsyncSession, Depends(get_db)]):
    result = await db.execute(select(Note).where(Note.id == note_id))
    note = result.scalar_one_or_none()
    if not note:
        raise HTTPException(status_code= status.HTTP_400_BAD_REQUEST, detail="Note does not exist")
    note.title = note_data.title
    note.content = note_data.content
    await db.commit()
    await db.refresh(note)
    return note

@router.patch("/{note_id}", response_model=NoteResponse)
async def update_note(note_id: int, note_data:NoteUpdate, db: Annotated[AsyncSession, Depends(get_db)]):
    result = await db.execute(select(Note).where(Note.id == note_id))
    note = result.scalar_one_or_none()
    if not note:
        raise HTTPException(status_code= status.HTTP_400_BAD_REQUEST, detail="Note does not exist")
    updated_note = note_data.model_dump(exclude_unset=True) # To remove those that are set by pydantic as default
    for field, value in updated_note.items():
        setattr(note, field, value)
    await db.commit()
    await db.refresh(note)
    return note

@router.delete("/",status_code=status.HTTP_204_NO_CONTENT)
async def delete_note(note_id, db: Annotated[AsyncSession, Depends(get_db)]):
    result = await db.execute(select(Note).where(Note.id == note_id))
    note = result.scalar_one_or_none()
    if not note:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Note not found")
    await db.delete(note)
    await db.commit()
    return None

@router.get("/{note_id}", response_model=NoteResponse)
async def get_note(note_id:int, db:Annotated[AsyncSession, Depends(get_db)]):
    result = await db.execute(select(Note).where(Note.id == note_id))
    note = result.scalar_one_or_none()
    if not note:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Note not found")
    return note