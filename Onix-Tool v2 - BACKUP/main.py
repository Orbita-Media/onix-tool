# main.py
# Einstiegspunkt für den modularen BoD MasteringOrder Generator

import tkinter as tk
from tkinter import ttk
from utils import load_json
import xml_export

from tabs.header_tab          import HeaderTab
from tabs.product_tab         import ProductTab
from tabs.contributor_tab     import ContributorTab
from tabs.classification_tab  import ClassificationTab
from tabs.pricing_tab         import PricingTab
from tabs.international_tab   import InternationalTab
from tabs.ebook_tab           import EBookTab
from tabs.upload_tab          import UploadTab

def main():
    # JSON-Codes laden
    wgs_codes   = load_json('warengruppe_codes.json')
    bisac_codes = load_json('bisac_codes.json')

    # Hauptfenster
    root = tk.Tk()
    root.title('BoD MasteringOrder Generator')
    root.geometry('950x900')

    # Top-Bar mit MasteringType + Buttons
    bar = ttk.Frame(root)
    bar.pack(fill='x', pady=4)

    ttk.Label(bar, text='MasteringType:').pack(side='left', padx=(5,0))
    master_type_var = tk.StringVar(value='Upload')
    master_type_cb = ttk.Combobox(
        bar, textvariable=master_type_var,
        values=['Upload','AddIntlDistribution','AddEBook'],
        state='readonly', width=24
    )
    master_type_cb.pack(side='left', padx=(0,10))

    # die drei Widgets (noch nicht packen)
    export_btn   = ttk.Button(bar, text='Nur XML erstellen')
    zip_btn      = ttk.Button(bar, text='Zip erstellen')
    optional_lbl = ttk.Label(bar, text='Optional:')

    # Notebook (Tabs)
    nb = ttk.Notebook(root)
    nb.pack(fill='both', expand=True)

    # prepare all frames & tabs
    frame_header  = ttk.Frame(nb)
    frame_product = ttk.Frame(nb)
    frame_contrib = ttk.Frame(nb)
    frame_class   = ttk.Frame(nb)
    frame_pricing = ttk.Frame(nb)
    frame_intl    = ttk.Frame(nb)
    frame_ebook   = ttk.Frame(nb)
    frame_upload  = ttk.Frame(nb)

    # instantiate tabs
    header_tab         = HeaderTab(frame_header)
    product_tab        = ProductTab(frame_product)
    contributor_tab    = ContributorTab(frame_contrib)
    classification_tab = ClassificationTab(frame_class, wgs_codes, bisac_codes)
    pricing_tab        = PricingTab(frame_pricing, on_price_update=None)
    international_tab  = InternationalTab(frame_intl)
    ebook_tab          = EBookTab(frame_ebook, product_tab.widgets['EAN'])
    upload_tab         = UploadTab(
        frame_upload,
        product_tab, ebook_tab,
        header_tab, contributor_tab, classification_tab,
        pricing_tab, international_tab
    )

    # add tabs
    nb.add(frame_header,  text='Header')
    nb.add(frame_product, text='Product')
    nb.add(frame_contrib, text='Contributor')
    nb.add(frame_class,   text='Classification')
    nb.add(frame_pricing, text='Pricing')
    nb.add(frame_intl,    text='International')
    nb.add(frame_ebook,   text='EBook')
    nb.add(frame_upload,  text='Upload')

    # Pricing→International callback für Upload
    pricing_tab.on_price_update = international_tab.update_suggestions

    # Button-Kommandos (mode mitgeben)
    export_btn.config(command=lambda:
        xml_export.export_xml(
            header_tab,
            product_tab,
            contributor_tab,
            classification_tab,
            pricing_tab,
            international_tab,
            ebook_tab,
            mode=master_type_var.get()
        )
    )
    zip_btn.config(command=lambda: upload_tab.make_full_zip(master_type_var.get()))

    def on_master_change(*_):
        mode = master_type_var.get()

        # Buttons zurücksetzen
        export_btn.pack_forget()
        zip_btn.pack_forget()
        optional_lbl.pack_forget()

        if mode == 'Upload':
            # alle Tabs sichtbar
            for fr in (
                frame_header, frame_product, frame_contrib,
                frame_class, frame_pricing, frame_intl,
                frame_ebook, frame_upload
            ):
                nb.tab(fr, state='normal')
            nb.select(frame_header)

            # wieder Pricing→Intl anhängen
            pricing_tab.on_price_update = international_tab.update_suggestions
            international_tab.unlock_mode()
            international_tab.hide_addintl_fields()
            header_tab.show_imprint()

            # Upload-Tab: alle Bereiche wieder einblenden
            for child in upload_tab.frame.winfo_children():
                if isinstance(child, ttk.LabelFrame):
                    child.grid()

            # Pack order: ZIP links, Optional, Export (Nur XML)
            export_btn.config(text='Nur XML erstellen')
            export_btn.pack(side='right')
            optional_lbl.pack(side='right', padx=(0,4))
            zip_btn.pack(side='right', padx=(0,12))

            # EAN gedrucktes Buch im Upload-Modus ausblenden
            ebook_tab.printed_ean_label.grid_remove()
            ebook_tab.printed_ean_entry.grid_remove()

            # E-Book-Checkbox zurücksetzen
            ebook_tab.eb.set(False)
            ebook_tab._toggle_fields()
            ebook_tab.chk.config(state='normal')

        elif mode == 'AddIntlDistribution':
            # nur Header + International-Tab
            for fr in (
                frame_product, frame_contrib,
                frame_class, frame_pricing,
                frame_ebook, frame_upload
            ):
                nb.tab(fr, state='hidden')
            nb.tab(frame_header, state='normal')
            nb.tab(frame_intl,  state='normal')
            nb.select(frame_header)

            # detach Pricing→Intl & zeige nur Intl UI
            pricing_tab.on_price_update = None
            international_tab.lock_mode()
            international_tab.show_addintl_fields()

            # Header: Imprint ausblenden
            header_tab.hide_imprint()

            # nur XML erstellen
            export_btn.config(text='XML erstellen')
            export_btn.pack(side='right', padx=6)

            # EAN gedrucktes Buch im AddIntlDistribution-Modus ausblenden
            ebook_tab.printed_ean_label.grid_remove()
            ebook_tab.printed_ean_entry.grid_remove()

        else:  # AddEBook
            # nur Header + Upload-Tab anzeigen
            for fr in (
                frame_product, frame_contrib,
                frame_class, frame_pricing,
                frame_intl
            ):
                nb.tab(fr, state='hidden')
            nb.tab(frame_header, state='normal')
            nb.tab(frame_upload,  state='normal')
            nb.select(frame_header)
            nb.tab(frame_ebook,  state='normal')

            # Header: Imprint ausblenden
            header_tab.hide_imprint()

            # E-Book im EBook-Tab automatisch aktivieren und ausgrauen
            ebook_tab.eb.set(True)
            ebook_tab._toggle_fields()
            ebook_tab.chk.config(state='disabled')

            # im Upload-Tab nur E-Book-Frame anzeigen
            for child in upload_tab.frame.winfo_children():
                if isinstance(child, ttk.LabelFrame):
                    if child.cget('text') == 'E-Book':
                        child.grid()
                    else:
                        child.grid_remove()

            # Pack order: ZIP links, Optional, Export (Nur XML)
            export_btn.config(text='Nur XML erstellen')
            export_btn.pack(side='right')
            optional_lbl.pack(side='right', padx=(0,4))
            zip_btn.pack(side='right', padx=(0,12))
            
            # EAN gedrucktes Buch im AddEBook-Modus einblenden
            ebook_tab.printed_ean_label.grid()
            ebook_tab.printed_ean_entry.grid()

    master_type_var.trace_add('write', on_master_change)
    on_master_change()

    root.mainloop()

if __name__ == '__main__':
    main()
