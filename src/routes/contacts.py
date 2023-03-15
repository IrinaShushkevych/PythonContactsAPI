from fastapi import APIRouter, HTTPException, Depends, status, Query
from sqlalchemy.orm import Session
from typing import List
from fastapi_limiter.depends import RateLimiter

from src.schemas import ContactsModel, ContactsResponse, ContactsBirthday, ContactsNotes
from src.services.auth import auth_service
from src.database.connect import get_db
from src.database.models import User
import src.repository.contacts as repository_contacts

router = APIRouter(prefix='/contacts', tags=['Contacts'])


@router.get('/', response_model=List[ContactsResponse], description='No more than 10 requests per minute',
            status_code=status.HTTP_200_OK)
            # dependencies=[Depends(RateLimiter(times=10, seconds=60))], status_code=status.HTTP_200_OK)
async def get_contacts(skip: int = 0, limit: int = 100, current_user: User = Depends(auth_service.get_current_user),
                       db: Session = Depends(get_db)):
    """
    The get_contacts function returns a list of contacts for the current user.

    :param skip: int: Skip the first n contacts
    :param limit: int: Specify the number of contacts to return
    :param current_user: User: Get the user from the database
    :param db: Session: Pass the database session to the repository
    :return: A list of contacts
    """
    return await repository_contacts.get_contacts(skip, limit, current_user, db)


@router.get('/{contact_id}', response_model=ContactsResponse, description='No more than 10 requests per minute',
            status_code=status.HTTP_200_OK)
            # dependencies=[Depends(RateLimiter(times=10, seconds=60))], status_code=status.HTTP_200_OK)
async def get_contact(contact_id: int, current_user: User = Depends(auth_service.get_current_user),
                      db: Session = Depends(get_db)):
    """
    The get_contact function is used to retrieve a single contact from the database.
    It takes in an integer representing the ID of the contact, and returns a Contact object.

    :param contact_id: int: Specify the contact to be retrieved
    :param current_user: User: Get the current user from the database
    :param db: Session: Get a database session
    :return: A contact object
    """
    contact = await repository_contacts.get_contact(contact_id, current_user, db)
    if contact is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Contact not found")
    return contact


@router.get('/birthdays/', response_model=List[ContactsResponse], description='No more than 10 requests per minute',
            status_code=status.HTTP_200_OK)
            # dependencies=[Depends(RateLimiter(times=10, seconds=60))], status_code=status.HTTP_200_OK)
async def get_birthdays(current_user: User = Depends(auth_service.get_current_user), db: Session = Depends(get_db)):
    """
    The get_birthdays function returns a list of contacts with birthdays in the current month.
        The function takes an optional user parameter, which is used to filter the results by owner.
        If no user is provided, all contacts are returned.

    :param current_user: User: Get the current user from the database
    :param db: Session: Get the database session
    :return: A list of contacts that have birthdays in the next 7 days
    """
    contacts = await repository_contacts.get_contacts_birthdays(current_user, db)
    return contacts


@router.get('/filter/', response_model=List[ContactsResponse], description='No more than 10 requests per minute',
            status_code=status.HTTP_200_OK)
            # dependencies=[Depends(RateLimiter(times=10, seconds=60))], status_code=status.HTTP_200_OK)
async def find_contacts(firstname: str | None = Query(default=None, min_length=2, max_length=150),
                        lastname: str | None = Query(default=None, min_length=2, max_length=150),
                        email: str | None = Query(default=None, max_length=150),
                        current_user: User = Depends(auth_service.get_current_user),
                        db: Session = Depends(get_db)):
    """
    The find_contacts function is used to find contacts in the database.
        It can be filtered by firstname, lastname and email.
        The current_user parameter is a dependency that will be injected automatically when the function runs.

    :param firstname: str | None: Filter contacts by firstname
    :param min_length: Set the minimum length of a string
    :param max_length: Limit the length of the input string
    :param lastname: str | None: Filter contacts by lastname
    :param min_length: Set the minimum length of a string
    :param max_length: Limit the length of the string
    :param email: str | None: Filter the contacts by email
    :param max_length: Limit the length of the input string
    :param current_user: User: Get the current user from the database
    :param db: Session: Pass the database session to the repository layer
    :return: A list of contacts
    """
    contacts = await repository_contacts.filtered_contacts(firstname, lastname, email, current_user, db)
    return contacts


@router.post("/", response_model=ContactsResponse, description='No more than 10 requests per minute',
             status_code=status.HTTP_201_CREATED)
             # dependencies=[Depends(RateLimiter(times=10, seconds=60))], status_code=status.HTTP_201_CREATED)
async def create_contact(body: ContactsModel, current_user: User = Depends(auth_service.get_current_user),
                         db: Session = Depends(get_db)):
    """
    The create_contact function creates a new contact in the database.

    :param body: ContactsModel: Get the data from the request body
    :param current_user: User: Get the user who is currently logged in
    :param db: Session: Get the database session
    :return: A contactmodel object, which is the same as the one in models
    """
    return await repository_contacts.create_contact(body, current_user, db)


@router.put('/{contact_id}', response_model=ContactsResponse, description='No more than 10 requests per minute',
            status_code=status.HTTP_200_OK)
            # dependencies=[Depends(RateLimiter(times=10, seconds=60))], status_code=status.HTTP_200_OK)
async def update_contact(body: ContactsModel, contact_id: int,
                         current_user: User = Depends(auth_service.get_current_user),
                         db: Session = Depends(get_db)):
    """
    The update_contact function updates a contact in the database.
        The function takes three arguments:
            - body: A ContactsModel object containing the new data for the contact.
            - contact_id: An integer representing the ID of an existing Contact to be updated.
            - current_user (optional): A User object representing a user who is logged in and making this request.  This argument is optional because it depends on auth_service, which may or may not return a value depending on whether authentication succeeds or fails.

    :param body: ContactsModel: Pass the contact data to be updated
    :param contact_id: int: Specify the contact to be deleted
    :param current_user: User: Get the user id of the current logged in user
    :param db: Session: Pass the database session to the repository layer
    :return: A contact object
    """
    contact = await repository_contacts.update_contact(contact_id, body, current_user, db)
    if contact is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Contact not found")
    return contact


@router.patch('/birthday/{contact_id}', response_model=ContactsResponse,
              description='No more than 10 requests per minute', status_code=status.HTTP_200_OK)
              # dependencies=[Depends(RateLimiter(times=10, seconds=60))], status_code=status.HTTP_200_OK)
async def update_born_date_of_contact(body: ContactsBirthday, contact_id: int,
                                      current_user: User = Depends(auth_service.get_current_user),
                                      db: Session = Depends(get_db)):
    """
    The update_born_date_of_contact function updates the born date of a contact.
        The function takes in the following parameters:
            - body: A ContactsBirthday object containing information about the new born date of a contact.
            - contact_id: An integer representing an existing Contact ID. This is used to identify which Contact's
                born date will be updated.

    :param body: ContactsBirthday: Pass the data from the request body to the function
    :param contact_id: int: Specify the id of the contact to be updated
    :param current_user: User: Get the current user
    :param db: Session: Get the database session
    :return: A contact object
    """
    contact = await repository_contacts.update_birthday(contact_id, body, current_user, db)
    if contact is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Contact not found")
    return contact


@router.patch('/notes/{contact_id}', response_model=ContactsResponse, description='No more than 10 requests per minute',
              status_code=status.HTTP_200_OK)
              # dependencies=[Depends(RateLimiter(times=10, seconds=60))], status_code=status.HTTP_200_OK)
async def update_notes_of_contact(body: ContactsNotes, contact_id: int,
                                  current_user: User = Depends(auth_service.get_current_user),
                                  db: Session = Depends(get_db)):
    """
    The update_notes_of_contact function updates the notes of a contact.
        The function takes in a body containing the new notes, and an id for the contact to be updated.
        It also takes in current_user and db as dependencies, which are used to verify that the user is logged in
        (current_user) and has access to a database session (db).

    :param body: ContactsNotes: Pass the data from the request body to the function
    :param contact_id: int: Specify the contact to be updated
    :param current_user: User: Get the current user, and the db: session parameter is used to get a database session
    :param db: Session: Pass the database session to the function
    :return: The contact object with the updated notes
    """
    contact = await repository_contacts.update_notes(contact_id, body, current_user, db)
    if contact is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Contact not found")
    return contact


@router.delete('/{contact_id}', description='No more than 10 requests per minute',
               status_code=status.HTTP_204_NO_CONTENT)
               # dependencies=[Depends(RateLimiter(times=10, seconds=60))], status_code=status.HTTP_204_NO_CONTENT)
async def remove_contact(contact_id: int, current_user: User = Depends(auth_service.get_current_user),
                         db: Session = Depends(get_db)):
    """
    The remove_contact function removes a contact from the database.
        Args:
            contact_id (int): The id of the contact to be removed.
            current_user (User): The user who is making this request. This is passed in by FastAPI's Depends() function, which calls auth_service's get_current_user function and passes it into remove_contact as an argument named current user.
            db (Session): A session object that allows us to interact with our database using SQLAlchemy Core statements, which are then translated into SQL by our database engine and executed for us automatically.

    :param contact_id: int: Specify the contact to be removed
    :param current_user: User: Get the current user from the auth_service
    :param db: Session: Pass the database session to the repository
    :return: A contact object
    """
    contact = await repository_contacts.remove_contact(contact_id, current_user, db)
    if contact is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Contact not found")
