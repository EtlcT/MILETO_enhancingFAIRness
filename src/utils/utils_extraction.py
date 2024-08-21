import re

def regex_exclude_meta(text) -> bool:
    """
    return True if text match one of the regex to exclude, false either

    case insensitive regex to keep only data tables
    """
    no_info = re.search(r"(?i)tables_info", text)
    no_meta = re.search(r"(?i)meta\_", text)
    no_DDict = re.search(r"(?i)DDict\_", text)

    return any([no_DDict, no_meta, no_info])


def get_datatables_list(sheets_dict) -> list:
    """
    Return a list containing the name of table that contains effective data

    exclude extra.*, meta.* and DDict.*, tables_info
    """
    datatable_list = list()
    for sheet_name in sheets_dict:
        if(regex_exclude_meta(sheet_name) == False):
            datatable_list.append(sheet_name)
    return datatable_list

def rm_extra_tables(sheets_dict) -> dict:
    """Remove tables that start with 'extra' from the database"""

    extra_tables = [key for key in sheets_dict if re.match(r"extra", key)]
    for key in extra_tables:
        del sheets_dict[key]
    
    return sheets_dict