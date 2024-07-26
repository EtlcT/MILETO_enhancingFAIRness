import sys
import os
import pdfkit
from datetime import datetime

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..')))

from conf.config import *
from src.dbcreate.dbcreate import sqliteCreate
from src.utils import resource_path, prettier_sql

class docCreate():
    """
        This class that read html file, include parameters and convert to pdf
    """

    def __init__(self, database, html_template = "src/templates/doc.html") -> None:
        if not isinstance(database, sqliteCreate):
            raise TypeError("database must be an instance of sqliteCreate")
        self.data = database.data
        self.output_path = f"{os.path.join(database.output_dir, database.data.db_name)}.pdf"
        self.template = resource_path(html_template)
        self.erd_path = os.path.normpath(f"{database.output_dir}/ERD_{self.data.db_name}.png")
        self.sql = prettier_sql(database.sql_dump)

    def createPDF(self) -> None:
        with open(self.template, 'r') as file:
            html_template = file.read()
        
        parameters = self._get_parameters()
        html_content = html_template.format(**parameters)

        css_template = resource_path("src/templates/doc.css")

        if(sys.platform.startswith('linux')):
        # code here is added to solve issue on Linux not finding path to binaries properly
            if getattr(sys, 'frozen', False):
                # define path tho qt platforms plugins
                qt_plugins_path = os.path.join(sys._MEIPASS, 'qt5', 'plugins', 'platforms')
                # Set the environment variable
                os.environ['QT_QPA_PLATFORM_PLUGIN_PATH'] = qt_plugins_path
                
                base_path_wkhtmltopdf = os.path.join(sys._MEIPASS, 'wkhtmltopdf', 'wkhtmltopdf')
                config = pdfkit.configuration(wkhtmltopdf=base_path_wkhtmltopdf)
                pdfkit.from_string(
                    html_content,
                    self.output_path,
                    options={"enable-local-file-access": ""},
                    css=css_template, configuration=config
                )

                return
            
        else:
            pdfkit.from_string(
                html_content,
                self.output_path,
                options={"enable-local-file-access": ""},
                css=css_template
            )

        return

    # to accept user's template
    def _get_template(self, html_template):
        """Return right path to the template"""
        pass
    
    def get_todays_date(self):
        """Return todays date month litteral in englis """
        today = datetime.now()
        
        # Format the date in a string with the literal month
        formatted_date = today.strftime("%A, %d %B %Y")
        
        return formatted_date
    
    def _get_parameters(self) -> dict:
        """Return a dictionnary with parameters to fill html template"""

        meta_ref = self.data.sheets_dict[METAREF]
        ddict_table = self.data.sheets_dict[DDICT_T]
        ddict_attr = self.data.sheets_dict[DDICT_A]
        meta_extra = self.data.sheets_dict[METAEXTRA]

        title = meta_ref.loc[
            meta_ref[METAREF_ATT["property"]] == 'Title'
            ][METAREF_ATT["value"]].iloc[0]
        
        authors_name = meta_ref.loc[
            meta_ref[METAREF_ATT["property"]] == 'Creator' 
            ][METAREF_ATT["value"]].iloc[0].split(sep=" ; ")
        
        authors_id = meta_ref.loc[
            meta_ref[METAREF_ATT["property"]] == 'nameIdentifier' 
            ][METAREF_ATT["value"]].iloc[0].split(sep=" ; ")

        authors_id_links = ""
        for name, link in zip(authors_name, authors_id):
            authors_id_links += (
                f"<a href='https://orcid.org/{link}' target='_blank'>{name}</a>&emsp;"
            )
        
        doi_a_tag = "incoming"

        keywords = meta_ref.loc[
            meta_ref[METAREF_ATT["property"]] == 'Subject' 
            ][METAREF_ATT["value"]].iloc[0]
        extra_synthesis = meta_extra.loc[
            meta_extra[METAEXTRA_ATT['property']] == METAEXTRA_PROP["synthesis"]
            ][METAEXTRA_ATT['value']].iloc[0]
        extra_desc = meta_extra.loc[
            meta_extra[METAEXTRA_ATT['property']] == METAEXTRA_PROP["description"]
            ][METAEXTRA_ATT['value']].iloc[0]

        img_tag_erd = (
            f"<img src='{self.erd_path}' class='full-page-image'"
            " alt='Entity Relationship Diagram'>"
        )
        
        ddict_table_content = ""
        for _, row in ddict_table.iterrows():
            ddict_table_content += (
                "<tr>"
                f"<td>{row[DDICT_T_ATT['table']]}</td>"
                f"<td>{row[DDICT_T_ATT['caption']]}</td>"
                "</tr>"
            )

        ddict_attr_content = ""
        for _, row in ddict_attr.iterrows():
            ddict_attr_content += (
                "<tr>"
                f"<td>{row[DDICT_A_ATT['attribute']]}</td>"
                f"<td>{row[DDICT_A_ATT['attType']]}</td>"
                f"<td>{row[DDICT_A_ATT['unit']]}</td>"
                f"<td>{row[DDICT_A_ATT['caption']]}</td>"
                "</tr>"
            )

        parameters = {
            'title': title,
            'authors_id_links': authors_id_links[:-6], #remove last emsp
            'creation_date': self.get_todays_date() ,
            'db_name': self.data.db_name,
            'DOI_a_tag': "incoming",
            'gitlab_repo_a_tag': doi_a_tag,
            'keywords': keywords,
            'extra_synthesis': extra_synthesis ,
            'extra_description': extra_desc,
            'img_tag_erd': img_tag_erd,
            'DDict_table_content': ddict_table_content,
            'DDict_attr_content': ddict_attr_content,
            'sql_dump': self.sql
        }

        return parameters
    