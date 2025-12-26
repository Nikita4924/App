from typing import Any
from database.db_manager import Database, safe_float

class AddServiceWindow:
    """
    РџСЂРѕСЃР»РѕР№РєР° РґР»СЏ СЂР°Р±РѕС‚С‹ СЃ СѓСЃР»СѓРіР°РјРё.
    """

    def __init__(self, db_path: str = "database/database.sqlite"):
        self.db = Database(db_path)

    def create_service(self, name: str, price: Any = 0.0) -> int:
        """
        Р’РѕР·РІСЂР°С‰Р°РµС‚ id СЃРµСЂРІРёСЃР° (СЃРѕР·РґР°С‘С‚, РµСЃР»Рё РЅРµ СЃСѓС‰РµСЃС‚РІСѓРµС‚).
        """
        pname = "" if name is None else str(name)
        price_v = safe_float(price, 0.0)
        sid = self.db.add_service(pname, price_v)
        return int(sid)