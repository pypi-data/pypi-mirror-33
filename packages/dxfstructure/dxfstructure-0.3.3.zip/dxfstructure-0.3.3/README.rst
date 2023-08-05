DxfStructure - structural engineering dxf drawing system                
--------------------------------------------------------

Changelog 
---------
0.3.3(beta)
 - hot fix - centre ignore for in meter bars
 - full backward compatibility

0.3.2(beta)
 - range pline endmark trick
 - range and bar pline intersection detection fixed
 - app window layout improved
 - full backward compatibility

0.3.1(beta)
 - check for quite similar bars number option added
 - color system updated
 - bar schedule format updated - shape column added
 - language version option added
 - in meter length element and bar available
 - possibility to define bar quantity as expression e.g 2*2#12-[4]
 - bar with forced straight shape in schedule
 - full backward compatibility

0.2.4(alpha)
 - updated to ezdxf 0.8.8
 - full backward compatibility

0.2.3(alpha)
 - profil anotation syntax changed to  4x(1)-IPE 300-1200-S235
 - full backward compatibility

0.2.2(alpha)
 - bar shape anotation changed to look like e.g. [1] - #12 L=2120
 - steel setion database list updated

0.2.1(alpha)
 - main features for steel implemented
 - command feature added

0.1(alpha)
 - main features for concrete implemented

0.0.2 (alpha)
 - first PyPI version

Prerequisites
-------------

1. Python 2.7.
2. Non-standard Python library needed

 - dxfstructure (https://pypi.python.org/pypi/dxfstructure)
 - strupy (https://pypi.python.org/pypi/strupy)
 - ezdxf (https://pypi.python.org/pypi/ezdxf)
 - strupypyqt4 (https://www.riverbankcomputing.com/software/pyqt)
 - tabulate (https://pypi.python.org/pypi/tabulate)
 - mistune (https://pypi.python.org/pypi/mistune)

Installation 
------------

After the Python and needed libraries  was installed use pip by typing:

	pip install dxfstructure

There is install instruction on project website.
To run dxfstructure execute dxfstructure.py from installed dxfstructure
package folder - probably it is "C:\Python27\Lib\site-packages\dxfstructure"
For easy run make shortcut on your system pulpit to this file.

Windows (7) and Linux (xubuntu, fedora) tested.

License 
-------

Copyright (C) 2017-2018 Lukasz Laba

Dxfstructure is distributed under the terms of GNU General Public License

The full license can be found in 'license.txt'


Other information
-----------------

Project website: https://bitbucket.org/lukaszlaba/dxfstructure/wiki/Home

E-mail : lukaszlab@o2.pl