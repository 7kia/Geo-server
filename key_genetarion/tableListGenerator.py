class TableListGenerator:
    @classmethod
    def generate_table_list(cls, prefixes, suffix):
        table_list = []
        for prefix in prefixes:
            table_list.append(prefix + suffix)
        return table_list

    @classmethod
    def generate_words(cls, start_word, ends_words):
        words = []
        for end_prefix in ends_words:
            words.append(start_word + end_prefix)
        return words
