-- 1) Estoque atual por produto (saldo = recebido conferido - saidas)
CREATE OR REPLACE VIEW vw_estoque_atual AS
SELECT
    p.id_produto,
    p.descricao,
    p.categoria,
    p.custo_unitario,
    p.estoque_minimo,
    COALESCE(r.total_recebido, 0) AS total_recebido,
    COALESCE(s.total_saido, 0)    AS total_saido,
    COALESCE(r.total_recebido, 0) - COALESCE(s.total_saido, 0) AS saldo_estoque,
    -- giro do periodo (simplificado: saidas / saldo atual)
    ROUND(COALESCE(s.total_saido, 0)::numeric
          / NULLIF(COALESCE(r.total_recebido, 0) - COALESCE(s.total_saido, 0), 0), 2) AS giro_periodo
FROM produtos p
LEFT JOIN (SELECT id_produto, SUM(qtd_conferida) AS total_recebido
           FROM recebimentos GROUP BY id_produto) r ON r.id_produto = p.id_produto
LEFT JOIN (SELECT id_produto, SUM(quantidade) AS total_saido
           FROM saidas GROUP BY id_produto) s ON s.id_produto = p.id_produto;

-- 2) Curva ABC por valor das saidas (A = ate 80%, B = ate 95%, C = resto)
CREATE OR REPLACE VIEW vw_curva_abc AS
WITH valor AS (
    SELECT p.id_produto, p.descricao, p.categoria,
           SUM(s.quantidade * p.custo_unitario) AS valor_saidas
    FROM saidas s
    JOIN produtos p ON p.id_produto = s.id_produto
    GROUP BY p.id_produto, p.descricao, p.categoria
),
acumulado AS (
    SELECT *,
           SUM(valor_saidas) OVER (ORDER BY valor_saidas DESC) / SUM(valor_saidas) OVER () AS pct_acumulado
    FROM valor
)
SELECT *,
       CASE WHEN pct_acumulado <= 0.80 THEN 'A'
            WHEN pct_acumulado <= 0.95 THEN 'B'
            ELSE 'C' END AS classe
FROM acumulado;

-- 3) Risco de ruptura (cobertura em dias x prazo de entrega do fornecedor)
CREATE OR REPLACE VIEW vw_risco_ruptura AS
WITH ref AS (
    SELECT MAX(data_saida) AS data_ref FROM saidas
),
consumo AS (
    SELECT s.id_produto, SUM(s.quantidade) / 90.0 AS media_diaria
    FROM saidas s, ref
    WHERE s.data_saida > ref.data_ref - 90
    GROUP BY s.id_produto
),
forn AS (
    SELECT DISTINCT r.id_produto, f.nome AS fornecedor, f.prazo_entrega_dias
    FROM recebimentos r
    JOIN fornecedores f ON f.id_fornecedor = r.id_fornecedor
)
SELECT
    e.id_produto, e.descricao, e.categoria,
    e.saldo_estoque, e.estoque_minimo,
    f.fornecedor, f.prazo_entrega_dias,
    ROUND(c.media_diaria, 2) AS media_diaria,
    ROUND(e.saldo_estoque / NULLIF(c.media_diaria, 0), 1) AS cobertura_dias,
    CASE
        WHEN e.saldo_estoque <= 0 THEN 'RUPTURA'
        WHEN e.saldo_estoque < e.estoque_minimo THEN 'ALTO'
        WHEN e.saldo_estoque / NULLIF(c.media_diaria, 0) < f.prazo_entrega_dias THEN 'ALTO'
        WHEN e.saldo_estoque / NULLIF(c.media_diaria, 0) < f.prazo_entrega_dias * 2 THEN 'MEDIO'
        ELSE 'BAIXO'
    END AS risco
FROM vw_estoque_atual e
JOIN forn f ON f.id_produto = e.id_produto
LEFT JOIN consumo c ON c.id_produto = e.id_produto;

-- 4) Divergencias no recebimento (nota fiscal x conferido)
CREATE OR REPLACE VIEW vw_divergencias_recebimento AS
SELECT
    r.id_recebimento,
    r.data_recebimento,
    p.descricao,
    f.nome AS fornecedor,
    r.qtd_nota_fiscal,
    r.qtd_conferida,
    r.qtd_conferida - r.qtd_nota_fiscal AS diferenca,
    (r.qtd_nota_fiscal - r.qtd_conferida) * p.custo_unitario AS valor_divergente,
    (r.qtd_nota_fiscal <> r.qtd_conferida) AS tem_divergencia
FROM recebimentos r
JOIN produtos p ON p.id_produto = r.id_produto
JOIN fornecedores f ON f.id_fornecedor = r.id_fornecedor;