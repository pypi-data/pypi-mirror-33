from  .Language import Language
import yaml
from pathlib import Path
import pkg_resources

class NameTranslator(object):
    def __init__(self, target_lang = Language.ENGLISH, source_lang = Language.ENGLISH):
        self._target_lang = str(Language(target_lang))
        self._source_lang = str(Language(source_lang))
        self._yaml_file = "Translatedata.yml"
        self._source_to_ir_map, self._ir_to_target_map = self._get_translate_map(self._source_lang, self._target_lang)

    def _validate_language(self, source_lang, target_lang, yaml_config):
        supported_langs = yaml_config["supported_languages"]

        if source_lang not in supported_langs:
            raise NotImplementedError("{} language is not supported".format(source_lang))

        if target_lang not in supported_langs:
            raise NotImplementedError("{} language is not supported".format(target_lang))

    def _get_config(self):
        package_name = __name__
        yaml_path_str = pkg_resources.resource_filename(package_name, self._yaml_file)
        yaml_path = Path(yaml_path_str)
        if not yaml_path.exists():
            raise FileNotFoundError("Looking for translation data file {}. Not found".format(yaml_path.absolute()))

        with yaml_path.open(encoding='utf-8') as fp:
            yaml_config = yaml.load(fp)

        return yaml_config

    def _get_translate_map(self, source_lang, target_lang):
        yaml_config = self._get_config()

        self._validate_language(source_lang, target_lang, yaml_config)

        source_to_ir_map = yaml_config[source_lang + "_to_ir"]
        ir_to_target_map = yaml_config["ir_to_" + target_lang]

        return source_to_ir_map, ir_to_target_map

    def _validate_lang(self, city_name):
        return True

    def translate(self, city_name):
        if not self._validate_lang(city_name):
            raise ValueError("Input city_name language invalid")

        if city_name not in self._source_to_ir_map:
            return "Not_supported"

        ir_word = self._source_to_ir_map[city_name]

        return self._ir_to_target_map[ir_word]
