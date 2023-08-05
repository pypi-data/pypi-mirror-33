# -*- coding: utf-8 -*-
"""
Scrapbag censal file
"""
import os
import structlog
from .csvs import csv_tolist
from .strings import normalizer
from .collections import add_element, force_list, flatten


logger = structlog.getLogger(__name__)
scrapbag_abspath = "/".join(os.path.abspath(__file__).split('/')[:-1])
COMUNIDADES_PATHNAME = os.path.join(scrapbag_abspath, 'assets/comunidades.csv')
PROVINCIAS_PATHNAME = os.path.join( scrapbag_abspath,'assets/provincias.csv')
LOCALIDADES_PATHNAME = os.path.join(scrapbag_abspath, 'assets/municipios.csv')


class IneCensal():
    """
    Construye una clase para interactuar con los datos censales proporcionados 
    por el INE.
    Internamente, almacena una serie de indices con informacion mapeada (e.g 
    mapeo nombre_de_comunidad => codigo_de_comunidad), y proporciona metodos 
    para acceder y recuperar dicha informacion.

    Destaca la propiedad `localidades_by_reference`, con un mapeo no del nombre 
    de las localidades (ya que esta no es unica, existiendo localidades con 
    igual nombre en provincias distintas) sino de un constructo, el nombre de 
    la localidad + nombre de la provicia + nombre de la comunidad, que 
    conjuntamente garantizan unicidad.
    """

    comunidades_by_name = {}
    comunidades_by_code = {}
    provincias_by_name = {}
    provincias_by_code = {}
    localidades_by_reference = {} #we cannot use their names, since they are not unique


    def __init__(self, **kwargs):
        # load official data
        lista_comunidades = csv_tolist(path=COMUNIDADES_PATHNAME, delimiter=';')
        lista_provincias = csv_tolist(path=PROVINCIAS_PATHNAME, delimiter=';')
        lista_localidades = csv_tolist(path=LOCALIDADES_PATHNAME, delimiter=';')

        # generate index for data
        self.comunidades_by_name, self.comunidades_by_code = self.make_index(lista_comunidades)
        self.provincias_by_name, self.provincias_by_code = self.make_index(lista_provincias)
        self.localidades_by_reference = self.make_index_localidades(lista_localidades)




    def make_index(self, lista):
        """
        In ine file data, there are some rows with this pattern,
        'florida, La' that we want to change to 'La florida'
        """
        index = {}
        inverted_index = {}

        # iteramos sobre la lista de comunidades, provinicas... proporionada, 
        # bajo la asuncion de que el primer registro es de headers
        for record in lista[1:]:
            try:
                #record[1] contiene el nombre de la entidad, posiblemente en 
                #dos lenguas cooficiales separadas por '/'
                for toponym in record[1].split('/'):
                    if ',' in toponym: 
                        toponym = " ".join(toponym.split(', ')[::-1])

                index[normalizer(toponym)] = record[0]

                #record[0] contiene el codigo de la entidad
                if record[0] in inverted_index:
                    inverted_index[record[0]] = "/".join([inverted_index[record[0]], normalizer(toponym)])
                else:
                    inverted_index[record[0]] = normalizer(toponym)

            except Exception as ex:
                logger.error('Fail to make index with parsed row data {} - {}'.format(record, ex))

        return index, inverted_index




    def make_index_localidades(self, lista):
        """
        In ine file data, there are some rows with this pattern,
        'florida, La' and we want to change to 'La florida'
        """
        index = {}

        # iteramos sobre la lista de localidades proporionada, bajo la 
        # asuncion de que el primer registro es de headers
        for record in lista[1:]:
            try:
                for toponym in record[4].split('/'):
                    if ',' in toponym: 
                        toponym = " ".join(toponym.replace('/', '-').split(', ')[::-1])

                    toponym = normalizer(toponym)
                    provincia = self.provincias_by_code.get(record[1])
                    comunidad = self.comunidades_by_code.get(record[0])
                    key = "{}/{}/{}".format(toponym, provincia, comunidad)
                    add_element(index, key, "".join(record[1:3]))

            except Exception as ex:
                logger.error('Fail to make index with parsed row data {} - {}'.format(record, ex))

        return index




    def get_codigo_provincia(self, name):
        return self.provincias_by_name.get(name)




    def get_provincia(self, code):
        return self.provincias_by_code.get(str(code))




    def get_codigo_comunidad(self, name):
        return self.comunidades_by_name.get(name)




    def get_comunidad(self, code):
        return self.comunidades_by_code.get(str(code))
    



    def get_codigo_censal(self, name, level=0, index={}, force_check=False, without_codigo_censal=set()):
        """
        """
        try:
            name = force_list(name)

            if not index: index = self.localidades_by_reference

            # assert input name normalizer
            # name_level = normalizer(name[level].replace('/', '-'))
            for name_level in name[level].split('/'):
                name_level = normalizer(name_level)
                codigo_censal = index.get(name_level, None)

                # if not found in dict let search it by string name
                if not codigo_censal:
                    result_key = None
                    search_data = list(index.keys())

                    if "_".join(name[:level+1]) not in without_codigo_censal:

                        for name_word in name_level.split('-'):
                            logger.debug('*Searching {}'.format(name_word))

                            if len(name_word) == 1:
                                continue

                            if not search_data:
                                break

                            for search_name in iter(list(search_data)):
                                if name_word not in search_name:
                                    search_data.remove(search_name)

                            if len(search_data) == 1:

                                # same word lenght
                                if len(search_data[0].split('-')) == len(name_level.split('-')):
                                    result_key = search_data[0]
                                    logger.debug('*** Found codigo censal: {}'.format(result_key))

                                    if (len(flatten(index.get(result_key, {}))) > 1 or (force_check == True and len(name[level:]) > 1)):

                                        if len(name[level:]) == 1:
                                            raise Exception('Need more level info {}'.format(codigo_censal))

                                        codigo_censal = self.get_codigo_censal(name, level+1, index.get(result_key, {}), force_check, without_codigo_censal)

                                    else:
                                        codigo_censal = [x for x in flatten(index.get(result_key)).values()][0]

                                    break

                    if result_key is None:
                        without_codigo_censal.add("_".join(name[:level+1]))
                        logger.error('* -- Fail Searching codigo_censal {}'.format(name))

                # if found the code in this level, return it
                elif not isinstance(codigo_censal, dict):
                    return codigo_censal

                # if got more than 1 level in result hierarchy
                elif (len(flatten(codigo_censal)) > 1 or (force_check == True and len(name[level:]) > 1)):

                    if len(name[level:]) == 1:
                        raise Exception('Need more level info {}'.format(codigo_censal))

                    codigo_censal = self.get_codigo_censal(name, level+1, codigo_censal, force_check, without_codigo_censal)

                # if have a simple hierarchy with one level
                else:
                    codigo_censal = [x for x in flatten(codigo_censal).values()][0]

                # not needed alternative name iteration so break
                if codigo_censal:
                    break

        except Exception as ex:
            without_codigo_censal.add("_".join(name[:level+1]))
            codigo_censal = None
            logger.error('Fail to retrieve codigo censal - {}'.format(ex))

        return codigo_censal
