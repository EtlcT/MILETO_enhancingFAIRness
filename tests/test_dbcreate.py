import unittest
import os
import time
from parameterized import parameterized
from unittest.mock import MagicMock

import pandas as pd
import numpy as np
from src import utils
from src.extraction.retrieve_data import GetSpreadsheetData
from src.dbcreate.dbcreate import sqliteCreate
from conf.config import *

TEST_CONF = utils.json2dict("tests/conf.json")
IMG_1 = TEST_CONF['img_path']["img_1"]
IMG_2 = TEST_CONF['img_path']["img_2"]
IMG_3 = TEST_CONF['img_path']["img_3"]

def rs_mock() -> pd.DataFrame:
    
    clients = pd.DataFrame(
        columns= ['client_name', 'client_address', "city_id"],
        data= [
            ["John Doe", 'address 1', 1],
            ["Jane Doe", 'address 2', 2],
            ["John Smith", 'address 3', 1],
        ]
    )

    orders = pd.DataFrame(
        columns= ['order_id', 'client_name', 'client_address', 'products', 'purchase_date'],
        data= [
            [1, "Jane doe", "address 2", ["product_1", "product_2", "product_3"], "27.01.2024"],
            [2, "Jane doe", "address 2", ["product_2", "product_2"], "14.03.2024"],
            [3, "John doe", "address 1", ["product_2", "product_3"], "09.06.2024"],
        ]
    )

    cities = pd.DataFrame(
        columns= ["city_id", "city_name", "total_clients"],
        data= [
            [1, "San Francisco", 2],
            [2, "Los Angeles", 1]
        ]
    )

    products = pd.DataFrame(
        columns= ['product_id', 'product_name', 'price', 'photo'],
        data= [
            ['product_1', 'suitcase_a', 98.50, IMG_1],
            ['product_2', 'phone_charger_b', 7.99, IMG_2],
            ['product_3', 'lotr_dvd', 15.50, IMG_3]
        ]
    )

    fields_tables_info = list(TEMP_CONF["info"]["tab_attr"].values())
    values_tables_info = [
        ['clients', 'client_name', 'Y', np.nan, np.nan],
        ['clients', 'client_address', 'Y', np.nan, np.nan],
        ['clients', 'city_id', np.nan, 'Y', "cities"],
        ['orders', 'order_id', 'Y', np.nan, np.nan],
        ['orders', 'client_name', np.nan, 'Y', "clients"],
        ['orders', 'client_address', np.nan, 'Y', "clients"],
        ['orders', 'products', np.nan, np.nan, np.nan],
        ['orders', 'purchase_date', np.nan, np.nan, np.nan],
        ['cities', 'city_id', 'Y', np.nan, np.nan],
        ['cities', 'city_name', np.nan, np.nan, np.nan],
        ['cities', 'total_clients', np.nan, np.nan, np.nan],
        ['products', 'product_id', 'Y', np.nan, np.nan],
        ['products', 'product_name', np.nan, np.nan, np.nan],
        ['products', 'price', np.nan, np.nan, np.nan],
        ['products', 'photo', np.nan, np.nan, np.nan],
    ]
    tables_info = pd.DataFrame(data=values_tables_info, columns=fields_tables_info)

    table_REF = pd.DataFrame(
            columns=list(TEMP_CONF['meta_references']['tab_attr'].values())[0:3],
            data=[
                [1, 'Identifier', "fake_doi"],
                [5, "PublicationYear", 2024],
            
            ]
        )
    
    fields_ddict_tables = ["table", "caption"]
    values_ddict_tables = [
        ["clients", "list of clients and information"],
        ["orders", "purchase orders"],
        ["products", "product in sales with price and photos"],
        ["cities", "list of cities and number of clients"]
    ]

    ddict_tables = pd.DataFrame(
        columns=fields_ddict_tables,
        data= values_ddict_tables
    )

    fields_ddict_attr = ["attributes", "attType", "unit", "caption"]
    values_ddict_attr = [
        ["client_name", "id", "", "client fullname"],
        ["client_address", "id", "", "clientaddress"],
        ["order_id", "id", "", "identifier for orders"],
        ["products", "list of txt", "", "list of products ordered"],
        ["purchase_date", "date", "", "date of the purchase"],
        ["city_id", "id", "", "identifier for city"],
        ["city_name", "txt", "", "name of the city"],
        ["total_clients", "num", "", "total number of client that lives in this city"],
        ["product_id", "id", "", "identifier for the product"],
        ["product_name", "txt", "", "name of the product"],
        ["price", "num", "euro", "price of the product in euros"],
        ["photo", "txt", "", "photo of the product"]
    ]
    ddict_attr = pd.DataFrame(
        columns=fields_ddict_attr,
        data= values_ddict_attr
    )

    return {
        'clients': clients,
        'orders': orders,
        'cities': cities,
        'products': products,
        INFO: tables_info,
        METAREF: table_REF,
        DDICT_T: ddict_tables,
        DDICT_A: ddict_attr
    }

class TestDBCreate(unittest.TestCase):
    GetSpreadsheetData._read_spreadsheet = MagicMock(return_value=rs_mock())

    def test_create_db(self):
        """Check that a sqlite file with database name is created
        in the output directory
        """

        data = GetSpreadsheetData('fakepath/to/spreadsheet/db_orders.xlsx')
        output_path = os.path.abspath(os.path.normpath("tests/tests_outputs/"))
        db_name = f"{data.db_name}.sqlite"
        db_file_path = os.path.join(output_path, db_name)

        sqlite_db = sqliteCreate(getData=data, output_dir=output_path)

        sqlite_db.create_db()

        self.assertTrue(os.path.exists(db_file_path))

        if os.path.exists(db_file_path):
            os.remove(db_file_path)


    def test_insert_data_and_meta_tables_create(self):
        """Check that insert_data and meta_tables_create 
        modify the sqlite file
        """

        data = GetSpreadsheetData('fakepath/to/spreadsheet/db_orders.xlsx')
        output_path = os.path.abspath(os.path.normpath("tests/tests_outputs/"))
        db_name = f"{data.db_name}.sqlite"
        db_file_path = os.path.join(output_path, db_name)

        self.assertFalse(os.path.exists(db_file_path))
        sqlite_db = sqliteCreate(getData=data, output_dir=output_path)
        sqlite_db.create_db()

        initial_modification_time = os.path.getmtime(db_file_path)

        # the modification is done too fast so we simulate more time
        time.sleep(0.2)

        sqlite_db.insert_data()

        first_modification_time = os.path.getmtime(db_file_path)

        self.assertGreater(first_modification_time, initial_modification_time)

        sqlite_db.meta_tables_create()

        second_modification_time = os.path.getmtime(db_file_path)

        self.assertGreater(second_modification_time, first_modification_time)

        if os.path.exists(db_file_path):
            os.remove(db_file_path)

    #! can't delete files after test becausse eralchimy render_er() keep
    #! connection to database opened
    def test_ddict_schema_create(self):
        """Check that ddict_schema_create modify the sqlite
        and create a ERD_dbname.png is created in output dir
        """

        
        data = GetSpreadsheetData('fakepath/to/spreadsheet/db_orders_test_erd.xlsx')
        output_path = os.path.abspath(os.path.normpath("tests/tests_outputs/"))
        db_name = f"{data.db_name}.sqlite"
        db_file_path = os.path.join(output_path, db_name)

        if os.path.exists(db_file_path):
            os.remove(db_file_path)

        sqlite_db = sqliteCreate(getData=data, output_dir=output_path)

        sqlite_db.create_db()
        sqlite_db.insert_data()

        # for file modification tracking
        initial_modification_time = os.path.getmtime(db_file_path)

        erd_name = f"ERD_{data.db_name}.png"
        erd_file_path = os.path.join(output_path, erd_name)

        time.sleep(0.2)
        sqlite_db.ddict_schema_create()

        first_modification_time = os.path.getmtime(db_file_path)

        # check sqlite is modified
        self.assertGreater(first_modification_time, initial_modification_time)

        # check ERD image is created
        self.assertTrue(os.path.exists(erd_file_path))

