# -*-coding: utf-8 -*-

""" This module create a simple ERD schema relative to the spreadsheet
which data is accessed by retrieve_data.py script
"""

import os
import pandas as pd
import numpy as np
import graphviz

from conf.config import *
from src.utils.utils import rotate_image

class ERD_maker():
    """
    Class that create ERD schema for database
    """

    def __init__(self, db_name: str, output_dir: str, tables_infos: pd.DataFrame) -> None:
        self.tables_info = tables_infos
        self.db_name = db_name
        self.output_erd = os.path.normpath((output_dir + '/ERD_' + self.db_name))

    def create_erd(self) -> bytes:
        """Create a simple ERD with Entities, their attributes,
        information about Primary keys and Foreign Keys and relation
        between entities

        Save the erd as svg and return it as Blob

        """

        # instanciate a graph object with no duplicate edges
        erd = graphviz.Graph(comment=self.db_name, strict=True)

        group_by_table = self.tables_info.groupby(INFO_ATT['table'])

        for table_name, table_info in group_by_table:

            html_label = str()
            for _, row in table_info.iterrows():

                # break line between each attribute
                html_label+= "<br/>"
                if row[INFO_ATT['isPK']] is not np.nan:
                    # if PK attribute is underlined
                    html_label+="<u>"
                    if row[INFO_ATT['isFK']] is not np.nan:
                        # if FK attribute in italic
                        html_label+=f"<i>{row[INFO_ATT['attribute']]}</i></u>"
                        # add relationship between table and reference table
                        erd.edge(table_name, row[INFO_ATT['refTable']])
                    else:
                        # close underline tag
                        html_label+= f"{row[INFO_ATT['attribute']]}</u>"
                elif row[INFO_ATT['isFK']] is not np.nan:
                    html_label+=f"<i>{row[INFO_ATT['attribute']]}</i>"
                    erd.edge(table_name, row[INFO_ATT['refTable']])
                else:
                    # neither PK nor FK
                    html_label+= row[INFO_ATT['attribute']]

            # Add table name as entity name in bold
            html_label = f"<b>{table_name}</b><br/>" + html_label
            self.add_entity(erd, table_name, html_label)
        
        # png to facilitate insertion in pdf,
        # deleted after pdf generation
        erd.render(self.output_erd, format='png', cleanup=True)
        rotate_image((self.output_erd + ".png"))

        # svg to facilitate customization by the user
        erd.render(self.output_erd, format='svg', cleanup=True)

        png_as_blob = erd.pipe(format='png')

        return png_as_blob

    def add_entity(self, graph, entity_name, html_label) -> None:
        """Create a node in graph object
        having rectangle shape, black border and label that include
        table name (entity) and attributes
        """

        graph.node(
            entity_name,
            label=f"<{html_label}>",
            shape="rectange",
            color="black",
        )

        return
    