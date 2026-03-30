import datetime

from sqlalchemy import ForeignKey
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column, relationship


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
    applications = relationship("Application", back_populates="employee")


class Application(Base):
    __tablename__: str = "application"

    id: Mapped[int] = mapped_column(primary_key=True)
    leave_start_date: Mapped[datetime.date]
    leave_end_date: Mapped[datetime.date]
    employee_id: Mapped[int] = mapped_column(ForeignKey("employee.id"))
    employee: Mapped["Employee"] = relationship(back_populates="applications")