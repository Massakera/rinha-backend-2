from sqlalchemy import Table, Column, Integer, String, DateTime, ForeignKey, MetaData
from sqlalchemy.sql import func

metadata = MetaData()

clientes = Table(
    "clientes",
    metadata,
    Column("id", Integer, primary_key=True),
    Column("nome", String(50), nullable=False),  
    Column("limite", Integer),
    Column("saldo", Integer, default=0)
)

transactions = Table(
    "transacoes",  
    metadata,
    Column("id", Integer, primary_key=True),
    Column("cliente_id", Integer, ForeignKey("clientes.id")), 
    Column("valor", Integer),
    Column("tipo", String(1)),
    Column("descricao", String(10)),
    Column("realizada_em", DateTime, default=func.now())
)

saldos = Table(
    "saldos",
    metadata,
    Column("id", Integer, primary_key=True),
    Column("cliente_id", Integer, ForeignKey("clientes.id")),
    Column("valor", Integer)
)