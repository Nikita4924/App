"""
Р“Р»Р°РІРЅС‹Р№ GUI-С„Р°Р№Р» вЂ” СЃРѕРґРµСЂР¶РёС‚:
- LoginFrame (РѕРєРЅРѕ РІС…РѕРґР°) СЃ РєРЅРѕРїРєРѕР№ "Р РµРіРёСЃС‚СЂР°С†РёСЏ" (РѕС‚РєСЂС‹РІР°РµС‚ RegisterWindow, РµСЃР»Рё РѕРЅ РµСЃС‚СЊ)
- MainAppWindow вЂ” РіР»Р°РІРЅРѕРµ РїСЂРёР»РѕР¶РµРЅРёРµ РїРѕСЃР»Рµ РІС…РѕРґР°, РѕС‚РІРµС‡Р°РµС‚ Р·Р° СЂРѕР»Рё manager/employee
- Р’СЃС‚СЂРѕРµРЅРЅС‹Рµ Р±РµР·РѕРїР°СЃРЅС‹Рµ РІС‹Р·РѕРІС‹ Рє Database СЃ fallback'Р°РјРё (РµСЃР»Рё API db_manager РѕС‚Р»РёС‡Р°РµС‚СЃСЏ)
"""
from typing import Optional, Any, Dict
import traceback

try:
    import customtkinter as ctk
except Exception as e:
    raise RuntimeError("РЈСЃС‚Р°РЅРѕРІРёС‚Рµ customtkinter (pip install customtkinter). РћС€РёР±РєР° РёРјРїРѕСЂС‚Р°: " + str(e))

from tkinter import messagebox

# РїС‹С‚Р°РµРјСЃСЏ РёРјРїРѕСЂС‚РёСЂРѕРІР°С‚СЊ РєР»Р°СЃСЃС‹ РѕРєРѕРЅ, РµСЃР»Рё Сѓ РІР°СЃ РѕРЅРё РµСЃС‚СЊ вЂ” Р±СѓРґСѓС‚ РёСЃРїРѕР»СЊР·РѕРІР°РЅС‹
try:
    from gui.windows.register_window import RegisterWindow  # РѕРєРЅРѕ СЂРµРіРёСЃС‚СЂР°С†РёРё (ctk)
except Exception:
    RegisterWindow = None

try:
    from gui.windows.quick_entry_window import QuickEntryWindow
except Exception:
    QuickEntryWindow = None

try:
    from gui.windows.employees_window import EmployeesWindow
except Exception:
    EmployeesWindow = None

try:
    from gui.windows.profile_window import ProfileWindow
except Exception:
    ProfileWindow = None

try:
    from gui.windows.manager_dashboard import ManagerDashboard
except Exception:
    ManagerDashboard = None

# Database
try:
    from database.db_manager import Database, safe_int, safe_float
except Exception:
    # РµСЃР»Рё РёРјРїРѕСЂС‚ РЅРµ СѓРґР°Р»СЃСЏ, РїРѕРґСЃРєР°Р¶РµРј РїРѕР»СЊР·РѕРІР°С‚РµР»СЋ
    raise RuntimeError("РќРµ СѓРґР°Р»РѕСЃСЊ РёРјРїРѕСЂС‚РёСЂРѕРІР°С‚СЊ database.db_manager вЂ” СѓР±РµРґРёС‚РµСЃСЊ, С‡С‚Рѕ С„Р°Р№Р» РµСЃС‚СЊ Рё РєРѕСЂСЂРµРєС‚РµРЅ.")

# --------------------------
# Р’СЃРїРѕРјРѕРіР°С‚РµР»СЊРЅС‹Рµ С„СѓРЅРєС†РёРё
# --------------------------


def try_authenticate(db: Database, username: str, password: str) -> Optional[Dict[str, Any]]:
    """
    Р‘РµР·РѕРїР°СЃРЅС‹Р№ РІС‹Р·РѕРІ Р°СѓС‚РµРЅС‚РёС„РёРєР°С†РёРё.
    РџС‹С‚Р°РµС‚СЃСЏ РёСЃРїРѕР»СЊР·РѕРІР°С‚СЊ РЅРµСЃРєРѕР»СЊРєРѕ РІРѕР·РјРѕР¶РЅС‹С… API: authenticate / authenticate_user / get_user_by_username.
    Р’РѕР·РІСЂР°С‰Р°РµС‚ РѕР±СЉРµРєС‚ РїРѕР»СЊР·РѕРІР°С‚РµР»СЏ (dict / tuple) РїСЂРё СѓСЃРїРµС…Рµ РёР»Рё None.
    """
    try:
        if hasattr(db, "authenticate"):
            return db.authenticate(username, password)
        if hasattr(db, "authenticate_user"):
            return db.authenticate_user(username, password)

        # fallback: РїРѕР»СѓС‡РёС‚СЊ РїРѕР»СЊР·РѕРІР°С‚РµР»СЏ Рё РїСЂРѕРІРµСЂРёС‚СЊ РїР°СЂРѕР»СЊ (РµСЃР»Рё С…СЂР°РЅРёС‚СЃСЏ РІ РѕС‚РєСЂС‹С‚РѕРј РІРёРґРµ)
        if hasattr(db, "get_user_by_username"):
            u = db.get_user_by_username(username)
            if not u:
                return None
            # u РјРѕР¶РµС‚ Р±С‹С‚СЊ dict РёР»Рё tuple
            pwd_fields = ["password", "pass", "phash", "password_hash"]
            upwd = None
            if isinstance(u, dict):
                for f in pwd_fields:
                    if f in u and u[f] is not None:
                        upwd = u[f]
                        break
            else:
                # tuple-like: РїСЂРѕР±СѓРµРј РїСЂРµРґРїРѕР»РѕР¶РёС‚СЊ, С‡С‚Рѕ РїРѕР»Рµ РїР°СЂРѕР»СЏ С‚СЂРµС‚СЊРµ
                if len(u) >= 3:
                    upwd = u[2]
            if upwd is None:
                # Р•СЃР»Рё РЅРµС‚ РїР°СЂРѕР»СЏ РІ Р‘Р” (РЅР°РїСЂРёРјРµСЂ, Р°СѓС‚РµРЅС‚РёС„РёРєР°С†РёСЏ РЅРµ СЂРµР°Р»РёР·РѕРІР°РЅР°), СЃС‡РёС‚Р°РµРј СѓСЃРїРµС€РЅС‹Рј РїРѕРёСЃРє РїРѕР»СЊР·РѕРІР°С‚РµР»СЏ.
                return u
            # РЎСЂР°РІРЅРёРІР°РµРј РІ СЏРІРЅРѕРј РІРёРґРµ
            if str(upwd) == str(password):
                return u
            return None
    except Exception:
        traceback.print_exc()
        return None


def user_role_of(u: Any) -> str:
    """
    РџРѕРїС‹С‚Р°С‚СЊСЃСЏ РёР·РІР»РµС‡СЊ СЂРѕР»СЊ РїРѕР»СЊР·РѕРІР°С‚РµР»СЏ: 'manager' РёР»Рё 'employee'.
    РџРѕРґРґРµСЂР¶РёРІР°РµС‚ СЂР°Р·РЅС‹Рµ С„РѕСЂРјР°С‚С‹ (dict/tuple) Рё РїРѕР»СЏ: role, is_admin, is_manager.
    """
    role = "employee"
    try:
        if not u:
            return role
        if isinstance(u, dict):
            if "role" in u and u["role"]:
                role = str(u["role"])
            elif "is_admin" in u:
                role = "manager" if bool(u["is_admin"]) else "employee"
            elif "is_manager" in u:
                role = "manager" if bool(u["is_manager"]) else "employee"
        else:
            # tuple-like: РїСЂРѕР±СѓРµРј СѓРіР°РґР°С‚СЊ (id, username, phash, is_admin, full_name, phone, email)
            # С‡Р°СЃС‚Рѕ is_admin РјРѕР¶РµС‚ РЅР°С…РѕРґРёС‚СЊСЃСЏ РЅР° РїРѕР·РёС†РёРё 3 (index 3)
            if len(u) >= 4:
                val = u[3]
                if val in (1, True, "1", "True", "true"):
                    role = "manager"
    except Exception:
        traceback.print_exc()
    return role


def user_to_dict(u: Any) -> Dict[str, Any]:
    """РЈРЅРёС„РёС†РёСЂСѓРµРј РїСЂРµРґСЃС‚Р°РІР»РµРЅРёРµ РїРѕР»СЊР·РѕРІР°С‚РµР»СЏ РєР°Рє dict СЃ РѕР¶РёРґР°РµРјС‹РјРё РєР»СЋС‡Р°РјРё."""
    if u is None:
        return {}
    if isinstance(u, dict):
        return u
    # tuple-like fallback: СЃРѕР±СЂР°С‚СЊ СЃР»РѕРІР°СЂСЊ РїРѕ СЂР°СЃРїСЂРѕСЃС‚СЂР°РЅС‘РЅРЅС‹Рј РїРѕР·РёС†РёСЏРј
    keys = ["id", "username", "password", "is_admin", "full_name", "phone", "email"]
    d = {}
    for i, k in enumerate(keys):
        if i < len(u):
            d[k] = u[i]
        else:
            d[k] = None
    # СЂРѕР»СЊ
    d["role"] = "manager" if d.get("is_admin") in (1, True, "1") else d.get("role", "employee")
    return d


# --------------------------
# LoginFrame (РІСЃС‚СЂР°РёРІР°РµРјС‹Р№)
# --------------------------


class LoginFrame(ctk.CTkFrame):
    """
    РџСЂРѕСЃС‚Р°СЏ РїР°РЅРµР»СЊ РІС…РѕРґР° (Р»РѕРіРёРЅ + РїР°СЂРѕР»СЊ) СЃ РєРЅРѕРїРєРѕР№ "Р РµРіРёСЃС‚СЂР°С†РёСЏ".
    РџСЂРё СѓСЃРїРµС€РЅРѕРј РІС…РѕРґРµ РІС‹Р·С‹РІР°РµС‚ callback on_login(user_dict).
    """

    def __init__(self, parent, db: Database, on_login, *args, **kwargs):
        super().__init__(parent, *args, **kwargs)
        self.db = db
        self.on_login = on_login

        # UI
        ctk.CTkLabel(self, text="Р’С…РѕРґ РІ СЃРёСЃС‚РµРјСѓ", font=ctk.CTkFont(size=18, weight="bold")).pack(pady=(8, 12))

        self.username = ctk.CTkEntry(self, placeholder_text="Р›РѕРіРёРЅ")
        self.username.pack(fill="x", padx=20, pady=6)

        self.password = ctk.CTkEntry(self, placeholder_text="РџР°СЂРѕР»СЊ", show="*")
        self.password.pack(fill="x", padx=20, pady=6)

        btn_frame = ctk.CTkFrame(self, fg_color="transparent")
        btn_frame.pack(fill="x", pady=(10, 0), padx=20)
        self.login_btn = ctk.CTkButton(btn_frame, text="Р’РѕР№С‚Рё", command=self._on_login)
        self.login_btn.pack(side="left", expand=True, fill="x", padx=(0, 6))

        self.reg_btn = ctk.CTkButton(btn_frame, text="Р РµРіРёСЃС‚СЂР°С†РёСЏ", command=self._on_register)
        self.reg_btn.pack(side="left", expand=True, fill="x", padx=(6, 0))

        self.status = ctk.CTkLabel(self, text="", text_color="red")
        self.status.pack(pady=(8, 0))

    def _on_register(self):
        # РѕС‚РєСЂС‹С‚СЊ РѕРєРЅРѕ СЂРµРіРёСЃС‚СЂР°С†РёРё (РµСЃР»Рё РµСЃС‚СЊ RegisterWindow) РёР»Рё РїРѕРєР°Р·Р°С‚СЊ СЃРѕРѕР±С‰РµРЅРёРµ
        if RegisterWindow is not None:
            try:
                RegisterWindow(self.db)  # СЂРµР°Р»РёР·Р°С†РёСЏ РІ РѕС‚РґРµР»СЊРЅРѕРј С„Р°Р№Р»Рµ РґРѕР»Р¶РЅР° РѕС‚РєСЂС‹С‚СЊ СЃРІРѕС‘ РѕРєРЅРѕ
            except Exception:
                traceback.print_exc()
                messagebox.showerror("РћС€РёР±РєР°", "РќРµ СѓРґР°Р»РѕСЃСЊ РѕС‚РєСЂС‹С‚СЊ РѕРєРЅРѕ СЂРµРіРёСЃС‚СЂР°С†РёРё.")
        else:
            messagebox.showinfo("Р РµРіРёСЃС‚СЂР°С†РёСЏ", "РћРєРЅРѕ СЂРµРіРёСЃС‚СЂР°С†РёРё РЅРµ РЅР°Р№РґРµРЅРѕ. РЎРѕР·РґР°Р№С‚Рµ РїРѕР»СЊР·РѕРІР°С‚РµР»СЏ С‡РµСЂРµР· РјРµРЅРµРґР¶РµСЂ Р‘Р”.")

    def _on_login(self):
        username = self.username.get().strip()
        password = self.password.get().strip()
        if not username or not password:
            self.status.configure(text="Р’РІРµРґРёС‚Рµ Р»РѕРіРёРЅ Рё РїР°СЂРѕР»СЊ")
            return
        user = try_authenticate(self.db, username, password)
        if not user:
            self.status.configure(text="РќРµРІРµСЂРЅС‹Р№ Р»РѕРіРёРЅ РёР»Рё РїР°СЂРѕР»СЊ")
            return
        userd = user_to_dict(user)
        self.status.configure(text="")
        # РІС‹Р·РІР°С‚СЊ callback СЃ user dict
        try:
            self.on_login(userd)
        except Exception:
            traceback.print_exc()


# --------------------------
# MainAppWindow
# --------------------------


class MainAppWindow:
    """
    Р“Р»Р°РІРЅРѕРµ РѕРєРЅРѕ РїСЂРёР»РѕР¶РµРЅРёСЏ вЂ” СЃРѕР·РґР°С‘С‚СЃСЏ РїРѕСЃР»Рµ СѓСЃРїРµС€РЅРѕРіРѕ Р»РѕРіРёРЅР°.
    РџР°СЂР°РјРµС‚СЂ user вЂ” dict (id, username, role, ...)
    """

    def __init__(self, user: Dict[str, Any], db: Database):
        self.user = user
        self.db = db
        self.root = ctk.CTk()
        self.root.title("Barber App")
        self.root.geometry("1000x650")
        self._build_ui()

    def _build_ui(self):
        # СЃС‚РѕСЂРѕРЅРё
        sidebar = ctk.CTkFrame(self.root, width=220, corner_radius=0)
        sidebar.pack(side="left", fill="y")

        content = ctk.CTkFrame(self.root)
        content.pack(side="right", expand=True, fill="both")

        # РІРµСЂС…РЅСЏСЏ РёРЅС„Рѕ
        ctk.CTkLabel(sidebar, text=f"РџРѕР»СЊР·РѕРІР°С‚РµР»СЊ:\n{self.user.get('username')}", wraplength=200).pack(pady=16)

        # РєРЅРѕРїРєРё (СѓРЅРёРІРµСЂСЃР°Р»СЊРЅС‹Рµ)
        ctk.CTkButton(sidebar, text="Р”РѕРјРѕР№", command=lambda: self.show_view("home")).pack(fill="x", padx=12, pady=6)
        ctk.CTkButton(sidebar, text="РџСЂРѕС„РёР»СЊ", command=lambda: self.show_view("profile")).pack(fill="x", padx=12, pady=6)
        ctk.CTkButton(sidebar, text="Р‘С‹СЃС‚СЂР°СЏ Р·Р°РїРёСЃСЊ", command=lambda: self.show_view("quick")).pack(fill="x", padx=12, pady=6)
        ctk.CTkButton(sidebar, text="РЈСЃР»СѓРіРё", command=lambda: self.show_view("services")).pack(fill="x", padx=12, pady=6)

        role = user_role_of(self.user)
        if role == "manager" or str(self.user.get("role")).lower() == "manager":
            ctk.CTkButton(sidebar, text="РЎРѕС‚СЂСѓРґРЅРёРєРё", command=lambda: self.show_view("employees")).pack(fill="x", padx=12, pady=6)
            ctk.CTkButton(sidebar, text="Dashboard (РјРµРЅРµРґР¶РµСЂ)", command=lambda: self.show_view("manager_dashboard")).pack(fill="x", padx=12, pady=6)

        ctk.CTkButton(sidebar, text="Р’С‹С…РѕРґ", fg_color="#d9534f", command=self.root.destroy).pack(side="bottom", fill="x", padx=12, pady=12)

        self.content = content
        self.current_view = None
        self.views = {}
        # РЅР°С‡Р°Р»СЊРЅС‹Р№
        self.show_view("home")

    def show_view(self, name: str):
        """РџРѕРєР°Р·С‹РІР°РµС‚ РѕРґРЅСѓ РёР· РїСЂРµРґРѕРїСЂРµРґРµР»С‘РЅРЅС‹С… РїР°РЅРµР»РµР№."""
        for w in self.content.winfo_children():
            w.destroy()
        if name == "home":
            self._show_home()
        elif name == "profile":
            self._show_profile()
        elif name == "quick":
            self._show_quick_entry()
        elif name == "employees":
            self._show_employees()
        elif name == "manager_dashboard":
            self._show_manager_dashboard()
        elif name == "services":
            self._show_services()
        else:
            self._show_home()

    def _show_home(self):
        ctk.CTkLabel(self.content, text="Р”РѕР±СЂРѕ РїРѕР¶Р°Р»РѕРІР°С‚СЊ РІ Barber App", font=ctk.CTkFont(size=20, weight="bold")).pack(pady=40)

    def _show_profile(self):
        # Р•СЃР»Рё РµСЃС‚СЊ ProfileWindow вЂ” РёСЃРїРѕР»СЊР·СѓРµРј РµРіРѕ РєР°Рє РјРѕРґР°Р»
        if ProfileWindow is not None:
            try:
                ProfileWindow(self.root, user_id=self.user.get("id"))
                return
            except Exception:
                traceback.print_exc()
        # fallback: РїСЂРѕСЃС‚РѕР№ РїСЂРѕС„РёР»СЊ
        frm = ctk.CTkFrame(self.content)
        frm.pack(expand=True, fill="both", padx=20, pady=20)
        ctk.CTkLabel(frm, text=f"РџСЂРѕС„РёР»СЊ: {self.user.get('username')}", font=ctk.CTkFont(size=16, weight="bold")).pack(pady=8)
        ctk.CTkLabel(frm, text=f"Р¤РРћ: {self.user.get('full_name', '')}").pack(pady=4)
        ctk.CTkLabel(frm, text=f"РўРµР»РµС„РѕРЅ: {self.user.get('phone', '')}").pack(pady=4)
        ctk.CTkButton(frm, text="Р РµРґР°РєС‚РёСЂРѕРІР°С‚СЊ РїСЂРѕС„РёР»СЊ", command=lambda: self._open_profile_editor()).pack(pady=12)

    def _open_profile_editor(self):
        if ProfileWindow is not None:
            try:
                ProfileWindow(self.root, user_id=self.user.get("id"))
                return
            except Exception:
                traceback.print_exc()
        messagebox.showinfo("РџСЂРѕС„РёР»СЊ", "РћРєРЅРѕ СЂРµРґР°РєС‚РёСЂРѕРІР°РЅРёСЏ РїСЂРѕС„РёР»СЏ РЅРµ РЅР°Р№РґРµРЅРѕ РІ РїСЂРѕРµРєС‚Рµ.")

    def _show_quick_entry(self):
        # QuickEntryWindow РґРѕР»Р¶РµРЅ Р±С‹С‚СЊ РІ РѕС‚РґРµР»СЊРЅРѕРј С„Р°Р№Р»Рµ; РїРѕРїС‹С‚Р°РµРјСЃСЏ РµРіРѕ РѕС‚РєСЂС‹С‚СЊ
        if QuickEntryWindow is not None:
            try:
                QuickEntryWindow(self.root, on_saved=lambda: messagebox.showinfo("РЎРѕС…СЂР°РЅРµРЅРѕ", "Р—Р°РїРёСЃСЊ РґРѕР±Р°РІР»РµРЅР°"))
                return
            except Exception:
                traceback.print_exc()
        # fallback РїСЂРѕСЃС‚Р°СЏ С„РѕСЂРјР°
        frm = ctk.CTkFrame(self.content)
        frm.pack(expand=True, fill="both", padx=20, pady=20)
        ctk.CTkLabel(frm, text="Р‘С‹СЃС‚СЂР°СЏ Р·Р°РїРёСЃСЊ (fallback)", font=ctk.CTkFont(size=16, weight="bold")).pack(pady=8)
        ctk.CTkLabel(frm, text="Р•СЃР»Рё РµСЃС‚СЊ QuickEntryWindow вЂ” РѕРЅР° РѕС‚РєСЂРѕРµС‚СЃСЏ РІРјРµСЃС‚Рѕ СЌС‚РѕРіРѕ СЌРєСЂР°РЅР°.").pack(pady=8)

    def _show_employees(self):
        # РћС‚РєСЂС‹С‚СЊ EmployeesWindow (РµСЃР»Рё РµСЃС‚СЊ), РёРЅР°С‡Рµ РїРѕРєР°Р·Р°С‚СЊ С‚Р°Р±Р»РёС†Сѓ РёР· Р‘Р”
        if EmployeesWindow is not None:
            try:
                EmployeesWindow(self.content, self.db)
                return
            except Exception:
                traceback.print_exc()
        # fallback: РІС‹РІРµСЃС‚Рё СЃРїРёСЃРѕРє РїРѕР»СЊР·РѕРІР°С‚РµР»РµР№
        frm = ctk.CTkFrame(self.content)
        frm.pack(expand=True, fill="both", padx=12, pady=12)
        ctk.CTkLabel(frm, text="РЎРѕС‚СЂСѓРґРЅРёРєРё (fallback)", font=ctk.CTkFont(size=16, weight="bold")).pack(pady=8)
        try:
            # РїРѕРїС‹С‚РєР° РїРѕР»СѓС‡РёС‚СЊ РїРѕР»СЊР·РѕРІР°С‚РµР»РµР№ С‡РµСЂРµР· РјРµС‚РѕРґ Р‘Р” РёР»Рё SQL
            users = []
            if hasattr(self.db, "get_users"):
                users = self.db.get_users()
            else:
                cur = getattr(self.db, "cursor", None)
                conn = getattr(self.db, "conn", None)
                if cur is None and conn is not None:
                    cur = conn.cursor()
                if cur is not None:
                    cur.execute("SELECT id, username, full_name FROM users ORDER BY id ASC")
                    users = [dict(r) for r in cur.fetchall()]
            txt = ctk.CTkTextbox(frm)
            txt.pack(expand=True, fill="both", padx=6, pady=6)
            for u in users:
                if isinstance(u, dict):
                    txt.insert("end", f"{u.get('id')} | {u.get('username')} | {u.get('full_name')}\n")
                else:
                    txt.insert("end", str(u) + "\n")
        except Exception as e:
            traceback.print_exc()
            ctk.CTkLabel(frm, text="РќРµ СѓРґР°Р»РѕСЃСЊ Р·Р°РіСЂСѓР·РёС‚СЊ СЃРѕС‚СЂСѓРґРЅРёРєРѕРІ: " + str(e)).pack(pady=6)

    def _show_manager_dashboard(self):
        # Dashboard РјРµРЅРµРґР¶РµСЂР° вЂ” РѕС‚РєСЂС‹РІР°РµРј РјРѕРґР°Р»СЊРЅРѕРµ РѕРєРЅРѕ, РµСЃР»Рё РµСЃС‚СЊ СЂРµР°Р»РёР·Р°С†РёСЏ
        if ManagerDashboard is not None:
            try:
                ManagerDashboard(self.root)
                return
            except Exception:
                traceback.print_exc()
        messagebox.showinfo("Dashboard", "РћРєРЅРѕ РґР°С€Р±РѕСЂРґР° РјРµРЅРµРґР¶РµСЂР° РЅРµ РЅР°Р№РґРµРЅРѕ.")

    def _show_services(self):
        frm = ctk.CTkFrame(self.content)
        frm.pack(expand=True, fill="both", padx=12, pady=12)
        ctk.CTkLabel(frm, text="РЈСЃР»СѓРіРё", font=ctk.CTkFont(size=16, weight="bold")).pack(pady=8)
        try:
            services = []
            if hasattr(self.db, "get_services"):
                services = self.db.get_services()
            else:
                cur = getattr(self.db, "cursor", None)
                conn = getattr(self.db, "conn", None)
                if cur is None and conn is not None:
                    cur = conn.cursor()
                if cur is not None:
                    cur.execute("SELECT id, name, price FROM services ORDER BY id ASC")
                    services = [dict(r) for r in cur.fetchall()]
            for s in services:
                if isinstance(s, dict):
                    ctk.CTkLabel(frm, text=f"{s.get('id')} вЂ” {s.get('name')} вЂ” {s.get('price')}").pack(anchor="w", padx=8, pady=4)
                else:
                    ctk.CTkLabel(frm, text=str(s)).pack(anchor="w", padx=8, pady=4)
        except Exception as e:
            traceback.print_exc()
            ctk.CTkLabel(frm, text="РћС€РёР±РєР° РїРѕР»СѓС‡РµРЅРёСЏ СѓСЃР»СѓРі: " + str(e)).pack(pady=6)

    def run(self):
        self.root.mainloop()


# --------------------------
# App starter вЂ” РѕР±СЉРµРґРёРЅСЏРµС‚ Login -> MainApp
# --------------------------


class App:
    def __init__(self, db_path: Optional[str] = None):
        self.db = Database(db_path) if db_path else Database()
        # РїСЂРёРјРµРЅРёРј С‚РµРјСѓ (РµСЃР»Рё РёСЃРїРѕР»СЊР·СѓРµС‚СЃСЏ customtkinter)
        try:
            ctk.set_appearance_mode("System")
            ctk.set_default_color_theme("blue")
        except Exception:
            pass

        self.root = ctk.CTk()
        self.root.geometry("420x380")
        self.root.title("Barber App вЂ” Р’С…РѕРґ / Р РµРіРёСЃС‚СЂР°С†РёСЏ")

        # С†РµРЅС‚СЂРёСЂСѓРµРј РѕРєРЅРѕ РїРѕ СЌРєСЂР°РЅСѓ (РїРѕРїС‹С‚РєР°, Р±РµР· РєСЂРёС‚РёС‡РЅРѕСЃС‚Рё)
        try:
            self.root.eval('tk::PlaceWindow %s center' % self.root.winfo_toplevel())
        except Exception:
            pass

        # РєРѕРЅС‚РµР№РЅРµСЂ РґР»СЏ login frame
        self.container = ctk.CTkFrame(self.root)
        self.container.pack(expand=True, fill="both", padx=12, pady=12)

        self.login_frame = LoginFrame(self.container, self.db, on_login=self._on_login)
        self.login_frame.pack(expand=True, fill="both")

    def _on_login(self, user: Dict[str, Any]):
        # Р—Р°РєСЂС‹РІР°РµРј РѕРєРЅРѕ РІС…РѕРґР° Рё РѕС‚РєСЂС‹РІР°РµРј РіР»Р°РІРЅРѕРµ РѕРєРЅРѕ
        try:
            self.root.destroy()
        except Exception:
            pass
        try:
            mw = MainAppWindow(user, self.db)
            mw.run()
        except Exception:
            traceback.print_exc()
            messagebox.showerror("РћС€РёР±РєР°", "РќРµ СѓРґР°Р»РѕСЃСЊ РѕС‚РєСЂС‹С‚СЊ РіР»Р°РІРЅРѕРµ РѕРєРЅРѕ")

    def run(self):
        self.root.mainloop()


# --------------------------
# Р•СЃР»Рё Р·Р°РїСѓС‰РµРЅРѕ РєР°Рє main вЂ” СЃС‚Р°СЂС‚СѓРµРј РїСЂРёР»РѕР¶РµРЅРёРµ
# --------------------------
if __name__ == "__main__":
    try:
        App().run()
    except Exception:
        traceback.print_exc()
        messagebox.showerror("РћС€РёР±РєР°", "РќРµ СѓРґР°Р»РѕСЃСЊ Р·Р°РїСѓСЃС‚РёС‚СЊ РїСЂРёР»РѕР¶РµРЅРёРµ. РџСЂРѕРІРµСЂСЊС‚Рµ Р»РѕРіРё.")


import customtkinter as ctk
from tkinter import ttk, messagebox
from database.db_manager import Database
from gui.windows.export_window import ExportWindow

class ManagerDashboard(ctk.CTkToplevel):
    """
    Dashboard РјРµРЅРµРґР¶РµСЂР°: С‚Р°Р±Р»РёС†Р° + С„РёР»СЊС‚СЂС‹ + СѓРґР°Р»РµРЅРёРµ Р·Р°РїРёСЃРё + СЌРєСЃРїРѕСЂС‚.
    """
    def __init__(self, parent):
        super().__init__(parent)
        self.title("Dashboard РјРµРЅРµРґР¶РµСЂР°")
        self.geometry("1000x600")
        self.db = Database()

        top = ctk.CTkFrame(self)
        top.pack(fill="x", padx=10, pady=6)

        ctk.CTkLabel(top, text="РЎ:").pack(side="left")
        self.start_entry = ctk.CTkEntry(top, width=120)
        self.start_entry.pack(side="left", padx=4)

        ctk.CTkLabel(top, text="РџРѕ:").pack(side="left")
        self.end_entry = ctk.CTkEntry(top, width=120)
        self.end_entry.pack(side="left", padx=4)

        ctk.CTkLabel(top, text="РњР°СЃС‚РµСЂ (ID):").pack(side="left")
        self.master_entry = ctk.CTkEntry(top, width=80)
        self.master_entry.pack(side="left", padx=4)

        ctk.CTkButton(top, text="Р¤РёР»СЊС‚СЂРѕРІР°С‚СЊ", command=self.refresh).pack(side="left", padx=6)
        ctk.CTkButton(top, text="РРєСЃРїРѕСЂС‚", command=lambda: ExportWindow(self)).pack(side="left", padx=6)
        ctk.CTkButton(top, text="Р—Р°РєСЂС‹С‚СЊ", command=self.destroy).pack(side="right", padx=6)

        center = ctk.CTkFrame(self)
        center.pack(fill="both", expand=True, padx=10, pady=6)

        columns = ("id","date","username","amount","master_income","boss_income","desc")
        self.tree = ttk.Treeview(center, columns=columns, show="headings")

        for col in columns:
            self.tree.heading(col, text=col)
            self.tree.column(col, width=120)

        self.tree.pack(fill="both", expand=True)

        bottom = ctk.CTkFrame(self)
        bottom.pack(fill="x", padx=10, pady=6)

        ctk.CTkButton(bottom, text="РЈРґР°Р»РёС‚СЊ Р·Р°РїРёСЃСЊ", command=self.delete_record).pack(side="left")

        self.refresh()

    def refresh(self):
        for i in self.tree.get_children():
            self.tree.delete(i)

        query = """
        SELECT s.id, s.date, u.username, s.amount, s.master_income, s.boss_income, s.description
        FROM services s
        LEFT JOIN users u ON u.id = s.user_id
        """

        where = []
        params = []

        if self.start_entry.get().strip():
            where.append("date(s.date) >= date(?)")
            params.append(self.start_entry.get().strip())

        if self.end_entry.get().strip():
            where.append("date(s.date) <= date(?)")
            params.append(self.end_entry.get().strip())

        if self.master_entry.get().strip():
            where.append("s.user_id = ?")
            params.append(int(self.master_entry.get().strip()))

        if where:
            query += " WHERE " + " AND ".join(where)

        query += " ORDER BY s.date DESC"

        cur = self.db.cursor
        cur.execute(query, tuple(params))
        rows = cur.fetchall()

        for r in rows:
            try:
                self.tree.insert("", "end", values=(
                    r["id"], r["date"], r["username"],
                    r["amount"], r["master_income"],
                    r["boss_income"], r["master_income"]
                ))
            except:
                self.tree.insert("", "end", values=list(r))

    def delete_record(self):
        sel = self.tree.selection()
        if not sel:
            messagebox.showwarning("РћС€РёР±РєР°", "Р’С‹Р±РµСЂРёС‚Рµ Р·Р°РїРёСЃСЊ")
            return

        item = self.tree.item(sel[0])
        rid = item["values"][0]

        if not messagebox.askyesno("РџРѕРґС‚РІРµСЂР¶РґРµРЅРёРµ", f"РЈРґР°Р»РёС‚СЊ Р·Р°РїРёСЃСЊ {rid}?"):
            return

        try:
            cur = self.db.cursor
            cur.execute("DELETE FROM services WHERE id=?", (rid,))
            self.db.conn.commit()
            self.refresh()
        except Exception as e:
            messagebox.showerror("РћС€РёР±РєР°", str(e))


