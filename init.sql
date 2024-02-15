CREATE UNLOGGED TABLE clientes (
    id SERIAL PRIMARY KEY,
    nome VARCHAR(50) NOT NULL,
    limite INTEGER NOT NULL
);

CREATE UNLOGGED TABLE transacoes (
    id SERIAL,
    cliente_id INTEGER NOT NULL,
    valor INTEGER NOT NULL,
    tipo CHAR(1) NOT NULL CHECK (tipo IN ('c', 'd')),
    descricao VARCHAR(10) NOT NULL,
    realizada_em TIMESTAMP NOT NULL DEFAULT NOW()
) PARTITION BY LIST (tipo);

CREATE UNLOGGED TABLE transacoes_c PARTITION OF transacoes FOR VALUES IN ('c');
CREATE UNLOGGED TABLE transacoes_d PARTITION OF transacoes FOR VALUES IN ('d');

CREATE UNIQUE INDEX ON transacoes (id, tipo);


CREATE UNLOGGED TABLE saldos (
    id SERIAL PRIMARY KEY,
    cliente_id INTEGER NOT NULL,
    valor INTEGER NOT NULL,
    CONSTRAINT fk_clientes_saldos_id
        FOREIGN KEY (cliente_id) REFERENCES clientes(id)
);

DO $$
BEGIN
    INSERT INTO clientes (nome, limite)
    VALUES
        ('o barato sai caro', 1000 * 100),
        ('zan corp ltda', 800 * 100),
        ('les cruders', 10000 * 100),
        ('padaria joia de cocaia', 100000 * 100),
        ('kid mais', 5000 * 100);
    
    INSERT INTO saldos (cliente_id, valor)
    SELECT id, 0 FROM clientes;
END;
$$;

CREATE OR REPLACE FUNCTION debitar(
    cliente_id_tx INT,
    valor_tx INT,
    descricao_tx VARCHAR(10)
)
RETURNS TABLE (
    novo_saldo INT,
    possui_erro BOOL,
    mensagem VARCHAR(20)
)
LANGUAGE plpgsql
AS $$
DECLARE
    limite_atual INT;
    saldo_atual INT;
BEGIN
    PERFORM pg_advisory_xact_lock(cliente_id_tx);

    WITH saldo_data AS (
        SELECT c.limite, COALESCE(s.valor, 0) AS saldo
        FROM clientes c
        LEFT JOIN saldos s ON c.id = s.cliente_id
        WHERE c.id = cliente_id_tx
    )
    SELECT limite, saldo INTO STRICT limite_atual, saldo_atual FROM saldo_data;

    IF saldo_atual - valor_tx >= limite_atual * -1 THEN
        INSERT INTO transacoes
            (cliente_id, valor, tipo, descricao, realizada_em)
            VALUES (cliente_id_tx, valor_tx, 'd', descricao_tx, NOW());

        UPDATE saldos
        SET valor = valor - valor_tx
        WHERE cliente_id = cliente_id_tx;

        RETURN QUERY SELECT valor, FALSE, 'ok'::VARCHAR(20) FROM saldos WHERE cliente_id = cliente_id_tx;
    ELSE
        RETURN QUERY SELECT valor, TRUE, 'saldo insuficiente'::VARCHAR(20) FROM saldos WHERE cliente_id = cliente_id_tx;
    END IF;
END;
$$;

CREATE OR REPLACE FUNCTION creditar(
    cliente_id_tx INT,
    valor_tx INT,
    descricao_tx VARCHAR(10))
RETURNS TABLE (
    novo_saldo INT,
    possui_erro BOOL,
    mensagem VARCHAR(20))
LANGUAGE plpgsql
AS $$
BEGIN
    PERFORM pg_advisory_xact_lock(cliente_id_tx);

    INSERT INTO transacoes_d
        (cliente_id, valor, tipo, descricao, realizada_em)
        VALUES (cliente_id_tx, valor_tx, 'c', descricao_tx, NOW());

    UPDATE saldos
    SET valor = valor + valor_tx
    WHERE cliente_id = cliente_id_tx;

    RETURN QUERY SELECT valor, FALSE, 'ok'::VARCHAR(20) FROM saldos WHERE cliente_id = cliente_id_tx;
END;
$$;
