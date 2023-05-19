from re import sub


def clean_string_with_extra_spaces(string: str) -> str:
    multiple_space_regex = r"\s{2,}"
    single_space = " "
    return sub(pattern=multiple_space_regex, repl=single_space, string=string)
