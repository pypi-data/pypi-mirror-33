from pipe import Pipe
import json

class DataSinkSubject(Pipe):

    def write(subjects):

        data = {
            "DISCIPLINAS_" + subjects.name_departament: {
                "CODIGO_DEPARTAMENTO_" + subjects.name_departament + ":" : subjects.cod_departament,
                "CODIGO_DISCIPLINA" : subjects.list_cods,
                "MATERIA": subjects.list_names
            }
        }

        with open("DISCIPLINAS_" + subjects.name_departament + ".json", "w") as write_file:
            json.dump(data, write_file)