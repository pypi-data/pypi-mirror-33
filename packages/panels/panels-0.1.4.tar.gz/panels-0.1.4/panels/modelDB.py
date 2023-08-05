r"""
Used to configure the main parameters for each implemented model.

.. currentmodule:: panels.modelDB


"""
from __future__ import absolute_import

from .models import *


db = {
    #'coneshell_clpt_donnell_bardell': {
                    #'linear static': True,
                    #'linear buckling': True,
                    #'non-linear static': False,
                    #'field': clpt_bardell_field,
                    #'matrices_num': coneshell_clpt_donnell_bardell_num,
                    #'dofs': 3,
                    #'e_num': 6,
                    #'num': 3,
                    #},
    'cylshell_clpt_donnell_bardell': {
                    'linear static': True,
                    'linear buckling': True,
                    'non-linear static': True,
                    'field': clpt_bardell_field,
                    'matrices_num': cylshell_clpt_donnell_bardell_num,
                    'dofs': 3,
                    'e_num': 6,
                    'num': 3,
                    },
    'plate_clpt_donnell_bardell': {
                    'linear static': True,
                    'linear buckling': True,
                    'non-linear static': True,
                    'field': clpt_bardell_field,
                    'matrices_num': plate_clpt_donnell_bardell_num,
                    'dofs': 3,
                    'e_num': 6,
                    'num': 3,
                    },
    'bladestiff1d_clpt_donnell_bardell': {
                    'linear static': True,
                    'linear buckling': True,
                    'non-linear static': False,
                    'field': clpt_bardell_field,
                    'matrices': bladestiff1d_clpt_donnell_bardell,
                    'connections': bladestiff1d_clpt_donnell_bardell,
                    'matrices_num': None,
                    'dofs': 3,
                    'e_num': 6,
                    'num': 3,
                    },
    'bladestiff2d_clpt_donnell_bardell': {
                    'linear static': True,
                    'linear buckling': True,
                    'non-linear static': False,
                    'field': clpt_bardell_field,
                    'matrices': bladestiff2d_clpt_donnell_bardell,
                    'connections': bladestiff2d_clpt_donnell_bardell,
                    'matrices_num': None,
                    'dofs': 3,
                    'e_num': 6,
                    'num': 3,
                    },
    }
