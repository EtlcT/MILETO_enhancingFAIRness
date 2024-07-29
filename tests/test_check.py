import unittest
from parameterized import parameterized

import pandas as pd
import numpy as np

from src.extraction import check
from conf.config import *

def read_spreadsheet_mock():
    """Example compliant with template"""

    fields_A = ['Attribute_A1', 'Attribute_A2', 'Attribute_A3']
    values_A = [
        ['Ref_A1', 'value_1', 'some_value_1'],
        ['Ref_A2', 'value_2', 'some_value_2'],
                ]
    table_A = pd.DataFrame(data=values_A, columns=fields_A)

    fields_B = ['Attribute_B1', 'Attribute_B2', 'Attribute_B3']
    values_B = [
        ['Ref_B1', 11, 'value_aa'],
        ['Ref_B2', 23, 'value_ab'],
        ['Ref_B1', 456, 'value_aa'],
        ['Ref_B2', 7, 'value_ac'],
    ]
    table_B = pd.DataFrame(data=values_B, columns=fields_B)

    fields_C = ['Attribute_C1', 'Attribute_B1', 'Attribute_B2', 'Attribute_D1', 'Attribute_C3']
    values_C = [
        ['Ref_C1', 'Ref_B1', '11', 'Ref_D2', 12],
        ['Ref_C2', 'Ref_B2', '7', 'Ref_D3', 42],
        ['Ref_C3', 'Ref_B2', '23', 'Ref_D1', 200]
    ]
    table_C = pd.DataFrame(data=values_C, columns=fields_C)

    fields_D = ['Attribute_D1', 'Attribute_D2', 'Attributa_A1']
    values_D = [
        ['Ref_D1', 'value_aa', 'Ref_A1'],
        ['Ref_D2', 'value_ab', 'Ref_A1'],
        ['Ref_D3', 'value_aa', 'Ref_A3']
    ]
    table_D = pd.DataFrame(data=values_D, columns=fields_D)

    fields_KEYS = list(TEMP_CONF["tables_info"]["tab_attr"].values())
    values_KEYS = [
        ['Table_A', 'Attribute_A1', 'Y', np.nan, np.nan],
        ['Table_A', 'Attribute_A2', np.nan, np.nan, np.nan],
        ['Table_A', 'Attribute_A3', np.nan, np.nan, np.nan],
        ['Table_B', 'Attribute_B1', 'Y', np.nan, np.nan],
        ['Table_B', 'Attribute_B2', 'Y', np.nan, np.nan],
        ['Table_B', 'Attribute_B3', np.nan, np.nan, np.nan],
        ['Table_C', 'Attribute_C1', 'Y', np.nan, np.nan],
        ['Table_C', 'Attribute_B1', np.nan, 'Y', 'Table_B'],
        ['Table_C', 'Attribute_B2', np.nan, 'Y', 'Table_B'],
        ['Table_C', 'Attribute_D1', np.nan, 'Y', 'Table_D'],
        ['Table_C', 'Attribute_C3', np.nan, np.nan, np.nan],
        ['Table_D', 'Attribute_D1', 'Y', np.nan, np.nan],
        ['Table_D', 'Attribute_D2', np.nan, np.nan, np.nan],
        ['Table_D', 'Attribute_A1', np.nan, 'Y','Table_A'],
    ]
    table_KEYS = pd.DataFrame(data=values_KEYS, columns=fields_KEYS)

    table_REF = pd.DataFrame(
        columns=list(TEMP_CONF["meta_references"]["tab_attr"].values())[1:3], # ['property', 'value']
        data=[
            ['Date', 2024],
            ['Title', '2022_Example#/Template_v2_1; ' ]
        ]
    )

    return {
        'Table_A': table_A,
        'Table_B': table_B,
        'Table_C': table_C,
        'Table_D': table_D,
        TEMP_CONF["tables_info"]["tab_name"]: table_KEYS,
        TEMP_CONF["meta_references"]["tab_name"]: table_REF
    }

def rs_mock_pk_duplicate():
    """Primary key not unique"""

    fields_A = ['Attribute_A1', 'Attribute_A2', 'Attribute_A3']
    values_A = [
        ['Ref_A1', 'value_1', 'some_value_1'],
        ['Ref_A1', 'value_2', 'some_value_2'],
        ['Ref_A2', 'value_2', 'some_value_2']
                ]
    table_A = pd.DataFrame(data=values_A, columns=fields_A)

    fields_B = ['Attribute_B1', 'Attribute_B2', 'Attribute_B3']
    values_B = [
        ['Ref_B1', 11, 'value_aa'],
        ['Ref_B2', 23, 'value_ab'],
        ['Ref_B1', 456, 'value_aa'],
        ['Ref_B2', 7, 'value_ac'],
    ]
    table_B = pd.DataFrame(data=values_B, columns=fields_B)

    fields_KEYS = list(TEMP_CONF["tables_info"]["tab_attr"].values())
    values_KEYS = [
        ['Table_A', 'Attribute_A1', 'Y', np.nan, np.nan],
        ['Table_A', 'Attribute_A2', np.nan, np.nan, np.nan],
        ['Table_A', 'Attribute_A3', np.nan, np.nan, np.nan],
        ['Table_B', 'Attribute_B1', 'Y', np.nan, np.nan],
        ['Table_B', 'Attribute_B2', 'Y', np.nan, np.nan],
        ['Table_B', 'Attribute_B3', np.nan, np.nan, np.nan],
    ]
    table_KEYS = pd.DataFrame(data=values_KEYS, columns=fields_KEYS)

    table_REF = pd.DataFrame(
        columns=list(TEMP_CONF["meta_references"]["tab_attr"].values())[1:3],
        data=[
            ['Date', 2024],
            ['Title', '2022_Example#/Template_v2_1; ' ]
        ]
    )

    return {
        'Table_A': table_A,
        'Table_B': table_B,
        TEMP_CONF["tables_info"]["tab_name"]: table_KEYS,
        TEMP_CONF["meta_references"]["tab_name"]: table_REF
    }

def rs_mock_cpk_duplicate():
    """Composite Primary Key not unique"""

    fields_A = ['Attribute_A1', 'Attribute_A2', 'Attribute_A3']
    values_A = [
        ['Ref_A1', 'value_1', 'some_value_1'],
        ['Ref_A2', 'value_2', 'some_value_2'],
                ]
    table_A = pd.DataFrame(data=values_A, columns=fields_A)

    fields_B = ['Attribute_B1', 'Attribute_B2', 'Attribute_B3']
    values_B = [
        ['Ref_B1', 11, 'value_aa'],
        ['Ref_B2', 23, 'value_ab'],
        ['Ref_B1', 11, 'value_ac'],
        ['Ref_B2', 7, 'value_ac'],
    ]
    table_B = pd.DataFrame(data=values_B, columns=fields_B)

    fields_KEYS = list(TEMP_CONF["tables_info"]["tab_attr"].values())
    values_KEYS = [
        ['Table_A', 'Attribute_A1', 'Y', np.nan, np.nan],
        ['Table_A', 'Attribute_A2', np.nan, np.nan, np.nan],
        ['Table_A', 'Attribute_A3', np.nan, np.nan, np.nan],
        ['Table_B', 'Attribute_B1', 'Y', np.nan, np.nan],
        ['Table_B', 'Attribute_B2', 'Y', np.nan, np.nan],
        ['Table_B', 'Attribute_B3', np.nan, np.nan, np.nan],
    ]
    table_KEYS = pd.DataFrame(data=values_KEYS, columns=fields_KEYS)

    table_REF = pd.DataFrame(
        columns=list(TEMP_CONF["meta_references"]["tab_attr"].values())[1:3],
        data=[
            ['Date', 2024],
            ['Title', '2022_Example#/Template_v2_1; ' ]
        ]
    )

    return {
        'Table_A': table_A,
        'Table_B': table_B,
        TEMP_CONF["tables_info"]["tab_name"]: table_KEYS,
        TEMP_CONF["meta_references"]["tab_name"]: table_REF
    }

def rs_mock_fk_not_unique():
    """Foreign key not unique"""

    fields_A = ['Attribute_A1', 'Attribute_A2', 'Attribute_A3']
    values_A = [
        ['Ref_A1', 'value_1', 'some_value_1'],
        ['Ref_A2', 'value_2', 'some_value_1'],
        ['Ref_A2', 'value_2', 'some_value_2'],
                ]
    table_A = pd.DataFrame(data=values_A, columns=fields_A)

    fields_B = ['Attribute_B1', 'Attribute_B2', 'Attribute_A3']
    values_B = [
        ['Ref_B1', 11, 'some_value_1'],
        ['Ref_B2', 23, 'some_value_1'],
        ['Ref_B1', 11, 'some_value_1'],
        ['Ref_B2', 7, 'some_value_1'],
    ]
    table_B = pd.DataFrame(data=values_B, columns=fields_B)

    fields_KEYS = list(TEMP_CONF["tables_info"]["tab_attr"].values())
    values_KEYS = [
        ['Table_A', 'Attribute_A1', 'Y', np.nan, np.nan],
        ['Table_A', 'Attribute_A2', np.nan, np.nan, np.nan],
        ['Table_A', 'Attribute_A3', np.nan, np.nan, np.nan],
        ['Table_B', 'Attribute_B1', 'Y', np.nan, np.nan],
        ['Table_B', 'Attribute_B2', 'Y', np.nan, np.nan],
        ['Table_B', 'Attribute_A3', np.nan, 'Y', 'Table_A'],
    ]
    table_KEYS = pd.DataFrame(data=values_KEYS, columns=fields_KEYS)

    table_REF = pd.DataFrame(
        columns=list(TEMP_CONF["meta_references"]["tab_attr"].values())[1:3],
        data=[
            ['Date', 2024],
            ['Title', '2022_Example#/Template_v2_1; ']
        ]
    )

    return {
        'Table_A': table_A,
        'Table_B': table_B,
        TEMP_CONF["tables_info"]["tab_name"]: table_KEYS,
        TEMP_CONF["meta_references"]["tab_name"]: table_REF
    }

def rs_mock_fk_not_exist():
    """Foreign key doesn't exist in reference table"""

    fields_A = ['Attribute_A1', 'Attribute_A2', 'Attribute_A3']
    values_A = [
        ['Ref_A1', 'value_1', 'some_value_1'],
        ['Ref_A2', 'value_2', 'some_value_2'],
        ['Ref_A3', 'value_2', 'some_value_3'],
                ]
    table_A = pd.DataFrame(data=values_A, columns=fields_A)

    fields_B = ['Attribute_B1', 'Attribute_B2', 'Attribute_B3']
    values_B = [
        ['Ref_B1', 11, 'value_aa'],
        ['Ref_B2', 23, 'value_ab'],
        ['Ref_B1', 456, 'value_ac'],
        ['Ref_B2', 7, 'value_ac'],
    ]
    table_B = pd.DataFrame(data=values_B, columns=fields_B)

    fields_KEYS = list(TEMP_CONF["tables_info"]["tab_attr"].values())
    values_KEYS = [
        ['Table_A', 'Attribute_A1', 'Y', np.nan, np.nan],
        ['Table_A', 'Attribute_A2', np.nan, np.nan, np.nan],
        ['Table_A', 'Attribute_A3', np.nan, np.nan, np.nan],
        ['Table_B', 'Attribute_B1', 'Y', np.nan, np.nan],
        ['Table_B', 'Attribute_B2', 'Y', np.nan, np.nan],
        ['Table_B', 'Attribute_B3', np.nan, 'Y', 'Table_A'],
    ]
    table_KEYS = pd.DataFrame(data=values_KEYS, columns=fields_KEYS)

    table_REF = pd.DataFrame(
        columns=list(TEMP_CONF["meta_references"]["tab_attr"].values())[1:3],
        data=[
            ['Date', 2024],
            ['Title', '2022_Example#/Template_v2_1; ' ]
        ]
    )
    
    return {
        'Table_A': table_A,
        'Table_B': table_B,
        TEMP_CONF["tables_info"]["tab_name"]: table_KEYS,
        TEMP_CONF["meta_references"]["tab_name"]: table_REF
    }

def rs_mock_fk_without_ref():
    """Foreign key has not reference table defined"""

    fields_A = ['Attribute_A1', 'Attribute_A2', 'Attribute_A3']
    values_A = [
        ['Ref_A1', 'value_1', 'some_value_1'],
        ['Ref_A2', 'value_2', 'some_value_2'],
        ['Ref_A2', 'value_2', 'some_value_3'],
                ]
    table_A = pd.DataFrame(data=values_A, columns=fields_A)

    fields_B = ['Attribute_B1', 'Attribute_B2', 'Attribute_B3']
    values_B = [
        ['Ref_B1', 11, 'value_aa'],
        ['Ref_B2', 23, 'value_ab'],
        ['Ref_B1', 11, 'value_ac'],
        ['Ref_B2', 7, 'value_ac'],
    ]
    table_B = pd.DataFrame(data=values_B, columns=fields_B)

    fields_KEYS = list(TEMP_CONF["tables_info"]["tab_attr"].values())
    values_KEYS = [
        ['Table_A', 'Attribute_A1', 'Y', np.nan, np.nan],
        ['Table_A', 'Attribute_A2', np.nan, np.nan, np.nan],
        ['Table_A', 'Attribute_A3', np.nan, np.nan, np.nan],
        ['Table_B', 'Attribute_B1', 'Y', np.nan, np.nan],
        ['Table_B', 'Attribute_B2', 'Y', np.nan, np.nan],
        ['Table_B', 'Attribute_B3', np.nan, 'Y', np.nan],
    ]
    table_KEYS = pd.DataFrame(data=values_KEYS, columns=fields_KEYS)

    table_REF = pd.DataFrame(
            columns=list(TEMP_CONF['meta_references']['tab_attr'].values())[1:3],
            data=[
                ['Date', 2024],
                ['Title', '2022_Example#/Template_v2_1; ' ]
            ]
        )

    return {
        'Table_A': table_A,
        'Table_B': table_B,
        TEMP_CONF['tables_info']['tab_name']: table_KEYS,
        TEMP_CONF['meta_references']['tab_name']: table_REF
    }

def rs_mock_undefined_pk():
    """Table with no Primary Key"""

    fields_A = ['Attribute_A1', 'Attribute_A2', 'Attribute_A3']
    values_A = [
        ['Ref_A1', 'value_1', 'some_value_1'],
        ['Ref_A2', 'value_2', 'some_value_2'],
                ]
    table_A = pd.DataFrame(data=values_A, columns=fields_A)

    fields_B = ['Attribute_B1', 'Attribute_B2', 'Attribute_B3']
    values_B = [
        ['Ref_B1', 11, 'value_aa'],
        ['Ref_B2', 23, 'value_ab'],
        ['Ref_B1', 456, 'value_aa'],
        ['Ref_B2', 7, 'value_ac'],
    ]
    table_B = pd.DataFrame(data=values_B, columns=fields_B)

    fields_KEYS = list(TEMP_CONF["tables_info"]["tab_attr"].values())
    values_KEYS = [
        ['Table_A', 'Attribute_A1', 'Y', np.nan, np.nan],
        ['Table_A', 'Attribute_A2', np.nan, np.nan, np.nan],
        ['Table_A', 'Attribute_A3', np.nan, np.nan, np.nan],
        ['Table_B', 'Attribute_B1', np.nan, np.nan, np.nan],
        ['Table_B', 'Attribute_B2', np.nan, np.nan, np.nan],
        ['Table_B', 'Attribute_B3', np.nan, np.nan, np.nan],
    ]
    table_KEYS = pd.DataFrame(data=values_KEYS, columns=fields_KEYS)

    table_REF = pd.DataFrame(
        columns=list(TEMP_CONF["meta_references"]["tab_attr"].values())[1:3],
        data=[
            ['Date', 2024],
            ['Title', '2022_Example#/Template_v2_1; ' ]
        ]
    )

    return {
        'Table_B': table_B,
        'Table_A': table_A,
        TEMP_CONF["tables_info"]["tab_name"]: table_KEYS,
        TEMP_CONF["meta_references"]["tab_name"]: table_REF
    }

def rs_mock_shared_name() -> pd.DataFrame:
    """Not foreign keys field have the same name as another field"""
    
    brand = pd.DataFrame(
        columns= ['id', 'brand_name'],
        data= [
            [1, 'Alfa romeo'],
            [2, 'Fiat']
        ]
    )

    car = pd.DataFrame(
        columns= ['id', 'model_name', 'brand_id'],
        data= [
            [1, '500', 2],
            [2, 'Panda', 2],
            [3, '147', 1]
        ]
    )

    fields_KEYS = list(TEMP_CONF["tables_info"]["tab_attr"].values())
    values_KEYS = [
        ['brand', 'id', 'Y', np.nan, np.nan],
        ['brand', 'brand_name', np.nan, np.nan, np.nan],
        ['car', 'id', 'Y', np.nan, np.nan],
        ['car', 'model_name', 'Y', np.nan, np.nan],
        ['car', 'brand_id', np.nan, 'Y', 'brand'],
    ]
    table_KEYS = pd.DataFrame(data=values_KEYS, columns=fields_KEYS)

    table_REF = pd.DataFrame(
            columns=list(TEMP_CONF['meta_references']['tab_attr'].values())[1:3],
            data=[
                ['Date', 2024],
                ['Title', '2022_Example#/Template_v2_1; ' ]
            ]
        )
    
    return {
        'brand': brand,
        'car': car,
        TEMP_CONF['tables_info']['tab_name']: table_KEYS,
        TEMP_CONF['meta_references']['tab_name']: table_REF
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

        checker = check.CheckSpreadsheet(sheet_dict, sheet_dict["tables_info"])
        if expected_exception:
            with self.assertRaises(check.InvalidData) as context:
                checker.validate_spreadsheet()
            aggregated_error = context.exception
            self.assertTrue(any(isinstance(e, expected_exception) for e in aggregated_error.errors))
            self.assertTrue(any(type(e).__name__ == expected_exception.__name__ for e in aggregated_error.errors))
        else:
            try:
                checker.validate_spreadsheet()
            except check.CheckDataError:
                self.fail(f"{name} raised CheckDataError unexpectedly!")
                