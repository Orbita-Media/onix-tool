"""
Module to export the BoD MasteringOrder data to XML and (optionally) ZIP archive.
Place this file in the project root next to main.py.
"""
import zipfile
import math
from datetime import datetime
from tkinter import filedialog, messagebox, Text
from lxml import etree

# Pflichtfelder für Product-Tab (ohne EAN)
REQUIRED_PRODUCT = [
    'Title','Blurb','Height','Width','Pages','PublicationDate',
    'ColouredPages','Quality','Paper','Binding','CoverDuplex','Finish'
]

# Pflicht-Header-Felder
REQUIRED_HEADER = [
    'FromCompany','FromCompanyNumber','SentDate','SentTime','FromEmail'
]


def export_xml(header_tab, product_tab, contributor_tab, classification_tab,
               pricing_tab, international_tab, ebook_tab,
               filename=None, mode='Upload'):
    """
    Collect all data from the tab instances and write a BoD XML file.
    Performs validation of required fields per tab.
    mode: 'Upload' (vollständig) oder 'AddIntlDistribution' (nur International).
    """
    # -- HEADER VALIDATION --
    hdr_data = header_tab.get_data()
    missing_hdr = [k for k in REQUIRED_HEADER if not hdr_data.get(k)]
    if missing_hdr:
        messagebox.showerror(
            'Pflichtfeld fehlt',
            f'Bitte im Header-Tab ausfüllen: {", ".join(missing_hdr)}'
        )
        return
    # Format-Validation SentDate YYYYMMDD
    try:
        datetime.strptime(hdr_data.get('SentDate',''), '%Y%m%d')
    except Exception:
        messagebox.showerror(
            'Ungültiges Format',
            'SentDate muss im Format YYYYMMDD vorliegen.'
        )
        return
    # Format-Validation SentTime HH:MM
    try:
        datetime.strptime(hdr_data.get('SentTime',''), '%H:%M')
    except Exception:
        messagebox.showerror(
            'Ungültiges Format',
            'SentTime muss im Format HH:MM vorliegen.'
        )
        return

    # --- neuer AddEBook-Branch ---
    if mode == 'AddEBook':
        # Printed Book EAN prüfen
        data = ebook_tab.get_data()
        printed_ean = data.get('PrintedEAN','')
        if not (printed_ean.isdigit() and len(printed_ean)==13):
            messagebox.showerror(
                'Ungültige EAN',
                'Bitte eine gültige 13-stellige EAN des gedruckten Buchs eingeben.'
            )
            return

        # E-Book EAN prüfen
        ebook_ean = data.get('EAN','')
        if not (ebook_ean.isdigit() and len(ebook_ean)==13):
            messagebox.showerror(
                'Ungültige EAN',
                'Bitte eine gültige 13-stellige EAN für das E-Book eingeben.'
            )
            return

        # E-Book-Preis prüfen
        price = data.get('Price','')
        if not price:
            messagebox.showerror(
                'Pflichtfeld fehlt',
                'Bitte einen Preis im E-Book-Tab auswählen.'
            )
            return

        # XML bauen
        root    = etree.Element('BoD')
        hdr_el  = etree.SubElement(root, 'Header')
        for tag in ['FromCompany','FromCompanyNumber','SentDate','SentTime','FromPerson','FromEmail']:
            val = hdr_data.get(tag)
            if val:
                el = etree.SubElement(hdr_el, tag)
                el.text = val

        mo      = etree.SubElement(root, 'MasteringOrder')
        prod_el = etree.SubElement(mo, 'Product')
        etree.SubElement(prod_el, 'MasteringType').text = 'AddEBook'
        etree.SubElement(prod_el, 'EAN').text          = printed_ean

        eb      = etree.SubElement(prod_el, 'EBook')
        # EBook-EAN mit Attribut
        etree.SubElement(eb, 'EAN', EBookFileType=data['EBookFileType']).text = ebook_ean
        etree.SubElement(eb, 'Conversion').text    = data['Conversion']
        etree.SubElement(eb, 'EBookFileType').text = data['EBookFileType']
        ebp = etree.SubElement(eb, 'Price')
        etree.SubElement(ebp, 'PriceValue').text    = price
        etree.SubElement(ebp, 'PriceCurrency').text = 'EUR'

        # XML speichern unter PrintedEAN_MasteringOrder.xml
        if filename:
            fn = filename
        else:
            fn = filedialog.asksaveasfilename(
                defaultextension='.xml',
                filetypes=[('XML','*.xml')],
                initialfile=f"{printed_ean}_MasteringOrder.xml"
            )
        if not fn:
            return
        etree.ElementTree(root).write(fn, xml_declaration=True,
                                     encoding='UTF-8', pretty_print=True)
        return fn

    # -------------------------------------------------------------------
    # AddIntlDistribution-Modus: nur International
    if mode == 'AddIntlDistribution':
        # EAN im International-Tab prüfen
        intl_data = international_tab.get_data()
        intl_ean  = intl_data.get('EAN','').strip()
        if not (intl_ean.isdigit() and len(intl_ean)==13):
            messagebox.showerror(
                'Ungültige EAN',
                'Bitte eine gültige 13-stellige EAN im International-Tab eingeben.'
            )
            return

        # Preise prüfen
        prices = international_tab.get_prices()
        missing_intl = [c for c in ['USD','GBP','AUD'] if not prices.get(c)]
        if missing_intl:
            messagebox.showerror(
                'Pflichtfeld fehlt',
                f'Bitte Preise eingeben: {", ".join(missing_intl)}'
            )
            return

        # XML bauen
        root    = etree.Element('BoD')
        hdr_el  = etree.SubElement(root, 'Header')
        for tag in ['FromCompany','FromCompanyNumber','SentDate','SentTime','FromPerson','FromEmail']:
            val = hdr_data.get(tag)
            if val:
                el = etree.SubElement(hdr_el, tag)
                el.text = val

        mo      = etree.SubElement(root, 'MasteringOrder')
        prod_el = etree.SubElement(mo, 'Product')
        etree.SubElement(prod_el, 'MasteringType').text = 'AddIntlDistribution'
        etree.SubElement(prod_el, 'EAN').text          = intl_ean

        # Price-Blöcke
        for cur in ['USD','GBP','AUD']:
            p = etree.SubElement(prod_el, 'Price')
            etree.SubElement(p, 'PriceValue').text    = prices[cur]
            etree.SubElement(p, 'PriceCurrency').text = cur

        # XML speichern
        if filename:
            fn = filename
        else:
            fn = filedialog.asksaveasfilename(
                defaultextension='.xml', filetypes=[('XML','*.xml')],
                initialfile=f"{intl_ean}_MasteringOrder.xml"
            )
        if not fn:
            return
        etree.ElementTree(root).write(
            fn, xml_declaration=True,
            encoding='UTF-8', pretty_print=True
        )
        return fn

    # -------------------------------------------------------------------
    # Upload-Modus: bestehender, kompletter Ablauf

    # -- PRODUCT-EAN VALIDATION --
    prod_ean = product_tab.widgets['EAN'].get().strip()
    if not (prod_ean.isdigit() and len(prod_ean) == 13):
        messagebox.showerror(
            'Ungültige EAN',
            'Bitte geben Sie eine gültige 13-stellige Produkt-EAN im Product-Tab ein.'
        )
        return

    # -- CONTRIBUTOR VALIDATION --
    contribs = contributor_tab.get_data()
    if not contribs:
        messagebox.showerror(
            'Pflichtfeld fehlt',
            'Bitte mindestens einen Contributor im Contributor-Tab hinzufügen.'
        )
        return

    # -- CLASSIFICATION VALIDATION --
    sel        = classification_tab.get_selected()
    sel_wgs    = sel['WGS']
    sel_bisac  = sel['BISAC']
    if not sel_wgs and not sel_bisac:
        messagebox.showerror(
            'Pflichtfeld fehlt',
            'Bitte mindestens eine Kategorie im Classification-Tab auswählen.'
        )
        return
    need_age_wgs   = any('Kinder' in classification_tab.wgs.get(code, '') for code in sel_wgs)
    need_age_bisac = any(code.startswith(('JUV','YAF')) for code in sel_bisac)
    if (need_age_wgs   and not sel.get('AgeWGS')) \
    or (need_age_bisac and not sel.get('AgeBISAC')):
        messagebox.showerror(
            'Pflichtfeld fehlt',
            'Bitte eine Altersgruppe im Classification-Tab wählen.'
        )
        return

    # -- PRODUCT FIELDS VALIDATION --
    errors = []
    for key in REQUIRED_PRODUCT:
        w = product_tab.widgets.get(key)
        if isinstance(w, Text):
            val = w.get('1.0', 'end-1c').strip()
        else:
            val = w.get().strip()
        if not val:
            errors.append(key)
    if errors:
        # 'Blurb' als 'Beschreibung' ausgeben
        display = ['Beschreibung' if k == 'Blurb' else k for k in errors]
        messagebox.showerror(
            'Pflichtfeld fehlt',
            f'Bitte füllen Sie alle Pflichtfelder im Product-Tab: {", ".join(display)}'
        )
        return

    # >>>>> NEUER BLOCK: ColouredPagesPosition Validierung <<<<<
    prod_data = product_tab.get_ordered_data()
    try:
        cp_count = int(prod_data.get('ColouredPages', '0'))
    except ValueError:
        cp_count = 0
    if cp_count > 0:
        cpp = prod_data.get('ColouredPagesPosition', '').strip()
        if not cpp:
            messagebox.showerror(
                'Pflichtfeld fehlt',
                'Bitte ColouredPagesPosition angeben (kommagetrennt, ohne Leerzeichen).'
            )
            return
        if ' ' in cpp:
            messagebox.showerror(
                'Formatfehler',
                'ColouredPagesPosition darf keine Leerzeichen enthalten.'
            )
            return
        parts = cpp.split(',')
        if len(parts) != cp_count:
            messagebox.showerror(
                'Pflichtfeld fehlt',
                f'Bitte {cp_count} Seitenzahlen angeben, kommagetrennt ohne Leerzeichen.'
            )
            return
        # nur Ziffern, keine 0, keine +/-
        for p in parts:
            if not p.isdigit():
                messagebox.showerror(
                    'Formatfehler',
                    'ColouredPagesPosition darf nur Ziffern enthalten (keine +, –, Buchstaben, Sonderzeichen).'
                )
                return
            if p == '0':
                messagebox.showerror(
                    'Formatfehler',
                    'ColouredPagesPosition darf keine 0 enthalten.'
                )
                return
        nums = [int(x) for x in parts]
        if nums != sorted(nums):
            messagebox.showerror(
                'Formatfehler',
                'ColouredPagesPosition muss in aufsteigender Reihenfolge sein.'
            )
            return
        # höchste Zahl ≤ Pages
        try:
            total = int(prod_data.get('Pages', '0'))
        except ValueError:
            total = 0
        if nums[-1] > total:
            messagebox.showerror(
                'Formatfehler',
                'ColouredPagesPosition darf nicht größer als Anzahl Pages sein.'
            )
            return
    # <<<<< ENDE BLOCK <<<<<

    # -- PRICING VALIDATION --
    eur = pricing_tab.get_price_eur()
    if not eur:
        messagebox.showerror(
            'Pflichtfeld fehlt',
            'Bitte geben Sie einen Preis in EUR im Pricing-Tab ein.'
        )
        return

    # -- INTERNATIONAL VALIDATION --
    if international_tab.is_enabled():
        intl_prices = international_tab.get_prices()
        missing_intl = [cur for cur in ['USD','GBP','AUD'] if not intl_prices.get(cur)]
        if missing_intl:
            messagebox.showerror(
                'Pflichtfeld fehlt',
                f'Bitte internationale Preise eingeben: {", ".join(missing_intl)}'
            )
            return

    # -- EBOOK VALIDATION --
    if ebook_tab.is_enabled():
        eb_data  = ebook_tab.get_data()
        eb_ean   = eb_data.get('EAN','').strip()
        eb_price = eb_data.get('Price','').strip()
        if not (eb_ean.isdigit() and len(eb_ean) == 13):
            messagebox.showerror(
                'Pflichtfeld fehlt',
                'Bitte eine gültige 13-stellige EAN im EBook-Tab eingeben.'
            )
            return
        if eb_ean == prod_ean:
            messagebox.showerror(
                'Ungültige EAN',
                'EBook-EAN darf nicht mit der Produkt-EAN übereinstimmen.'
            )
            return
        if not eb_price:
            messagebox.showerror(
                'Pflichtfeld fehlt',
                'Bitte einen Preis im EBook-Tab auswählen.'
            )
            return

    # -- XML-Baum aufbauen im Upload-Modus --
    root    = etree.Element('BoD')
    hdr_el  = etree.SubElement(root, 'Header')
    for tag in ['FromCompany','FromCompanyNumber','SentDate','SentTime','FromPerson','FromEmail']:
        val = hdr_data.get(tag)
        if val:
            el = etree.SubElement(hdr_el, tag)
            el.text = val

    mo      = etree.SubElement(root, 'MasteringOrder')
    prod_el = etree.SubElement(mo, 'Product')
    etree.SubElement(prod_el, 'MasteringType').text = 'Upload'
    etree.SubElement(prod_el, 'EAN').text          = prod_ean

    # Contributors
    for contrib in contribs:
        c_el = etree.SubElement(prod_el, 'Contributor')
        etree.SubElement(c_el, 'ContributorRole').text      = contrib['Role'].lower()
        etree.SubElement(c_el, 'ContributorName').text      = f"{contrib['LastName']}, {contrib['FirstName']}"
        if contrib.get('ShortBio'):
            etree.SubElement(c_el, 'ContributorShortBio').text = contrib['ShortBio']

    # Produktspezifische Tags in korrekter Reihenfolge
    prod_data = product_tab.get_ordered_data()

    # Title, SubTitle
    for tag in ['Title','SubTitle']:
        val = prod_data.get(tag,'')
        if val:
            el = etree.SubElement(prod_el, tag)
            el.text = val

    # Series (nur wenn eingetragen)
    series = prod_data.get('Series','')
    if series:
        el = etree.SubElement(prod_el, 'Series')
        el.text = series

    # PartNumber
    part = prod_data.get('PartNumber','')
    if part:
        el = etree.SubElement(prod_el, 'PartNumber')
        el.text = part

    # Imprint (immer aus Header-Tab)
    imprint = hdr_data.get('Imprint','')
    el      = etree.SubElement(prod_el, 'Imprint')
    el.text = imprint

    # EditionNumber, PublicationDate
    for tag in ['EditionNumber','PublicationDate']:
        val = prod_data.get(tag,'')
        if val:
            el = etree.SubElement(prod_el, tag)
            el.text = val

    # Blurb
    blurb = prod_data.get('Blurb','')
    if blurb:
        el = etree.SubElement(prod_el, 'Blurb')
        el.text = blurb

    # Height, Width
    for tag in ['Height','Width']:
        val = prod_data.get(tag,'')
        if val:
            el = etree.SubElement(prod_el, tag)
            el.text = val

    # Pages
    pages = prod_data.get('Pages','')
    if pages:
        el = etree.SubElement(prod_el, 'Pages')
        el.text = pages

    # ColouredPages & ColouredPagesPosition
    cp = prod_data.get('ColouredPages','')
    if cp:
        el = etree.SubElement(prod_el, 'ColouredPages')
        el.text = cp
    cpp = prod_data.get('ColouredPagesPosition','')
    if cpp:
        el = etree.SubElement(prod_el, 'ColouredPagesPosition')
        el.text = cpp

    # Quality, Paper, Binding, CoverDuplex, Finish
    for tag in ['Quality','Paper','Binding','CoverDuplex','Finish']:
        val = prod_data.get(tag,'')
        if val:
            el = etree.SubElement(prod_el, tag)
            el.text = val

    # Language (immer aus Classification-Tab)
    lang = sel.get('Language','')
    el   = etree.SubElement(prod_el, 'Language')
    el.text = lang

    # Classification Subjects
    for code in sel['WGS']:
        attrs = {'Scheme': 'WGS'}
        desc = classification_tab.wgs.get(code, '')
        if 'Kinder' in desc:
            age_code = sel.get('AgeWGS','')
            if age_code:
                attrs['AudienceRangeFrom'] = age_code
        subj = etree.SubElement(prod_el, 'Subject', **attrs)
        subj.text = code

    for code in sel['BISAC']:
        attrs = {'Scheme': 'BISAC'}
        if code.startswith(('JUV','YAF')):
            age_code = sel.get('AgeBISAC','')
            if age_code:
                attrs['AudienceRangeFrom'] = age_code
        subj = etree.SubElement(prod_el, 'Subject', **attrs)
        subj.text = code

    # Prices EUR & International
    p = etree.SubElement(prod_el, 'Price')
    etree.SubElement(p, 'PriceValue').text    = eur
    etree.SubElement(p, 'PriceCurrency').text = 'EUR'
    if international_tab.is_enabled():
        etree.SubElement(prod_el, 'InternationalDistribution').text = 'Yes'
        intl_prices = international_tab.get_prices()
        for cur in ['USD','GBP','AUD']:
            val = intl_prices.get(cur)
            if val:
                p2 = etree.SubElement(prod_el, 'Price')
                etree.SubElement(p2, 'PriceValue').text    = val
                etree.SubElement(p2, 'PriceCurrency').text = cur

    # EBook Block
    if ebook_tab.is_enabled():
        eb_data  = ebook_tab.get_data()
        eb_ean   = eb_data.get('EAN','').strip()
        eb       = etree.SubElement(prod_el, 'EBook')
        attrs    = {'EBookFileType': eb_data.get('EBookFileType','')}
        etree.SubElement(eb, 'EAN', **attrs).text         = eb_ean
        etree.SubElement(eb, 'Conversion').text          = eb_data.get('Conversion','')
        etree.SubElement(eb, 'EBookFileType').text       = eb_data.get('EBookFileType','')
        ebp      = etree.SubElement(eb, 'Price')
        etree.SubElement(ebp, 'PriceValue').text         = eb_data.get('Price','').strip()
        etree.SubElement(ebp, 'PriceCurrency').text      = 'EUR'

    # XML speichern
    if filename:
        fn = filename
    else:
        fn = filedialog.asksaveasfilename(
            defaultextension='.xml', filetypes=[('XML','*.xml')],
            initialfile=f"{prod_ean}_MasteringOrder.xml"
        )
    if not fn:
        return
    etree.ElementTree(root).write(
        fn, xml_declaration=True,
        encoding='UTF-8', pretty_print=True
    )
    return fn


def make_zip(product_tab, manuscript=None, cover=None, xml_path=None):
    """
    Create a ZIP archive containing the XML, manuscript and cover.
    """
    # Manuscript wählen
    if not manuscript:
        manuscript = filedialog.askopenfilename(
            title='Manuskript wählen', filetypes=[('PDF','*.pdf')]
        )
        if not manuscript: return
    # Cover wählen
    if not cover:
        cover = filedialog.askopenfilename(
            title='Cover wählen', filetypes=[('PDF','*.pdf')]
        )
        if not cover: return
    # ISBN/EAN
    prod_ean = product_tab.widgets['EAN'].get().strip()
    if not prod_ean:
        messagebox.showerror('Fehler', 'Bitte zuerst eine gültige EAN eingeben.')
        return
    # XML wählen
    if not xml_path:
        xml_path = filedialog.askopenfilename(
            title='Erzeugte XML wählen', filetypes=[('XML','*.xml')]
        )
        if not xml_path: return
    # ZIP-Pfad wählen
    zip_path = filedialog.asksaveasfilename(
        title='ZIP speichern als',
        defaultextension='.zip', filetypes=[('ZIP','*.zip')],
        initialfile=f'{prod_ean}_MasteringOrder.zip'
    )
    if not zip_path: return
    # ZIP erstellen
    with zipfile.ZipFile(zip_path, 'w') as z:
        z.write(xml_path, arcname=f'{prod_ean}_MasteringOrder.xml')
        z.write(manuscript, arcname=f'{prod_ean}_Bookblock.pdf')
        z.write(cover, arcname=f'{prod_ean}_Cover.pdf')
    messagebox.showinfo('ZIP erstellt', f'ZIP erstellt:\n{zip_path}')
