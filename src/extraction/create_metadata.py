import pandas as pd
import re
import os

from conf.config import *
from src.utils.utils_extraction import regex_exclude_meta
from src.utils.utils import json2dict, get_relative_items, format_as_json

class GenerateMeta:
    """
        This class generate empty metadata tables compliant
        with the template
    """

    def __init__(self, spreadsheet):
        ## GUI: spreadsheet has already been loaded and is stored as dict
        if isinstance(spreadsheet, dict):
            self.sheets_dict = spreadsheet
        ## CLI: spreadsheet is read for the first time
        else:
            self.sheets_dict = pd.read_excel(spreadsheet, sheet_name=None)
    
    def create_metatable(self):
        """Create metadata tables if not exist"""

        missing_tables = []
        for metatable in META_TABLES:
            if metatable not in list(self.sheets_dict.keys()):
                missing_tables.append(metatable)
                if metatable == METAREF:
                    self.generate_meta_ref()
                elif metatable == INFO:
                    self.generate_tables_info()
                elif metatable == DDICT_T:
                    self.generate_ddict_tables()
                elif metatable == DDICT_A:
                    self.generate_ddict_attr()
                elif metatable == METAEXTRA:
                    self.generate_meta_extra()
            else:
                if metatable == INFO:
                    # metadata table tables_info already exists
                    # infer sqlite type
                    self.upt_attribute_type()
                    # reorgarnize column
                    self.sheets_dict[INFO] = self.sheets_dict[INFO].reindex(
                        [
                            INFO_ATT["table"],
                            INFO_ATT["attribute"],
                            INFO_ATT["type"],
                            INFO_ATT["usr_type"],
                            INFO_ATT["isPK"],
                            INFO_ATT["isFK"],
                            INFO_ATT["refTable"]
                        ],
                        axis="columns"
                    )
        return missing_tables

    def upt_attribute_type(self):
        """Infer sqlite type and store it in tables_info type column
        This function only executes when tables_infos already exists
        """

        for table_name, table in self.sheets_dict.items():
            if regex_exclude_meta(table_name)==False:
                for column_name in table.columns:
                    attr_type = self.infer_sqlite_type(
                        column_name=column_name, 
                        column=self.sheets_dict[table_name][column_name]
                    )
                    self.sheets_dict[INFO].loc[
                        (self.sheets_dict[INFO][INFO_ATT["table"]]==table_name) &
                        (self.sheets_dict[INFO][INFO_ATT["attribute"]]==column_name),
                        "type"
                    ] = attr_type
        
        return
                        
    def generate_ddict_tables(self, inplace=True):
        """Generate DDict_tables metadata table which contains
        information relative to table content
        """
        
        data = {DDICT_T_ATT["table"]: [], DDICT_T_ATT["desc"]: []}

        for table_name in self.sheets_dict:
            if regex_exclude_meta(table_name)==False:
                data[DDICT_T_ATT["table"]].append(table_name)
                data[DDICT_T_ATT["desc"]].append(str())

        ddict_tables = pd.DataFrame(data)
        if inplace == True:
            self.sheets_dict[DDICT_T] = ddict_tables

        return ddict_tables

    def generate_ddict_attr(self, inplace=True):
        """Generate DDict_attributes metadata table which contains
        attributes description
        """
        data = {DDICT_A_ATT["attribute"]: [], DDICT_A_ATT["unit"]: [], DDICT_T_ATT["desc"]: []}
        attribute_list = set()
        for table_name, table in self.sheets_dict.items():
            if regex_exclude_meta(table_name)==False:
                attribute_list.update(table.columns)

        data[DDICT_A_ATT["attribute"]] = list(attribute_list)
        for i in range(len(attribute_list)):
            data[DDICT_A_ATT["unit"]].append(str())
            data[DDICT_T_ATT["desc"]].append(str())

        ddict_attr = pd.DataFrame(data)
        if inplace == True:
            self.sheets_dict[DDICT_A] = ddict_attr
        
        return ddict_attr

    def generate_tables_info(self, inplace=True):
        """Generate tables_infos metadata table which contains
        information schema data, ie. Primary Key and Foreign Key
        constraints, reference_table
        """
        data = {value: [] for value in INFO_ATT.values()}
        for table_name, table in self.sheets_dict.items():
            if regex_exclude_meta(table_name)==False:
                for column in table.columns:
                    data[INFO_ATT["table"]].append(table_name)
                    data[INFO_ATT["attribute"]].append(column)
                    data[INFO_ATT["type"]].append(self.infer_sqlite_type(column, table[column]))
                    data[INFO_ATT["usr_type"]].append(str())
                    data[INFO_ATT["isPK"]].append(str())
                    data[INFO_ATT["isFK"]].append(str())
                    data[INFO_ATT["refTable"]].append(str())
        tables_infos = pd.DataFrame(data)
        if inplace == True:
            self.sheets_dict[INFO] = tables_infos
        return tables_infos
    
    @staticmethod
    def infer_sqlite_type(column_name: str, column: pd.Series):
        """Infer attributes type based on dataframe content"""
        col_type = column.dtype
        for regex in IMG_COL_REGEX:
            if re.search(regex, column_name):
                return "BLOB"
        if re.search('int', str(col_type)) != None:
            return 'INTEGER'
        elif re.search('float', str(col_type)) != None:
            return "REAL"
        else:
            return "TEXT"


    def generate_meta_ref(self):
        """Generate meta_dc_terms metadata table which contains
        Datacite schema mandatory metadata terms
        """

        terms_name = pd.Series(DC_JSON_OBJECT.keys())
        terms_value = [str() for _ in range(len(DC_JSON_OBJECT.keys()))]

        data = {
            METAREF_ATT["property"]: terms_name,
            METAREF_ATT["value"]: terms_value
        }

        metaref = pd.DataFrame(data)
        self.sheets_dict[METAREF] = metaref
        return metaref

    def generate_meta_extra(self):
        """Generate meta_extra metadata table which contains abstract
        and description fiels for rich metadata
        """

        data_prop = pd.Series([key for key in METAEXTRA_PROP.keys()])
        data_value = pd.Series([str() for _ in range(len(data_prop))])
        data = {METAEXTRA_ATT["property"]: data_prop, METAEXTRA_ATT["value"]: data_value}

        meta_extra = pd.DataFrame(data)
        self.sheets_dict[METAEXTRA] = meta_extra
        return meta_extra

# TODO
def update_metatable(self):
    """Update metadata tables:
    - remove attributes that does not exist anymore,
    - add new attributes,
    - keep unchanged others
    """

    pass

    