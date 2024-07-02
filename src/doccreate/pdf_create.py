import sys
import os
import pdfkit
import base64
from datetime import datetime
import argparse

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..')))

from src.utils import resource_path, json2dict
from src.extraction.retrieve_data import GetSpreadsheetData

TEMP_CONF = json2dict("conf/template_conf.json")
METAREF = TEMP_CONF["meta_references"]["tab_name"]
METAREF_ATT = TEMP_CONF["meta_references"]["tab_attr"]
INFO = TEMP_CONF["infos"]["tab_name"]
INFO_ATT = TEMP_CONF["infos"]["tab_attr"]
DDICT_T = TEMP_CONF["DDict_tables"]["tab_name"]
DDICT_T_ATT = TEMP_CONF["DDict_tables"]["tab_attr"]
DDICT_A = TEMP_CONF["DDict_attributes"]["tab_name"]
DDICT_A_ATT = TEMP_CONF["DDict_attributes"]["tab_attr"]

class createDoc():
    """
        Class that read html file, include parameter and convert to pdf
    """

    def __init__(self, getData: object, output_dir, html_template = "src/templates/doc.html") -> None:
        self.template = resource_path(html_template)
        self.data = getData
        self.output_path = f"{os.path.join(output_dir, self.data.db_name)}.pdf"
        self.erd_path = f"{output_dir}/ERD_{self.data.db_name}.png"

    def createPDF(self) -> None:
        
        with open(self.template, 'r') as file:
            html_template = file.read()
        
        parameters = self._get_parameters()
        html_content = html_template.format(**parameters)

        pdfkit.from_string(html_content, self.output_path, options={"enable-local-file-access": None}, css="src/templates/doc.css")

    # to accept user's template
    def _get_template(self, html_template):
        """Return right path to the template"""
        pass
    
    def get_todays_date(self):
        """Return todays date month litteral in englis """
        today = datetime.now()
        
        # Format the date in a string with the literal month
        formatted_date = today.strftime("%A, %B %d, %Y")
        
        return formatted_date
    
    def _get_parameters(self) -> dict:
        """Return a dictionnary with parameters to fill html template"""

        meta_ref = self.data.sheets_dict[METAREF]
        ddict_table = self.data.sheets_dict[DDICT_T]
        ddict_attr = self.data.sheets_dict[DDICT_A]

        title = meta_ref.loc[
            meta_ref[METAREF_ATT["property"]] == 'Title'
            ][METAREF_ATT["value"]].iloc[0]
        
        authors_name = meta_ref.loc[
            meta_ref[METAREF_ATT["property"]] == 'Creator' 
            ][METAREF_ATT["value"]].iloc[0].split(sep=";")
        
        authors_id = meta_ref.loc[
            meta_ref[METAREF_ATT["property"]] == 'nameIdentifier' 
            ][METAREF_ATT["value"]].iloc[0].split(sep=";")

        authors_id_links = ""
        for name, link in zip(authors_name, authors_id):
            authors_id_links += (
                f"<a href='{link}'>{name}</a> "
            )
        
        doi_a_tag = "incoming"

        keywords = meta_ref.loc[
            meta_ref[METAREF_ATT["property"]] == 'Subject' 
            ][METAREF_ATT["value"]].iloc[0]

        exp_synthesis = "incoming"
        exp_desc = "incoming"

        img_tag_erd = (
            f"<img src='{os.path.abspath(self.erd_path)}' class='full-page-image'"
            " alt='Entity Relationship Diagram' </img>"
        )

        # img_tag_erd = (
        #     f"<img src=data:image/png;base64, '{self.img_base64(self.erd_path)}' class='full-page-image'"
        #     " alt='Entity Relationship Diagram' </img>"
        # )

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

        sql_dump = "incoming"

        parameters = {
            'title': title,
            'authors_id_links': authors_id_links,
            'creation_date': self.get_todays_date() ,
            'db_name': self.data.db_name,
            'DOI_a_tag': "incoming",
            'gitlab_repo_a_tag': doi_a_tag,
            'keywords': keywords,
            'experiment_synthesis': exp_synthesis ,
            'experiment_description': exp_desc,
            'img_tag_erd': img_tag_erd,
            'DDict_table_content': ddict_table_content,
            'DDict_attr_content': ddict_attr_content,
            'sql_dump': sql_dump
        }

        return parameters

    def img_base64(self, img_path):
        
        with open(img_path, "rb") as image_file:
            img_base64_encoded = base64.b64encode(image_file.read())
        
        return img_base64_encoded

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("filepath", help="path to the spreadsheet you want to convert")
    #parser.add_argument("output_dir", help="absolute path to the output directory")
    args = parser.parse_args()
    
    getData = GetSpreadsheetData(filepath=args.filepath)

    doc = createDoc(getData, "data/")
    doc.createPDF()