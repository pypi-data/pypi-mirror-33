# encoding: utf-8

from collections import OrderedDict

from tableutil.table import Table

import logging_helper

logging = logging_helper.setup_logging()


def extract_field(lines,
                  join_lines=True):
    line_parts = lines[0].split(u':')
    if len(line_parts) == 1 or not line_parts:
        return u'\n'.join(lines) if join_lines else lines
    lines.pop(0)
    indent = len(line_parts[0]) + 1
    key = line_parts[0].strip().lower()
    value = u':'.join(line_parts[1:])
    if value:
        indent += len(value[0]) - len(value[0].lstrip(u' '))
    value = [value.strip()]
    while lines:
        if lines[0].startswith(u' '):
            start_char = len(lines[0]) - len(lines[0].lstrip(u' '))
            if start_char < indent:
                value.append(lines.pop(0).strip())
            else:
                value.append(lines.pop(0)[indent:])
        else:
            break
    return key, u'\n'.join(value) if join_lines else value


def extract_fields(lines,
                   join_lines=True):
    fields = OrderedDict()
    line_count = len(lines)
    while lines:
        key, value = extract_field(lines=lines,
                                   join_lines=join_lines)
        fields[key] = value
        if len(lines) == line_count:
            raise ValueError(u'Field expected. Got {lines}'
                             .format(lines=lines))
        line_count = len(lines)
    return fields


def strip_leading_and_trailing_blank_lines(section):
    while section and not section[0]:
        section.pop(0)
    while section and not section[-1]:
        section.pop()
    return section


def extract_sections_from_docstring(docstring_lines):
    sections = []
    line = docstring_lines.pop(0)
    while docstring_lines:
        section = []
        while docstring_lines and not (line.startswith(u'--') or
                                       line.startswith(u'==')):
            section.append(line)
            try:
                line = docstring_lines.pop(0)
            except IndexError:
                pass
        section = strip_leading_and_trailing_blank_lines(section)
        if section:
            sections.append(section)
        try:
            line = docstring_lines.pop(0)
        except IndexError:
            pass  # Empty list

    return sections


def make_modifier_tooltip_from_docstring(mod):

    u"""
    converts a module's docstring to containing a tabulated representation

    e.g.
    docstring:
        ============================================================
        Delays the response for a number of seconds.
        ------------------------------------------------------------
        Filter     : N/A
        Override   : N/A
        Parameters : wait value in seconds
        ============================================================

    Result:
        ┌──────────────────────────────────────────────┐
        │            body.generate_timeout             │
        ├──────────────────────────────────────────────┤
        │ Delays the response for a number of seconds. │
        ├──────────────────────────────────────────────┤
        │    ┌────────────┬───────────────────────┐    │
        │    │ filter     │ N/A                   │    │
        │    │ override   │ N/A                   │    │
        │    │ parameters │ wait value in seconds │    │
        │    └────────────┴───────────────────────┘    │
        └──────────────────────────────────────────────┘

    :param mod: a python module object
    :return: unicode string
    """


    docstring = (mod.__doc__
                 if mod.__doc__
                 else u'No documentation available\nfor {modifier}'
                      .format(modifier=mod))
    try:
        unicode(docstring)
    except UnicodeDecodeError:
        raise ValueError(u"Docstring contains unicode."
                         u"Add a 'u' to the front of the string!")

    if u'\t' in docstring:
        raise ValueError(u"Docstring contains tabs. "
                         u"Don't use tabs, this is Python!")

    docstring_lines = docstring.splitlines()

    sections = [[mod.__name__]]
    sections.extend(extract_sections_from_docstring(docstring_lines))

    for i, section in enumerate(sections):
        try:
            fields = extract_fields(section)
            sections[i] = Table.init_from_tree(fields).text()
        except ValueError:
            sections[i] = u'\n'.join(section)
            # sections[i] = make_table(sections[i])

    tooltip_text = Table.init_as_grid(sections,
                                      columns=1).text()
    return tooltip_text


if __name__ == u"__main__":
    from pyhttpintercept.intercept.modifiers.body import generate_timeout
    T = make_modifier_tooltip_from_docstring(mod=generate_timeout)
    print(T)
    pass
