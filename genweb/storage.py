#!/usr/bin/env python3

""" Structure for storing data

    All names will be in the Name table.
    A Person may be a user, but may just be a relative.
        (open question) How do we connect new users to existing relative records?
        (open question) How do we handle privacy with living Person?

    You cannot make direct changes to a person's information.
    Instead you make a Proposal.
    Proposal's can have spotty information.
    You can propose a Name, and Event, and/or a relationship.
    Only the creator of the proposal can edit it.
    The creator can invalidate a proposal.
    Newer proposals can override existing (eg name).
    The latest proposal is what is shown by default, but all proposals can be seen
        and commented on.


    For example:
        Person #58
            Proposal #1
                status = valid
                Proposer = Person #22
                Name = Doe, "Jonny" John Alexander
                Event = 1986-May Marriage @ US/California/Orange/Irvine
                EventPerson = Marriage - John Doe
                EventPerson = Marriage - Jane Austin
                Relationship = Spouse John -> Jane
                Comment (from Person #22): "I was at the wedding"
                Comment (from Person #36): "Please provide the marriage date"
        Person #22
            Contact = 619-555-5309
            Contact = JohnDoe@company.com

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

    death = 0
    birth = 1
    residence = 2
    marriage = 3
    baptism = 4
    christening = 5
    endowment = 6
    sealed_to_spouse = 7
    sealed_to_child = 8


class Status(enum.Enum):
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


class Person(Table):
    """Site user or relative"""

    _db = None
    id = Identifier()
    login_email = String(50, allow_null=True)
    password_hash = String(64, allow_null=True)
    sex = IntEnum(Sex, allow_null=False)


class Proposal(Table):
    """A proposed set of information"""

    id = Identifier()
    status = IntEnum(Status, allow_null=False)
    proposer_id = ForeignKey("Person", allow_null=False)


class ProposedName(Table):
    """Proposed information about a person"""

    _db = None
    id = Identifier()
    proposal_id = ForeignKey("Proposal", allow_null=False)
    person_id = ForeignKey("Person", allow_null=False)
    surname_id = ForeignKey("Name", allow_null=True)
    nickname_id = ForeignKey("Name", allow_null=True)
    first_id = ForeignKey("Name", allow_null=True)
    second_id = ForeignKey("Name", allow_null=True)
    third_id = ForeignKey("Name", allow_null=True)
    fourth_id = ForeignKey("Name", allow_null=True)
    fifth_id = ForeignKey("Name", allow_null=True)


class ProposedEvent(Table):
    """A proposed event"""

    _db = None
    id = Identifier()
    proposal_id = ForeignKey("Proposal", allow_null=False)
    type = IntEnum(EventType, allow_null=False)
    year = Integer(allow_null=True)
    month = Integer(allow_null=True)
    day = Integer(allow_null=True)
    country_id = ForeignKey("Name", allow_null=True)
    province_id = ForeignKey("Name", allow_null=True)
    county_id = ForeignKey("Name", allow_null=True)
    city_id = ForeignKey("Name", allow_null=True)
    postal_id = ForeignKey("Name", allow_null=True)
    burrow_id = ForeignKey("Name", allow_null=True)
    street_id = ForeignKey("Name", allow_null=True)
    street_class_id = ForeignKey("Name", allow_null=True)  # street, avenue, road, etc
    street_direction_id = ForeignKey("Name", allow_null=True)  # north, south, east, etc
    address_id = ForeignKey("Name", allow_null=True)
    apartment_id = ForeignKey("Name", allow_null=True)


class ProposedEventPerson(Table):
    """A proposed person involved in event"""

    _db = None
    id = Identifier()
    proposal_id = ForeignKey("Proposal", allow_null=False)
    event_id = ForeignKey("ProposedEvent", allow_null=False)
    person_id = ForeignKey("Person", allow_null=False)


class ProposedRelationship(Table):
    """Relationship to another Person"""

    _db = None
    id = Identifier()
    proposal_id = ForeignKey("Proposal", allow_null=False)
    person_id = ForeignKey("Person", allow_null=False)
    relation_id = ForeignKey("Person", allow_null=False)
    type = IntEnum(RelationshipType, allow_null=False)


class Comment(Table):
    """Comment on the proposal
    first comment should be from proposer with source infomration
    """

    _db = None
    id = Identifier()
    proposal_id = ForeignKey("Proposal", allow_null=False)
    commentor_id = ForeignKey("Person", allow_null=False)
    comment = String(2048)


class Contact(Table):
    """Contact information"""

    _db = None
    id = Identifier()
    status = IntEnum(Status, allow_null=False)
    person_id = ForeignKey("Person", allow_null=False)
    type = IntEnum(ContactType, allow_null=False)
    contact = String(128, allow_null=False)


def connect(url):
    """Connect to the database"""
    tables = [
        Name,
        Metaphone,
        Person,
        Proposal,
        ProposedName,
        ProposedEvent,
        ProposedEventPerson,
        ProposedRelationship,
        Comment,
        Contact,
    ]
    database = genweb.database.Connection.connect(url, default_return_objects=False)
    database.create_tables(**Table.database_description(*tables))

    for table in tables:
        table._db = database  # pylint: disable=protected-access

    return database
