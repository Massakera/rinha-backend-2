import datetime
from fastapi import FastAPI, HTTPException, Path
from database.config import database
from database.db_models import clientes, transactions, saldos   # Corrected import
from sqlalchemy import select, desc
import logging

from domain.models import StatementResponse, TransactionRequest

app = FastAPI()

@app.post("/clientes/{client_id}/transacoes", response_model=dict)
async def transacao(client_id: int, request: TransactionRequest):
    async with database.transaction():
        client_query = select([clientes.c.limite, saldos.c.valor.label("saldo")]).select_from(clientes.join(saldos, clientes.c.id == saldos.c.cliente_id)).where(clientes.c.id == client_id).with_for_update()
        client = await database.fetch_one(client_query)
        
        if client is None:
            raise HTTPException(status_code=404, detail="Cliente não encontrado")
        
        new_saldo = client['saldo'] + (request.valor if request.tipo == 'c' else -request.valor)
        if request.tipo == 'd' and new_saldo < -client['limite']:
            raise HTTPException(status_code=422, detail="Saldo insuficiente")
        
        transaction_dict = {
            "cliente_id": client_id,
            "valor": request.valor,
            "tipo": request.tipo,
            "descricao": request.descricao
        }
        await database.execute(transactions.insert().values(**transaction_dict))
        await database.execute(saldos.update().where(saldos.c.cliente_id == client_id).values(valor=new_saldo))

    return {"limite": client['limite'], "saldo": new_saldo}

@app.get("/clientes/{client_id}/extrato", response_model=StatementResponse)
async def extrato(client_id: int = Path(..., gt=0)):
    client_saldos_join = clientes.join(saldos, clientes.c.id == saldos.c.cliente_id)
    client_query = select([clientes.c.limite, saldos.c.valor.label("saldo")]).select_from(client_saldos_join).where(clientes.c.id == client_id)
    
    client_info = await database.fetch_one(client_query)

    if client_info is None:
        raise HTTPException(status_code=404, detail="Cliente não encontrado")

    transactions_query = select(
        [transactions.c.valor, transactions.c.tipo, transactions.c.descricao, transactions.c.realizada_em]
    ).where(transactions.c.cliente_id == client_id).order_by(desc(transactions.c.realizada_em)).limit(10)
    transaction_records = await database.fetch_all(transactions_query)

    ultimas_transacoes = [{
        "valor": transaction["valor"],
        "tipo": transaction["tipo"],
        "descricao": transaction["descricao"],
        "realizada_em": transaction["realizada_em"]
    } for transaction in transaction_records]

    return {
        "saldo": {
            "total": client_info["saldo"],  
            "data_extrato": datetime.datetime.utcnow(),
            "limite": client_info["limite"]
        },
        "ultimas_transacoes": ultimas_transacoes
    }

@app.on_event("startup")
async def startup():
    await database.connect()

@app.on_event("shutdown")
async def shutdown():
    await database.disconnect()
