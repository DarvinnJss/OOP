def validate_price(price_str):
    """Validate price input"""
    try:
        price = float(price_str)
        return price >= 0
    except ValueError:
        return False


def validate_stock(stock_str):
    """Validate stock input"""
    try:
        stock = int(stock_str)
        return stock >= 0
    except ValueError:
        return False


def validate_text(text):
    """Validate text input (non-empty)"""
    return bool(text and text.strip())
