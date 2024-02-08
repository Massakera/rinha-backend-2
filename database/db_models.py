from sqlalchemy import Table, Column, Integer, String, DateTime, ForeignKey
from sqlalchemy.sql import func
from .config import metadata

clientes = Table(
    "clientes",
    metadata,
    Column("id", Integer, primary_key=True),
    Column("limite", Integer),
    Column("saldo", Integer, default=0)
)

transactions = Table(
    "transactions",
    metadata,
    Column("id", Integer, primary_key=True),
    Column("client_id", Integer, ForeignKey("clients.id")),
    Column("valor", Integer),
    Column("tipo", String(1)),
    Column("descricao", String(10)),
    Column("realizada_em", DateTime, default=func.now())
)
