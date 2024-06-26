import unittest
from parameterized import parameterized
from unittest.mock import MagicMock

import pandas as pd
import numpy as np

from src.extraction import retrieve_data, utils

def _read_spreadsheet_mock():
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

    fields_KEYS = ['Table', 'Attribute', 'isPK', 'isFK', 'ReferenceTable']
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

def rs_mock_undefined_pk():
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

    fields_KEYS = ['Table', 'Attribute', 'isPK', 'isFK', 'ReferenceTable']
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
        columns=['key', 'value'],
        data=[
            ['Date', 2024],
            ['Title', 'Template2024'],
            ['DBfileName', '2022_Example#/Template_v2_1; ' ]
        ]
    )

    return {
        'Table_B': table_B,
        'Table_A': table_A,
        'KEYS': table_KEYS,
        'meta.REFERENCES': table_REF
    }

def df1_no_duplicate():
    
    fields_A = ['Attribute_A1', 'Attribute_A2', 'Attribute_A3']
    values_A = [
        ['Ref_A1', 'value_1', 'some_value_1'],
        ['Ref_A2', 'value_2', 'some_value_2'],
        ['Ref_A3', 'value_2', 'some_value_2']
                ]
    table_A = pd.DataFrame(data=values_A, columns=fields_A)

    return table_A

def df1_with_duplicate():
    
    fields_A = ['Attribute_A1', 'Attribute_A2', 'Attribute_A3']
    values_A = [
        ['Ref_A1', 'value_1', 'some_value_1'],
        ['Ref_A1', 'value_2', 'some_value_2'],
        ['Ref_A2', 'value_2', 'some_value_2']
                ]
    table_A = pd.DataFrame(data=values_A, columns=fields_A)

    return table_A

def df2_with_duplicate():

    fields_B = ['Attribute_B1', 'Attribute_B2', 'Attribute_B3']
    values_B = [
        ['Ref_B1', 11, 'value_aa'],
        ['Ref_B2', 23, 'value_ab'],
        ['Ref_B1', 11, 'value_ac'],
        ['Ref_B2', 7, 'value_ac'],
    ]
    table_B = pd.DataFrame(data=values_B, columns=fields_B)

    return table_B

def df3_no_duplicate():

    fields_B = ['Attribute_B1', 'Attribute_B2', 'Attribute_B3']
    values_B = [
        ['Ref_B1', 11, 'value_aa'],
        ['Ref_B2', 23, 'value_ab'],
        ['Ref_B1', 456, 'value_ac'],
        ['Ref_B2', 7, 'value_ac'],
    ]
    table_B = pd.DataFrame(data=values_B, columns=fields_B)

    return table_B

def rs_mock_pk_duplicate():
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

    fields_KEYS = ['Table', 'Attribute', 'isPK', 'isFK', 'ReferenceTable']
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
        'KEYS': table_KEYS,
        'meta.REFERENCES': table_REF
    }

def rs_mock_cpk_duplicate():

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

    fields_KEYS = ['Table', 'Attribute', 'isPK', 'isFK', 'ReferenceTable']
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
        'KEYS': table_KEYS,
        'meta.REFERENCES': table_REF
    }

def rs_mock_fk_not_unique():

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

    fields_KEYS = ['Table', 'Attribute', 'isPK', 'isFK', 'ReferenceTable']
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
        'KEYS': table_KEYS,
        'meta.REFERENCES': table_REF
    }

def rs_mock_fk_not_exist():

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

    fields_KEYS = ['Table', 'Attribute', 'isPK', 'isFK', 'ReferenceTable']
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
        'KEYS': table_KEYS,
        'meta.REFERENCES': table_REF
    }

def rs_mock_fk_without_ref():

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

    fields_KEYS = ['Table', 'Attribute', 'isPK', 'isFK', 'ReferenceTable']
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
        'KEYS': table_KEYS,
        'meta.REFERENCES': table_REF
    }
################################################

class TestExtraction(unittest.TestCase):
    

    @parameterized.expand([
        ('meta.Something', True),
        ('MeTa.CaseUnsensitive', True),
        ('metacognitive', False),
        ('KeYS', True),
        ('not_keys_table', False),
    ])

    def test_regex_exclude_meta(self, text, regexMatch):
        """Check that sheet that contains either 'meta.', 'keys' or 'extra' 
        matches the regex and so return True.
        """

        result = retrieve_data.GetSpreadsheetData._regex_exclude_meta(self, text=text)

        self.assertEqual(result, regexMatch)


    def test_get_datatables_list(self):
        """Check that all tables that contains data are correctly retrieved"""

        retrieve_data.GetSpreadsheetData._read_spreadsheet = MagicMock(return_value=_read_spreadsheet_mock())
        getData = retrieve_data.GetSpreadsheetData('fakepath')
        result = getData._get_datatables_list()

        self.assertListEqual(result, ['Table_A', 'Table_B', 'Table_C', 'Table_D'])

    def test_get_dbname(self):
        """Check that db_name is correctly retrieved without forbidden character"""

        getData = retrieve_data.GetSpreadsheetData('fakepath')
        expected_result = '2022_ExampleTemplate_v2_1'
        result = getData._get_dbname()

        self.assertEqual(expected_result, result)
        
    def test_composite_pk(self):
        """Check that all composite PK are retrieved"""

        retrieve_data.GetSpreadsheetData._read_spreadsheet = MagicMock(return_value=_read_spreadsheet_mock())
        expected_data = [
            ['Table_B', ['Attribute_B1', 'Attribute_B2']]
        ]
        expected_result = pd.DataFrame(
            columns=['Table', 'pk_fields'],
            data=expected_data
        )

        getData = retrieve_data.GetSpreadsheetData('fakepath')
        result = getData._get_composite_pk()

        self.assertEqual(expected_result.equals(result), True)

    @parameterized.expand([
        (df1_no_duplicate(), 'Attribute_A1', True),
        (df1_with_duplicate(), 'Attribute_A1', False),
        (df1_with_duplicate(), ['Attribute_A1'], False),
        (df2_with_duplicate(), ['Attribute_B1', 'Attribute_B2'], False),
        (df3_no_duplicate(), ['Attribute_B1', 'Attribute_B2'], True)
    ])

    def test_check_uniqueness(self, table_df, fields, expected_result):
        """
            Check that function utils.check_uniqueness properly return False
            when there are duplicate True if not
        """

        result = utils.check_uniqueness(table=table_df, fields=fields)
        
        self.assertEqual(result, expected_result)
        
        

    error_pk_not_unique = (
        "invalid primary key constraint ['Attribute_A1'] for table Table_A\n"
        "Primary must be unique"
    )
    
    error_cpk_not_unique = (
        "invalid primary key constraint ['Attribute_B1', 'Attribute_B2'] for table Table_B\n"
        "Primary must be unique"
    )
    
    @parameterized.expand([
        (MagicMock(return_value=rs_mock_pk_duplicate()), error_pk_not_unique ),
        (MagicMock(return_value=rs_mock_cpk_duplicate()), error_cpk_not_unique),
    ])

    def test_check_PK_uniqueness(self, mock_object, errorRaised):
        """
            Check that an assertion is raised if primary key or composite
            primary key contain duplicate
        """

        retrieve_data.GetSpreadsheetData._read_spreadsheet = mock_object
        getData = retrieve_data.GetSpreadsheetData('fakepath')

        with self.assertRaises(AssertionError) as custom_error:
            getData.check_pk_uniqueness()

        
        self.assertEqual(str(custom_error.exception), errorRaised)

    
    error_fk_not_unique = (
        "invalid Foreign key ['Attribute_A3'] for Table_B\n"
        "the reference attribute in Table_A should be unique"
    )
    error_fk_not_exist = (
        "invalid Foreign key ['Attribute_B3'] for Table_B\n"
        "all attributes must be present in Table_A"
    )

    @parameterized.expand([
        (MagicMock(return_value=rs_mock_fk_not_unique()), error_fk_not_unique),
        (MagicMock(return_value=rs_mock_fk_not_exist()), error_fk_not_exist),
        (MagicMock(return_value=_read_spreadsheet_mock()), None)
    ])

    def test_check_fk_existence_and_uniqueness(self, mockObject, expected_result):
        """
        Check that an assertion error is raised if :
         - FK reference does not exist in the reference table
         - FK reference exists but does not comply with unicity constraint
        """
        retrieve_data.GetSpreadsheetData._read_spreadsheet = mockObject
        getData = retrieve_data.GetSpreadsheetData('fakepath')

        if expected_result is not None:

            with self.assertRaises(AssertionError) as custom_error:
                getData.check_FK_existence_and_uniqueness()
            self.assertEqual(str(custom_error.exception), expected_result)

        else:
            self.assertEqual(getData.check_FK_existence_and_uniqueness(),expected_result)

    
    def test_check_pk_defined(self):
        """
        Check that an assertion error is raised if a table has no
        primary key defined
        """

        retrieve_data.GetSpreadsheetData._read_spreadsheet = MagicMock(return_value=rs_mock_undefined_pk())
        getData = retrieve_data.GetSpreadsheetData('fakepath')
        expected_result = 'Table Table_B has no Primary Key defined'

        with self.assertRaises(AssertionError) as custom_error:
            getData.check_pk_defined()

        self.assertEqual(str(custom_error.exception), expected_result)


    def test_check_fk_get_ref(self):
        """
        Check that an assertion is raised if a field is defined as
        a foreing key without having a reference table defined
        """

        retrieve_data.GetSpreadsheetData._read_spreadsheet = MagicMock(return_value=rs_mock_fk_without_ref())
        getData = retrieve_data.GetSpreadsheetData('fakepath')

        with self.assertRaises(AssertionError) as custom_error:
            getData.check_fk_get_ref()
        
        self.assertIn("Every FK should have a reference table defined", str(custom_error.exception))