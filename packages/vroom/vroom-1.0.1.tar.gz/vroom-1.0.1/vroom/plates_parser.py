"""License plate parser for cars registered in Poland."""

import re
from collections import namedtuple
import yaml
import pkg_resources

PlateDetails = namedtuple('PlateDetails', ['plate', 'unit', 'voivodeship'])

def load_area_codes():
    """
    Loads and returns area codes dictionary.
    """
    with pkg_resources.resource_stream(__name__, "area_codes.yml") as file:
        area_codes = yaml.safe_load(file)
    return area_codes

def load_regex_patterns():
    """
    Loads and returns regex patterns dictionary.
    """
    with pkg_resources.resource_stream(__name__, "regex_patterns.yml") as file:
        regex_patterns = yaml.safe_load(file)
    return regex_patterns


class RegexPattern(object):
    """
    Class representing regex pattern. It contains compiled regex
    and information about matching administrative unit.
    """

    def __init__(self, area_code, pattern, unit_dict, ignore_case):
        self.pattern = pattern
        self.regexp = self.compile(ignore_case)
        self.area_code = area_code
        self.unit = unit_dict['unit']
        self.voivodeship = unit_dict['voivodeship']

    def compile(self, ignore_case):
        """
        Compiles regex pattern with flags.
        """
        if ignore_case:
            return re.compile(self.pattern, flags=re.IGNORECASE)
        else:
            return re.compile(self.pattern)


class Parser(object):
    """
    Main parser class.
    """

    AREA_CODES = load_area_codes()
    REGEX_PATTERNS = load_regex_patterns()


    def __init__(self, force_space=False, ignore_case=False):
        self.force_space = force_space
        self.ignore_case = ignore_case
        self.regexes = self.construct_regexes(self.force_space, self.ignore_case)


    def construct_regexes(self, force_space=False, ignore_case=False):
        """
        Constructs a list of regex patterns.
        """
        regexes = []

        for area_code, unit_dict in self.AREA_CODES.items():
            #load all possible patterns for signature length
            patterns = self.REGEX_PATTERNS[str(len(area_code))]

            #Construct base regex string
            if force_space:
                regex_base = r"\b{} {}\b"
            else:
                regex_base = r"\b{} ?{}\b"

            regexes.extend([RegexPattern(area_code,
                                         regex_base.format(area_code, pattern),
                                         unit_dict,
                                         ignore_case
                                        ) for pattern in patterns])
        return regexes

    def search_plates(self, text):
        """
        Searches text for license plates, returns True if any matches found.
        """
        found = False
        for regex in self.regexes:
            if re.search(regex.regexp, text):
                found = True
                break
        return found

    def findall_plates(self, text, return_units=False):
        """
        Searches text for license plates, returns all matches.
        """

        found_plates = set()
        for regex in self.regexes:
            result = set(re.findall(regex.regexp, text))
            if result:
                if return_units:
                    result_units = {PlateDetails(res,
                                                 regex.unit,
                                                 regex.voivodeship
                                                ) for res in result}
                    found_plates = found_plates | result_units
                else:
                    found_plates = found_plates | result
        if found_plates:
            return found_plates

    def match_plate(self, text):
        """
        Checks if text matches license plate pattern and returns
        namedtuple PlateDetails with administrative unit information.
        """

        for regex in self.regexes:
            if re.match(regex.regexp, text):
                return PlateDetails(text, regex.unit, regex.voivodeship)
