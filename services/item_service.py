from schmeas.item import ItemRead

items_db: dict[int, ItemRead] = {
    1: ItemRead(id=1, name="Wireless Mouse", price=25.50),
    2: ItemRead(id=2, name="Mechanical Keyboard", price=75.00),
    3: ItemRead(id=3, name="USB-C Monitor", price=200.00),
}


def get_all_items():
    return list(items_db.values())


def get_item_by_id(item_id: int):
    item = items_db.get(item_id)
    return item
