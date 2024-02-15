from typing import List
from pydantic import BaseModel, Field
from datetime import datetime

class TransactionRequest(BaseModel):
    valor: int
    tipo: str
    descricao: str

class Transaction(BaseModel):
    valor: int
    tipo: str
    descricao: str
    realizada_em: datetime = Field(default_factory=datetime.utcnow)

class SaldoInfo(BaseModel):
    total: int
    data_extrato: datetime = Field(default_factory=datetime.utcnow)
    limite: int

class StatementResponse(BaseModel):
    saldo: SaldoInfo
    ultimas_transacoes: List[Transaction]