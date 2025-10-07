# tabs/contributor_tab.py
"""
Module for the Contributor tab of BoD MasteringOrder Generator.
Provides inline entry for contributors and a Treeview.
Place this file in the folder `tabs/`.
"""
import tkinter as tk
from tkinter import ttk, messagebox

class ContributorTab:
    def __init__(self, parent):
        """
        parent: ttk.Frame from the Notebook where this tab lives.
        After initialization, the Treeview and input widgets are available in self.
        """
        self.frame = parent
        self._build_ui()

    def _build_ui(self):
        f = self.frame
        # Entry panel
        entry_frame = ttk.LabelFrame(f, text='Neuen Contributor hinzufügen')
        entry_frame.grid(row=0, column=0, sticky='ew', padx=5, pady=5)
        labels = ['Role','LastName','FirstName','ISNI','ORCID','ShortBio']
        self.entries = {}
        for i, lab in enumerate(labels):
            ttk.Label(entry_frame, text=lab+':').grid(row=i, column=0, sticky='e', padx=5, pady=2)
            if lab == 'Role':
                cb = ttk.Combobox(entry_frame, values=[
                    'Author','Editor','Illustrator','Photographer','Drawer','VolumeEditor',
                    'SeriesEditor','FoundedBy','PrefaceBy','ForewordBy','IntroductionBy',
                    'AfterwordBy','NotesBy','CommentariesBy','ContributionsBy','RevisedBy',
                    'AdaptedBy','TranslatedBy','CompiledBy','SelectedBy'
                ], state='readonly', width=20)
                cb.set('Author')
                cb.grid(row=i, column=1, sticky='w', padx=5, pady=2)
                self.entries['Role'] = cb
            elif lab == 'ShortBio':
                # Larger text box for short bio
                txt = tk.Text(entry_frame, width=60, height=6)
                sb = ttk.Scrollbar(entry_frame, orient='vertical', command=txt.yview)
                txt.configure(yscrollcommand=sb.set)
                txt.grid(row=i, column=1, sticky='ew', padx=5, pady=2)
                sb.grid(row=i, column=2, sticky='ns', padx=(0,5), pady=2)
                self.entries['ShortBio'] = txt
            elif lab in ['ISNI','ORCID']:
                vcmd = (f.register(self._validate_code), '%P')
                ent = ttk.Entry(entry_frame, validate='key', validatecommand=vcmd, width=25)
                ent.grid(row=i, column=1, sticky='w', padx=5, pady=2)
                self.entries[lab] = ent
            else:
                ent = ttk.Entry(entry_frame, width=25)
                ent.grid(row=i, column=1, sticky='w', padx=5, pady=2)
                self.entries[lab] = ent
        # Add button
        ttk.Button(entry_frame, text='Hinzufügen', command=self._add_contributor).grid(
            row=len(labels), column=0, columnspan=3, pady=5)

        # Treeview for added contributors
        cols = ['Role','LastName','FirstName','ISNI','ORCID','ShortBio']
        self.tree = ttk.Treeview(f, columns=cols, show='headings', height=8)
        for c in cols:
            self.tree.heading(c, text=c)
            self.tree.column(c, width=120)
        self.tree.grid(row=1, column=0, sticky='nsew', padx=5, pady=5)
        # Prevent full expansion to bottom, keep fixed height
        # f.rowconfigure(1, weight=0)
        f.columnconfigure(0, weight=1)

        # Delete button
        ttk.Button(f, text='Löschen', command=self._delete_contributor).grid(row=2, column=0, pady=5)

        # Unselect on click
        self.tree.bind('<Button-1>', self._on_tree_click)

    def _validate_code(self, P):
        return P.isdigit() or P == ''

    def _add_contributor(self):
        vals = {}
        for key, widget in self.entries.items():
            if isinstance(widget, tk.Text):
                vals[key] = widget.get('1.0', 'end-1c').strip()
            else:
                vals[key] = widget.get().strip()
        if not vals['LastName'] or not vals['FirstName']:
            messagebox.showerror('Fehler', 'Vor- und Nachname sind erforderlich.')
            return
        self.tree.insert('', 'end', values=(
            vals['Role'], vals['LastName'], vals['FirstName'],
            vals['ISNI'], vals['ORCID'], vals['ShortBio']
        ))
        # Clear entries
        for key, widget in self.entries.items():
            if isinstance(widget, tk.Text):
                widget.delete('1.0', 'end')
            else:
                widget.delete(0, 'end')

    def _delete_contributor(self):
        for iid in self.tree.selection():
            self.tree.delete(iid)

    def _on_tree_click(self, event):
        iid = self.tree.identify_row(event.y)
        if iid in self.tree.selection():
            self.tree.selection_remove(iid)

    def get_data(self):
        data = []
        for iid in self.tree.get_children():
            vals = self.tree.item(iid, 'values')
            data.append({
                'Role': vals[0],
                'LastName': vals[1],
                'FirstName': vals[2],
                'ISNI': vals[3],
                'ORCID': vals[4],
                'ShortBio': vals[5]
            })
        return data
