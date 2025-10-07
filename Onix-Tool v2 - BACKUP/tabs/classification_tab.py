# tabs/classification_tab.py
"""
Module for the Classification tab of BoD MasteringOrder Generator.
Place this file in the folder `tabs/`.
"""
import tkinter as tk
from tkinter import ttk

class ClassificationTab:
    def __init__(self, parent, wgs_codes, bisac_codes):
        """
        parent: ttk.Frame from the Notebook where this tab lives.
        wgs_codes: dict from JSON warengruppe_codes.json
        bisac_codes: dict from JSON bisac_codes.json
        After initialization, selections are in self.selected_wgs, self.selected_bisac,
        """
        self.frame = parent
        self.wgs = wgs_codes
        self.bisac = bisac_codes
        self.selected_wgs = []
        self.selected_bisac = []
        # Maps for age codes and languages
        self.age_map = {
            '0-3 Jahre': '0', '3-5 Jahre': '3', '5-8 Jahre': '5',
            '8-12 Jahre': '8', 'ab 12 Jahre': '12'
        }
        self.lang_map = {'Deutsch': 'de', 'Englisch': 'en', 'Französisch': 'fr', 'Spanisch': 'es'}
        # Build UI
        self._build_ui()

    def _build_ui(self):
        f = self.frame
        # Configure columns for full width
        f.columnconfigure(0, weight=1)
        f.columnconfigure(1, weight=1)

        # WGS panel
        ttk.Label(f, text='WGS').grid(row=0, column=0, sticky='w', padx=5, pady=(5,4))
        self.wgs_search_var = tk.StringVar()
        wgs_search = ttk.Entry(f, textvariable=self.wgs_search_var)
        wgs_search.grid(row=1, column=0, sticky='ew', padx=5, pady=(0,4))
        self.wgs_search_var.trace('w', lambda *args: self._filter('WGS'))

        wgs_frame = ttk.Frame(f)
        wgs_frame.grid(row=2, column=0, sticky='nsew', padx=5, pady=(0,4))
        wgs_frame.columnconfigure(0, weight=1)
        self.wgs_listbox = tk.Listbox(wgs_frame, height=6)
        self.wgs_listbox.grid(row=0, column=0, sticky='nsew')
        wgs_scroll = ttk.Scrollbar(wgs_frame, orient='vertical', command=self.wgs_listbox.yview)
        wgs_scroll.grid(row=0, column=1, sticky='ns')
        self.wgs_listbox.config(yscrollcommand=wgs_scroll.set)
        for code, desc in self.wgs.items():
            self.wgs_listbox.insert('end', f"{code} | {desc}")

        ttk.Button(f, text='Übernehmen', command=lambda: self._add('WGS'))\
            .grid(row=3, column=0, padx=5, pady=(4,4))
        self.wgs_tree = ttk.Treeview(f, columns=['Code','Description'], show='headings', height=4)
        for col,width in [('Code',100),('Description',200)]:
            self.wgs_tree.heading(col, text=col)
            self.wgs_tree.column(col, width=width)
        self.wgs_tree.grid(row=4, column=0, sticky='nsew', padx=5, pady=(0,4))
        ttk.Button(f, text='Löschen', command=lambda: self._remove('WGS'))\
            .grid(row=5, column=0, padx=5, pady=(0,4))
        self.wgs_tree.bind('<Button-1>', self._tree_toggle('WGS'))

        # Altersgruppe WGS + Code
        wgs_age = ttk.Frame(f)
        wgs_age.grid(row=6, column=0, sticky='w', padx=5, pady=(4,4))
        ttk.Label(wgs_age, text='Altersgruppe:').pack(side='left')
        self.age_wgs = ttk.Combobox(wgs_age, values=list(self.age_map.keys()), state='disabled', width=15)
        self.age_wgs.pack(side='left', padx=(5,0))
        self.age_wgs.bind('<<ComboboxSelected>>', lambda e: self._update_age_code('WGS'))
        ttk.Label(wgs_age, text='Code:').pack(side='left', padx=(10,0))
        self.age_wgs_code = ttk.Entry(wgs_age, width=5, state='disabled')
        self.age_wgs_code.pack(side='left', padx=(5,0))

        # BISAC panel
        ttk.Label(f, text='BISAC').grid(row=0, column=1, sticky='w', padx=5, pady=(5,4))
        self.bisac_search_var = tk.StringVar()
        bisac_search = ttk.Entry(f, textvariable=self.bisac_search_var)
        bisac_search.grid(row=1, column=1, sticky='ew', padx=5, pady=(0,4))
        self.bisac_search_var.trace('w', lambda *args: self._filter('BISAC'))

        bisac_frame = ttk.Frame(f)
        bisac_frame.grid(row=2, column=1, sticky='nsew', padx=5, pady=(0,4))
        bisac_frame.columnconfigure(0, weight=1)
        self.bisac_listbox = tk.Listbox(bisac_frame, height=6)
        self.bisac_listbox.grid(row=0, column=0, sticky='nsew')
        bisac_scroll = ttk.Scrollbar(bisac_frame, orient='vertical', command=self.bisac_listbox.yview)
        bisac_scroll.grid(row=0, column=1, sticky='ns')
        self.bisac_listbox.config(yscrollcommand=bisac_scroll.set)
        for code, desc in self.bisac.items():
            self.bisac_listbox.insert('end', f"{code} | {desc}")

        ttk.Button(f, text='Übernehmen', command=lambda: self._add('BISAC'))\
            .grid(row=3, column=1, padx=5, pady=(4,4))
        self.bisac_tree = ttk.Treeview(f, columns=['Code','Description'], show='headings', height=4)
        for col,width in [('Code',100),('Description',200)]:
            self.bisac_tree.heading(col, text=col)
            self.bisac_tree.column(col, width=width)
        self.bisac_tree.grid(row=4, column=1, sticky='nsew', padx=5, pady=(0,4))
        ttk.Button(f, text='Löschen', command=lambda: self._remove('BISAC'))\
            .grid(row=5, column=1, padx=5, pady=(0,4))
        self.bisac_tree.bind('<Button-1>', self._tree_toggle('BISAC'))

        # Altersgruppe BISAC + Code
        bisac_age = ttk.Frame(f)
        bisac_age.grid(row=6, column=1, sticky='w', padx=5, pady=(4,4))
        ttk.Label(bisac_age, text='Altersgruppe:').pack(side='left')
        self.age_bisac = ttk.Combobox(bisac_age, values=list(self.age_map.keys()), state='disabled', width=15)
        self.age_bisac.pack(side='left', padx=(5,0))
        self.age_bisac.bind('<<ComboboxSelected>>', lambda e: self._update_age_code('BISAC'))
        ttk.Label(bisac_age, text='Code:').pack(side='left', padx=(10,0))
        self.age_bisac_code = ttk.Entry(bisac_age, width=5, state='disabled')
        self.age_bisac_code.pack(side='left', padx=(5,0))

        # Sprache
        ttk.Label(f, text='Sprache:').grid(row=7, column=0, sticky='e', padx=5, pady=(8,5))
        self.lang_cb = ttk.Combobox(f, values=list(self.lang_map.keys()), state='readonly', width=15)
        self.lang_cb.set('Spanisch')
        self.lang_cb.grid(row=7, column=1, sticky='w', padx=5, pady=(8,5))

    def _tree_toggle(self, label):
        def _handler(event):
            tree = self.wgs_tree if label=='WGS' else self.bisac_tree
            item = tree.identify_row(event.y)
            if item in tree.selection():
                tree.selection_remove(item)
                return 'break'
        return _handler

    def _filter(self, label):
        term = getattr(self, f"{label.lower()}_search_var").get().lower()
        lb = getattr(self, f"{label.lower()}_listbox")
        data = self.wgs if label=='WGS' else self.bisac
        lb.delete(0, 'end')
        for c, d in data.items():
            if term in c.lower() or term in d.lower():
                lb.insert('end', f"{c} | {d}")

    def _add(self, label):
        lb = getattr(self, f"{label.lower()}_listbox")
        sel = lb.curselection()
        if not sel: return
        code, desc = lb.get(sel[0]).split(' | ',1)
        tree = getattr(self, f"{label.lower()}_tree")
        sel_list = self.selected_wgs if label=='WGS' else self.selected_bisac
        if (code, desc) not in sel_list:
            tree.insert('', 'end', values=(code, desc))
            sel_list.append((code, desc))
        self._update_age_state()

    def _remove(self, label):
        tree = getattr(self, f"{label.lower()}_tree")
        sel_list = self.selected_wgs if label=='WGS' else self.selected_bisac
        for iid in tree.selection():
            code, val = tree.item(iid, 'values')[:2]
            tree.delete(iid)
            sel_list[:] = [x for x in sel_list if x[0] != code]
        # **kein direktes Leeren mehr hier** – das macht jetzt _update_age_state()
        self._update_age_state()

    def _update_age_state(self):
        need_w = any('Kinder' in desc for _, desc in self.selected_wgs)
        need_b = any(code.startswith(('JUV','YAF')) for code, _ in self.selected_bisac)
        if need_w:
            self.age_wgs.config(state='readonly')
        else:
            # **Erst wenn wirklich keine Kinder-Kategorien mehr da sind, leeren und deaktivieren**
            self.age_wgs.set('')
            self.age_wgs.config(state='disabled')
            self.age_wgs_code.config(state='normal')
            self.age_wgs_code.delete(0, 'end')
            self.age_wgs_code.config(state='disabled')

        if need_b:
            self.age_bisac.config(state='readonly')
        else:
            self.age_bisac.set('')
            self.age_bisac.config(state='disabled')
            self.age_bisac_code.config(state='normal')
            self.age_bisac_code.delete(0, 'end')
            self.age_bisac_code.config(state='disabled')

    def _update_age_code(self, label):
        if label == 'WGS':
            sel = self.age_wgs.get()
            code = self.age_map.get(sel, '')
            self.age_wgs_code.config(state='normal')
            self.age_wgs_code.delete(0, 'end')
            self.age_wgs_code.insert(0, code)
            self.age_wgs_code.config(state='disabled')
        else:
            sel = self.age_bisac.get()
            code = self.age_map.get(sel, '')
            self.age_bisac_code.config(state='normal')
            self.age_bisac_code.delete(0, 'end')
            self.age_bisac_code.insert(0, code)
            self.age_bisac_code.config(state='disabled')

    def get_selected(self):
        """
        Returns selected codes and age codes and language.
        """
        wgs_codes = [code for code, _ in self.selected_wgs]
        bisac_codes = [code for code, _ in self.selected_bisac]
        return {
            'WGS':       wgs_codes,
            'BISAC':     bisac_codes,
            'AgeWGS':    self.age_wgs_code.get(),
            'AgeBISAC':  self.age_bisac_code.get(),
            'Language':  self.lang_map.get(self.lang_cb.get())
        }
