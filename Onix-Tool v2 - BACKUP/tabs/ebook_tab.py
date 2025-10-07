# tabs/ebook_tab.py
"""
Module for the EBook tab of BoD MasteringOrder Generator.
Handles the E-Book creation options and fields.
Place this file in the folder `tabs/`.
"""
import tkinter as tk
from tkinter import ttk, filedialog, messagebox
import zipfile

class EBookTab:
    def __init__(self, parent, prod_ean_entry):
        """
        parent: ttk.Frame from the Notebook where this tab lives.
        prod_ean_entry: Entry widget from ProductTab to avoid duplicate EAN.
        """
        self.frame = parent
        self.prod_ean = prod_ean_entry
        self._build_ui()

    def _build_ui(self):
        f = self.frame
        # Checkbox to enable E-Book fields
        self.eb = tk.BooleanVar(value=False)
        self.chk = ttk.Checkbutton(f, text='E-Book erstellen', variable=self.eb,
                                   command=self._toggle_fields)
        self.chk.grid(row=0, column=0, sticky='w', padx=5, pady=5)

        # Frame for EAN field
        frame_ean = ttk.LabelFrame(f, text='EAN')
        frame_ean.grid(row=1, column=0, sticky='ew', padx=10, pady=5)

        # EAN gedrucktes Buch
        self.printed_ean_label = ttk.Label(frame_ean, text='EAN gedrucktes Buch:*')
        self.printed_ean_label.grid(row=0, column=0, sticky='e', padx=5, pady=2)
        vcmd_print = (f.register(lambda P: (P.isdigit() and len(P) <= 13) or P == ''), '%P')
        self.printed_ean_entry = ttk.Entry(frame_ean, width=30, validate='key', validatecommand=vcmd_print)
        self.printed_ean_entry.grid(row=0, column=1, sticky='w', padx=5, pady=2)

        # EAN E-Book
        ttk.Label(frame_ean, text='EAN E-Book:*').grid(
            row=1, column=0, sticky='e', padx=5, pady=2
        )
        vcmd = (f.register(self._validate_ebook_ean), '%P')
        self.eb_ean = ttk.Entry(frame_ean, width=30, validate='key', validatecommand=vcmd)
        self.eb_ean.grid(row=1, column=1, sticky='w', padx=5, pady=2)
        self.eb_ean.bind('<FocusOut>', lambda e: self._on_ebook_ean_focusout())

        # Frame for Format and Conversion
        frame_format = ttk.LabelFrame(f, text='Dateiformat')
        frame_format.grid(row=2, column=0, sticky='ew', padx=10, pady=5)
        ttk.Label(frame_format, text='E-Book Format:*').grid(
            row=0, column=0, sticky='e', padx=5, pady=2
        )
        self.eb_format = tk.StringVar(value='ePub')
        self.eb_format_cb = ttk.Combobox(
            frame_format, textvariable=self.eb_format,
            values=['ePub','ePDF'], state='readonly', width=10
        )
        self.eb_format_cb.grid(row=0, column=1, sticky='w', padx=5, pady=2)
        self.eb_format_cb.bind('<<ComboboxSelected>>', lambda e: self._sync_ebook_filetype())
        ttk.Label(frame_format, text='Conversion:').grid(
            row=1, column=0, sticky='e', padx=5, pady=2
        )
        self.eb_conversion = tk.StringVar(value='No')
        self.eb_conversion_cb = ttk.Combobox(
            frame_format, textvariable=self.eb_conversion,
            values=['No'], state='disabled', width=10
        )
        self.eb_conversion_cb.grid(row=1, column=1, sticky='w', padx=5, pady=2)
        ttk.Label(frame_format, text='E-Book Dateityp:').grid(
            row=2, column=0, sticky='e', padx=5, pady=2
        )
        self.eb_filetype = tk.StringVar(value='ePub')
        self.eb_filetype_cb = ttk.Combobox(
            frame_format, textvariable=self.eb_filetype,
            values=['ePub','ePDF'], state='disabled', width=10
        )
        self.eb_filetype_cb.grid(row=2, column=1, sticky='w', padx=5, pady=2)

        # Frame for Price
        frame_price = ttk.LabelFrame(f, text='Preis')
        frame_price.grid(row=3, column=0, sticky='ew', padx=10, pady=5)
        ttk.Label(frame_price, text='Preis in EUR:*').grid(
            row=0, column=0, sticky='e', padx=5, pady=2
        )
        prices = [
            '0.99','1.49','1.99','2.49','2.99','3.49','3.99','4.49','4.99','5.49',
            '5.99','6.49','6.99','7.49','7.99','8.49','8.99','9.49','9.99',
            '10.99','11.99','12.99','13.99','14.99','15.99','16.99','17.99','18.99','19.99',
            '20.99','21.99','22.99','23.99','24.99','25.99','26.99','27.99','28.99','29.99',
            '30.99','31.99','32.99','33.99','34.99','35.99','36.99','37.99','38.99','39.99',
            '40.99','41.99','42.99','43.99','44.99','45.99','46.99','47.99','48.99','49.99',
            '52.99','54.99','57.99','59.99','62.99','64.99','67.99','69.99','72.99','74.99',
            '77.99','79.99','82.99','84.99','87.99','89.99','92.99','94.99','97.99','99.99',
            '104.99','109.99','114.99','119.99','124.99','129.99','134.99','139.99','144.99','149.99',
            '154.99','159.99','164.99','169.99','174.99','179.99','184.99','189.99','194.99','199.99',
            '204.99','209.99','214.99','219.99','229.99','239.99','249.99','259.99','269.99','279.99',
            '289.99','299.99','349.99','399.99','449.99','499.99','549.99','599.99','649.99','699.99'
        ]
        self.eb_price = tk.StringVar()
        self.eb_price_cb = ttk.Combobox(
            frame_price, textvariable=self.eb_price,
            values=prices, state='readonly', width=10
        )
        self.eb_price_cb.grid(row=0, column=1, sticky='w', padx=5, pady=2)

        # Initially hide frames
        self.eb_frame = (frame_ean, frame_format, frame_price)
        for fr in self.eb_frame:
            fr.grid_remove()

    def _toggle_fields(self):
        visible = self.eb.get()
        for fr in self.eb_frame:
            if visible:
                fr.grid()
            else:
                fr.grid_remove()

    def _validate_ebook_ean(self, P):
        # Allow empty
        if P == '':
            return True
        # Only digits, max length 13, and not equal to printed-book EAN
        return P.isdigit() and len(P) <= 13 and (P.strip() != self.printed_ean_entry.get().strip())

    def _on_ebook_ean_focusout(self):
        val = self.eb_ean.get().strip()
        printed = self.printed_ean_entry.get().strip()
        valid = val.isdigit() and len(val) == 13 and (val != printed)
        self.eb_ean.config(background='white' if valid else 'pink')

    def _sync_ebook_filetype(self):
        self.eb_filetype.set(self.eb_format.get())

    def is_enabled(self):
        """Return True if E-Book creation is activated."""
        return bool(self.eb.get())

    def get_data(self):
        """Collect E-Book field values as dict for XML export."""
        return {
            'PrintedEAN':     self.printed_ean_entry.get().strip(),
            'EAN':            self.eb_ean.get().strip(),
            'EBookFormat':    self.eb_format.get(),
            'Conversion':     self.eb_conversion.get(),
            'EBookFileType':  self.eb_filetype.get(),
            'Price':          self.eb_price.get().strip(),
        }
