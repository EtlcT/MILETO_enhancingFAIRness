import re

def regex_exclude_meta(text) -> bool:
    """
    return True if text match one of the regex to exclude, false either

    case insensitive regex to keep only data tables
    """
    no_info = re.search(r"(?i)tables_info", text)
    no_meta = re.search(r"(?i)meta\_", text)
    no_DDict = re.search(r"(?i)DDict\_", text)
    no_extra = re.search(r"(?i)^extra\.", text)
    return any([no_DDict, no_meta, no_extra, no_info])


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