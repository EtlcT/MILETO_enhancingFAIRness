import unittest
from unittest.mock import patch
from parameterized import parameterized

import pandas as pd
import numpy as np

from src.extraction import check
from conf.config import *

def read_spreadsheet_mock():
    """Example compliant with data requirements"""

    fields_A = ["Attribute_A1", "Attribute_A2", "Attribute_A3"]
    values_A = [
        ["Ref_A1", "value_1", "some_value_1"],
        ["Ref_A2", "value_2", "some_value_2"],
                ]
    table_A = pd.DataFrame(data=values_A, columns=fields_A)

    fields_B = ["Attribute_B1", "Attribute_B2", "Attribute_B3"]
    values_B = [
        ["Ref_B1", 11, "value_aa"],
        ["Ref_B2", 23, "value_ab"],
        ["Ref_B1", 456, "value_aa"],
        ["Ref_B2", 7, "value_ac"],
    ]
    table_B = pd.DataFrame(data=values_B, columns=fields_B)

    fields_C = ["Attribute_C1", "Attribute_B1", "Attribute_B2", "Attribute_D1", "Attribute_C2"]
    values_C = [
        ["Ref_C1", "Ref_B1", 11, "Ref_D2", 12],
        ["Ref_C2", "Ref_B2", 7, "Ref_D3", 42],
        ["Ref_C3", "Ref_B2", 23, "Ref_D1", 200]
    ]
    table_C = pd.DataFrame(data=values_C, columns=fields_C)

    fields_D = ["Attribute_D1", "Attribute_D2", "Attributa_A1"]
    values_D = [
        ["Ref_D1", "value_aa", "Ref_A1"],
        ["Ref_D2", "value_ab", "Ref_A1"],
        ["Ref_D3", "value_aa", "Ref_A3"]
    ]
    table_D = pd.DataFrame(data=values_D, columns=fields_D)

    fields_info = list(INFO_ATT.values())
    values_info = [
        ["Table_A", "Attribute_A1", "TEXT", "", "Y", "", ""],
        ["Table_A", "Attribute_A2", "TEXT", "", "", "", ""],
        ["Table_A", "Attribute_A3", "TEXT", "", "", "", ""],
        ["Table_B", "Attribute_B1", "TEXT", "", "Y", "", ""],
        ["Table_B", "Attribute_B2", "INTEGER", "", "Y", "", ""],
        ["Table_B", "Attribute_B3", "TEXT", "", "", "", ""],
        ["Table_C", "Attribute_C1", "TEXT", "", "Y", "", ""],
        ["Table_C", "Attribute_B1", "TEXT", "", "", "Y", "Table_B"],
        ["Table_C", "Attribute_B2", "INTEGER", "", "", "Y", "Table_B"],
        ["Table_C", "Attribute_D1", "TEXT", "", "", "Y", "Table_D"],
        ["Table_C", "Attribute_C2", "INTEGER", "", "", "", ""],
        ["Table_D", "Attribute_D1", "TEXT", "", "Y", "", ""],
        ["Table_D", "Attribute_D2", "TEXT", "", "", "", ""],
        ["Table_D", "Attribute_A1", "TEXT", "", "", "Y","Table_A"],
    ]
    tables_info = pd.DataFrame(data=values_info, columns=fields_info)

    meta_terms_info = [
            ['publicationYear', 2024],
            ['Title', 'Example dataset for NFS-FAIR-DDP']
        ]
    table_ref = pd.DataFrame(
        columns=list(METAREF_ATT.values()),
        data=meta_terms_info
    )

    fields_ddict_a = list(DDICT_A_ATT.values())
    values_ddict_a = [
        ["Attribute_A1", "", ""],
        ["Attribute_A2", "", ""],
        ["Attribute_A3", "", ""],
        ["Attribute_B1", "", ""],
        ["Attribute_B2", "", ""],
        ["Attribute_B3", "", ""],
        ["Attribute_C1", "", ""],
        ["Attribute_C2", "", ""],
        ["Attribute_D1", "", ""],
        ["Attribute_D2", "", ""],
    ]
    ddict_a = pd.DataFrame(data=values_ddict_a, columns=fields_ddict_a)

    fields_ddict_t = list(DDICT_T_ATT.values())
    values_ddict_t = [
        ["Table_A", ""],
        ["Table_B", ""],
        ["Table_C", ""],
        ["Table_D", ""],
    ]
    ddict_t = pd.DataFrame(data=values_ddict_t, columns=fields_ddict_t)


    return {
        "Table_A": table_A,
        "Table_B": table_B,
        "Table_C": table_C,
        "Table_D": table_D,
        INFO: tables_info,
        METAREF: table_ref,
        DDICT_A: ddict_a,
        DDICT_T: ddict_t,
    }

def rs_mock_pk_duplicate():
    """Primary key not unique"""

    fields_A = ["Attribute_A1", "Attribute_A2", "Attribute_A3"]
    values_A = [
        ["Ref_A1", "value_1", "some_value_1"],
        ["Ref_A1", "value_2", "some_value_2"],
        ["Ref_A2", "value_2", "some_value_2"]
                ]
    table_A = pd.DataFrame(data=values_A, columns=fields_A)

    fields_B = ["Attribute_B1", "Attribute_B2", "Attribute_B3"]
    values_B = [
        ["Ref_B1", 11, "value_aa"],
        ["Ref_B2", 23, "value_ab"],
        ["Ref_B1", 456, "value_aa"],
        ["Ref_B2", 7, "value_ac"],
    ]
    table_B = pd.DataFrame(data=values_B, columns=fields_B)

    fields_info = list(INFO_ATT.values())
    values_info = [
        ["Table_A", "Attribute_A1", "TEXT", "", "Y", "", ""],
        ["Table_A", "Attribute_A2", "TEXT", "", "", "", ""],
        ["Table_A", "Attribute_A3", "TEXT", "", "", "", ""],
        ["Table_B", "Attribute_B1", "TEXT", "", "Y", "", ""],
        ["Table_B", "Attribute_B2", "INTEGER", "", "Y", "", ""],
        ["Table_B", "Attribute_B3", "TEXT", "", "", "", ""],
    ]
    tables_info = pd.DataFrame(data=values_info, columns=fields_info)

    meta_terms_info = [
            ['publicationYear', 2024],
            ['Title', 'Example dataset for NFS-FAIR-DDP']
        ]
    
    table_ref = pd.DataFrame(
        columns=list(METAREF_ATT.values()),
        data=meta_terms_info
    )
    
    fields_ddict_a = list(DDICT_A_ATT.values())
    values_ddict_a = [
        ["Attribute_A1", "", ""],
        ["Attribute_A2", "", ""],
        ["Attribute_A3", "", ""],
        ["Attribute_B1", "", ""],
        ["Attribute_B2", "", ""],
        ["Attribute_B3", "", ""]
    ]
    ddict_a = pd.DataFrame(data=values_ddict_a, columns=fields_ddict_a)

    fields_ddict_t = list(DDICT_T_ATT.values())
    values_ddict_t = [
        ["Table_A", ""],
        ["Table_B", ""]
    ]
    ddict_t = pd.DataFrame(data=values_ddict_t, columns=fields_ddict_t)

    return {
        "Table_A": table_A,
        "Table_B": table_B,
        INFO: tables_info,
        METAREF: table_ref,
        DDICT_A: ddict_a,
        DDICT_T: ddict_t,
    }

def rs_mock_with_meta():
    """Return an example compliant with template"""
    table_1 = pd.DataFrame(
        columns=["id", "num", "value"],
        data=[
            ["id_1", 1, "value_a"],
            ["id_2", 1, "value_b"]
        ]
    )

    table_2 = pd.DataFrame(
        columns=["id", "measure", "dd"],
        data=[
            ["id_1", 12, "07.08.24"],
            ["id_1", 22, "08.08.24"],
            ["id_2", 35, "06.08.24"]
        ]
    )

    meta_terms_info = [
            ['publicationYear', 2024],
            ['Title', 'Example dataset for NFS-FAIR-DDP']
        ]
    table_ref = pd.DataFrame(
        columns=list(METAREF_ATT.values()),
        data=meta_terms_info
    )

    tables_info = pd.DataFrame(
        columns=list(INFO_ATT.values()),
        data= [
            ["table_1", "id", "TEXT", "", "Y", "", ""],
            ["table_1", "num", "INTEGER", "", "", "", ""],
            ["table_1", "value", "TEXT", "", "", "", ""],
            ["table_2", "id", "TEXT", "", "Y", "Y", "table_1"],
            ["table_2", "measure", "INTEGER", "", "", "", ""],
            ["table_2", "dd", "TEXT", "", "Y", "", ""],
        ]
    )

    table_attr = pd.DataFrame(
        columns=list(DDICT_A_ATT.values()),
        data=[
            ["id", None, "object identifier"],
            ["num", None, "characteristic"],
            ["value", None, "value relative to the object"],
            ["measure", "m", "Lenght in metre"],
            ["dd", None, "Date of measure"]
        ]
    )

    table_dict = pd.DataFrame(
        columns=list(DDICT_T_ATT.values()),
        data=[
            ["table_1", "first table in database"],
            ["table_2", "second table"]
        ]
    )

    return{
        "table_1": table_1,
        "table_2": table_2,
        METAREF: table_ref,
        INFO: tables_info,
        DDICT_T: table_dict,
        DDICT_A: table_attr
    }

def rs_mock_cpk_duplicate():
    """Composite Primary Key not unique"""

    fields_A = ["Attribute_A1", "Attribute_A2", "Attribute_A3"]
    values_A = [
        ["Ref_A1", "value_1", "some_value_1"],
        ["Ref_A2", "value_2", "some_value_2"],
                ]
    table_A = pd.DataFrame(data=values_A, columns=fields_A)

    fields_B = ["Attribute_B1", "Attribute_B2", "Attribute_B3"]
    values_B = [
        ["Ref_B1", 11, "value_aa"],
        ["Ref_B2", 23, "value_ab"],
        ["Ref_B1", 11, "value_ac"],
        ["Ref_B2", 7, "value_ac"],
    ]
    table_B = pd.DataFrame(data=values_B, columns=fields_B)

    fields_info = list(INFO_ATT.values())
    values_info = [
        ["Table_A", "Attribute_A1", "TEXT", "", "Y", "", ""],
        ["Table_A", "Attribute_A2", "TEXT", "", "", "", ""],
        ["Table_A", "Attribute_A3", "TEXT", "", "", "", ""],
        ["Table_B", "Attribute_B1", "TEXT", "", "Y", "", ""],
        ["Table_B", "Attribute_B2", "INTEGER", "", "Y", "", ""],
        ["Table_B", "Attribute_B3", "TEXT", "", "", "", ""],
    ]
    tables_info = pd.DataFrame(data=values_info, columns=fields_info)

    meta_terms_info = [
            ['publicationYear', 2024],
            ['Title', 'Example dataset for NFS-FAIR-DDP']
        ]
    table_ref = pd.DataFrame(
        columns=list(METAREF_ATT.values()),
        data=meta_terms_info
    )

    fields_ddict_a = list(DDICT_A_ATT.values())
    values_ddict_a = [
        ["Attribute_A1", "", ""],
        ["Attribute_A2", "", ""],
        ["Attribute_A3", "", ""],
        ["Attribute_B1", "", ""],
        ["Attribute_B2", "", ""],
        ["Attribute_B3", "", ""]
    ]
    ddict_a = pd.DataFrame(data=values_ddict_a, columns=fields_ddict_a)

    fields_ddict_t = list(DDICT_T_ATT.values())
    values_ddict_t = [
        ["Table_A", ""],
        ["Table_B", ""]
    ]
    ddict_t = pd.DataFrame(data=values_ddict_t, columns=fields_ddict_t)

    return {
        "Table_A": table_A,
        "Table_B": table_B,
        INFO: tables_info,
        METAREF: table_ref,
        DDICT_A: ddict_a,
        DDICT_T: ddict_t,
    }


def rs_mock_fk_not_unique():
    """Foreign key not unique"""

    fields_A = ["Attribute_A1", "Attribute_A2", "Attribute_A3"]
    values_A = [
        ["Ref_A1", "value_1", "some_value_1"],
        ["Ref_A2", "value_2", "some_value_1"],
        ["Ref_A2", "value_2", "some_value_2"],
                ]
    table_A = pd.DataFrame(data=values_A, columns=fields_A)

    fields_B = ["Attribute_B1", "Attribute_B2", "Attribute_A3"]
    values_B = [
        ["Ref_B1", 11, "some_value_1"],
        ["Ref_B2", 23, "some_value_1"],
        ["Ref_B1", 11, "some_value_1"],
        ["Ref_B2", 7, "some_value_1"],
    ]
    table_B = pd.DataFrame(data=values_B, columns=fields_B)

    fields_info = list(INFO_ATT.values())
    values_info = [
        ["Table_A", "Attribute_A1", "TEXT", "", "Y", "", ""],
        ["Table_A", "Attribute_A2", "TEXT", "", "", "", ""],
        ["Table_A", "Attribute_A3", "TEXT", "", "", "", ""],
        ["Table_B", "Attribute_B1", "TEXT", "", "Y", "", ""],
        ["Table_B", "Attribute_B2", "INTEGER", "", "Y", "", ""],
        ["Table_B", "Attribute_A3", "TEXT", "", "", "Y", "Table_A"],
    ]
    tables_info = pd.DataFrame(data=values_info, columns=fields_info)

    meta_terms_info = [
            ['publicationYear', 2024],
            ['Title', 'Example dataset for NFS-FAIR-DDP']
        ]
    table_ref = pd.DataFrame(
        columns=list(METAREF_ATT.values()),
        data=meta_terms_info
    )

    fields_ddict_a = list(DDICT_A_ATT.values())
    values_ddict_a = [
        ["Attribute_A1", "", ""],
        ["Attribute_A2", "", ""],
        ["Attribute_A3", "", ""],
        ["Attribute_B1", "", ""],
        ["Attribute_B2", "", ""]
    ]
    ddict_a = pd.DataFrame(data=values_ddict_a, columns=fields_ddict_a)

    fields_ddict_t = list(DDICT_T_ATT.values())
    values_ddict_t = [
        ["Table_A", ""],
        ["Table_B", ""]
    ]
    ddict_t = pd.DataFrame(data=values_ddict_t, columns=fields_ddict_t)

    return {
        "Table_A": table_A,
        "Table_B": table_B,
        INFO: tables_info,
        METAREF: table_ref,
        DDICT_A: ddict_a,
        DDICT_T: ddict_t,
    }


def rs_mock_fk_not_exist():
    """Foreign key doesn"t exist in reference table"""

    fields_A = ["Attribute_A1", "Attribute_A2", "Attribute_A3"]
    values_A = [
        ["Ref_A1", "value_1", "some_value_1"],
        ["Ref_A2", "value_2", "some_value_2"],
        ["Ref_A3", "value_2", "some_value_3"],
                ]
    table_A = pd.DataFrame(data=values_A, columns=fields_A)

    fields_B = ["Attribute_B1", "Attribute_B2", "Attribute_B3"]
    values_B = [
        ["Ref_B1", 11, "value_aa"],
        ["Ref_B2", 23, "value_ab"],
        ["Ref_B1", 456, "value_ac"],
        ["Ref_B2", 7, "value_ac"],
    ]
    table_B = pd.DataFrame(data=values_B, columns=fields_B)

    fields_info = list(INFO_ATT.values())
    values_info = [
        ["Table_A", "Attribute_A1", "TEXT", "", "Y", "", ""],
        ["Table_A", "Attribute_A2", "TEXT", "", "", "", ""],
        ["Table_A", "Attribute_A3", "TEXT", "", "", "", ""],
        ["Table_B", "Attribute_B1", "TEXT", "", "Y", "", ""],
        ["Table_B", "Attribute_B2", "INTEGER", "", "Y", "", ""],
        ["Table_B", "Attribute_B3", "TEXT", "", "", "Y", "Table_A"],
    ]
    tables_info = pd.DataFrame(data=values_info, columns=fields_info)

    meta_terms_info = [
            ['publicationYear', 2024],
            ['Title', 'Example dataset for NFS-FAIR-DDP']
        ]
    table_ref = pd.DataFrame(
        columns=list(METAREF_ATT.values()),
        data=meta_terms_info
    )
    
    fields_ddict_a = list(DDICT_A_ATT.values())
    values_ddict_a = [
        ["Attribute_A1", "", ""],
        ["Attribute_A2", "", ""],
        ["Attribute_A3", "", ""],
        ["Attribute_B1", "", ""],
        ["Attribute_B2", "", ""],
        ["Attribute_B3", "", ""]
    ]
    ddict_a = pd.DataFrame(data=values_ddict_a, columns=fields_ddict_a)

    fields_ddict_t = list(DDICT_T_ATT.values())
    values_ddict_t = [
        ["Table_A", ""],
        ["Table_B", ""]
    ]
    ddict_t = pd.DataFrame(data=values_ddict_t, columns=fields_ddict_t)

    return {
        "Table_A": table_A,
        "Table_B": table_B,
        INFO: tables_info,
        METAREF: table_ref,
        DDICT_A: ddict_a,
        DDICT_T: ddict_t,
    }


def rs_mock_fk_without_ref():
    """Foreign key has not reference table defined"""

    fields_A = ["Attribute_A1", "Attribute_A2", "Attribute_A3"]
    values_A = [
        ["Ref_A1", "value_1", "some_value_1"],
        ["Ref_A2", "value_2", "some_value_2"],
        ["Ref_A2", "value_2", "some_value_3"],
                ]
    table_A = pd.DataFrame(data=values_A, columns=fields_A)

    fields_B = ["Attribute_B1", "Attribute_B2", "Attribute_B3"]
    values_B = [
        ["Ref_B1", 11, "value_aa"],
        ["Ref_B2", 23, "value_ab"],
        ["Ref_B1", 11, "value_ac"],
        ["Ref_B2", 7, "value_ac"],
    ]
    table_B = pd.DataFrame(data=values_B, columns=fields_B)

    fields_info = list(INFO_ATT.values())
    values_info = [
        ["Table_A", "Attribute_A1", "TEXT", "", "Y", "", ""],
        ["Table_A", "Attribute_A2", "TEXT", "", "", "", ""],
        ["Table_A", "Attribute_A3", "TEXT", "", "", "", ""],
        ["Table_B", "Attribute_B1", "TEXT", "", "Y", "", ""],
        ["Table_B", "Attribute_B2", "INTEGER", "", "Y", "", ""],
        ["Table_B", "Attribute_B3", "TEXT", "", "", "Y", ""],
    ]
    tables_info = pd.DataFrame(data=values_info, columns=fields_info)

    meta_terms_info = [
            ['publicationYear', 2024],
            ['Title', 'Example dataset for NFS-FAIR-DDP']
        ]
    table_ref = pd.DataFrame(
        columns=list(METAREF_ATT.values()),
        data=meta_terms_info
    )

    fields_ddict_a = list(DDICT_A_ATT.values())
    values_ddict_a = [
        ["Attribute_A1", "", ""],
        ["Attribute_A2", "", ""],
        ["Attribute_A3", "", ""],
        ["Attribute_B1", "", ""],
        ["Attribute_B2", "", ""],
        ["Attribute_B3", "", ""]
    ]
    ddict_a = pd.DataFrame(data=values_ddict_a, columns=fields_ddict_a)

    fields_ddict_t = list(DDICT_T_ATT.values())
    values_ddict_t = [
        ["Table_A", ""],
        ["Table_B", ""]
    ]
    ddict_t = pd.DataFrame(data=values_ddict_t, columns=fields_ddict_t)

    return {
        "Table_A": table_A,
        "Table_B": table_B,
        INFO: tables_info,
        METAREF: table_ref,
        DDICT_A: ddict_a,
        DDICT_T: ddict_t,
    }


def rs_mock_undefined_pk():
    """Table with no Primary Key"""

    fields_A = ["Attribute_A1", "Attribute_A2", "Attribute_A3"]
    values_A = [
        ["Ref_A1", "value_1", "some_value_1"],
        ["Ref_A2", "value_2", "some_value_2"],
                ]
    table_A = pd.DataFrame(data=values_A, columns=fields_A)

    fields_B = ["Attribute_B1", "Attribute_B2", "Attribute_B3"]
    values_B = [
        ["Ref_B1", 11, "value_aa"],
        ["Ref_B2", 23, "value_ab"],
        ["Ref_B1", 456, "value_aa"],
        ["Ref_B2", 7, "value_ac"],
    ]
    table_B = pd.DataFrame(data=values_B, columns=fields_B)

    fields_info = list(INFO_ATT.values())
    values_info = [
        ["Table_A", "Attribute_A1", "TEXT", "", "Y", "", ""],
        ["Table_A", "Attribute_A2", "TEXT", "", "", "", ""],
        ["Table_A", "Attribute_A3", "TEXT", "", "", "", ""],
        ["Table_B", "Attribute_B1", "TEXT", "", "", "", ""],
        ["Table_B", "Attribute_B2", "INTEGER", "", "", "", ""],
        ["Table_B", "Attribute_B3", "TEXT", "", "", "", ""],
    ]
    tables_info = pd.DataFrame(data=values_info, columns=fields_info)

    meta_terms_info = [
            ['publicationYear', 2024],
            ['Title', 'Example dataset for NFS-FAIR-DDP']
        ]
    table_ref = pd.DataFrame(
        columns=list(METAREF_ATT.values()),
        data=meta_terms_info
    )

    fields_ddict_a = list(DDICT_A_ATT.values())
    values_ddict_a = [
        ["Attribute_A1", "", ""],
        ["Attribute_A2", "", ""],
        ["Attribute_A3", "", ""],
        ["Attribute_B1", "", ""],
        ["Attribute_B2", "", ""],
        ["Attribute_B3", "", ""]
    ]
    ddict_a = pd.DataFrame(data=values_ddict_a, columns=fields_ddict_a)

    fields_ddict_t = list(DDICT_T_ATT.values())
    values_ddict_t = [
        ["Table_A", ""],
        ["Table_B", ""]
    ]
    ddict_t = pd.DataFrame(data=values_ddict_t, columns=fields_ddict_t)

    return {
        "Table_A": table_A,
        "Table_B": table_B,
        INFO: tables_info,
        METAREF: table_ref,
        DDICT_A: ddict_a,
        DDICT_T: ddict_t,
    }


def rs_mock_shared_name() -> pd.DataFrame:
    """Not foreign keys field have the same name as another field"""
    
    brand = pd.DataFrame(
        columns= ["id", "brand_name"],
        data= [
            [1, "Alfa romeo"],
            [2, "Fiat"]
        ]
    )

    car = pd.DataFrame(
        columns= ["id", "model_name", "brand_id"],
        data= [
            [1, "500", 2],
            [2, "Panda", 2],
            [3, "147", 1]
        ]
    )

    fields_info = list(INFO_ATT.values())
    values_info = [
        ["brand", "id", "INTEGER", "", "Y", "", ""],
        ["brand", "brand_name", "TEXT", "", "", "", ""],
        ["car", "id", "INTEGER", "", "Y", "", ""],
        ["car", "model_name", "TEXT", "", "Y", "", ""],
        ["car", "brand_id", "INTEGER", "", "", "Y", "brand"],
    ]
    tables_info = pd.DataFrame(data=values_info, columns=fields_info)

    meta_terms_info = [
            ['publicationYear', 2024],
            ['Title', 'Example dataset for NFS-FAIR-DDP']
        ]
    table_ref = pd.DataFrame(
        columns=list(METAREF_ATT.values()),
        data=meta_terms_info
    )
    
    fields_ddict_a = list(DDICT_A_ATT.values())
    values_ddict_a = [
        ["id", "", ""],
        ["brand_name", "", ""],
        ["model_name", "", ""],
        ["brand_id", "", ""]
    ]
    ddict_a = pd.DataFrame(data=values_ddict_a, columns=fields_ddict_a)

    fields_ddict_t = list(DDICT_T_ATT.values())
    values_ddict_t = [
        ["brand", ""],
        ["car", ""]
    ]
    ddict_t = pd.DataFrame(data=values_ddict_t, columns=fields_ddict_t)

    return {
        "brand": brand,
        "car": car,
        INFO: tables_info,
        METAREF: table_ref,
        DDICT_A: ddict_a,
        DDICT_T: ddict_t,
    }

def rs_mock_no_meta():
    """Example compliant with data requirements"""

    fields_A = ["Attribute_A1", "Attribute_A2", "Attribute_A3"]
    values_A = [
        ["Ref_A1", "value_1", "some_value_1"],
        ["Ref_A2", "value_2", "some_value_2"],
                ]
    table_A = pd.DataFrame(data=values_A, columns=fields_A)

    fields_B = ["Attribute_B1", "Attribute_B2", "Attribute_B3"]
    values_B = [
        ["Ref_B1", 11, "value_aa"],
        ["Ref_B2", 23, "value_ab"],
        ["Ref_B1", 456, "value_aa"],
        ["Ref_B2", 7, "value_ac"],
    ]
    table_B = pd.DataFrame(data=values_B, columns=fields_B)

    fields_C = ["Attribute_C1", "Attribute_B1", "Attribute_B2", "Attribute_D1", "Attribute_C2"]
    values_C = [
        ["Ref_C1", "Ref_B1", 11, "Ref_D2", 12],
        ["Ref_C2", "Ref_B2", 7, "Ref_D3", 42],
        ["Ref_C3", "Ref_B2", 23, "Ref_D1", 200]
    ]
    table_C = pd.DataFrame(data=values_C, columns=fields_C)

    fields_D = ["Attribute_D1", "Attribute_D2", "Attributa_A1"]
    values_D = [
        ["Ref_D1", "value_aa", "Ref_A1"],
        ["Ref_D2", "value_ab", "Ref_A1"],
        ["Ref_D3", "value_aa", "Ref_A3"]
    ]
    table_D = pd.DataFrame(data=values_D, columns=fields_D)

    return {
            "Table_A": table_A,
            "Table_B": table_B,
            "Table_C": table_C,
            "Table_D": table_D
        }

    

################################################

class TestCheckSpreadsheet(unittest.TestCase):
    
    @parameterized.expand([
        ("Primary Key not defined", rs_mock_undefined_pk(), check.PrimaryKeyMissingError),
        ("Primary Key contains duplicate", rs_mock_pk_duplicate(), check.PrimaryKeyNonUniqueError),
        ("Composite Primary Key duplicate", rs_mock_cpk_duplicate(), check.PrimaryKeyNonUniqueError),
        ("Foreign Key with no reference table", rs_mock_fk_without_ref(), check.ReferenceUndefinedError),
        ("Foreing Key doesn't exist in reference table", rs_mock_fk_not_exist(), check.ForeignKeyNotFoundError),
        ("Foreign Key contains duplicate", rs_mock_fk_not_unique(), check.ForeignKeyNonUniqueError),
        ("Fields have the same name without being Foreing keys", rs_mock_shared_name(), check.AttributesDuplicateError),
        ("Valid spreadsheet does not raise error", read_spreadsheet_mock(), None)
    ])

    def test_validate_spreadsheet(self, name, sheet_dict, expected_exception):

        with patch.object(check.CheckSpreadsheet, '__init__', lambda self, sheet_dict: sheet_dict):
            checker = check.CheckSpreadsheet(None)
            checker.sheets_dict = sheet_dict
            checker.metadata_tables = [METAREF, INFO, DDICT_T, DDICT_A]
            checker.tables_info = checker._get_tables_info()

            if expected_exception:
                with self.assertRaises(check.InvalidData) as context:
                    checker.validate_spreadsheet()
                exception_message = context.exception.errors
                self.assertTrue(any([expected_exception.__name__ in msg for msg in exception_message]))
            else:
                try:
                    checker.validate_spreadsheet()
                except check.CheckSpreadsheetError:
                    self.fail(f"{name} raised CheckSpreadsheetError unexpectedly!")
    
    @parameterized.expand([
        ("No metadata tables", rs_mock_no_meta(), check.MissingMetadataError),
        ("Valid spreadsheet does not raise error", rs_mock_with_meta(), None)
    ])

    def test_validate_template(self, name, sheet_dict, expected_exception):

            if expected_exception:
                with self.assertRaises(check.InvalidTemplate) as context:
                    checker = check.CheckSpreadsheet(sheet_dict, "fake_path")
                exception_message = context.exception.errors
                self.assertTrue(any(expected_exception.__name__ in msg for msg in exception_message))
            else:
                try:
                    checker = check.CheckSpreadsheet(sheet_dict, "kafe_path")
                except check.CheckSpreadsheetError:
                    self.fail(f"{name} raised CheckSpreadsheetError unexpectedly!")