from typing import Dict
from ..data import BASE_LOCATION_ID, LOCATIONS_DATA
from ..common.Util import build_item_name_to_id_dict, build_item_id_to_name_dict


def build_location_name_to_id_dict() -> Dict[str, int]:
    location_name_to_id: Dict[str, int] = {}
    current_index = BASE_LOCATION_ID
    for loc_name in LOCATIONS_DATA:
        location_name_to_id[loc_name] = current_index
        current_index += 1
    return location_name_to_id