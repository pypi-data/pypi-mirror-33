from .NameTranslator import NameTranslator
from .Language import Language

def test_english_to_english():
    translator = NameTranslator(source_lang=Language.ENGLISH, target_lang=Language.ENGLISH)

    result = translator.translate("ajmer")
    assert result == "AjayMeru"

    result = translator.translate("delhi")
    assert result == "Indraprastha"

def test_english_to_hindi():
    translator = NameTranslator(source_lang=Language.ENGLISH, target_lang=Language.HINDI)

    result = translator.translate("ajmer")
    assert result == "अजयमेरु"

    result = translator.translate("delhi")
    assert result == "इंद्रप्रस्थ"
