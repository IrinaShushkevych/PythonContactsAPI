from src.database import get_db, Contact, User, Base, POSTGRES_URL
from src.schemas import ContactsModel, ContactsResponse, ContactsBirthday, ContactsNotes, UserModel, UserResponse, \
    TokenModel, UserDB
from src.repository import contacts as repository_contacts
from src.repository import auth as repository_auth
from src.routes.contacts import router as router_contacts
from src.routes.auth import router as router_auth
# from src.services.auth import auth_service