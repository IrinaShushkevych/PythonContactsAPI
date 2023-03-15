import unittest
from unittest.mock import MagicMock
from sqlalchemy.orm import Session

from src.database.models import Contact, User
from src.schemas import ContactsModel, ContactsNotes, ContactsBirthday
import src.repository.contacts as r_contact


class TestRepositoryContact(unittest.IsolatedAsyncioTestCase):
    def setUp(self) -> None:
        self.session = MagicMock(spec=Session)
        self.user = User(id=1)
        self.contact = Contact(id=1)
        self.body = ContactsModel(
            firstname='Irina',
            lastname='Shushkevych',
            email='test@gmail.com',
            phone='0667897896',
            born_date='1999-02-03',
            notes=None
        )

    async def test_get_contacts(self):
        contacts = [Contact(), Contact(), Contact()]
        self.session.query().filter().offset().limit().all.return_value = contacts
        result = await r_contact.get_contacts(skip=0, limit=3, user=self.user, db=self.session)
        self.assertEqual(result, contacts)

    async def test_get_contact(self):
        self.session.query().filter().first.return_value = self.contact
        result = await r_contact.get_contact(contact_id=self.contact.id, user=self.user, db=self.session)
        self.assertEqual(result, self.contact)

    async def test_get_contact_not_found(self):
        self.session.query().filter().first.return_value = None
        result = await r_contact.get_contact(contact_id=1, user=self.user, db=self.session)
        self.assertIsNone(result)

    async def test_create_contact(self):
        result = await r_contact.create_contact(body=self.body, user=self.user, db=self.session)
        self.assertEqual(result.firstname, self.body.firstname)
        self.assertEqual(result.lastname, self.body.lastname)
        self.assertEqual(result.email, self.body.email)
        self.assertEqual(result.phone, self.body.phone)
        self.assertEqual(result.born_date, self.body.born_date)
        self.assertEqual(result.notes, self.body.notes)
        self.assertTrue(hasattr(result, 'id'))

    async def test_update_contact(self):
        self.session.query().filter().first.return_value = self.contact
        result = await r_contact.update_contact(contact_id=self.contact.id, body=self.body, user=self.user,
                                                db=self.session)
        self.assertEqual(result.id, self.contact.id)
        self.assertEqual(result.firstname, self.body.firstname)
        self.assertEqual(result.lastname, self.body.lastname)
        self.assertEqual(result.email, self.body.email)
        self.assertEqual(result.phone, self.body.phone)
        self.assertEqual(result.born_date, self.body.born_date)
        self.assertEqual(result.notes, self.body.notes)

    async def test_update_contact_not_found(self):
        self.session.query().filter().first.return_value = None
        result = await r_contact.update_contact(contact_id=self.contact.id, body=self.body, user=self.user,
                                                db=self.session)
        self.assertIsNone(result)

    async def test_update_birthday(self):
        body = ContactsBirthday(born_date=self.body.born_date)
        self.session.query().filter().first.return_value = self.contact
        result = await r_contact.update_birthday(contact_id=self.contact.id, body=body, user=self.user, db=self.session)
        self.assertEqual(result.id, self.contact.id)
        self.assertEqual(result.born_date, body.born_date)

    async def test_update_birthday_contact_not_found(self):
        body = ContactsBirthday(born_date=self.body.born_date)
        self.session.query().filter().first.return_value = None
        result = await r_contact.update_birthday(contact_id=self.contact.id, body=body, user=self.user, db=self.session)
        self.assertIsNone(result)

    async def test_update_notes(self):
        body = ContactsNotes(notes='Hello')
        self.session.query().filter().first.return_value = self.contact
        result = await r_contact.update_notes(contact_id=self.contact.id, body=body, user=self.user, db=self.session)
        self.assertEqual(result.id, self.contact.id)
        self.assertEqual(result.notes, body.notes)

    async def test_update_notes_contact_not_found(self):
        body = ContactsNotes(notes='Hello')
        self.session.query().filter().first.return_value = None
        result = await r_contact.update_notes(contact_id=self.contact.id, body=body, user=self.user, db=self.session)
        self.assertIsNone(result)

    async def test_remove_contact(self):
        self.session.query().filter().first.return_value = self.contact
        result = await r_contact.remove_contact(contact_id=self.contact.id, user=self.user, db=self.session)
        self.assertEqual(result, self.contact)

    async def test_remove_contact_not_found(self):
        self.session.query().filter().first.return_value = None
        result = await r_contact.remove_contact(contact_id=self.contact.id, user=self.user, db=self.session)
        self.assertIsNone(result)

    async def test_get_contacts_birthdays(self):
        contacts = [Contact(), Contact()]
        self.session.query().filter().all.return_value = contacts
        result = await r_contact.get_contacts_birthdays(user=self.user, db=self.session)
        self.assertEqual(result, contacts)

    async def test_filtered_contacts(self):
        contacts = [Contact(), Contact()]
        self.session.query().filter().all.return_value = contacts
        result = await r_contact.filtered_contacts(firstname=self.body.firstname, lastname=None, email=None,
                                                   user=self.user, db=self.session)
        self.assertEqual(result, contacts)


if __name__ == '__main__':
    unittest.main()
