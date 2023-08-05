'''
--------------------------------------------------------------------------
Copyright (C) 2017-2018 Lukasz Laba <lukaszlab@o2.pl>

This file is part of DxfStructure (structural engineering dxf drawing system).

DxfStructure is free software; you can redistribute it and/or modify
it under the terms of the GNU General Public License as published by
the Free Software Foundation; either version 2 of the License, or
(at your option) any later version.

DxfStructure is distributed in the hope that it will be useful,
but WITHOUT ANY WARRANTY; without even the implied warranty of
MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
GNU General Public License for more details.

You should have received a copy of the GNU General Public License
along with Foobar; if not, write to the Free Software
Foundation, Inc., 51 Franklin St, Fifth Floor, Boston, MA  02110-1301  USA
--------------------------------------------------------------------------
'''

import re

#-----regular expresion for 'Element Bk1 x 2.5 mb' ------

re_text = re.compile('\A\s*(Element )*\s*([a-zA-Z0-9_-]*)\s*x\s*([0-9.]+)\s*(\D*)\s*\Z')
                  
def has_correct_format(text):
    if re_text.search(text):
        return True
    else:
        return False

def data_get(text):
    if has_correct_format(text):
        data = re_text.findall(text)[0]
        #---
        Name = data[1] 
        Number = float(data[2])
        InMeterLength = (data[3] in ['mb', 'lm'])
        #---
        return { 'Number':Number, 'Name':Name, 'InMeterLength':InMeterLength }
    else:
        return None

# Test if main        
if __name__ == "__main__":
    print has_correct_format('Element sc-1 x 20.5 mb')
    print has_correct_format('sc-1 x 20.5 mb')
    print has_correct_format('   sc-1 x 20.5 mb   ')
    print has_correct_format('sc-1 x 20.5')
    print '========'
    test_text = 'Element sc-1 x 20.5 mb'
    print has_correct_format(test_text)
    print data_get(test_text)