Vroom: license plate parser
=========================================================

**vroom** provides tools for identifying license plates in text.


Basic usage
-----------

.. code:: python

    from vroom import plates_parser

    parser = plates_parser.Parser()
    
    plates_string = "Lorem ipsum SY12345 dolor sit amet, SK 1A234 consectetur adipiscing elit STA12AA"
    found_plates = parser.findall_plates(plates_string)
    print(found_plates)
    
    single_plate = "SY12345"
    plate_info = parser.match_plate(single_plate)
    print(single_plate)


Currently supported countries
-----------------------------

* Poland [PL] (`source <http://prawo.sejm.gov.pl/isap.nsf/download.xsp/WDU20120000585/O/D20120585.pdf>`_)