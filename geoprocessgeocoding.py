# encoding: utf-8
#desdegvsig àìñ

import gvsig
from gvsig import commonsdialog
from gvsig import geom
from gvsig.libs.toolbox import *
from es.unex.sextante.core import OutputObjectsSet
from es.unex.sextante.outputs import OutputVectorLayer
from es.unex.sextante.outputs import FileOutputChannel
from geopy.geocoders import get_geocoder_for_service
import ssl


class Geocoding(ToolboxProcess):
  """Tabla con campo direccion a shape file"""
  
  def defineCharacteristics(self):
    """Definir los parametros de entrada y salida"""
    # Fijamos el nombre con el que se va a mostrar nuestro proceso
    self.setName("Geocodificacion Online: direcciones a puntos")
    
    # Indicamos el grupo en el que aparecera
    self.setGroup("Herramientas de geocodificacion")
    self.setDescription("Herramienta para geocodificacion de tablas con un campo de direccion en geometrias de tipo punto")
        
    params = self.getParameters()
    
    # Indicamos que precisamos un parametro LAYER, del tipo punto y que es obligatorio
    
    # http://geopy.readthedocs.io/en/latest/
    params.addSelection("GEOLOCATOR", "Seleciona Geocoder", ['googlev3', 'arcgis', 'google', 'yandex', 'photon', 'databc', 'liveaddress','nominatim'])
    params.addInputTable("TABLE", "Tabla de direcciones", True)
    params.addString("STRING_PREFIX", "Agregar prefijo","")
    params.addString("STRING_SUFFIX", "Agregar sufijo","")
    params.addTableField("ADDRESS", "Campo de direcciones", "TABLE", True)
    params.addBoolean("ADD_NOT_FOUND", "Agregar direcciones no encontradas", False)
    
    #params.addFixedTable("PARAMS_TABLE", "Tabla de parametros", ["Param","Key"], 1, False) 
    #table = params.getParameter("PARAMS_TABLE")
    #table.setParameterValue(MyFixedTableModel(params.getParameter("GEOLOCATOR")))
    
    # Y por ultimo indicamos que precisaremos una capa de salida de puntos.
    self.addOutputVectorLayer("RESULT_POINT", "Geocoding_point", SHAPE_TYPE_POINT)
    self.addOutputTable("ERROR_TABLE", "Tabla de errores")
    self.setUserCanDefineAnalysisExtent(False)
    

  def processAlgorithm(self):

    features=None
    try:
      """
      Recogemos los parametros y creamos el conjunto de entidades asociadas a la capa
      de entrada.
      """
      params = self.getParameters()
      table = params.getParameterValueAsTable("TABLE")
      field = params.getParameterValueAsInt("ADDRESS")
      service = params.getParameterValueAsString("GEOLOCATOR")
      string_prefix = params.getParameterValueAsString("STRING_PREFIX")
      string_suffix = params.getParameterValueAsString("STRING_SUFFIX")
      add_not_found = params.getParameterValueAsBoolean("ADD_NOT_FOUND")
      #params_table = params.getParameterValueAsArrayList("PARAMS_TABLE")[0]

      
      if string_prefix != "" or string_suffix != "":
          set_string_format = True
      else: 
          set_string_format = False

      input_store = table.getBaseDataObject().getFeatureStore()
      features = input_store.getFeatureSet()
      featureType = features.getDefaultFeatureType()
      """
      Generamos la capa de salida con la misma estructura que la capa de entrada
      """
  
      output_store = self.buildOutPutStore(
        featureType, 
        SHAPE_TYPE_POINT,
        "Geocoding_point",
        "RESULT_POINT"
      )
      #tabla errores
      
      #output_table = self.buildOutPutStore(
      #  featureType, 
      #  SHAPE_TYPE_POINT,
      #  "Geocoding_point",
      #  "RESULT_POINT"
      #)
      filename = self.getOutPutFile("ERROR_TABLE")
      if filename == "#":
          import datetime
          now = datetime.datetime.now()
          
          filename = gvsig.getTempFile("Error_geocoding"+ "_" + str(now.hour)+"-"+str(now.minute), ".dbf")
      table_schema = gvsig.createFeatureType(featureType)
      dbf = gvsig.createDBF(table_schema, DbfFile=filename) 
      dbf_store = dbf.getFeatureStore()
      dbf_store.edit()
      
      
      # Establecemos la proyeccion de la capa de salida
      #parameters = output_store().getParameters()
      #parameters.setCRS("EPSG:4326")
      # Se transforma las geometrias a la vista

      # Barra de progreso
      self.setRangeOfValues(0, features.getSize())
      
      #Locator geocoder
      geolocator = get_geocoder_for_service(service)
      
      # Reprojection
      crs_input = gvsig.getCRS("EPSG:4326")
      crs_output = gvsig.currentView().getProjection()
      ICoordTrans1 = crs_input.getCT(crs_output)
      for feature in features: #.iterator():
        
        if self.isCanceled():
          # Si el usuario cancela el proceso
          print "Proceso cancelado"
          break
        
        # Incrementamos el progreso de nuestro proceso.
        self.next()
  
        # Get direction coordinates
        address = feature.get(field)
        
        if set_string_format:
            address = "".join([string_prefix,address,string_suffix])

        location = geolocator().geocode(address)
        # Seria solo en fallo

        try:
            y = location.latitude
            x = location.longitude

        except Exception as inst:
            print "Geolocator error: ", inst
            newdbffeature = self.createNewFeature(dbf_store, feature)
            dbf_store.insert(newdbffeature)
            if add_not_found:
                print "Setting geometry values to: 0, 0"
                x = 0
                y = 0
            else:
                print "Processing next feature"
                continue
        
        #print"Direccion: ", (location.address), "Coordenadas: ", ((x, y))
  
        # Creamos una nueva entidad para nuestro almacen de salida.
        newfeature = self.createNewFeature(output_store, feature)
        
        # Desplazamos la geometria de la nueva entidad
        fgeom = geom.createPoint(geom.D2, x, y)
        fgeom.reProject(ICoordTrans1)
        newfeature.set("GEOMETRY", fgeom)
        
        # Guardamos la nueva entidad
        output_store.insert(newfeature)
  
      # Cuando hemos terminado de recorrernos las entidades terminamos la edicion.
      output_store.finishEditing()
      dbf_store.finishEditing()
      try:
          #if dbf_store.getFeatureSet().getCount() > 0:
          gvsig.loadDBF(filename)
      except Exception as inst:
          print "Table loading: ", inst
          pass

    except Exception as inst:
      print "Geocoding error: ", inst
    finally:
      DisposeUtils.disposeQuietly(features)
      print "Proceso terminado %s" % self.getCommandLineName() 
    
    return True
    

def main(*args):
    # Creamos nuesto geoproceso
    process = Geocoding()
    print "Commandline: ", process.getCommandLineHelp()
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
    print "** Proceso cargado **"
