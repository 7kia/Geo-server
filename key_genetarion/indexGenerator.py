class IndexGenerator:
    @classmethod
    def generate_db_index(cls, table_name, criterias):
        request = "CREATE INDEX " + cls.__generate_index_name(table_name, criterias)
        request += " ON " + "\"" + table_name + "\" "
        request += cls.__generate_field_list(criterias) + ";"
        request += "\n"
        return request

    @classmethod
    def __generate_index_name(cls, table_name, criterias):
        criteria_suffix = cls.__generate_criteria_suffix(criterias)
        return "\"idx__" + table_name + "__" + criteria_suffix + "\""

    @classmethod
    def __generate_criteria_suffix(cls, criterias):
        suffix = ""
        for criteria in criterias:
            if suffix != "":
                suffix += "-and-"
            suffix += criteria
        return suffix

    @classmethod
    def __generate_field_list(cls, criterias):
        field_list = "(\n"
        criteria_amount = len(criterias)
        for i in range(criteria_amount):
            criteria = criterias[i]
            field_list += "\"" + criteria + "\""
            if (i + 1) < criteria_amount:
                field_list += ",\n"
            else:
                field_list += "\n"
        field_list += ")"
        return field_list
