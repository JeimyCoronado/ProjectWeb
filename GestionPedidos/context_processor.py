
def cart_total_amount(request):
    subtotal = 0.0
    descuento = 0.0
    total = 0.0
    if "carrito" in request.session.keys():
        for key, value in request.session.get("carrito").items():
            subtotal += (value["precio"]*value['cantidad'])
            subtotal = round(subtotal,2)
            descuento += (value["descuento"] * value["cantidad"])
            descuento = round(descuento, 2)
        total = subtotal-descuento
        total = round(total, 2)
    return {"cart_total_amount": subtotal, "descuento": descuento, "total": total}
