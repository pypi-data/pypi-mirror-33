from data_source_departament import DataSourceDepartament
from data_source_subject import DataSourceSubject,DataSourceSubjectsDarcy
from data_sink_subject import DataSinkSubject
from data_sink_departament import DataSinkDepartament
from data_sink_course import DataSinkCourse
import requests
from bs4 import BeautifulSoup
from filters import Filter
from models import Courses

DARCY = "DARCY"
FUP = "FUP"
FCE = "FCE"
FGA = "FGA"

list_departaments = [FGA,FCE,FUP,DARCY]
list_departaments_numbers = [4,3,2,1]
list_campi_numbers = [4,3,2,1]
list_departaments_cods = [650,660,638]

def run ():

    for aux in range(len(list_departaments)):

        departament = DataSourceDepartament.read("https://matriculaweb.unb.br/graduacao/oferta_dep.aspx?cod=" +
                                                 str(list_departaments_numbers[aux]), list_departaments[aux])
        DataSinkDepartament.write(departament, list_departaments[aux])

    for new_aux in range(len(list_departaments_cods)):

        subjects = DataSourceSubject.read("https://matriculaweb.unb.br/graduacao/oferta_dis.aspx?cod=" +
                                              str(list_departaments_cods[new_aux]), new_aux)
        DataSinkSubject.write(subjects)


    subjects_darcy = DataSourceDepartament.read("https://matriculaweb.unb.br/graduacao/oferta_dep.aspx?cod=" +
                                                str(list_departaments_numbers[3]),list_departaments[3])

    subjects_darcy_cods = subjects_darcy.list_cods
    subjects_darcy_initials = subjects_darcy.list_initials
    size_subjects_darcy = 76

    for aux in range(size_subjects_darcy):

        subject = DataSourceSubjectsDarcy.read("https://matriculaweb.unb.br/graduacao/oferta_dis.aspx?cod=" +
                                               str(subjects_darcy_cods[aux]),
                                               subjects_darcy_initials[aux],
                                               subjects_darcy_cods[aux])
        DataSinkSubject.write(subject)


    for aux in range(len(list_campi_numbers)):

        request = requests.get("https://matriculaweb.unb.br/graduacao/curso_rel.aspx?cod=" +
                                                         str(list_campi_numbers[aux]))
        soup = BeautifulSoup(request.content, "html.parser")

        courses = Courses()
        list_content = []
        for tr in soup.find_all('tr'):

            for td in tr.find_all('td'):
                list_content.append(td.text)

                list_content = Filter.blank_space(list_content)
                list_content = Filter.upper_words(list_content)
                list_content = Filter.remove_accents(list_content)
                list_cods = Filter.remove_vogals(list_content)
                list_modalities = Filter.get_modalities(list_content)
                list_shift = Filter.get_shift(list_content)
                list_names = Filter.get_names(list_content)

                courses.codes = list_cods
                courses.modalities = list_modalities
                courses.list_shift = list_shift
                courses.names = list_names

        DataSinkCourse.write(courses, list_departaments[aux])

run()
