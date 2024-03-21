import re

# Проверка для регулярных выражений
def check_regex(pattern_string, string):
    try:
        pattern = re.compile(pattern_string)
    except re.error:
        pattern = re.compile("")
    return re.match(pattern, string)
