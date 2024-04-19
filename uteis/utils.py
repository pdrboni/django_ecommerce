def formata_preco(val):
    return f'R$ {val:.2f}'.replace('.', ',')

def cart_total_qtd(carrinho):
    return sum([item['quantity'] for item in carrinho.values()])

def cart_totals(carrinho):
    return sum([
        item.get('promotional_quantitative_price') if item.get('promotional_quantitative_price') else item.get('quantitative_price') for item in carrinho.values()
    ])

def cart_totals_mais_frete(carrinho, frete=0):
    soma_carrinho = sum([
        item.get('promotional_quantitative_price') if item.get('promotional_quantitative_price') else item.get('quantitative_price') for item in carrinho.values()
    ])
    soma_carrinho_mais_frete = soma_carrinho + frete
    return f'R$ {soma_carrinho_mais_frete:.2f}'.replace('.', ',')
