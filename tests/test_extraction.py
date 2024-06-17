import unittest
from parameterized import parameterized
from unittest.mock import MagicMock

import pandas as pd
import numpy as np

from src.extraction import retrieve_data

def _read_spreadsheet_mock():
    fields_A = ['Attribute_A1', 'Attribute_A2', 'Attribute_A3']
    values_A = [
        ['Ref_A1', 'value_1', 'some_value_1'],
        ['Ref_A2', 'value_2', 'some_value_2'],
                ]
    table_A = pd.DataFrame(data=values_A, columns=fields_A)

    fields_B = ['Attribute_A1', 'Attribute_B2', 'Attribute_B3']
    values_B = [
        ['Ref_A1', 'Ref_B1', 11],
        ['Ref_A1', 'Ref_B2', 23],
        ['Ref_A2', 'Ref_B1', 456],
        ['Ref_A2', 'Ref_B2', 7],
    ]
    table_B = pd.DataFrame(data=values_B, columns=fields_B)

    fields_C = ['Attribute_A1', 'Attribute_B1', 'Attribute_C1', 'Attribute_D1', 'Attribute_C3']
    values_C = [
        ['Ref_A1', 'Ref_B1', 'Ref_C1', 'Ref_D2', 12],
        ['Ref_A2', 'Ref_B1', 'Ref_C2', 'Ref_D3', 42],
        ['Ref_A1', 'Ref_B1', 'Ref_C3', 'Ref_D1', 200]
    ]
    table_C = pd.DataFrame(data=values_C, columns=fields_C)

    fields_D = ['Attribute_D1', 'Attribute_D2']
    values_D = [
        ['Ref_D1', 'value_aa'],
        ['Ref_D2', 'value_ab'],
        ['Ref_D3', 'value_aa']
    ]
    table_D = pd.DataFrame(data=values_D, columns=fields_D)

    fields_KEYS = ['Table', 'Attribute', 'isPK', 'isFK', 'ReferenceTab']
    values_KEYS = [
        ['Table_A', 'Attribute_A1', 'Y', np.nan, np.nan],
        ['Table_A', 'Attribute_A2', np.nan, np.nan, np.nan],
        ['Table_A', 'Attribute_A3', np.nan, np.nan, np.nan],
        ['Table_B', 'Attribute_A1', 'Y', 'Y', 'Table_A'],
        ['Table_B', 'Attribute_B1', 'Y', np.nan, np.nan],
        ['Table_B', 'Attribute_B2', np.nan, np.nan, np.nan],
        ['Table_C', 'Attribute_A1', np.nan, 'Y', 'Table_A'],
        ['Table_C', 'Attribute_B1', np.nan, 'Y', 'Table_B'],
        ['Table_C', 'Attribute_C1', 'Y', np.nan, np.nan],
        ['Table_C', 'Attribute_D1', np.nan, 'Y', 'Table_D'],
        ['Table_C', 'Attribute_C3', np.nan, np.nan, np.nan],
        ['Table_D', 'Attribute_D1', 'Y', np.nan, np.nan],
        ['Table_D', 'Attribute_D2', np.nan, np.nan, np.nan],
    ]
    table_KEYS = pd.DataFrame(data=values_KEYS, columns=fields_KEYS)

    table_REF = pd.DataFrame(
        columns=['key', 'value'],
        data=[
            ['Date', 2024],
            ['Title', 'Template2024'],
            ['DBfileName', '2022_Example#/Template_v2_1; ' ]
        ]
    )

    return {
        'Table_A': table_A,
        'Table_B': table_B,
        'Table_C': table_C,
        'Table_D': table_D,
        'KEYS': table_KEYS,
        'meta.REFERENCES': table_REF
    }


class TestExtraction(unittest.TestCase):
    retrieve_data.GetSpreadsheetData._read_spreadsheet = MagicMock(return_value=_read_spreadsheet_mock())

    @parameterized.expand([
        ('meta.Something', True),
        ('MeTa.CaseUnsensitive', True),
        ('metacognitive', False),
        ('KeYS', True),
        ('not_keys_table', False),
    ])

    def test_regex_exclude_meta(self, text, regexMatch):
        """Check that sheet that contains either 'meta', 'keys' or 'extra' 
        matches the regex and so return True.
        """

        result = retrieve_data.GetSpreadsheetData._regex_exclude_meta(self, text=text)

        self.assertEqual(result, regexMatch)


    def test_get_datatables_list(self):
        """Check that all tables that contains data are correctly retrieved"""
        
        getData = retrieve_data.GetSpreadsheetData('fakepath')
        getData._read_spreadsheet = MagicMock(_read_spreadsheet_mock)
        result = getData._get_datatables_list()

        self.assertListEqual(result, ['Table_A', 'Table_B', 'Table_C', 'Table_D'])

    def test_get_keys_df(self):
        """Check that we retrieve all attributes that are either defined
        as PK or FK and not the others
        """

        getData = retrieve_data.GetSpreadsheetData('fakepath')
        result = getData._get_keys_df()

        expected_result = pd.DataFrame(
            columns= ['Table', 'Attribute', 'isPK', 'isFK', 'ReferenceTab'],
            data= [
                ['Table_A', 'Attribute_A1', 'Y', np.nan, np.nan],
                ['Table_B', 'Attribute_A1', 'Y', 'Y', 'Table_A'],
                ['Table_B', 'Attribute_B1', 'Y', np.nan, np.nan],
                ['Table_C', 'Attribute_A1', np.nan, 'Y', 'Table_A'],
                ['Table_C', 'Attribute_B1', np.nan, 'Y', 'Table_B'],
                ['Table_C', 'Attribute_C1', 'Y', np.nan, np.nan],
                ['Table_C', 'Attribute_D1', np.nan, 'Y', 'Table_D'],
                ['Table_D', 'Attribute_D1', 'Y', np.nan, np.nan]
            ]
        )

        self.assertEqual(expected_result.equals(result), True) # use Dataframe.equals from pandas library to check