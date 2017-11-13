# encoding: utf-8

import gvsig
import os

open(os.path.normpath(os.path.join(__file__,"..","..", "__init__.py")), "a").close()

from addons.GeocodingPlugin.geoprocessgeocoding import Geocoding

def main(*args):

    process = Geocoding()
    # Lo registramos entre los procesos disponibles en el grupo de "Scripting"
    process.selfregister("Scripting")
    # Actualizamos el interface de usuario de la Toolbox
    process.updateToolbox()
