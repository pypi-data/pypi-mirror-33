# -*- coding: utf-8 -*-
#
# This file is part of the pyFDA project hosted at https://github.com/chipmuenk/pyfda
#
# Copyright © pyFDA Project Contributors
# Licensed under the terms of the MIT License
# (see file LICENSE in root directory for details)
# -*- coding: utf-8 -*-

"""
Common settings for some IIR filter types (Cheby1, Cheby2, Ellip, EllipZero, MA)
"""
from __future__ import print_function, division, unicode_literals, absolute_import

class Common(object):
    
    def __init__(self):
                      
        self.rt_base_iir = {
            'COM':{'man':{'fo': ('a', 'N')},
                   'min':{'fo': ('d', 'N'),
                          'msg':('a',
                   "Enter maximum pass band ripple <b><i>A<sub>PB</sub></i></b>, "
                    "minimum stop band attenuation <b><i>A<sub>SB</sub> </i></b>"
                    "&nbsp;and the corresponding corner frequencies of pass and "
                    "stop band(s), <b><i>F<sub>PB</sub></i></b>&nbsp; and "
                    "<b><i>F<sub>SB</sub></i></b> .")
                        }
                    },
            'LP': {'man':{'fspecs': ('a','F_C'),
                          'tspecs': ('u', {'frq':('u','F_PB','F_SB'), 
                                           'amp':('a','A_PB','A_SB')})
                          },
                   'min':{'fspecs': ('d','F_C'),
                          'tspecs': ('a', {'frq':('a','F_PB','F_SB'), 
                                           'amp':('a','A_PB','A_SB')})
                        }
                },
            'HP': {'man':{'fspecs': ('a','F_C'),
                          'tspecs': ('u', {'frq':('u','F_SB','F_PB'), 
                                           'amp':('a','A_SB','A_PB')})
                         },
                   'min':{'fspecs': ('d','F_C'),
                          'tspecs': ('a', {'frq':('a','F_SB','F_PB'), 
                                           'amp':('a','A_SB','A_PB')})
                         }
                    },
            'BP': {'man':{'fspecs': ('a','F_C', 'F_C2'),
                          'tspecs': ('u', {'frq':('u','F_SB','F_PB','F_PB2','F_SB2'), 
                                           'amp':('a','A_SB','A_PB')})
                         },
                   'min':{'fspecs': ('d','F_C','F_C2'),
                          'tspecs': ('a', {'frq':('a','F_SB','F_PB','F_PB2','F_SB2'), 
                                           'amp':('a','A_SB','A_PB')})
                         },
                    },
            'BS': {'man':{'fspecs': ('a','F_C','F_C2'),
                          'tspecs': ('u', {'frq':('u','F_PB','F_SB','F_SB2','F_PB2'), 
                                           'amp':('a','A_PB','A_SB')})
                          },
                   'min':{'fspecs': ('d','F_C','F_C2'),
                          'tspecs': ('a', {'frq':('a','F_PB','F_SB','F_SB2','F_PB2'), 
                                           'amp':('a','A_PB','A_SB')})
                        }
                }
            }
        


#------------------------------------------------------------------------------

if __name__ == '__main__':
    pass    