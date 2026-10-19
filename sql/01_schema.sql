CREATE TABLE fornecedores (
    id_fornecedor INT PRIMARY KEY,
    nome VARCHAR(150) NOT NULL,
    prazo_entrega_dias INT NOT NULL
);

CREATE TABLE produtos (
    id_produto INT PRIMARY KEY,
    descricao VARCHAR(150) NOT NULL,
    categoria VARCHAR(50) NOT NULL,
    custo_unitario NUMERIC(10,2) NOT NULL,
    estoque_minimo INT NOT NULL
);

CREATE TABLE recebimentos (
    id_recebimento INT PRIMARY KEY,
    id_produto INT NOT NULL REFERENCES produtos(id_produto),
    id_fornecedor INT NOT NULL REFERENCES fornecedores(id_fornecedor),
    data_recebimento DATE NOT NULL,
    qtd_nota_fiscal INT NOT NULL,
    qtd_conferida INT NOT NULL
);

CREATE TABLE saidas (
    id_saida INT PRIMARY KEY,
    id_produto INT NOT NULL REFERENCES produtos(id_produto),
    data_saida DATE NOT NULL,
    quantidade INT NOT NULL
);