#!/usr/bin/env python
# -*- coding: utf-8 -*-

##########################################################################
#  
#  Copyright (C) 2011-2016 Dr Adam S. Candy
# 
#  Shingle:  An approach and software library for the generation of
#            boundary representation from arbitrary geophysical fields
#            and initialisation for anisotropic, unstructured meshing.
# 
#            Web: https://www.shingleproject.org
#
#            Contact: Dr Adam S. Candy, contact@shingleproject.org
#
#  This file is part of the Shingle project.
#  
#  Shingle is free software: you can redistribute it and/or modify
#  it under the terms of the GNU General Public License as published by
#  the Free Software Foundation, either version 3 of the License, or
#  (at your option) any later version.
#  
#  Shingle is distributed in the hope that it will be useful,
#  but WITHOUT ANY WARRANTY; without even the implied warranty of
#  MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#  GNU General Public License for more details.
#  
#  You should have received a copy of the GNU General Public License
#  along with Shingle.  If not, see <http://www.gnu.org/licenses/>.
#
##########################################################################

import os
import sys

shingle_path = os.path.realpath(os.path.join(os.path.realpath(os.path.dirname(os.path.realpath(__file__))), os.path.pardir, os.path.pardir, 'shingle'))
sys.path.insert(0, shingle_path)

from Spud import specification

brml = os.path.join(shingle_path, 'unittest', 'data', 'UK_NorthSea_region_opendap.brml')

class TestClass:
    def test_read_model_name(self):
        specification.clear_options()
        specification.load_options(brml)
        assert specification.get_option('/model_name') == 'UK_NorthSea_region_opendap'
        assert specification.option_count('/geoid_surface_representation::NorthSea/brep_component::NorthSea/form::Raster/region') == 3

if __name__ == '__main__':
    t = TestClass()
    for method in [method for method in dir(t) if callable(getattr(t, method)) if not method.startswith('_')]:
        print method
        getattr(t, method)() 

