from typing import TypedDict


class Produto(TypedDict):
    nome: str
    preco: float
    quantidade_estoque: int