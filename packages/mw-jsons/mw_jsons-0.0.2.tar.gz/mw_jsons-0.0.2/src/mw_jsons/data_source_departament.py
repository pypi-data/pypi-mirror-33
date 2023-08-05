import requests
from bs4 import BeautifulSoup
from models import Departament
from pipe import Pipe
from filters import Filter

class DataSourceDepartament(Pipe):

    def read(url,type):

        departament = Departament()

        request = requests.get(url)
        soup = BeautifulSoup(request.content, "html.parser")
        filter_subjects = Filter

        list_content = []
        for tr in soup.find_all('tr'):

            for td in tr.find_all('td'):
                list_content.append(td.text)

        list_content = filter_subjects.blank_space(list_content)
        list_content = filter_subjects.remove_accents(list_content)
        departament.cod = list_content[0]

        if (type == "FGA"):

            departament.name = "UnB - Faculdade do Gama"
            departament.initials = "FGA"
            departament.name.upper()

        elif (type == "FCE"):

            departament.name = "UnB - Faculdade do Ceilandia"
            departament.initials = "FCE"
            departament.name.upper()

        elif (type == "FUP") :

            departament.name = "UnB - Faculdade do Planaltina"
            departament.initials = "FUP"
            departament.name.upper()

        else:

            type = "DARCY"
            request = requests.get(url)
            soup = BeautifulSoup(request.content, "html.parser")
            filter_subjects = Filter

            list_content = []

            for tr in soup.find_all('tr'):

                for td in tr.find_all('td'):
                    list_content.append(td.text)

            list_content = filter_subjects.blank_space(list_content)
            list_content = filter_subjects.upper_words(list_content)
            list_cods = filter_subjects.remove_vogals(list_content)
            list_cods = filter_subjects.remove_initials(list_cods)
            list_initials = filter_subjects.remove_cod_of_list_name(list_cods, list_content)
            list_names = filter_subjects.search_names(list_initials)
            list_initials = filter_subjects.search_initials(list_initials)

            departament.list_cods = list_cods
            departament.list_initials = list_initials
            departament.list_names = filter_subjects.remove_accents(list_names)
            departament.initials = type

        return departament