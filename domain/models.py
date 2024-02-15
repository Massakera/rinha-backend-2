from enum import Enum
from pydantic import BaseModel, Field, StringConstraints
from typing import Annotated, List, Literal
from datetime import datetime

class TransactionType(str, Enum):
    CREDIT = 'c'
    DEBIT = 'd'

class TransactionRequest(BaseModel):
    valor: Annotated[int, Field(strict=True, gt=0)]  
    tipo: TransactionType  
    descricao: Annotated[str, StringConstraints(min_length=1, max_length=10)]


class Transaction(BaseModel):
    valor: int
    tipo: Literal['c', 'd'] 
    descricao: str
    realizada_em: datetime = Field(default_factory=datetime.utcnow)

class SaldoInfo(BaseModel):
    total: int
    data_extrato: datetime = Field(default_factory=datetime.utcnow)
    limite: int

class StatementResponse(BaseModel):
    saldo: SaldoInfo
    ultimas_transacoes: List[Transaction]
