# core/db/models.py

from sqlalchemy import MetaData, Table, Column, Integer, String, DateTime, Boolean, ForeignKey, DECIMAL
from datetime import datetime

metadata = MetaData()

Users = Table("Users", metadata,
    Column("UserID", Integer, primary_key=True, autoincrement=True),
    Column("Username", String(50), nullable=False, unique=True),
    Column("PasswordHash", String(256), nullable=False),
    Column("Email", String(100)),
    Column("IsActive", Boolean, default=True)
)

Products = Table("Products", metadata,
    Column("ProductID", Integer, primary_key=True, autoincrement=True),
    Column("ProductCode", String(20), nullable=False, unique=True),
    Column("Name", String(100), nullable=False),
    Column("Description", String(255)),
    Column("Price", DECIMAL(18, 2), nullable=False),
    Column("QuantityInStock", Integer, default=0),
    Column("IsActive", Boolean, default=True)
)

Orders = Table("Orders", metadata,
    Column("OrderID", Integer, primary_key=True, autoincrement=True),
    Column("OrderDate", DateTime, default=datetime.utcnow),
    Column("CustomerName", String(100), nullable=False),
    Column("TotalAmount", DECIMAL(18, 2), nullable=False),
    Column("CreatedBy", Integer, ForeignKey("Users.UserID"))
)

OrderDetails = Table("OrderDetails", metadata,
    Column("OrderDetailID", Integer, primary_key=True, autoincrement=True),
    Column("OrderID", Integer, ForeignKey("Orders.OrderID")),
    Column("ProductID", Integer, ForeignKey("Products.ProductID")),
    Column("Quantity", Integer, nullable=False),
    Column("UnitPrice", DECIMAL(18, 2), nullable=False)
)

AuditLog = Table("AuditLog", metadata,
    Column("LogID", Integer, primary_key=True, autoincrement=True),
    Column("TableName", String(50)),
    Column("RecordID", Integer),
    Column("Operation", String(10)),  # INSERT, UPDATE, DELETE
    Column("ChangedBy", Integer, ForeignKey("Users.UserID")),
    Column("ChangeDate", DateTime, default=datetime.utcnow),
    Column("Details", String)
)