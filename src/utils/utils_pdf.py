def html_formatted_sql(raw_sql: str) -> str:
    """Return readable sql statement from sqlite_master statement"""

    formatted_sql = (
        raw_sql
        .replace('    ', '&emsp;')
        .replace('\n', '<br>')
    )

    return formatted_sql

def format_as_pre(user_txt: str) -> str:
    """Return user_txt with break line and tab space formatted in
    html readable way to display in p as if it is pre tag
    """
    text_with_br = "<br>".join(user_txt.splitlines())
    text_with_br_and_tab = "&emsp;".join(text_with_br.split(sep = "\t"))

    return text_with_br_and_tab
        