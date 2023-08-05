import re


def to_snake_case(string):
    """
    Transforms text written in CamelCase format to snake_case format.

    :param string: string to transform.
    :return: transformed string.
    """
    result = [string[0].lower()]  # list of letters.
    for c in string[1:]:
        if c.islower():
            # add letter to the list.
            result.append(c)
        else:
            # this will ignore the underscore before the first uppercase letter.
            result.append('_')

            # add letter to the list.
            result.append(c.lower())

    # join all letters and return.
    return ''.join(result)


replacements = {
    "[b]": "<b>",
    "[/b]": "</b>"
}


def to_rich_text(string):
    """
    Replaces special tags to create a rich text version using reportlab tags.

    :param string: string to be replaced with rich text.
    :return: the rich text version.
    """
    rep = dict((re.escape(k), v) for k, v in replacements.items())
    pattern = re.compile("|".join(rep.keys()))
    return pattern.sub(lambda m: rep[re.escape(m.group(0))], string)
