from model.Adminmodel import Member, Organization, Role, User


database_tables = [
    Organization.__table__,
    User.__table__,
    Role.__table__,
    Member.__table__
]
