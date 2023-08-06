from sqlalchemy import Column
from sqlalchemy.dialects.postgresql import ARRAY, JSONB
from sqlalchemy.types import Boolean, Float, Text, BigInteger, DateTime

from pipet.utils import PipetBase


SCHEMANAME = 'intercom'
CLASS_REGISTRY = {}
metadata = MetaData(schema=SCHEMANAME)


@as_declarative(metadata=metadata, class_registry=CLASS_REGISTRY)
class Base(PipetBase):
    """Intercom return values add "type"
    Some response values are just lists of dictionaries with just an id.
    These are better expressed as Postgres arrays.
    """
    id = Column(Text, primary_key=True)


class User(Base):
    created_at = Column(DateTime)
    signed_up_at = Column(DateTime)
    updated_at = Column(DateTime)
    user_id = Column(Text)
    email = Column(Text)
    phone = Column(Text)
    custom_attributes = Column(JSONB)
    last_request_at = Column(DateTime)
    session_count = Column(BigInteger)
    avatar = Column(JSONB)
    unsubscribed_from_emails = Column(Boolean)
    location_data = Column(JSONB)
    user_agent_data = Column(Text)
    last_seen_ip = Column(Text)
    pseudonym = Column(Text)
    anonymous = Column(Boolean)
    companies = Column(ARRAY)
    social_profiles = Column(JSONB)
    tags = Column(ARRAY)
    name = Column(Text)


class Lead(Base):
    created_at = Column(DateTime)
    updated_at = Column(DateTime)
    user_id = Column(Text)
    email = Column(Text)
    phone = Column(Text)
    name = Column(Text)
    custom_attributes = Column(JSONB)
    last_request_at = Column(DateTime)
    avatar = Column(JSONB)
    unsubscribed_from_emails = Column(Boolean)
    location_data = Column(JSONB)
    user_agent_data = Column(Text)
    last_seen_ip = Column(Text)
    companies = Column(ARRAY)
    social_profiles = Column(JSONB)
    segments = Column(ARRAY)
    tags = Column(ARRAY)


