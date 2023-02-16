from typing import List
from sqlalchemy import or_, and_
from sqlalchemy.orm import Session
from src import Contact, ContactsResponse, ContactsModel, ContactsNotes, ContactsBirthday, User
from datetime import datetime, timedelta


async def get_contacts(skip: int, limit: int, user: User, db: Session) -> List[ContactsResponse]:
    return db.query(Contact).filter(Contact.user_id == user.id).offset(skip).limit(limit).all()


async def get_contact(contact_id: int, user: User, db: Session) -> ContactsResponse | None:
    return db.query(Contact).filter(and_(Contact.id == contact_id, Contact.user_id == user.id)).first()


async def create_contact(body: ContactsModel, user: User, db: Session) -> ContactsResponse:
    contact = Contact(
        firstname=body.firstname,
        lastname=body.lastname,
        email=body.email,
        phone=body.phone,
        born_date=body.born_date,
        notes=body.notes,
        user_id=user.id
    )
    db.add(contact)
    db.commit()
    db.refresh(contact)
    return contact


async def update_contact(contact_id: int, body: ContactsModel, user: User, db: Session) -> ContactsResponse | None:
    contact = db.query(Contact).filter(and_(Contact.id == contact_id, Contact.user_id == user.id)).first()
    if contact:
        contact.firstname = body.firstname
        contact.lastname = body.lastname
        contact.email = body.email
        contact.phone = body.phone
        contact.born_date = body.born_date
        contact.notes = body.notes
        db.commit()
    return contact

async def update_birthday(contact_id: int, body: ContactsBirthday, user: User, db: Session) -> ContactsResponse | None:
    contact = db.query(Contact).filter(and_(Contact.id == contact_id, Contact.user_id == user.id)).first()
    if contact:
        contact.born_date = body.born_date
        db.commit()
    return contact

async def update_notes(contact_id: int, body: ContactsNotes, user: User, db: Session) -> ContactsResponse | None:
    contact = db.query(Contact).filter(and_(Contact.id == contact_id, Contact.user_id == user.id)).first()
    if contact:
        contact.notes = body.notes
        db.commit()
    return contact


async def remove_contact(contact_id: int, user: User, db: Session) -> ContactsResponse | None:
    contact = db.query(Contact).filter(and_(Contact.id == contact_id, Contact.user_id == user.id)).first()
    if contact:
        db.delete(contact)
        db.commit()
    return contact

async def get_contacts_birthdays(user: User, db: Session) -> List[ContactsResponse]:
    date_begin = datetime.now().date()
    date_end = date_begin + timedelta(7)

    contacts = db.query(Contact).filter(and_(Contact.born_date.between(date_begin, date_end), Contact.user_id == user.id)).all()
    return contacts

async def filtered_contacts(firstname: str | None , lastname: str | None, email: str | None, user: User, db: Session) -> List[ContactsResponse]:
    print(firstname)
    list_reg = []
    if firstname:
        list_reg.append(Contact.firstname.ilike(f"%{firstname}%"))
    if lastname:
        list_reg.append(Contact.lastname.ilike(f"%{lastname}%"))
    if email:
        list_reg.append(Contact.email.ilike(f"%{email}%"))
    contacts = db.query(Contact).filter(and_(or_(*list_reg), Contact.user_id == user.id)).all()
    return contacts