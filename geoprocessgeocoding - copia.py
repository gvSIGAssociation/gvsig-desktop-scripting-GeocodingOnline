# encoding: utf-8


import gvsig
from gvsig import commonsdialog
from gvsig import geom
from gvsig.libs.toolbox import *
from es.unex.sextante.core import OutputObjectsSet
from es.unex.sextante.outputs import OutputVectorLayer
from es.unex.sextante.outputs import FileOutputChannel
from geopy.geocoders import get_geocoder_for_service
 
   
class Geocoding(ToolboxProcess):
  """Tabla con campo direccion a shape file"""
  def defineCharacteristics(self):
    """
En esta operacion debemos definir los parametros de netrada y salida que va a precisar nuetro proceso.
    """
    # Fijamos el nombre con el que se va a mostrar nuestro proceso
    self.setName("Geocodificacion")
    
    # Indicamos el grupo en el que aparecera
    self.setGroup("Herramientas de geocodificacion")
        
    params = self.getParameters()
    # Indicamos que precisamos un parametro LAYER, del tipo punto y que es obligatorio
    #params.addInputVectorLayer("LAYER","Caoa de entrada", SHAPE_TYPE_POINT,True)
    # Indicamos que precisamos un par de valores numericos, X e Y 
    #params.addNumericalValue("X", "X_traslation",0, NUMERICAL_VALUE_DOUBLE)
    #params.addNumericalValue("Y", "Y_traslation", 0, NUMERICAL_VALUE_DOUBLE)
    
    # http://geopy.readthedocs.io/en/latest/
    params.addSelection("GEOLOCATOR", "Seleciona Geocoder", ['googlev3','google','arcgis', 'yandex', 'databc'])
    params.addInputTable("TABLE", "Tabla de direcciones", True)
    params.addTableField("DIRECTION", "Campo de direcciones", "TABLE", True)
    
    # Y por ultimo indicamos que precisaremos una capa de salida de puntos.
    self.addOutputVectorLayer("RESULT_POINT", "Geocoding_point", SHAPE_TYPE_POINT)
    
    self.setUserCanDefineAnalysisExtent(False)
    

  def processAlgorithm(self):
    """
Esta operacion es la encargada de realizar nuetro proceso.
    """
    features=None
    #try:
    """
    Recogemos los parametros y creamos el conjunto de entidades asociadas a la capa
    de entrada.
    """
    params = self.getParameters()
    table = params.getParameterValueAsTable("TABLE")
    field = params.getParameterValueAsInt("DIRECTION")
    service = params.getParameterValueAsString("GEOLOCATOR")
    filename = self.getOutPutFile("RESULT_POINT")
    
    if filename == "#":
        filename = gvsig.getTempFile("geocodif", ".shp")
    print "filename: ", filename
    print "table type: ", type(table.getBaseDataObject())
    print "##"
    input_store = table.getBaseDataObject().getFeatureStore()

    features = input_store.getFeatureSet()
    featureType = features.getDefaultFeatureType()
    newFeatureType = gvsig.createFeatureType(featureType)
    newFeatureType.append("GEOMETRY", "GEOMETRY")
    newFeatureType.get("GEOMETRY").setGeometryType(geom.POINT, geom.D2)
    output_shape = gvsig.createShape(newFeatureType, filename, CRS="EPSG:4326")
    """
    Generamos la capa de salida con la misma estructura que la capa de entrada
    """
    output_store = output_shape.getFeatureStore()
    output_shape.edit()
    #output_store = self.buildOutPutStore(
    #  featureType, 
    #  SHAPE_TYPE_POINT,
    #  "Geocoding_point",
    #  "RESULT_POINT"
    #)
    print "output crs: ", self.getOutputCRS()

    """
    Nos recorremos todas las entidades de entrada, y creamos las de salida desplazando la geometria
    en los valores indicados por la X e Y de los parametros.
    """
    self.setRangeOfValues(0,features.getSize())
    #Locator geocoder
    
    geolocator = get_geocoder_for_service(service)
    
    for feature in features: #.iterator():
      
      if self.isCanceled():
        # Si el usuario indico que quiere cancelar el proceso abortamos.
        print "Proceso cancelado"
        break
      
      # Incrementamos el progreso de nuestro proceso.
      self.next()

      # Get direction coordinates
      address = feature.get(field)
      location = geolocator().geocode(address)

      try:
          y = location.latitude
          x = location.longitude
      except Exception as inst:
          print "Geolocator error: ", inst
          x = 0
          y = 0
      
      #print"Direccion: ", (location.address), "Coordenadas: ", ((x, y))

      # Creamos una nueva entidad para nuestro almacen de salida.
      newfeature = self.createNewFeature(output_store, feature)
      
      # Desplazamos la geometria de la nueva entidad
      fgeom = geom.createPoint(geom.D2, x, y)
      newfeature.set("GEOMETRY", fgeom)
      
      # Guardamos la nueva entidad
      output_store.insert(newfeature)

    # Cuando hemos terminado de recorrernos las entidades terminamos la edicion.
    #output_store.finishEditing()
    output_shape.commit()
    #except Exception as inst:
    #    print "Geocoding error: ", inst
    #finally:
    DisposeUtils.disposeQuietly(features)
    #  print "Proceso terminado %s" % self.getCommandLineName() 
    
    newOutputObjectsSet = OutputObjectsSet()
    outputObject = OutputVectorLayer()
    outputObject.setOutputChannel(FileOutputChannel(filename))
    outputObject.setName("Geocodificacion")
    #outputObject.setShapeType()
    newOutputObjectsSet.add(outputObject)
    
    self.setOutputObjects(newOutputObjectsSet)
    return True
    

def main(*args):
    # Creamos nuesto geoproceso
    process = Geocoding()
    # Lo registramos entre los procesos disponibles en el grupo de "Scripting"
    process.selfregister("Scripting")
    # Actualizamos el interface de usuario de la Toolbox
    process.updateToolbox()
    commonsdialog.msgbox("Incorporado el script '%s/%s/%s' a la paleta de geoprocesos." % (
        "Scripting",
        process.getGroup(),
        process.getName()
      )
    )
    print "hola"
