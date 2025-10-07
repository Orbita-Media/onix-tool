# tabs/pricing_tab.py
"""
Module for the Pricing tab of BoD MasteringOrder Generator.
Handles the EUR price entry and notifies a callback for international suggestions.
Place this file in the folder `tabs/`.
"""
import tkinter as tk
from tkinter import ttk, messagebox
import re

class PricingTab:
    def __init__(self, parent, on_price_update=None):
        """
        parent: ttk.Frame from the Notebook where this tab lives.
        on_price_update: function accepting a float (EUR price) for callbacks.
        """
        self.frame = parent
        self.on_price_update = on_price_update
        self._build_ui()

    def _build_ui(self):
        # Rahmen um das Preis-Feld
        pf = ttk.LabelFrame(self.frame, text='Price (EUR)')
        pf.pack(fill='x', padx=10, pady=10)
        pf.columnconfigure(1, weight=1)

        # Label + EUR entry
        ttk.Label(pf, text='EUR:*').grid(row=0, column=0, sticky='e', padx=5, pady=5)
        self.eur_entry = ttk.Entry(pf, width=12)
        # nur Ziffern, optional ein Komma/Punkt, max. 2 Nachkommastellen
        vcmd = (pf.register(self._validate_price), '%P')
        self.eur_entry.config(validate='key', validatecommand=vcmd)
        self.eur_entry.grid(row=0, column=1, sticky='w', padx=5, pady=5)

        # Callback bei Fokus-Verlust und Enter
        self.eur_entry.bind('<FocusOut>', self._price_changed)
        self.eur_entry.bind('<Return>',    self._price_changed)

    def _validate_price(self, P):
        """
        Erlaubt nur:
        - Ziffern
        - optional ein Komma oder Punkt
        - bis zu zwei Nachkommastellen
        """
        if P == "":
            return True
        pattern = r'^\d*(?:[.,]\d{0,2})?$'
        return re.match(pattern, P) is not None

    def _price_changed(self, event):
        # Komma → Punkt normalisieren
        val = self.eur_entry.get().replace(',', '.').strip()
        # nur formatieren, wenn tatsächlich etwas eingegeben wurde
        if not val:
            return
        # float-Conversion und auf zwei Stellen formatieren
        try:
            eur = float(val)
        except ValueError:
            messagebox.showerror(
                'Ungültiger Preis',
                'Bitte nur Zahlen mit Komma oder Punkt eingeben (z.B. 15,90).'
            )
            self.eur_entry.delete(0, tk.END)
            return
        formatted = f"{eur:.2f}"
        self.eur_entry.delete(0, tk.END)
        self.eur_entry.insert(0, formatted)
        # Callback auslösen
        if self.on_price_update:
            self.on_price_update(eur)

    def get_price_eur(self) -> str:
        """
        Gibt den eingegebenen EUR-Preis als String zurück
        (oder '' wenn leer/ungültig).
        """
        val = self.eur_entry.get().strip()
        # Hier könnte man noch prüfen, ob es ein korrektes Format ist
        return val
