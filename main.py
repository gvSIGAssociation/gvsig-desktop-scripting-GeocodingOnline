# encoding: utf-8

import gvsig
from gvsig import commonsdialog
from gvsig import geom

from geopy.geocoders import get_geocoder_for_service
from geopy.geocoders import ArcGIS, DataBC, Nominatim
import geopy
reload(geopy)
import ssl

def example(*args):
 
    # Google v3: de direccion a coordenadas
    #address = commonsdialog.inputbox("Search Address", "Search Address",1)
    address = "Carrer del Metge Gomez Ferrer, Sedavi, Valencia"
    address = "Gallo, Potsdamer Platz, Tiergarten, Mitte, Berlin, 10785, Deutschland"
    print address
    #geocoders = ["googlev3","osm","arcgis","baidu","base","bing","databc","dot_us","geocodefarm","geonames","ignfrance","navidata","opencage","openmapquest","photon","placefinder","smartystreets","what3words","yandex"]
    geocoders = ['geocoderdotus', 'navidata', 'geocodefarm', 'googlev3', 'geonames', 'arcgis', 'placefinder', 'what3words', 'baidu', 'google', 'bing', 'openmapquest', 'ignfrance', 'nominatim', 'opencage', 'yandex', 'yahoo', 'databc', 'liveaddress']
    working = ['nominatim','googlev3', 'arcgis', 'google', 'yandex', 'photon', 'databc', 'liveaddress']
    working = ['what3words']
    for g in working:
        try:
            geolocator = get_geocoder_for_service(g)
            #ssl.get_server_certificate(("nominatim.openstreetmap.org",5432))
            #location = geolocator().reverse("52.509669, 13.376294")
            #print location.address
            
            location = geolocator("S8BXNPN4").geocode(address)
            print"\tService:", g, "Coordenadas: ", ((location.latitude, location.longitude))
            #print "\t\t", location.address
        
        except Exception as inst:
            print "\tService:", g, "Fail! -- ", inst
            
 
    #geomPoint = geom.createPoint(geom.D2, location.longitude, location.latitude)
    #gvsig.currentView().centerView(geomPoint.getEnvelope())
 
def main(*args):
    print "hole"
    example()

    #crs_input = gvsig.getCRS("EPSG:4326")
    #crs_output = gvsig.currentView().getProjection()
    
    #print crs_output, type(crs_output)
    #print crs_input, type(crs_input)
    #ICoordTrans1 = crs_input.getCT(crs_output)
    pass
    