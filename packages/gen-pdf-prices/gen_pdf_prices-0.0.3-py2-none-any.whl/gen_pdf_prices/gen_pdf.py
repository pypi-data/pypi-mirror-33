import os
import datetime
from io import BytesIO

from reportlab.pdfgen import canvas
from reportlab.pdfbase import pdfmetrics
from reportlab.lib.pagesizes import letter

class GeneratePdf:

    # fname - the font file name without extension
    # The font files can be found in /usr/share/fonts/default/Type1 
    fname = os.path.join(os.path.dirname(os.path.abspath(__file__)),
                         'fonts', 'a010013l')

    # faceName - view a010013l.AFM file as a plain text and look at
    # row beginning with 'FontName' word (it's usually the fourth row).
    # The word after 'FontName' is the faceName ('URWGothicL-Book' in this case).
    faceName = 'URWGothicL-Book'

    # Define new Type 1 font
    cyrFace = pdfmetrics.EmbeddedType1Face(fname+'.afm', fname+'.pfb')

    # Create a new encoding called 'CP1251'
    cyrenc = pdfmetrics.Encoding('CP1251')

    # Fill in the tuple with Unicode glyphs in accordance with cp1251 (win1251)
    # encoding
    cp1251=(
        'afii10051', 'afii10052', 'quotesinglbase', 'afii10100', 'quotedblbase',
        'ellipsis', 'dagger', 'daggerdbl', 'Euro', 'perthousand', 'afii10058',
        'guilsinglleft', 'afii10059', 'afii10061', 'afii10060', 'afii10145',
        'afii10099', 'quoteleft', 'quoteright', 'quotedblleft', 'quotedblright',
        'bullet', 'endash', 'emdash', 'tilde', 'trademark', 'afii10106',
        'guilsinglright', 'afii10107', 'afii10109', 'afii10108', 'afii10193',
        'space', 'afii10062', 'afii10110', 'afii10057', 'currency', 'afii10050',
        'brokenbar', 'section', 'afii10023', 'copyright', 'afii10053',
        'guillemotleft', 'logicalnot', 'hyphen', 'registered', 'afii10056',
        'degree', 'plusminus', 'afii10055', 'afii10103', 'afii10098', 'mu1',
        'paragraph', 'periodcentered', 'afii10071', 'afii61352', 'afii10101',
        'guillemotright', 'afii10105', 'afii10054', 'afii10102', 'afii10104',
        'afii10017', 'afii10018', 'afii10019', 'afii10020', 'afii10021',
        'afii10022', 'afii10024', 'afii10025', 'afii10026', 'afii10027',
        'afii10028', 'afii10029', 'afii10030', 'afii10031', 'afii10032',
        'afii10033', 'afii10034', 'afii10035', 'afii10036', 'afii10037',
        'afii10038', 'afii10039', 'afii10040', 'afii10041', 'afii10042',
        'afii10043', 'afii10044', 'afii10045', 'afii10046', 'afii10047',
        'afii10048', 'afii10049', 'afii10065', 'afii10066', 'afii10067',
        'afii10068', 'afii10069', 'afii10070', 'afii10072', 'afii10073',
        'afii10074', 'afii10075', 'afii10076', 'afii10077', 'afii10078',
        'afii10079', 'afii10080', 'afii10081', 'afii10082', 'afii10083',
        'afii10084', 'afii10085', 'afii10086', 'afii10087', 'afii10088',
        'afii10089', 'afii10090', 'afii10091', 'afii10092', 'afii10093',
        'afii10094', 'afii10095', 'afii10096', 'afii10097'
    )

    def __init__(self, path_dir, product_lists):
        # we need to give table and table_info here,
        # because if set it like simple class atribute it will
        # rewrite old data, and if we will want to do many pdf docs 
        # we will get old data instead of new data
        # lines coords for table
        self.table = [
                #out
                [15,785,248,785], # top horizontal line
                [15,660,248,660], # bottom horizontal line
                [15,785,15,660], # left horizontal line
                [248,785,248,660], # right horizontal line
                #in
                [18,782,245,782], # top horizontal line
                [18,663,245,663], # bottom horizontal line
                [18,782,18,663], # left horizontal line
                [245,782,245,663] # right horizontal line
                ]

        # coords for table info
        self.table_i = {
                'name': [128, 750],
                'price_str': [28, 700],
                'currency': [220, 700],
                'firm': [19, 667],
                'barcode': [128, 687],
                'date_str': [148, 667],
                'date': [202, 667],
                'price': [215, 702],
                'total': [242, 677]
                }

        # Replace glyphs from code 128 to code 256 with cp1251 values
        for i in range(128, 256):
            self.cyrenc[i] = self.cp1251[i-128]

        # Register newly created encoding
        pdfmetrics.registerEncoding(self.cyrenc)

        # Register type face
        pdfmetrics.registerTypeFace(self.cyrFace)

        # Register the font with adding '1251' to its name
        pdfmetrics.registerFont(pdfmetrics.Font(self.faceName+'1251', self.faceName, 'CP1251'))

        self.today = datetime.date.today().strftime('%d.%m.%Y')

        self.product_lists = product_lists

        self.canvas = canvas.Canvas(path_dir, pagesize=letter)
        self.canvas.setLineWidth(.1)
        self.canvas.setFont('Helvetica', 12)

        self.gen()

    def gen(self):
        """
        generage pdf file
        """
        for x, prod in enumerate(self.product_lists, 1):
            # set table info
            assert prod['po_name'] is not None
            assert prod['po_bar_code'] is not None
            assert prod['po_price_vat'] is not None
            assert prod['po_kg_price_vat'] is not None

            self.canvas.setFont(self.faceName+'1251', 14)
            
            self.canvas.drawCentredString(self.table_i['name'][0],
                                        self.table_i['name'][1],
                                        prod.get('po_name', 'unknown'))

            self.canvas.setFont('Helvetica-Bold', 14)
            self.canvas.drawString(self.table_i['price_str'][0],
                                self.table_i['price_str'][1],
                                'Pret:')
            self.canvas.drawString(self.table_i['currency'][0],
                                self.table_i['currency'][1],
                                'LEI')

            self.canvas.setFont('Helvetica', 8)
            self.canvas.drawString(self.table_i['firm'][0],
                                self.table_i['firm'][1],
                                'I.M "Tirex-Petrol" SA')
            self.canvas.drawRightString(self.table_i['barcode'][0],
                                        self.table_i['barcode'][1],
                                        '*{}*'.format(prod.get(
                                                    'po_bar_code', 'unknown')))
            self.canvas.drawString(self.table_i['date_str'][0],
                                self.table_i['date_str'][1],
                                'Data emiterii : ')
            self.canvas.drawString(self.table_i['date'][0],
                                self.table_i['date'][1],
                                self.today)
            
            self.canvas.setFont('Helvetica', 34)
            self.canvas.drawRightString(self.table_i['price'][0],
                                        self.table_i['price'][1],
                                        '{:.2f}'.format(prod.get(
                                                            'po_price_vat', 0)))

            self.canvas.setFont('Helvetica', 11)
            self.canvas.drawRightString(self.table_i['total'][0],
                                        self.table_i['total'][1],
                                        '1 kg/l = {:.2f}'.format(prod.get(
                                                        'po_kg_price_vat', 0)))

            # create lines first four from table are for out table
            for i, (x1, y1, x2, y2) in enumerate(self.table):
                if i < 4:
                    self.canvas.setLineWidth(.1)
                else:
                    self.canvas.setLineWidth(1.5)
                self.canvas.line(x1,y1,x2,y2)

            # if we create 12 tables we need to create another page
            if x % 12 == 0:
                self.canvas.showPage()

            # after all 6 create table we check , if table[0][0] is 365 that
            # means that we end to create 6 table from right side, and we need
            # to create the first table from left side
            if x % 6 == 0:
                # if table[0][0] == 365 this is mean that we create 6 tables
                # from right we need now to go to top left to start to create
                # one table from left side
                if self.table[0][0] == 365:
                    # draw first table from right side
                    for i, subtables in enumerate(self.table):
                        self.table[i][0] -= 350
                        self.table[i][1] += 780
                        self.table[i][2] -= 350
                        self.table[i][3] += 780

                    #start to draw first table_info for top left side
                    for info in self.table_i.values():
                        info[0] -= 350
                        info[1] += 780
                else:
                    # draw first table from top left side
                    for i, subtables in enumerate(self.table):
                        self.table[i][0] += 350
                        self.table[i][1] += 780
                        self.table[i][2] += 350
                        self.table[i][3] += 780

                    #start to draw first table_info for top right side
                    for info in self.table_i.values():
                        info[0] += 350
                        info[1] += 780

            # go down and draw table
            for i, subtables in enumerate(self.table):
                self.table[i][1] -= 130
                self.table[i][3] -= 130

            # go down and draw table_info
            for info in self.table_i.values():
                info[1] -= 130

        # save pdf file
        self.canvas.save()

    @classmethod
    def from_bytes_io(cls, products):
        buff = BytesIO()
        cls(buff, products)
        cls.pdf = buff.getvalue()
        buff.close()

        return cls
