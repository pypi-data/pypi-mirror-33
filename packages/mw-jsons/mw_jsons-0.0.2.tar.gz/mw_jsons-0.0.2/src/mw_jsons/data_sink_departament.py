from pipe import Pipe
import json

class DataSinkDepartament(Pipe):

    def write(departament,type):

        if (type == "DARCY"):

            data = {
                "DEPARTAMENTOS_" + departament.initials: {
                    "CODIGO": departament.list_cods,
                    "SIGLA": departament.list_initials,
                    "DENOMINACAO": departament.list_names
                }
            }

        else:

            data = {
                "DEPARTAMENTOS_" + departament.initials: {
                    "CODIGO": departament.cod,
                    "SIGLA": departament.initials,
                    "DENOMINACAO": departament.name
                }
            }

        with open("DEPARTAMENTOS_" + departament.initials +".json", "w") as write_file:
            json.dump(data, write_file)