from ..data import ITEMS_DATA


def get_item_id_and_subid(item: dict):
    # Remote item, use the generic "Archipelago Item"
    if item["item"] == "Archipelago Item" or ("player" in item and not item["progression"]):
        return 0x41, 0x00
    if item["item"] == "Archipelago Progression Item" or ("player" in item and item["progression"]):
        return 0x41, 0x01

    # Local item, put the real item in there
    item_data = ITEMS_DATA[item["item"]]
    item_id = item_data["id"]
    item_subid = item_data["subid"] if "subid" in item_data else 0x00
    if item_id == 0x30:
        item_subid = item_subid & 0x7F  # TODO : Remove when/if master key becomes available on non-master key worlds
    return item_id, item_subid