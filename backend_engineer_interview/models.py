import datetime

from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column


class Base(DeclarativeBase):
    """
    Base sqlalchemy model that all downstream models inherit from
    """

    pass


class Employee(Base):
    __tablename__: str = "employee"

    id: Mapped[int] = mapped_column(primary_key=True)
    first_name: Mapped[str]
    last_name: Mapped[str]
    date_of_birth: Mapped[datetime.date]
    secret: Mapped[str]
