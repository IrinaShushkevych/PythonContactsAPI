from src.database import get_db, Contact, Base, POSTGRES_URL
from src.schemas import ContactsModel, ContactsResponse, ContactsBirthday, ContactsNotes
from src.repository import contacts as repository_contacts
from src.routes.contacts import router