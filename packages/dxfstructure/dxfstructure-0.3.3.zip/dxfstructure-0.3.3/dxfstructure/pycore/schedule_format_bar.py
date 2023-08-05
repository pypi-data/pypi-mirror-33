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

from tabulate import tabulate

language = 'PL'

def get_available_languages():
    return ['PL', 'EN']

def set_language(newlanguage='PL'):
    global language
    if newlanguage in get_available_languages():
        language = newlanguage

def title():
    if language == 'EN':
        title =      'BAR SCHEDULE'
    if language == 'PL':
        title =      'ZESTAWIENIE PRETOW ZBROJENIOWYCH'
    print language
    return title

def header():
    if language == 'EN':
        header_1 =      ['Element',  'Bar',   'Steel',      'Bar',      'Bar',       'Bar',       'Bar',       'Number',    'Number of bars',    'Total',     'Total',   'Total']
        header_2 =      [      '',   'mark',  'type',    'diameter',    'length',    'shape',     'mass',    'of elements',   'in element',     'number',    'length',    'mass']
        header_3 =      [   '   ',    '   ',   '   ',      '   ',       '[mm]',       '   ',      '[kg]',      '   ',            '   ',           '   ',      '[m]',      '[kg]']
    if language == 'PL':
        header_1 =      ['Element',  'Poz.',   'Typ',      'Sred.',      'Dl.',      'Ksztalt',         'Masa',       'Ilosc',   'Pretow',     'Laczna',     'Laczna',   'Laczna']
        header_2 =      [      '',    'nr',   'stali',     'preta',     'preta',      'preta',       'preta',       'elem.',   'w elem.',    'ilosc',      'dl.',       'masa']
        header_3 =      [   '   ',    '   ',   '   ',      '   ',       '[mm]',        '   ',        '[kg]',         '   ',     '   ',        '   ',       '[m]',      '[kg]']
    return [header_1, header_2, header_3]

def breake_mark():
    return [len(header()[0]) * ['---']]

def record(bar):
    #---Member
    Member = bar.element.name
    #---Bar_mark
    Bar_mark = bar.Mark
    #---Steel_type
    Steel_type = bar.Grade
    #---Bar_diameter
    Bar_diameter = bar.Size
    #---Bar_length
    Bar_length = bar.Length
    if bar.is_cut_on_site() or bar.is_in_meters():
        if bar.is_cut_on_site():
            Bar_length = str(round(bar.Length / 1000.0, 2))
        if bar.is_in_meters():
            Bar_length = str(int(bar.Length / 1000.0))      
        if language == 'EN':
            Bar_length += 'lm'
        if language == 'PL':
            Bar_length += 'mb'
    #---Bar_shape
    if language == 'EN':
        if bar.is_straight():Bar_shape = 'straight'
        else:Bar_shape = 'acc. dwg'
    if language == 'PL':
        if bar.is_straight():Bar_shape = 'prosty'
        else:Bar_shape = 'wg rys.'
    #---Bar_mass
    Bar_mass = bar.Mass
    #---Number_of_members
    Number_of_members = bar.element.quantity
    if bar.element.is_in_meter_length:
        Number_of_members = str(Number_of_members)
        if language == 'EN':
            Number_of_members += 'lm'
        if language == 'PL':
            Number_of_members += 'mb'
    #---Number_of_bars_in_element  
    Number_of_bars_in_element = bar.Number_In_One_Element
    #---Total_number
    Total_number = bar.Number_In_All_Elements
    #---Total_length
    Total_length = bar.Length_In_All_Elements / 1000.0
    Total_length = round(Total_length, 2)
    #---Total_mass
    Total_mass = round(bar.Mass_In_All_Elements, 2)
    #---
    record =[ Member,   Bar_mark,   Steel_type,   Bar_diameter,   Bar_length, Bar_shape,  Bar_mass, Number_of_members,  Number_of_bars_in_element,   Total_number,  Total_length, Total_mass]
    return [record]

def summary():
    if language == 'EN':
        sumary =      'TOTAL MASS FOR DRAWING :'
    if language == 'PL':
        sumary =      'CALKOWITA MASA DLA RYSUNKU :'
    return sumary

# Test if main        
if __name__ == "__main__":
    from environment import*
    DRAWING.open_file()
    SCANER.load_data_to_model()
    print tabulate(header(), numalign="right")  
    bar = CONCRETE_MODEL.barlist[3]
    print tabulate(record(bar), numalign="right") 
    print tabulate(header() + record(bar), numalign="right") 