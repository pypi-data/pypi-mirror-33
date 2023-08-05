from pipe import Pipe
import json

class DataSinkCourse(Pipe):

    def write(courses, department):

        data = {
            "CURSOS_" + department: {
                "MODALIDADE" : courses.modalities,
                "CODIGO" : courses.codes,
                "DENOMINACAO": courses.names,
                "TURNO": courses.list_shift,
            }
        }

        with open("CURSOS_" + department + ".json", "w") as write_file:
            json.dump(data, write_file)
