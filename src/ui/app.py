"""
app.py
──────
Main application entry point.

Typical usage (from project root, with your real controller):

    from controller.PredictionController import PredictionController
    from UI.app import HeartApp

    HeartApp(controller=PredictionController()).run()

For UI development without the controller:

    from UI.app import HeartApp
    HeartApp().run()            # uses a built-in stub controller
"""

import sys
import os
import tkinter as tk
from tkinter import ttk

# Allow sibling imports regardless of where the script is launched from
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from ui.theme import COLORS, FONTS, DIMS
from ui.components.nav_sidebar import NavSidebar
from ui.components.status_bar  import StatusBar
from ui.views.single_prediction_view import SinglePredictionView
from ui.views.bulk_prediction_view   import BulkPredictionView
from ui.views.performance_view       import PerformanceView
from ui.views.history_view           import HistoryView
from ui.views.statistics_view        import StatisticsView


class HeartApp:
    """
    Root application window.

    Responsibilities
    ────────────────
    • Build the three-zone layout: sidebar | content | status bar
    • Instantiate all views once and stack them with place()
    • Handle navigation (raise active view, update sidebar highlight)
    • Forward the notify callback to all views
    """

    # (route_key, sidebar_label, ViewClass)
    _NAV_ITEMS = [
        ("predict",    "🫀  Predict",       SinglePredictionView),
        ("bulk",       "📋  Bulk Predict",  BulkPredictionView),
        ("evaluate",   "📊  Evaluate",      PerformanceView),
        ("history",    "🕐  History",       HistoryView),
        ("statistics", "📈  Statistics",    StatisticsView),
    ]

    def __init__(self, controller=None):
        self.controller = controller or _StubController()

        # ── Root window ──────────────────────────────────────────────────────
        self.root = tk.Tk()
        self.root.title("CardioAI — Heart Disease Prediction System")
        self.root.geometry("1280x780")
        self.root.minsize(960, 620)
        self.root.configure(bg=COLORS["window_bg"])
        _apply_ttk_styles(self.root)

        # ── Build layout ─────────────────────────────────────────────────────
        self._build_layout()

        # ── Start on predict view ────────────────────────────────────────────
        self._active_key: str | None = None
        self.navigate("predict")

    # ── Layout construction ──────────────────────────────────────────────────────
    def _build_layout(self):
        # Left: sidebar (fixed width, full height)
        self.sidebar = NavSidebar(
            self.root,
            items=[(k, lbl) for k, lbl, _ in self._NAV_ITEMS],
            on_select=self.navigate,
        )
        self.sidebar.pack(side=tk.LEFT, fill=tk.Y)

        # Right: column containing content + status bar
        right_col = tk.Frame(self.root, bg=COLORS["window_bg"])
        right_col.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)

        # Status bar pinned to bottom
        self.status_bar = StatusBar(right_col)
        self.status_bar.pack(side=tk.BOTTOM, fill=tk.X)

        # Content host — views are placed on top of each other here
        self.content = tk.Frame(right_col, bg=COLORS["window_bg"])
        self.content.pack(fill=tk.BOTH, expand=True)

        # Instantiate every view (hidden until navigated to)
        self._views: dict[str, tk.Frame] = {}
        for key, _, ViewClass in self._NAV_ITEMS:
            view = ViewClass(
                self.content,
                controller=self.controller,
                notify=self.status_bar.notify,
            )
            # Stack all views at the same position; tkraise() shows the top one
            view.place(relx=0, rely=0, relwidth=1, relheight=1)
            self._views[key] = view

    # ── Navigation ───────────────────────────────────────────────────────────────
    def navigate(self, key: str):
        """Raise `key` view, update sidebar, and call on_show() if defined."""
        if key == self._active_key:
            return
        self._active_key = key
        self._views[key].tkraise()
        self.sidebar.set_active(key)

        view = self._views[key]
        if hasattr(view, "on_show"):
            view.on_show()

    # ── Run / quit ───────────────────────────────────────────────────────────────
    def run(self):
        """Start the Tk event loop (blocking)."""
        self.root.mainloop()

    def quit(self):
        self.root.destroy()


# ── ttk style registration ────────────────────────────────────────────────────────
def _apply_ttk_styles(root: tk.Tk):
    """Configure all ttk widget styles for the application."""
    style = ttk.Style(root)
    style.theme_use("clam")

    C = COLORS
    F = FONTS
    D = DIMS

    # ── Base reset ────────────────────────────────────────────────────────────
    style.configure(".", background=C["window_bg"], foreground=C["text_primary"],
                    font=F["body"], borderwidth=0, relief="flat",
                    focuscolor=C["primary"])

    # ── TFrame ────────────────────────────────────────────────────────────────
    style.configure("TFrame",         background=C["window_bg"])
    style.configure("Surface.TFrame", background=C["surface"])

    # ── TLabel ────────────────────────────────────────────────────────────────
    style.configure("TLabel",
                    background=C["window_bg"], foreground=C["text_primary"])

    # ── Primary button (filled blue) ──────────────────────────────────────────
    style.configure("Primary.TButton",
                    background=C["primary"], foreground=C["primary_text"],
                    font=F["body_bold"], borderwidth=0, relief="flat",
                    padding=(D["btn_pad_x"], D["btn_pad_y"]))
    style.map("Primary.TButton",
              background=[("active",   C["primary_hover"]),
                          ("disabled", C["border_strong"])],
              foreground=[("disabled", C["text_muted"])])

    # ── Secondary button (outlined) ───────────────────────────────────────────
    style.configure("Secondary.TButton",
                    background=C["surface"], foreground=C["primary"],
                    font=F["body_bold"], borderwidth=1, relief="solid",
                    padding=(D["btn_pad_x"], D["btn_pad_y"]))
    style.map("Secondary.TButton",
              background=[("active", C["primary_light"])],
              bordercolor=[("focus", C["primary"]), ("!focus", C["border_strong"])])

    # ── Danger button (red) ───────────────────────────────────────────────────
    style.configure("Danger.TButton",
                    background=C["danger"], foreground="#FFFFFF",
                    font=F["body_bold"], borderwidth=0, relief="flat",
                    padding=(D["btn_pad_x"], D["btn_pad_y"]))
    style.map("Danger.TButton",
              background=[("active",   C["danger_hover"]),
                          ("disabled", C["border_strong"])],
              foreground=[("disabled", C["text_muted"])])

    # ── Coming-soon placeholder button ────────────────────────────────────────
    style.configure("ComingSoon.TButton",
                    background=C["border"], foreground=C["text_muted"],
                    font=F["body"], borderwidth=0, relief="flat",
                    padding=(D["btn_pad_x"], D["btn_pad_y"]))
    style.map("ComingSoon.TButton",
              background=[("active", C["border_strong"])])

    # ── TEntry ────────────────────────────────────────────────────────────────
    style.configure("TEntry",
                    fieldbackground=C["input_bg"],
                    foreground=C["text_primary"],
                    bordercolor=C["input_border"],
                    insertcolor=C["primary"],
                    padding=(8, 5))
    style.map("TEntry",
              bordercolor=[("focus", C["input_focus_border"]),
                           ("!focus", C["input_border"])],
              fieldbackground=[("disabled", C["input_disabled_bg"])],
              foreground=[("disabled", C["input_disabled_text"])])

    # ── TCombobox ─────────────────────────────────────────────────────────────
    style.configure("TCombobox",
                    fieldbackground=C["input_bg"],
                    foreground=C["text_primary"],
                    bordercolor=C["input_border"],
                    arrowcolor=C["text_secondary"],
                    padding=(8, 5))
    style.map("TCombobox",
              bordercolor=[("focus", C["input_focus_border"])],
              fieldbackground=[("disabled", C["input_disabled_bg"])],
              foreground=[("disabled", C["input_disabled_text"])])

    # ── Treeview ──────────────────────────────────────────────────────────────
    style.configure("Treeview",
                    background=C["surface"], fieldbackground=C["surface"],
                    foreground=C["text_primary"], font=F["body"],
                    rowheight=30, borderwidth=0)
    style.configure("Treeview.Heading",
                    background=C["table_header_bg"], foreground=C["table_header_fg"],
                    font=F["subheading"], borderwidth=0, relief="flat",
                    padding=(8, 6))
    style.map("Treeview",
              background=[("selected", C["table_select_bg"])],
              foreground=[("selected", C["table_select_fg"])])
    style.map("Treeview.Heading",
              background=[("active", C["border"])])

    # ── Scrollbar ─────────────────────────────────────────────────────────────
    style.configure("TScrollbar",
                    background=C["scrollbar"], bordercolor=C["window_bg"],
                    troughcolor=C["window_bg"], arrowcolor=C["text_muted"],
                    relief="flat")
    style.map("TScrollbar",
              background=[("active", C["text_muted"])])

    # ── Progressbar ───────────────────────────────────────────────────────────
    style.configure("TProgressbar",
                    troughcolor=C["border"], background=C["primary"], thickness=6)


# ── Development stub controller ─────────────────────────────────────────────────
class _StubController:
    """
    Drop-in stub used when no real controller is provided.
    Returns plausible dummy responses so the UI can be developed and tested
    without the ML backend.
    """

    import uuid as _uuid
    from datetime import datetime as _datetime

    def makePrediction(self, modelName, featureJson):
        return {
            "status": "success",
            "message": {
                "Id": str(self._uuid.uuid4()),
                "modelName": modelName,
                "featureVector": featureJson,
                "isMalignant": sum(featureJson.values()) % 2 == 0,
                "timeStamp": self._datetime.now().isoformat(),
            },
        }

    def makeBulkPredictions(self, modelName, filePath, dropColumn):
        import random, uuid
        from datetime import datetime
        return {
            "status": "success",
            "message": [
                {
                    "Id": str(uuid.uuid4()),
                    "modelName": modelName,
                    "featureVector": {},
                    "isMalignant": random.choice([True, False]),
                    "timeStamp": datetime.now().isoformat(),
                }
                for _ in range(5)
            ],
        }

    def calculatePerformance(self, modelName, filePath, dropColumn, targetColumn):
        return {
            "status": "success",
            "message": {
                "modelName": modelName,
                "accuracy":  0.8745,
                "precision": 0.8612,
                "recall":    0.8523,
            },
        }

    def getAllPredictions(self):
        return {"status": "success", "message": []}

    def getAllPaginatedPredictions(self, page, pageSize):
        return {"status": "success", "message": {"predictions": [], "predictionCount": 0}}

    def getPredictionsByNamePaginated(self, modelName, page, pageSize):
        return {"status": "success", "message": {"predictions": [], "predictionCount": 0}}

    def getPredictionsByModel(self, modelName):
        return {"status": "success", "message": []}

    def deletePrediction(self, predictionId):
        return {"status": "success", "message": True}

    def deleteAllPrediction(self):
        return {"status": "success", "message": True}

    def getStatistics(self):
        return {
            "status": "success",
            "message": {
                "stat": {"NaiveBayes": 25, "SVM": 18, "DecisionTree": 32},
                "totalCount": 75,
            },
        }