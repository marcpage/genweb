#!/usr/bin/env python3

""" Structure for storing data

    A Person may be a user, but may just be a relative.
        (open question) How do we connect new users to existing relative records?

    You cannot make direct changes to a person's information.
    Instead you make a Proposal.
    Proposal's can be spotty information.

    For example:
        Person #58
            Proposal #1
                status = valid
                Proposer = Person #22
                Surname = Doe
                First = John
                Marriage year = 1923
                Marriage Country = United States
                Marriage State = Texas
                Marriage County = Travis
                Marriage City = Pflugerville
                Marriage postal = 78660
                Marriage street = North Heatherwilde
                Marriage street class = Boulevard
                Marriage address = 700
                Comment (from Person #22): "I was at the wedding"
                Comment (from Person #36): "Please provide the marriage date"

    Only proposer can modify the proposal.
    Proposals layer to fill in all information with the latest addition overriding.
"""


import enum

import genweb.database
from genweb.table import Table, Identifier, String, IntEnum, ForeignKey, Integer

# from genweb.metaphone import double_metaphone


# pylint: disable=invalid-name


class EventType(enum.Enum):
    """type of life event"""

    birth = 1
    christening = 2
    residence = 3
    marriage = 4
    sealing = 5
    death = 6


class NameType(enum.Enum):
    """type of name"""

    surname = 0
    first = 1
    second = 2
    third = 3
    fourth = 4


class LocationLevel(enum.Enum):
    """scope of location"""

    country = 1
    province = 2
    county = 3
    city = 4
    burrow = 5
    street = 6
    street_class = 7  # street, avenue, road, cicle, drive, etc
    address = 8
    apartment = 9
    postal = 10


class ProposalStatus(enum.Enum):
    """status of proposal"""

    invalid = 0
    valid = 1


class Sex(enum.Enum):
    """status of proposal"""

    male = 0
    female = 1


class RelationshipType(enum.Enum):
    """type of relationship"""

    spouse = 1
    child = 2
    adopted = 3


class ContactType(enum.Enum):
    """type of contact info"""

    phone = 1
    email = 2


class Person(Table):
    """Site user or relative"""

    _db = None
    id = Identifier()
    login_email = String(50, allow_null=True)
    password_hash = String(64, allow_null=True)
    sex = IntEnum(Sex, allow_null=False)


class Name(Table):
    """A single name"""

    _db = None
    id = Identifier()
    name = String(128)


class Metaphone(Table):
    """A 'sounds like' version of a Name"""

    _db = None
    id = Identifier()
    name_id = ForeignKey("Name", allow_null=False)
    metaphone = String(128)


class Proposal(Table):
    """Proposed information about a person"""

    _db = None
    id = Identifier()
    person_id = ForeignKey("Person", allow_null=False)
    proposer_id = ForeignKey("Person", allow_null=False)
    status = IntEnum(ProposalStatus, allow_null=False)


class PersonName(Table):
    """A proposed name for a person"""

    _db = None
    id = Identifier()
    proposal_id = ForeignKey("Proposal", allow_null=False)
    order = IntEnum(NameType, allow_null=False)
    name_id = ForeignKey("Name", allow_null=False)


class Event(Table):
    """A proposed event"""

    _db = None
    id = Identifier()
    proposal_id = ForeignKey("Proposal", allow_null=False)
    type = IntEnum(EventType, allow_null=False)
    year = Integer(allow_null=True)
    month = Integer(allow_null=True)
    day = Integer(allow_null=True)


class EventLocation(Table):
    """A proposed event"""

    _db = None
    id = Identifier()
    event_id = ForeignKey("Event", allow_null=False)
    level = IntEnum(LocationLevel, allow_null=False)
    name_id = ForeignKey("Name", allow_null=False)


class Relationship(Table):
    """Relationship to another Person"""

    _db = None
    id = Identifier()
    proposal_id = ForeignKey("Proposal", allow_null=False)
    relation_id = ForeignKey("Person", allow_null=False)
    type = IntEnum(RelationshipType, allow_null=False)


class Comment(Table):
    """Comment on the proposal
    first comment should be from proposer with source infomration
    """

    _db = None
    id = Identifier()
    commentor_id = ForeignKey("Person", allow_null=False)
    comment = String(2048)


class Contact(Table):
    """Contact information"""

    _db = None
    id = Identifier()
    type = IntEnum(ContactType, allow_null=False)
    contact = String(128, allow_null=False)


def connect(url):
    """Connect to the database"""
    tables = [
        Person,
        Name,
        Metaphone,
        Proposal,
        PersonName,
        Event,
        EventLocation,
        Relationship,
        Comment,
        Contact,
    ]
    database = genweb.database.Connection.connect(url, default_return_objects=False)
    database.create_tables(**Table.database_description(*tables))

    for table in tables:
        table._db = database  # pylint: disable=protected-access

    return database
