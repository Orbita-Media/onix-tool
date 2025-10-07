# tabs/international_tab.py
"""
Module for the International tab of BoD MasteringOrder Generator.
Handles Internationaler Vertrieb checkbox, optional EAN + "Bisheriger Preis",
currency entries (USD, GBP, AUD), price suggestion labels and apply buttons.
Place this file in the folder `tabs/`.
"""
import tkinter as tk
from tkinter import ttk
import math

class InternationalTab:
    def __init__(self, parent):
        """
        parent: ttk.Frame from the Notebook where this tab lives.
        """
        self.frame = parent
        self.intl_var = tk.BooleanVar(value=True)

        # store widgets
        self.chk = None
        self.ean_frame = None
        self.ean_entry = None
        self.prev_price_label = None
        self.prev_price = None
        self.entries = {}
        self.buttons = {}
        self.suggestion_labels = {}
        self.suggestion_values = {}

        self._build_ui()

    def _build_ui(self):
        # Checkbox
        self.chk = ttk.Checkbutton(
            self.frame,
            text='Internationaler Vertrieb',
            variable=self.intl_var,
            command=self._toggle_enabled
        )
        self.chk.grid(row=0, column=0, sticky='w', padx=10, pady=(10,5))

        # EAN frame (hidden by default)
        self.ean_frame = ttk.Frame(self.frame)
        ttk.Label(self.ean_frame, text='EAN:').grid(row=0, column=0, sticky='e', padx=5)
        vcmd = (self.frame.register(self._validate_ean), '%P')
        self.ean_entry = ttk.Entry(self.ean_frame, width=15, validate='key', validatecommand=vcmd)
        self.ean_entry.grid(row=0, column=1, padx=5)
        self.ean_frame.grid(row=1, column=0, sticky='w', padx=10, pady=(0,5))

        # Preise frame
        pf = ttk.LabelFrame(self.frame, text='Preise')
        pf.grid(row=2, column=0, sticky='ew', padx=10, pady=5)
        pf.columnconfigure(1, weight=1)

        # Bisheriger Preis (EUR)
        self.prev_price_label = ttk.Label(pf, text='Bisheriger Preis (EUR):')
        self.prev_price_label.grid(row=0, column=0, sticky='e', padx=5, pady=3)
        self.prev_price = ttk.Entry(pf, width=12)
        self.prev_price.grid(row=0, column=1, padx=5, pady=3, sticky='ew')
        self.prev_price.bind('<FocusOut>', lambda e: self._on_prev_price())
        self.prev_price.bind('<Return>',    lambda e: self._on_prev_price())

        # Currency rows
        for i, cur in enumerate(['USD','GBP','AUD'], start=1):
            ttk.Label(pf, text=f'Preis {cur}:').grid(row=i, column=0, sticky='e', padx=5, pady=3)
            ent = ttk.Entry(pf, width=12)
            ent.grid(row=i, column=1, padx=5, pady=3, sticky='ew')
            ent.bind('<FocusOut>', lambda e, c=cur: self._normalize_price(c))
            ent.bind('<Return>',    lambda e, c=cur: self._normalize_price(c))
            self.entries[cur] = ent

            lbl = ttk.Label(pf, text='Vorschlag: -')
            lbl.grid(row=i, column=2, sticky='w', padx=5, pady=3)
            self.suggestion_labels[cur] = lbl

            btn = ttk.Button(pf, text='Übernehmen', width=12,
                             command=lambda c=cur: self._apply_suggestion(c))
            btn.grid(row=i, column=3, padx=5, pady=3)
            self.buttons[cur] = btn

        self._toggle_enabled()

    def _toggle_enabled(self):
        state = 'normal' if self.intl_var.get() else 'disabled'
        for w in (self.ean_entry, self.prev_price):
            w.config(state=state)
        for ent in self.entries.values():
            ent.config(state=state)
        for lbl in self.suggestion_labels.values():
            lbl.config(state=state)
        for btn in self.buttons.values():
            btn.config(state=state)

    def lock_mode(self):
        self.intl_var.set(True)
        self.chk.config(state='disabled')
        self._toggle_enabled()

    def unlock_mode(self):
        self.chk.config(state='normal')
        self._toggle_enabled()

    def show_addintl_fields(self):
        self.ean_frame.grid()
        self.prev_price_label.grid()
        self.prev_price.grid()

    def hide_addintl_fields(self):
        self.ean_frame.grid_remove()
        self.prev_price_label.grid_remove()
        self.prev_price.grid_remove()

    def _validate_ean(self, P):
        if P=='':
            return True
        return P.isdigit() and len(P)<=13

    def _on_prev_price(self):
        txt = self.prev_price.get().replace(',', '.')
        self.prev_price.delete(0, tk.END)
        self.prev_price.insert(0, txt)
        try:
            eur = float(txt)
        except ValueError:
            return
        self.update_suggestions(eur)

    def update_suggestions(self, eur: float):
        # USD
        usd = math.ceil(eur*1.42) - 0.01
        self._set_suggestion('USD', usd)
        # GBP
        gbp_val = eur*1.07
        c1 = math.floor(gbp_val)-0.01
        c2 = math.ceil(gbp_val)-0.01
        gbp = c1 if abs(c1-gbp_val)<=abs(c2-gbp_val) else c2
        self._set_suggestion('GBP', gbp)
        # AUD
        aud = math.ceil(eur*2.22)
        self._set_suggestion('AUD', aud)

    def _set_suggestion(self, currency, value):
        self.suggestion_values[currency] = value
        lbl = self.suggestion_labels.get(currency)
        if lbl:
            lbl.config(text=f'Vorschlag: {value:.2f}')

    def _normalize_price(self, currency):
        ent = self.entries.get(currency)
        txt = ent.get().replace(',', '.')
        ent.delete(0, tk.END)
        ent.insert(0, txt)

    def _apply_suggestion(self, currency):
        val = self.suggestion_values.get(currency)
        if val is None:
            return
        ent = self.entries[currency]
        ent.delete(0, tk.END)
        ent.insert(0, f'{val:.2f}')

    def is_enabled(self) -> bool:
        return self.intl_var.get()

    def get_prices(self) -> dict:
        return {cur: self.entries[cur].get().strip() for cur in self.entries}

    def get_data(self):
        """
        Return the entered EAN and previous EUR price.
        """
        return {
            'EAN': self.ean_entry.get().strip(),
            'PrevPrice': self.prev_price.get().strip()
        }

