import datetime
from typing import List
from pydantic import BaseModel, constr, PositiveInt

class TransactionRequest(BaseModel):
    valor: PositiveInt
    tipo: str
    descricao: constr(min_length=1, max_length=10)

class TransactionResponse(BaseModel):
    limite: int
    saldo: int

class TransactionDetail(BaseModel):
    valor: int
    tipo: str
    descricao: str
    realizada_em: datetime.datetime

class SaldoDetail(BaseModel):
    total: int
    data_extrato: datetime.datetime
    limite: int

class StatementResponse(BaseModel):
    saldo: SaldoDetail
    ultimas_transacoes: List[TransactionDetail]