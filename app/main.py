import datetime
from domain import StatementResponse, TransactionRequest, TransactionResponse
from fastapi import FastAPI, HTTPException, Path
from database.config import database
from database.db_models import clientes, transactions  # Corrected import
from sqlalchemy import select, desc

app = FastAPI()

@app.post("/clientes/{client_id}/transacoes", response_model=TransactionResponse)
async def transacao(client_id: int, request: TransactionRequest):
    query = select([clientes.c.limite, clientes.c.saldo]).where(clientes.c.id == client_id)
    client = await database.fetch_one(query)

    if client is None:
        raise HTTPException(status_code=404, detail="Cliente não encontrado")

    new_saldo = client['saldo'] + (request.valor if request.tipo == 'c' else -request.valor)

    if request.tipo == 'd' and new_saldo < -client['limite']:
        raise HTTPException(status_code=422, detail="Saldo insuficiente")

    transaction_dict = {
        "client_id": client_id,
        "valor": request.valor,
        "tipo": request.tipo,
        "descricao": request.descricao
    }
    await database.execute(transactions.insert().values(**transaction_dict))

    await database.execute(clientes.update().where(clientes.c.id == client_id).values(saldo=new_saldo))

    return {"limite": client['limite'], "saldo": new_saldo}

@app.get("/clientes/{client_id}/extrato", response_model=StatementResponse)
async def extrato(client_id: int = Path(..., gt=0)):
    client_query = select([clientes.c.saldo, clientes.c.limite]).where(clientes.c.id == client_id)
    client_info = await database.fetch_one(client_query)

    if client_info is None:
        raise HTTPException(status_code=404, detail="Cliente não encontrado")

    transactions_query = select([transactions]).where(transactions.c.client_id == client_id).order_by(desc(transactions.c.realizada_em)).limit(10)
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
