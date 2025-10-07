# tabs/product_tab.py
"""
Module for the Product tab of BoD MasteringOrder Generator.
Place this file in the folder `tabs/`.
"""
import tkinter as tk
from tkinter import ttk, messagebox
from datetime import datetime
from tkcalendar import DateEntry

class ProductTab:
    def __init__(self, parent):
        """
        parent: ttk.Frame from the Notebook where this tab lives.
        After initialization, the Entry and Text widgets are
        available in self.widgets dict for later XML export.
        """
        self.frame = parent
        self.widgets = {}
        self._build_ui()

    def _validate_ean(self, P):
        """Validate that EAN is digits up to 13 characters or empty."""
        return (P.isdigit() and len(P) <= 13) or P == ''

    def _on_ean_focusout(self, event):
        """Highlight EAN entry pink if invalid length or non-digit."""
        ent = self.widgets.get('EAN')
        if ent:
            val = ent.get().strip()
            ent.config(background='white' if len(val) == 13 and val.isdigit() else 'pink')

    def _validate_pub_date(self, event):
        """Validate that PublicationDate is in YYYYMMDD format."""
        ent = self.widgets.get('PublicationDate')
        if ent:
            val = ent.get().strip()
            try:
                datetime.strptime(val, '%Y%m%d')
                ent.config(background='white')
            except ValueError:
                ent.config(background='pink')
                messagebox.showerror('Formatfehler', 'PublicationDate muss im Format YYYYMMDD sein.')

    def _limit_blurb(self, widget):
        text = widget.get('1.0', 'end-1c')
        if len(text) > 4000:
            widget.delete('1.0', 'end')
            widget.insert('1.0', text[:4000])

    def _apply_size(self):
        mapping = {
            'A5':    (210, 148), 'A4':    (297, 210), '17x17': (170, 170),
            '17x22': (220, 170), '21x15': (150, 210), '19x27': (270, 190),
            '21x21': (210, 210)
        }
        sel = self.size_var.get()
        if sel in mapping:
            h, w = mapping[sel]
            self.widgets['Height'].delete(0, tk.END)
            self.widgets['Height'].insert(0, str(h))
            self.widgets['Width'].delete(0, tk.END)
            self.widgets['Width'].insert(0, str(w))

    def _pick_date(self, ent_pub, lbl_display):
        top = tk.Toplevel(self.frame)
        cal = DateEntry(top, date_pattern='dd.MM.yyyy')
        cal.pack(padx=10, pady=10)
        def set_pub():
            d = cal.get_date().strftime('%Y%m%d')
            d_disp = cal.get_date().strftime('%d.%m.%Y')
            ent_pub.delete(0, tk.END)
            ent_pub.insert(0, d)
            lbl_display.config(text=d_disp)
            top.destroy()
        ttk.Button(top, text='OK', command=set_pub).pack(pady=5)

    def _build_ui(self):
        f = self.frame; w = self.widgets
        # Buchdaten
        bf = ttk.LabelFrame(f, text='Buchdaten')
        bf.pack(fill='x', padx=5, pady=5)
        fields = [
            ('EAN', 'EAN:*', self._validate_ean, self._on_ean_focusout),
            ('Title', 'Titel:*', None, None),
            ('SubTitle', 'Untertitel', None, None),
            ('Serie', 'Buchreihe (optional)', None, None),
            ('PartNumber', 'Band (optional)', None, None),
            ('EditionNumber', 'Editionnummer', None, None)
        ]
        for i, (tag, label, vcmd, fo) in enumerate(fields):
            ttk.Label(bf, text=label).grid(row=i, column=0, sticky='e', padx=5, pady=2)
            if tag == 'EAN':
                reg = bf.register(vcmd)
                ent = ttk.Entry(bf, width=50, validate='key', validatecommand=(reg, '%P'))
                ent.bind('<FocusOut>', fo)
            else:
                ent = ttk.Entry(bf, width=50)
                if tag == 'EditionNumber': ent.insert(0, '1')
            ent.grid(row=i, column=1, sticky='ew', padx=5, pady=2)
            w[tag] = ent
        bf.columnconfigure(1, weight=1)

        # Beschreibung
        bb = ttk.LabelFrame(f, text='Beschreibung')
        bb.pack(fill='both', padx=5, pady=5)
        ent_bl = tk.Text(bb, width=120, height=15)
        sb = ttk.Scrollbar(bb, command=ent_bl.yview)
        ent_bl.configure(yscrollcommand=sb.set)
        ent_bl.pack(side='left', fill='both', expand=True)
        sb.pack(side='right', fill='y')
        ent_bl.bind('<KeyRelease>', lambda e, widget=ent_bl: self._limit_blurb(widget))
        w['Blurb'] = ent_bl

        # Maße & Seiten
        ms = ttk.LabelFrame(f, text='Maße & Seiten')
        ms.pack(fill='x', padx=5, pady=5)
        # Dimensions
        ttk.Label(ms, text='Height (mm):*').grid(row=0, column=0, sticky='e', padx=5, pady=2)
        e_h = ttk.Entry(ms, width=10); e_h.grid(row=0, column=1, sticky='w', padx=5)
        w['Height'] = e_h
        ttk.Label(ms, text='Width (mm):*').grid(row=1, column=0, sticky='e', padx=5, pady=2)
        e_w = ttk.Entry(ms, width=10); e_w.grid(row=1, column=1, sticky='w', padx=5)
        w['Width'] = e_w
        ttk.Label(ms, text='Pages:*').grid(row=2, column=0, sticky='e', padx=5, pady=2)
        e_p = ttk.Entry(ms, width=10); e_p.grid(row=2, column=1, sticky='w', padx=5)
        w['Pages'] = e_p
        # Format
        ttk.Label(ms, text='Format:').grid(row=0, column=2, sticky='e', padx=5)
        self.size_var = tk.StringVar()
        cb = ttk.Combobox(ms, textvariable=self.size_var,
            values=['A5','A4','17x17','17x22','21x15','19x27','21x21'],
            state='readonly', width=10)
        cb.grid(row=0, column=3, sticky='w', padx=5)
        ttk.Button(ms, text='Übernehmen', command=self._apply_size).grid(row=0, column=4, padx=5)
        # PublicationDate
        r = 3
        ttk.Label(ms, text='PublicationDate:*').grid(row=r, column=0, sticky='e', padx=5)
        ent_pub = ttk.Entry(ms, width=12); ent_pub.insert(0, datetime.today().strftime('%Y%m%d'))
        ent_pub.grid(row=r, column=1, sticky='w', padx=5)
        ent_pub.bind('<FocusOut>', self._validate_pub_date)
        w['PublicationDate'] = ent_pub
        lbl = ttk.Label(ms, text=datetime.today().strftime('%d.%m.%Y'), foreground='black')
        lbl.grid(row=r, column=2, padx=5)
        ttk.Button(ms, text='Datum wählen', command=lambda: self._pick_date(ent_pub, lbl)).grid(row=r, column=3, padx=5)
        # Coloured Pages
        ttk.Label(ms, text='ColouredPages:*').grid(row=r+1, column=0, sticky='e', padx=5, pady=2)
        e_cp = ttk.Entry(ms, width=5); e_cp.insert(0, '0'); e_cp.grid(row=r+1, column=1, sticky='w', padx=5)
        w['ColouredPages'] = e_cp
        ttk.Label(ms, text='ColouredPagesPosition').grid(row=r+2, column=0, sticky='e', padx=5)
        e_pos = ttk.Entry(ms, width=30); e_pos.grid(row=r+2, column=1, sticky='w', padx=5)
        w['ColouredPagesPosition'] = e_pos
        ms.columnconfigure(1, weight=1)

        # Optionen
        op = ttk.LabelFrame(f, text='Optionen')
        op.pack(fill='x', padx=5, pady=5)
        opts = [
            ('Quality:*', ['Standard','Premium'], 'Standard'),
            ('Paper:*', ['white','chamois'], 'white'),
            ('Binding:*', ['PB'], 'PB'),
            ('CoverDuplex:*', ['Yes','No'], 'No'),
            ('Finish:*', ['matt','glossy'], 'matt')
        ]
        for i,(label, vals, defv) in enumerate(opts):
            ttk.Label(op, text=label).grid(row=i, column=0, sticky='e', padx=5, pady=2)
            cbx = ttk.Combobox(op, values=vals, state='readonly', width=10)
            cbx.set(defv); cbx.grid(row=i, column=1, sticky='w', padx=5, pady=2)
            w[label.rstrip(':*')] = cbx

    def get_ordered_data(self):
        data = {}
        w = self.widgets
        data['Title'] = w['Title'].get().strip()
        data['SubTitle'] = w['SubTitle'].get().strip()
        # bisheriges Feld
        data['Serie'] = w['Serie'].get().strip()
        # zusätzlich key 'Series' für den XML-Export
        data['Series'] = data['Serie']
        data['PartNumber'] = w['PartNumber'].get().strip()
        data['EditionNumber'] = w['EditionNumber'].get().strip()
        data['PublicationDate'] = w['PublicationDate'].get().strip()
        data['Blurb'] = w['Blurb'].get('1.0','end-1c').strip()
        data['Height'] = w['Height'].get().strip()
        data['Width'] = w['Width'].get().strip()
        data['Pages'] = w['Pages'].get().strip()
        data['ColouredPages'] = w['ColouredPages'].get().strip()
        data['ColouredPagesPosition'] = w['ColouredPagesPosition'].get().strip()
        for key in ['Quality','Paper','Binding','CoverDuplex','Finish']:
            data[key] = w[key].get().strip()
        return data
