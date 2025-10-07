# tabs/upload_tab.py
import tkinter as tk
from tkinter import ttk, filedialog, messagebox
import os
import tempfile
from zipfile import ZipFile
import xml_export

class UploadTab:
    def __init__(self, parent,
                 product_tab, ebook_tab,
                 header_tab, contributor_tab, classification_tab,
                 pricing_tab, international_tab):
        self.frame = parent
        self.prod = product_tab
        self.eb = ebook_tab
        self.header = header_tab
        self.contrib = contributor_tab
        self.classif = classification_tab
        self.price = pricing_tab
        self.intl = international_tab

        # Speichert Pfade
        self.paths = {
            'manuscript':   None,
            'cover':        None,
            'ebook':        None,
            'ebook_cover':  None
        }
        self._build_ui()

    def _build_ui(self):
        f = self.frame
        f.columnconfigure(0, weight=1)

        # Frame für gedrucktes Buch
        gedruckt = ttk.LabelFrame(f, text='Gedrucktes Buch')
        gedruckt.grid(row=0, column=0, sticky='ew', padx=10, pady=5)
        gedruckt.columnconfigure(2, weight=1)
        self.gedruckt_frame = gedruckt  # <--- speichern

        # Manuskript
        ttk.Label(gedruckt, text='Manuskript (PDF):') \
            .grid(row=0, column=0, sticky='e', padx=5, pady=4)
        btn1 = ttk.Button(gedruckt, text='Datei wählen', command=self._pick_manuscript)
        btn1.grid(row=0, column=1, sticky='w', padx=5, pady=4)
        self.lbl_man = ttk.Label(gedruckt, text='(keine Datei)')
        self.lbl_man.grid(row=0, column=2, sticky='w', padx=5, pady=4)

        # Cover
        ttk.Label(gedruckt, text='Cover (PDF):') \
            .grid(row=1, column=0, sticky='e', padx=5, pady=4)
        btn2 = ttk.Button(gedruckt, text='Datei wählen', command=self._pick_cover)
        btn2.grid(row=1, column=1, sticky='w', padx=5, pady=4)
        self.lbl_cov = ttk.Label(gedruckt, text='(keine Datei)')
        self.lbl_cov.grid(row=1, column=2, sticky='w', padx=5, pady=4)

        # Frame für E-Book
        ebook_fr = ttk.LabelFrame(f, text='E-Book')
        ebook_fr.grid(row=1, column=0, sticky='ew', padx=10, pady=5)
        ebook_fr.columnconfigure(2, weight=1)
        self.ebook_frame = ebook_fr  # <--- speichern

        # E-Book Datei
        self.lbl_ebook_desc = ttk.Label(ebook_fr, text='E-Book Datei (ePub):')
        self.lbl_ebook_desc.grid(row=0, column=0, sticky='e', padx=5, pady=4)
        self.btn_ebook = ttk.Button(ebook_fr, text='Datei wählen', state='disabled', command=self._pick_ebook)
        self.btn_ebook.grid(row=0, column=1, sticky='w', padx=5, pady=4)
        self.lbl_ebook = ttk.Label(ebook_fr, text='(keine Datei)')
        self.lbl_ebook.grid(row=0, column=2, sticky='w', padx=5, pady=4)

        # E-Book Cover
        self.lbl_ebook_cov_desc = ttk.Label(ebook_fr, text='E-Book Cover (jpg):')
        self.lbl_ebook_cov_desc.grid(row=1, column=0, sticky='e', padx=5, pady=4)
        self.btn_ebook_cov = ttk.Button(ebook_fr, text='Datei wählen', state='disabled', command=self._pick_ebook_cover)
        self.btn_ebook_cov.grid(row=1, column=1, sticky='w', padx=5, pady=4)
        self.lbl_ebook_cov = ttk.Label(ebook_fr, text='(keine Datei)')
        self.lbl_ebook_cov.grid(row=1, column=2, sticky='w', padx=5, pady=4)

        # Beobachte: E-Book aktiv und Format-Änderung
        self.eb.eb.trace('w', lambda *a: self._update_ebook_buttons())
        self.eb.eb_format.trace('w', lambda *a: self._update_ebook_buttons())

    def _update_ebook_buttons(self):
        enabled = self.eb.is_enabled()
        fmt = self.eb.eb_format.get()  # 'ePub' oder 'ePDF'
        # Label-Text anpassen
        self.lbl_ebook_desc.config(text=f"E-Book Datei ({fmt}):")
        # Buttons aktivieren / deaktivieren
        state = 'normal' if enabled else 'disabled'
        self.btn_ebook.config(state=state)
        self.btn_ebook_cov.config(state=state)

    def _pick_manuscript(self):
        p = filedialog.askopenfilename(filetypes=[('PDF', '*.pdf')])
        if p:
            self.paths['manuscript'] = p
            self.lbl_man.config(text=os.path.basename(p))

    def _pick_cover(self):
        p = filedialog.askopenfilename(filetypes=[('PDF', '*.pdf')])
        if p:
            self.paths['cover'] = p
            self.lbl_cov.config(text=os.path.basename(p))

    def _pick_ebook(self):
        fmt = self.eb.eb_format.get().lower()
        # wenn ePDF ausgewählt, wähle normale PDF-Dateien, sonst *.epub
        if fmt == 'epdf':
            filetypes = [('PDF', '*.pdf')]
        else:
            filetypes = [(fmt.upper(), f"*.{fmt}")]
        p = filedialog.askopenfilename(filetypes=filetypes)
        if p:
            self.paths['ebook'] = p
            self.lbl_ebook.config(text=os.path.basename(p))


    def _pick_ebook_cover(self):
        p = filedialog.askopenfilename(filetypes=[('JPEG', '*.jpg')])
        if p:
            self.paths['ebook_cover'] = p
            self.lbl_ebook_cov.config(text=os.path.basename(p))

    def make_full_zip(self, mode):
        # --- AddEBook-Fall: nur eBook + Cover, kein Manuskript/Cover-Upload ---
        if mode == 'AddEBook':
            # 1) Gedrucktes-Buch-EAN muss kommen aus EBookTab.print_ean
            printed_ean = self.eb.printed_ean_entry.get().strip()
            if not (printed_ean.isdigit() and len(printed_ean) == 13):
                messagebox.showerror(
                    'Fehler',
                    'Bitte eine gültige 13-stellige EAN des gedruckten Buchs eingeben.'
                )
                return

            # 2) Nur eBook-Datei + Cover prüfen
            if not self.paths['ebook'] or not self.paths['ebook_cover']:
                messagebox.showerror(
                    'Fehler',
                    'Bitte E-Book Datei und Cover hochladen.'
                )
                return

            # 3) XML mit mode='AddEBook' erzeugen
            tmp = tempfile.NamedTemporaryFile(suffix='.xml', delete=False)
            tmp.close()
            xml_path = xml_export.export_xml(
                self.header, self.prod, self.contrib,
                self.classif, self.price, self.intl, self.eb,
                filename=tmp.name,
                mode='AddEBook'
            )
            if not xml_path:
                return

            # 4) ZIP-Dialog, Dateiname = gedruckte-EAN_MasteringOrder.zip
            zipfn = filedialog.asksaveasfilename(
                defaultextension='.zip',
                filetypes=[('ZIP','*.zip')],
                initialfile=f"{printed_ean}_MasteringOrder.zip"
            )
            if not zipfn:
                return

            # 5) packen & umbenennen
            with ZipFile(zipfn, 'w') as z:
                z.write(xml_path, arcname=f"{printed_ean}_MasteringOrder.xml")
                eb_isbn = self.eb.eb_ean.get().strip()
                ext     = self.eb.eb_format.get().lower()
                z.write(self.paths['ebook'],       arcname=f"E-Book-{eb_isbn}.{ext}")
                z.write(self.paths['ebook_cover'], arcname=f"E-Book-{eb_isbn}.jpg")

            messagebox.showinfo('ZIP erstellt', f'ZIP gespeichert als:\n{zipfn}')
            return

        # --- Standard Upload-Fall: Manuskript + Cover (+ ggf. eBook) ---
        # 1) Manuskript & Cover immer für Upload-Mode erforderlich
        if mode == 'Upload':
            if not self.paths['manuscript'] or not self.paths['cover']:
                messagebox.showerror(
                    'Fehler',
                    'Bitte Manuskript und Cover hochladen.'
                )
                return

        # 2) eBook nur prüfen, wenn aktiviert
        if self.eb.is_enabled():
            if not self.paths['ebook'] or not self.paths['ebook_cover']:
                messagebox.showerror(
                    'Fehler',
                    'Bitte E-Book Datei und Cover hochladen.'
                )
                return

            # Format vs. Dateiendung
            fmt = self.eb.eb_format.get().lower()  # 'epub' oder 'epdf'
            _, ext = os.path.splitext(self.paths['ebook'])
            if fmt == 'epdf':
                valid_ext  = '.pdf'
                display_fmt = 'PDF'
            else:
                valid_ext  = f".{fmt}"
                display_fmt = fmt.upper()
            if ext.lower() != valid_ext:
                messagebox.showerror(
                    'Falsches Format',
                    f'Bitte eine {display_fmt}-Datei als E-Book hochladen.'
                )
                return

        # 3) XML erzeugen wie beim reinen XML-Button (mode bleibt 'Upload')
        tmp = tempfile.NamedTemporaryFile(suffix='.xml', delete=False)
        tmp.close()
        xml_path = xml_export.export_xml(
            self.header, self.prod, self.contrib,
            self.classif, self.price, self.intl, self.eb,
            filename=tmp.name,
            mode=mode
        )
        if not xml_path:
            return

        # 4) ZIP-Dialog
        isbn = self.prod.widgets['EAN'].get().strip()
        zipfn = filedialog.asksaveasfilename(
            defaultextension='.zip',
            filetypes=[('ZIP','*.zip')],
            initialfile=f"{isbn}_MasteringOrder.zip"
        )
        if not zipfn:
            return

        # 5) Packen & umbenennen
        with ZipFile(zipfn, 'w') as z:
            band   = self.prod.widgets.get('PartNumber').get().strip()
            suffix = f"_{band}" if band else ""
            z.write(self.paths['manuscript'], arcname=f"{isbn}{suffix}_Bookblock.pdf")
            z.write(self.paths['cover'],      arcname=f"{isbn}_Cover.pdf")
            z.write(xml_path,                 arcname=f"{isbn}_MasteringOrder.xml")
            if self.eb.is_enabled():
                eb_isbn = self.eb.eb_ean.get().strip()
                fmt     = self.eb.eb_format.get().lower()
                ext     = 'pdf' if fmt == 'epdf' else fmt
                z.write(self.paths['ebook'],       arcname=f"E-Book-{eb_isbn}.{ext}")
                z.write(self.paths['ebook_cover'], arcname=f"E-Book-{eb_isbn}.jpg")

        messagebox.showinfo('ZIP erstellt', f'ZIP gespeichert als:\n{zipfn}')
        return


        # -- Standard Upload-Modus: Manuskript + Cover (+ ggf. E-Book) --
        # Manuskript & Cover nur dann erforderlich, wenn das "Gedrucktes Buch"-Frame sichtbar ist
        if self.gedruckt_frame.winfo_ismapped():
            if not self.paths['manuscript'] or not self.paths['cover']:
                messagebox.showerror(
                    'Fehler',
                    'Bitte Manuskript und Cover hochladen.'
                )
                return

        # E-Book nur prüfen, wenn aktiviert
        if self.eb.is_enabled():
            # E-Book-Datei & Cover
            if not self.paths['ebook'] or not self.paths['ebook_cover']:
                messagebox.showerror(
                    'Fehler',
                    'Bitte E-Book Datei und Cover hochladen.'
                )
                return

            # Format vs. hochgeladene Datei prüfen
            fmt = self.eb.eb_format.get().lower()  # 'epub' oder 'epdf'
            _, ext = os.path.splitext(self.paths['ebook'])
            if fmt == 'epdf':
                valid_ext = '.pdf'
                display_fmt = 'PDF'
            else:
                valid_ext = f".{fmt}"
                display_fmt = fmt.upper()

            if ext.lower() != valid_ext:
                messagebox.showerror(
                    'Falsches Format',
                    f'Bitte eine {display_fmt}-Datei als E-Book hochladen.'
                )
                return



        # 3) XML erzeugen wie beim reinen XML-Button
        tmp = tempfile.NamedTemporaryFile(suffix='.xml', delete=False)
        tmp.close()
        xml_path = xml_export.export_xml(
            self.header, self.prod, self.contrib,
            self.classif, self.price, self.intl, self.eb,
            filename=tmp.name
        )
        if not xml_path:
            return

        # 4) ZIP-Pfad
        isbn = self.prod.widgets['EAN'].get().strip()
        zipfn = filedialog.asksaveasfilename(
            defaultextension='.zip',
            filetypes=[('ZIP','*.zip')],
            initialfile=f"{isbn}_MasteringOrder.zip"
        )
        if not zipfn:
            return

        # 5) Packen & umbenennen – gedruckt + Buch + (optional E-Book)
        with ZipFile(zipfn, 'w') as z:
            band   = self.prod.widgets.get('PartNumber').get().strip()
            suffix = f"_{band}" if band else ""
            z.write(self.paths['manuscript'], arcname=f"{isbn}{suffix}_Bookblock.pdf")
            z.write(self.paths['cover'],      arcname=f"{isbn}_Cover.pdf")
            z.write(xml_path,                 arcname=f"{isbn}_MasteringOrder.xml")
            if self.eb.is_enabled():
                eb_isbn = self.eb.eb_ean.get().strip()
                fmt     = self.eb.eb_format.get().lower()
                ext     = 'pdf' if fmt == 'epdf' else fmt
                z.write(self.paths['ebook'],       arcname=f"E-Book-{eb_isbn}.{ext}")
                z.write(self.paths['ebook_cover'], arcname=f"E-Book-{eb_isbn}.jpg")

        messagebox.showinfo('ZIP erstellt', f'ZIP gespeichert als:\n{zipfn}')
