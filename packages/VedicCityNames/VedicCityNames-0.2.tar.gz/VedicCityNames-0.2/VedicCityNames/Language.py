class Language:
    ENGLISH = 1
    HINDI = 2
    SANSKRIT = 3

    def __init__(self, lang):
        self._lang_code = lang
        self.code_to_string = {
            1: "english",
            2: "hindi",
            3: "sanskrit"
        }

    def __repr__(self):
        return self.code_to_string[self._lang_code]

    def __str__(self):
        return self.code_to_string[self._lang_code]

    def __add__(self, other):
        return self.__str__() + str(other)