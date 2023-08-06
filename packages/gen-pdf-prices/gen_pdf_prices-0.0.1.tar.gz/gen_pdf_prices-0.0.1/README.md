Module name: script_create_pdf.py

Package: reportlab
Docs: https://www.reportlab.com/docs/reportlab-userguide.pdf

In this module are `GeneratePdf` class, on every init

1) We give to attribute `table` of the class a list with lists of x1,x2,y1,y2 params
this params create table borders, there are two type of borders in, and out:

  +------------------------+   <- out
  |+----------------------+|
  || <- in                ||
  ||                      ||
  ||                      ||
  |+----------------------+|
  +------------------------+

# dont change values of table manualy in __init__: it is default params
  to create first table borders in left top side of pdf page
# or change it if you know what do to
example : of params 
table = [
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


2) We give to attribute `table_info` of the class params where will be setup our 
    table information

Default table information are in this position, also created in
left top side of the pdf page

# coords for table info
self.table_info = {
    # key : value[x1,x2]
    'name': [128, 750],
    'price_str': [28, 700],
    'currency': [220, 700],
    'firm': [19, 667],
    'barcode': [128, 687],
    'date_str': [152, 667],
    'date': [202, 667],
    'price': [215, 702],
    'total': [242, 677]
}

### Important ### this default values are in __init__ method, they are given by default when class are init,
   don't move this default values from __init__ method to simple class attributes, because we will rewrite this values in gen() method
   and if this values will be in class attributes but not in __init__ method wi will take not default params, but changed params that was 
   changed last time.

3) init params
  3.1) path_dir: where to save PDF file
  3.2) product_list: a list of product objects
       product_lists example:
       [{
        'name': 'Dorna',
        'barcode': 2345,
        ....
       }]

4) call gen() method

How it works:
  we use for loop statment to go through all `product_lists`,
  draw first table_info with default params and also draw first table borders ( this will be on top left side )
  
  in for statment we check if `x` # x is the number of current product object in for statment, 
  if `x % 12 == 0` this mean that if `x == 12` we already create 12 tables and we need to create another
  pdf page to continue our table draws, for this we execute `canvas.showPage()` method, it will create another
  clear pdf page where we need to draw() another tables, 

  another if is `x % 6 == 0` this means that if `x == 6` we need to create a table on the top, but how we know what 
  table we need to draw ? on the left side or on the right side, for this in this if statment we have another 
  if statment, where we check if `table[0][0] == 365` that means that we already created the top right side table
  and now we need to create a left one, if `table[0][0] != 365` we create a table on top left side

  after this checks on each iteration we go down and draw our table borders and table info 

  save() it and it is all.

  Total: we have 6 table on the left side and 6 on ther right side
