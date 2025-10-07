# tabs/header_tab.py
"""
Module for the Header tab of BoD MasteringOrder Generator.
Place this file in the folder `tabs/`.
"""
import tkinter as tk
from tkinter import ttk, messagebox
from datetime import datetime

class HeaderTab:
    def __init__(self, parent):
        """
        parent: ttk.Frame from the Notebook where this tab lives.
        After init, widgets stored in self.hdr for data extraction.
        """
        self.frame = parent
        self.hdr = {}
        self.defaults = {
            'FromCompany': 'Orbita Media GmbH',
            'FromCompanyNumber': '40501700',
            'FromEmail': 'kontakt@orbita-media.de'
        }
        self._build_ui()

    def _build_ui(self):
        # Main container
        f = self.frame
        f.columnconfigure(1, weight=1)

        # Frame for company info
        cf = ttk.LabelFrame(f, text='Absender')
        cf.grid(row=0, column=0, columnspan=3, sticky='ew', padx=10, pady=5)

        # FromCompany
        ttk.Label(cf, text='Firma:*').grid(row=0, column=0, sticky='e', padx=5, pady=2)
        ent_co = ttk.Entry(cf, width=40)
        ent_co.insert(0, self.defaults['FromCompany'])
        ent_co.grid(row=0, column=1, sticky='ew', padx=5, pady=2)
        ttk.Button(cf, text='Zurücksetzen', width=12,
                   command=lambda: self._reset_field(ent_co, self.defaults['FromCompany'])
        ).grid(row=0, column=2, padx=5)
        self.hdr['FromCompany'] = ent_co

        # FromCompanyNumber
        ttk.Label(cf, text='Kundennummer:*').grid(row=1, column=0, sticky='e', padx=5, pady=2)
        ent_num = ttk.Entry(cf, width=20)
        ent_num.insert(0, self.defaults['FromCompanyNumber'])
        ent_num.grid(row=1, column=1, sticky='w', padx=5, pady=2)
        cb_vals = ['40501700 (Spanien)', '11026617 (Frankreich)', '11022642 (Deutschland)']
        cb_num = ttk.Combobox(cf, values=cb_vals, state='readonly', width=25)
        sel = next((v for v in cb_vals if v.startswith(self.defaults['FromCompanyNumber'])), cb_vals[0])
        cb_num.set(sel)
        cb_num.grid(row=1, column=2, padx=5, pady=2)
        cb_num.bind('<<ComboboxSelected>>', lambda e: self._on_number_select(cb_num, ent_num))
        self.hdr['FromCompanyNumber'] = ent_num

        # FromPerson
        ttk.Label(cf, text='Ansprechpartner:').grid(row=2, column=0, sticky='e', padx=5, pady=2)
        ent_person = ttk.Entry(cf, width=40)
        ent_person.grid(row=2, column=1, sticky='ew', padx=5, pady=2)
        self.hdr['FromPerson'] = ent_person

        # FromEmail
        ttk.Label(cf, text='E-Mail:*').grid(row=3, column=0, sticky='e', padx=5, pady=2)
        ent_email = ttk.Entry(cf, width=40)
        ent_email.insert(0, self.defaults['FromEmail'])
        ent_email.grid(row=3, column=1, sticky='ew', padx=5, pady=2)
        ttk.Button(cf, text='Zurücksetzen', width=12,
                   command=lambda: self._reset_field(ent_email, self.defaults['FromEmail'])
        ).grid(row=3, column=2, padx=5)
        self.hdr['FromEmail'] = ent_email

        # Frame for date/time
        tf = ttk.LabelFrame(f, text='Zeitstempel')
        tf.grid(row=1, column=0, columnspan=3, sticky='ew', padx=10, pady=5)

        # SentDate
        ttk.Label(tf, text='Datum:*').grid(row=0, column=0, sticky='e', padx=5, pady=2)
        ent_date = ttk.Entry(tf, width=12)
        ent_date.insert(0, datetime.now().strftime('%Y%m%d'))
        ent_date.grid(row=0, column=1, sticky='w', padx=5, pady=2)
        ttk.Button(tf, text='Aktualisieren', width=12, command=self._update_date
        ).grid(row=0, column=2, padx=5)
        self.hdr['SentDate'] = ent_date

        # SentTime
        ttk.Label(tf, text='Uhrzeit:*').grid(row=1, column=0, sticky='e', padx=5, pady=2)
        ent_time = ttk.Entry(tf, width=6)
        ent_time.insert(0, datetime.now().strftime('%H:%M'))
        ent_time.grid(row=1, column=1, sticky='w', padx=5, pady=2)
        ttk.Button(tf, text='Aktualisieren', width=12, command=self._update_time
        ).grid(row=1, column=2, padx=5)
        self.hdr['SentTime'] = ent_time

        # Imprint
        self.imprint_label = ttk.Label(f, text='Imprint:')
        self.imprint_label.grid(row=2, column=0, sticky='e', padx=5, pady=2)
        self.imprint_cb = ttk.Combobox(
            f,
            values=['Lucid Page Media', 'Orbita Media GmbH'],
            state='readonly', width=30
        )
        self.imprint_cb.set('Lucid Page Media')
        self.imprint_cb.grid(row=2, column=1, sticky='w', padx=5, pady=2)
        self.hdr['Imprint'] = self.imprint_cb

    def hide_imprint(self):
        """Hide the Imprint field (for AddIntlDistribution mode)."""
        self.imprint_label.grid_remove()
        self.imprint_cb.grid_remove()

    def show_imprint(self):
        """Show the Imprint field (for Upload mode)."""
        self.imprint_label.grid()
        self.imprint_cb.grid()

    def _reset_field(self, entry, default):
        entry.delete(0, tk.END)
        entry.insert(0, default)

    def _on_number_select(self, combobox, entry):
        num = combobox.get().split()[0]
        entry.delete(0, tk.END)
        entry.insert(0, num)

    def _update_date(self):
        d = datetime.now().strftime('%Y%m%d')
        e = self.hdr.get('SentDate')
        if e:
            e.delete(0, tk.END)
            e.insert(0, d)

    def _update_time(self):
        t = datetime.now().strftime('%H:%M')
        e = self.hdr.get('SentTime')
        if e:
            e.delete(0, tk.END)
            e.insert(0, t)

    def get_data(self):
        data = {}
        for lab, w in self.hdr.items():
            val = w.get().strip()
            if lab in ['FromCompany','FromCompanyNumber','FromEmail','SentDate','SentTime'] and not val:
                messagebox.showerror('Fehler', f'Bitte {lab} ausfüllen')
                raise ValueError(lab)
            if lab == 'SentDate':
                try:
                    datetime.strptime(val, '%Y%m%d')
                except:
                    messagebox.showerror('Formatfehler', 'Datum YYYYMMDD nötig')
                    raise
            if lab == 'SentTime':
                try:
                    datetime.strptime(val, '%H:%M')
                except:
                    messagebox.showerror('Formatfehler', 'Uhrzeit HH:MM nötig')
                    raise
            if lab == 'FromPerson' and not val:
                continue
            data[lab] = val
        return data
