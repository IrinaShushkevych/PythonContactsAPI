from fastapi import APIRouter, HTTPException, Depends, status, Query
from sqlalchemy.orm import Session
from typing import List

from src import get_db, ContactsModel, ContactsResponse, ContactsBirthday, ContactsNotes, repository_contacts

router = APIRouter(prefix='/contacts', tags=['Contacts'])


@router.get('/', response_model=List[ContactsResponse])
async def get_contacts(skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    return await repository_contacts.get_contacts(skip, limit, db)


@router.get('/{contact_id}', response_model=ContactsResponse)
async def get_contact(contact_id: int, db: Session = Depends(get_db)):
    contact = await repository_contacts.get_contact(contact_id, db)
    if contact is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Contact not found")
    return contact


@router.get('/birthdays/', response_model=List[ContactsResponse])
async def get_birthdays(db: Session = Depends(get_db)):
    contacts = await repository_contacts.get_contacts_birthdays(db)
    return contacts


@router.get('/filter/', response_model=List[ContactsResponse])
async def find_contacts(firstname: str | None = Query(default=None, min_length=2, max_length=150),
                        lastname: str | None = Query(default=None, min_length=2, max_length=150),
                        email: str | None = Query(default=None, max_length=150),
                        db: Session = Depends(get_db)):
    contacts = await repository_contacts.filtered_contacts(firstname, lastname, email, db)
    print(firstname, lastname, email)
    return contacts

@router.post("/", response_model=ContactsResponse)
async def create_contact(body: ContactsModel, db: Session = Depends(get_db)):
    return await repository_contacts.create_contact(body, db)


@router.put('/{contact_id}', response_model=ContactsResponse)
async def update_contact(body: ContactsModel, contact_id: int, db: Session = Depends(get_db)):
    contact = await repository_contacts.update_contact(contact_id, body, db)
    if contact is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Contact not found")
    return contact


@router.patch('/birthday/{contact_id}', response_model=ContactsResponse)
async def update_born_date_of_contact(body: ContactsBirthday, contact_id: int, db: Session = Depends(get_db)):
    print(contact_id)
    contact = await repository_contacts.update_birthday(contact_id, body, db)
    if contact is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Contact not found")
    return contact


@router.patch('/notes/{contact_id}', response_model=ContactsResponse)
async def update_notes_of_contact(body: ContactsNotes, contact_id: int, db: Session = Depends(get_db)):
    contact = await repository_contacts.update_notes(contact_id, body, db)
    if contact is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Contact not found")
    return contact


@router.delete('/{contact_id}', response_model=ContactsResponse)
async def remove_contact(contact_id: int, db: Session = Depends(get_db)):
    contact = await repository_contacts.remove_contact(contact_id, db)
    if contact is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Contact not found")
    return contact