class Filter(object):

    def blank_space(list):

        while '' in list:

            list.remove('')

        return list

    def remove_word_event_note(list):

        while 'event_note' in list:

            list.remove('event_note')

        return list

    def remove_hours(list):

        list = [aux for aux in list if "h" not in aux]

        return list

    def remove_letter_a(list):

        list_codes = [aux for aux in list if "A" not in aux]

        return list_codes

    def remove_letter_e(list):

        list_codes = [aux for aux in list if "E" not in aux]

        return list_codes

    def remove_letter_i(list):

        list_codes = [aux for aux in list if "I" not in aux]

        return list_codes

    def remove_letter_o(list):

        list_codes = [aux for aux in list if "O" not in aux]

        return list_codes

    def remove_letter_u(list):

        list_codes = [aux for aux in list if "U" not in aux]

        return list_codes

    def remove_letter_c(list):

        list_codes = [aux for aux in list if "C" not in aux]

        return list_codes

    def remove_letter_p(list):

        list_codes = [aux for aux in list if "P" not in aux]

        return list_codes

    def remove_letter_f(list):

        list_codes = [aux for aux in list if "F" not in aux]

        return list_codes

    def remove_initials(list):

        list_C = Filter.remove_letter_c(list)
        list_P = Filter.remove_letter_p(list_C)
        list_F = Filter.remove_letter_f(list_P)
        list_final = list_F

        return list_final

    def remove_vogals(list):

        list_A = Filter.remove_letter_a(list)
        list_E = Filter.remove_letter_e(list_A)
        list_I = Filter.remove_letter_i(list_E)
        list_O = Filter.remove_letter_o(list_I)
        list_U = Filter.remove_letter_u(list_O)
        list_final = list_U

        return list_final

    def remove_cod_of_list_name(list_code,list):

        list_names = [x for x in list if not any(ignore in x for ignore in list_code)]

        return list_names

    def remove_accents(list_names):

        list_names = [x.replace('Á', 'A') for x in list_names]
        list_names = [x.replace('À', 'A') for x in list_names]
        list_names = [x.replace('Â', 'A') for x in list_names]
        list_names = [x.replace('Ã', 'A') for x in list_names]
        list_names = [x.replace('É', 'E') for x in list_names]
        list_names = [x.replace('Ê', 'E') for x in list_names]
        list_names = [x.replace('Í', 'I') for x in list_names]
        list_names = [x.replace('Õ', 'O') for x in list_names]
        list_names = [x.replace('Ô', 'O') for x in list_names]
        list_names = [x.replace('Ó', 'O') for x in list_names]
        list_names = [x.replace('Ú', 'U') for x in list_names]
        list_names = [x.replace('Ç', 'C') for x in list_names]

        return list_names

    def upper_words(list):

        list = [x.upper() for x in list]

        return list

    def search_initials(list):

        list_initials = []

        for aux in range(len(list)):

            if aux % 2 == 0:

                list_initials.append(list[aux])

        return list_initials

    def search_names(list):

        list_names = []

        for aux in range(len(list)):

            if aux % 2 != 0:

                list_names.append(list[aux])

        return list_names

    def get_modalities(list):

        list_modalities = []
        modality_position = 0
        counter = 0

        for aux in range(len(list)):
            if counter == modality_position:
                list_modalities.append(list[aux])
                modality_position += 4

            counter+= 1

        return list_modalities

    def get_shift(list):

        list_shift = []
        shift_position = 3
        counter = 0

        for aux in range(len(list)):
            if counter == shift_position:
                list_shift.append(list[aux])
                shift_position += 4

            counter+= 1

        return list_shift

    def get_names(list):

        list_names = []
        name_position = 2
        counter = 0

        for aux in range(len(list)):
            if counter == name_position:
                list_names.append(list[aux])
                name_position += 4

            counter+= 1

        return list_names
