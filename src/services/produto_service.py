from entities.produto import Produto


class ProdutoService:
    def __init__(self):
        self.produtos = [
            Produto(nome="Monitor", preco=999.90, quantidade_estoque=75),
            Produto(nome="Teclado", preco=150.00, quantidade_estoque=120),
            Produto(nome="Mouse Gamer", preco=99.50, quantidade_estoque=80),
            Produto(nome="Webcam", preco=120.00, quantidade_estoque=40),
            Produto(nome="Headset", preco=180.00, quantidade_estoque=60),
            Produto(nome="Impressora", preco=750.00, quantidade_estoque=15)
        ]

    def consultar_estoque(self, item: str) -> str:
        """
        Simula a consulta de estoque de um item no inventário.
        """
        print(f"Consultando estoque para o item: {item}")
        item = item.lower()

        for produto in self.produtos:
            if produto["nome"].lower() == item:
                return f"Temos {produto['quantidade_estoque']} {item}s em estoque."
        return f"Item '{item}' não encontrado no inventário."

    def consultar_preco_produto(self, produto: str) -> str:
        """
        Simula a consulta do preço unitário de um produto.
        """
        produto = produto.lower()
        
        for p in self.produtos:
            if p["nome"].lower() == produto:
                return f"O preço de um(a) {produto} é R$ {p['preco']:.2f}."
            
        return f"Produto '{produto}' não encontrado na lista de preços."
    
    def listar_produtos(self, max_items: int = 10) -> list[dict]:
        """
        Lista todos os produtos disponíveis no inventário.
        Retorna eles com seu preço e estoque em formato json
        """
        print("Listando todos os produtos disponíveis:")
        produtos_info = [
            {
                "nome": produto["nome"],
                "preco": produto["preco"],
                "quantidade_estoque": produto["quantidade_estoque"]
            }
            for produto in self.produtos[:max_items]
        ]
        return produtos_info