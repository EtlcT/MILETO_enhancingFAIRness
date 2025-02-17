from src.utils.utils_pdf import format_as_pre, html_formatted_sql
from src.utils.utils import resource_path, json2dict
from src.dbcreate.dbcreate import sqliteCreate
from conf.config import *
import sys
import os
import pdfkit
import sqlite3
import pandas as pd

from datetime import datetime

sys.path.insert(0, os.path.abspath(
    os.path.join(os.path.dirname(__file__), '..', '..')))


options = {
    "enable-local-file-access": "",
    "footer-right": "[page] of [toPage]",
    "footer-font-name": "Liberation Sans",
    "footer-font-size": "8"
}


class docCreate():
    """
        This class generate pdf documentation for sqlite database from an
        sqliteCreate object
        Predefined html file (see templates folder) is read, parameters from dbcreate
        are inserted and wkhtmltopdf is used to retrieve pdf format
    """

    def __init__(self, dbcreated, html_template="src/templates/doc.html") -> None:
        if not isinstance(dbcreated, sqliteCreate):
            raise TypeError(f"{dbcreated} must be an instance of sqliteCreate")
        self.data = dbcreated.data
        self.sql = html_formatted_sql(dbcreated.sql_dump)
        self.output_pdf = self._get_pdf_path(dbcreated.output_dir)
        self.erd_path = self._get_erd_path(dbcreated.output_dir)
        self.metadata_path = self._get_json_path(dbcreated.output_dir)
        self.template = resource_path(html_template)

    def createPDF(self) -> None:

        with open(self.template, 'r') as file:
            html_template = file.read()

        parameters = self._get_parameters()
        html_content = html_template.format(**parameters)

        css_template = resource_path("src/templates/doc.css")

        if (sys.platform.startswith('linux')) and getattr(sys, 'frozen', False):
            # code here is added to solve issue on Linux not finding path to binaries properly
            # define path tho qt platforms plugins
            qt_plugins_path = os.path.join(
                sys._MEIPASS, 'qt5', 'plugins', 'platforms')
            # Set the environment variable
            os.environ['QT_QPA_PLATFORM_PLUGIN_PATH'] = qt_plugins_path

            base_path_wkhtmltopdf = os.path.join(
                sys._MEIPASS, 'wkhtmltopdf', 'wkhtmltopdf')
            config = pdfkit.configuration(wkhtmltopdf=base_path_wkhtmltopdf)
            pdfkit.from_string(
                html_content,
                self.output_pdf,
                options=options,
                css=css_template, configuration=config
            )

            return

        else:
            pdfkit.from_string(
                html_content,
                self.output_pdf,
                options=options,
                css=css_template
            )

        return

    def _get_template(self, html_template):
        """Return right path to the template"""
        # TODO
        pass

    def get_todays_date(self):
        """Return todays date month litteral in englis """
        today = datetime.now()

        # Format the date in a string with the literal month
        formatted_date = today.strftime("%A, %d %B %Y")

        return formatted_date

    def _get_parameters(self) -> dict:
        """Return a dictionnary with parameters to fill html template"""

        meta_ref = json2dict(self.metadata_path)
        ddict_table = self.data.sheets_dict[DDICT_T]
        ddict_attr = self.data.sheets_dict[DDICT_A]
        meta_extra = self.data.sheets_dict[METAEXTRA]

        title = meta_ref["data"]["attributes"]["titles"][0]["title"]

        authors_name_and_id = {creator["name"]: creator["nameIdentifiers"][0]
                               ["nameIdentifier"] for creator in meta_ref["data"]["attributes"]["creators"]}

        authors_id_links = ""
        for name, link in authors_name_and_id.items():
            if link != "":
                authors_id_links += (
                    f"<a href='{link}' target='_blank'>{name}</a>&emsp;"
                )
            else:
                authors_id_links += f"{name}&emsp;"

        doi_a_tag = meta_ref["data"]["attributes"]["doi"]
        software_repo_ul_tag = (
            "<ul>"
            "<li><a href='' target='_blank'>MILETO's project website</a></li>"
            "<li><a href='https://github.com/EtlcT/MILETO_enhancingFAIRness' target='_blank'>Github repository</a></li>"
            "<li><a href='https://gitlab.com/EtlcT/miletto_enhancingfairness' target='_blank'>Gitlab repository</a></li>"
            "</ul>"
        )

        keywords = [subject["subject"] for subject in meta_ref["data"]["attributes"]["subjects"] if subject["subject"] is not None]
        if keywords:
            keywords = ", ".join(keywords)

        extra_synthesis = next((item["description"] for item in meta_ref["data"]
                               ["attributes"]["descriptions"] if item["descriptionType"] == "Abstract"), "")
        extra_desc = next((item["description"] for item in meta_ref["data"]
                          ["attributes"]["descriptions"] if item["descriptionType"] == "Other"), "")

        img_tag_erd = (
            "<figure>"
            f"<img src='{self.erd_path}' class='full-page-image' alt='Entity Relationship Diagram'>"
            f"<figcaption>Figure 1: {self.data.db_name} database schema ERD like</figcaption>"
            "</figure>"
        )

        ddict_table_content = ""
        for _, row in ddict_table.iterrows():
            ddict_table_content += (
                "<tr>"
                f"<td>{row[DDICT_T_ATT['table']]}</td>"
                f"<td>{row[DDICT_T_ATT['desc']]}</td>"
                "</tr>"
            )

        ddict_attr_content = ""
        for _, row in ddict_attr.iterrows():
            ddict_attr_content += (
                "<tr>"
                f"<td>{row[DDICT_A_ATT['attribute']]}</td>"
                f"<td>{row[DDICT_A_ATT['unit']]}</td>"
                f"<td>{row[DDICT_A_ATT['desc']]}</td>"
                "</tr>"
            )

        # TODO ? add parameter to conf as dict to facilitate future changes
        parameters = {
            'title': title,
            'authors_id_links': authors_id_links[:-6],  # remove last emsp
            'creation_date': self.get_todays_date(),
            'db_name': self.data.db_name,
            'DOI_a_tag': doi_a_tag,
            'software_repo_ul_tag': software_repo_ul_tag,
            'keywords': keywords,
            'extra_synthesis': format_as_pre(extra_synthesis),
            'extra_description': format_as_pre(extra_desc),
            'img_tag_erd': img_tag_erd,
            'DDict_table_content': ddict_table_content,
            'DDict_attr_content': ddict_attr_content,
            'sql_dump': self.sql
        }

        return parameters

    def _get_erd_path(self, output_dir):
        return os.path.normpath(os.path.join(output_dir, "ERD_" + self.data.db_name + ".png"))

    def _get_pdf_path(self, output_dir):
        return os.path.normpath(os.path.join(output_dir, self.data.db_name + ".pdf"))

    def _get_json_path(self, output_dir):
        return os.path.normpath(os.path.join(output_dir, "metadata_" + self.data.db_name + ".json"))


class sqlite2pdf():
    """Generate pdf documentation directly from sqlite database
    This database must be organized as well as the one generated by 
    sqliteCreate class and must respect the spreadsheet template defined
    """

    def __init__(self, dbpath, output_dir, html_template="src/templates/doc.html") -> None:
        self.data = self.get_sheets_dict_from_db(dbpath)
        self.sql = self.get_sql_from_db()
        self.db_name = self.get_dbname(dbpath)
        self.output_pdf = self._get_pdf_path(output_dir)
        self.erd_path = self._get_erd_path(output_dir)
        self.metadata_path = self._get_json_path(output_dir)
        self.template = resource_path(html_template)

    def createPDF(self) -> None:
        with open(self.template, 'r') as file:
            html_template = file.read()

        parameters = self._get_parameters()
        html_content = html_template.format(**parameters)

        css_template = resource_path("src/templates/doc.css")

        if (sys.platform.startswith('linux')):
            # code here is added to solve issue on Linux not finding path to binaries properly
            if getattr(sys, 'frozen', False):
                # define path tho qt platforms plugins
                qt_plugins_path = os.path.join(
                    sys._MEIPASS, 'qt5', 'plugins', 'platforms')
                # Set the environment variable
                os.environ['QT_QPA_PLATFORM_PLUGIN_PATH'] = qt_plugins_path

        pdfkit.from_string(
            html_content,
            self.output_pdf,
            options=options,
            css=css_template
        )

        return

    def _get_template(self, html_template):
        """Return right path to the template"""
        # TODO
        pass

    def get_todays_date(self):
        """Return todays date month litteral in englis """
        today = datetime.now()

        # Format the date in a string with the literal month
        formatted_date = today.strftime("%A, %d %B %Y")

        return formatted_date

    def _get_parameters(self) -> dict:
        """Return a dictionnary with parameters to fill html template"""

        meta_ref = json2dict(self.metadata_path)

        ddict_table = self.data[DDICT_T]
        ddict_attr = self.data[DDICT_A]
        meta_extra = self.data[METAEXTRA]

        title = meta_ref["data"]["attributes"]["titles"][0]["title"]

        authors_name_and_id = {creator["name"]: creator["nameIdentifiers"][0]
                               ["nameIdentifier"] for creator in meta_ref["data"]["attributes"]["creators"]}

        authors_id_links = ""
        for name, link in authors_name_and_id.items():
            if link != "":
                authors_id_links += (
                    f"<a href='{link}' target='_blank'>{name}</a>&emsp;"
                )
            else:
                authors_id_links += f"{name}&emsp;"

        doi_a_tag = meta_ref["data"]["attributes"]["doi"]
        software_repo_ul_tag = (
            "<ul>"
            "<li><a href='' target='_blank'>MILETO's project website</a></li>"
            "<li><a href='https://github.com/EtlcT/MILETO_enhancingFAIRness' target='_blank'>Github repository</a></li>"
            "<li><a href='https://gitlab.com/EtlcT/miletto_enhancingfairness' target='_blank'>Gitlab repository</a></li>"
            "</ul>"
        )

        keywords = [subject["subject"] for subject in meta_ref["data"]["attributes"]["subjects"] if subject["subject"] is not None]
        if keywords:
            keywords = ", ".join(keywords)

        extra_synthesis = next((item["description"] for item in meta_ref["data"]
                               ["attributes"]["descriptions"] if item["descriptionType"] == "Abstract"), "")
        extra_desc = next((item["description"] for item in meta_ref["data"]
                          ["attributes"]["descriptions"] if item["descriptionType"] == "Other"), "")

        img_tag_erd = (
            "<figure>"
            f"<img src='{self.erd_path}' class='full-page-image' alt='Entity Relationship Diagram'>"
            f"<figcaption>Figure 1: {self.db_name} database schema ERD like</figcaption>"
            "</figure>"
        )

        ddict_table_content = ""
        for _, row in ddict_table.iterrows():
            ddict_table_content += (
                "<tr>"
                f"<td>{row[DDICT_T_ATT['table']]}</td>"
                f"<td>{row[DDICT_T_ATT['desc']]}</td>"
                "</tr>"
            )

        ddict_attr_content = ""
        for _, row in ddict_attr.iterrows():
            ddict_attr_content += (
                "<tr>"
                f"<td>{row[DDICT_A_ATT['attribute']]}</td>"
                f"<td>{row[DDICT_A_ATT['unit']]}</td>"
                f"<td>{row[DDICT_A_ATT['desc']]}</td>"
                "</tr>"
            )

        # TODO ? add parameter to conf as dict to facilitate future changes
        parameters = {
            'title': title,
            'authors_id_links': authors_id_links[:-6],  # remove last emsp
            'creation_date': self.get_todays_date(),
            'db_name': self.db_name,
            'DOI_a_tag': doi_a_tag,
            'software_repo_ul_tag': software_repo_ul_tag,
            'keywords': keywords,
            'extra_synthesis': extra_synthesis,
            'extra_description': extra_desc,
            'img_tag_erd': img_tag_erd,
            'DDict_table_content': ddict_table_content,
            'DDict_attr_content': ddict_attr_content,
            'sql_dump': self.sql
        }

        return parameters

    def get_sheets_dict_from_db(self, dbpath) -> dict:
        """Connect to the database provided and
        Return a dictionnary of pd.dataframes containing values
        in tables as sheets_dict variable used by sqliteCreate
        """

        # connect to database and retrieve tables list
        conn = sqlite3.connect(dbpath)
        cursor = conn.cursor()
        cursor.execute("SELECT name FROM sqlite_master WHERE type = 'table'")
        tables = cursor.fetchall()

        sheets_dict = {}
        # iterate through table, retrieve content and store into dict
        for table in tables:
            table_name = table[0]
            df = pd.read_sql_query("SELECT * FROM {}".format(table_name), conn)
            sheets_dict[table_name] = df

        conn.close()

        return sheets_dict

    def get_sql_from_db(self) -> str:
        """Retrieve the sql statement stored in metadata table and
        formats it in html readable way"""
        return html_formatted_sql(self.data[DDICT_S][DDICT_S_ATT['sql']][0])

    def get_dbname(self, dbpath) -> str:
        return os.path.splitext(os.path.basename(dbpath))[0]

    def _get_erd_path(self, output_dir):
        return os.path.normpath(os.path.join(output_dir, "ERD_" + self.db_name + ".png"))

    def _get_pdf_path(self, output_dir):
        return os.path.normpath(os.path.join(output_dir, self.db_name + ".pdf"))

    def _get_json_path(self, output_dir):
        return os.path.normpath(os.path.join(output_dir, "metadata_" + self.db_name + ".json"))
