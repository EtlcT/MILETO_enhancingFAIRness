import logging
import pandas as pd
import numpy as np
import json

from conf.config import *
from src.extraction.create_metadata import *
from src.utils.utils import check_uniqueness, parse_json
from src.utils.utils_extraction import get_datatables_list, rm_extra_tables, process_item

logging.basicConfig(level=logging.ERROR, 
                    format="%(asctime)s %(levelname)s %(message)s",
                    handlers=[logging.FileHandler("Ss2db.log"),
                              logging.StreamHandler()])

class CheckSpreadsheet:
    """
        This class checks that data from spreadsheet is compliant with 
        relationnal schema and template
    """

    def __init__(self, spreadsheet, filename):
        if isinstance(spreadsheet, dict):
        ## GUI: spreadsheet has already been loaded and is stored as dict
            self.sheets_dict = rm_extra_tables(spreadsheet)
        else:
        ## CLI: spreadsheet is read for the first time
            self.sheets_dict = rm_extra_tables(pd.read_excel(spreadsheet, sheet_name=None))
        
        self.metadata_tables = [METAREF, INFO, DDICT_T, DDICT_A]
        # check template is respected before all
        self.json_file = self.create_dc_api_request(filename)
        self.validate_template()
        self.tables_info = self._get_tables_info()
        
    def create_dc_api_request(self, filename):
        """ Create a json file containing metadata in the folder where
        the initial spreadsheet is saved with the name of actual spreadsheet

        This metadata json file is formatted like the json request
        expected by Datacite API (without event information for instance)

        Later in the process this file is moved from input folder to
        output folder ith the named chosed by researcher
        """

        id_dict = json.loads(self.sheets_dict[METAREF].loc[
            self.sheets_dict[METAREF][METAREF_ATT["property"]]=="identifier",
            METAREF_ATT["value"]
            ].values[0])
        doi = id_dict["identifier"]
        dc_request = {}
        dc_request["data"] = {}
        dc_request["data"]["type"] = "dois"
        dc_request["data"]["attributes"] = {}
        dc_request["data"]["attributes"]["doi"] = doi if not doi =="" else ":tba"

        values = self.sheets_dict[METAREF][METAREF_ATT["value"]].apply(parse_json)
        json_dict = dict(zip(
            self.sheets_dict[METAREF][METAREF_ATT["property"]],
            values
        ))
        dc_request["data"]["attributes"].update(json_dict)

        with open(f"{filename}.json", "w", encoding="utf-8") as f:
            json.dump(dc_request, f, ensure_ascii=True, indent=4)


    def validate_template(self):
        """Raise error if spreasheet is not compliant with template"""

        errors = []
        check_tasks = [
            self.check_metadata_exists,
            self.check_infos,
            self.check_attributes,
            self.check_tables,
            self.check_dc_terms, #TODO
        ]
        for check in check_tasks:
            try:
                check()
            except CheckSpreadsheetError as e:
                logging.error(f"{e.__class__.__name__}: {str(e)}\n")
                errors.append(f"{e.__class__.__name__}: {e}\n")
            except KeyError as e:
                pass
        
        if errors:
            raise InvalidTemplate(errors)

    def validate_spreadsheet(self):
        """Raise error if spreadsheet contains errors"""
        errors = []
        check_tasks = [
            self.check_pk_defined,
            self.check_pk_uniqueness,
            self.check_fk_get_ref,
            self.check_fk_existence,
            self.check_fk_uniqueness,
            self.check_no_shared_name
        ]

        for check in check_tasks:
            try:
                check()
            except CheckSpreadsheetError as e:
                logging.error(f"{e.__class__.__name__}: {str(e)}")
                errors.append(f"{e.__class__.__name__}: {e}")
            except KeyError as e:
                pass
        
        if errors:
            raise InvalidData(errors)
    
    def check_metadata_exists(self):
        """
            Raise error if mandatory metadata tables does not exist
        """
        missing_tables = []
        for table_name in self.metadata_tables:
            if self.sheets_dict.get(table_name, None) is None:
                missing_tables.append(table_name)
        if missing_tables:
            raise MissingMetadataTermError(missing_tables)
        
        return

    def check_dc_terms(self):
        """
            Raise error if required datacite metadata terms or secondly
            required terms are not completed
        """

        meta_ref = json2dict("data/output/metadata_2018_ErosionExperiment_Marganai_v2024.json")

        def check_strictly_req(meta_ref):
            """Retrieve required property that have not been compiled"""
            missing_req = []
            for key, value in TERMS_REQ_BY_OBJECT.items():
                match DC_INFO["items"]["required"][key]["type"]:
                    case "list":
                        for entity in meta_ref["data"]["attributes"][key]:
                            if entity[value] is None:
                                missing_req.append(value)
                    case "object":
                        if meta_ref["data"]["attributes"][key][value] is None:
                            missing_req.append(value)
                    case _:
                        if meta_ref["data"]["attributes"][key] is None:
                            missing_req.append(value)
            return missing_req

        missing_req = check_strictly_req(meta_ref)
        
        def check_induced_req(meta_ref):
            """Retrieve datacite property that become mandatory because
            relative property has been compiled
            """

            def get_req_induced_dict():
                """Retrieve a dictionnary of induced required terms with
                DC_JSON_OBJECT value : {term_name: [induced_req_term_name]}
                for sub sub required induced term:
                DC_JSON_OBJECT value : {term_name: {sub_term_name: [induced_req_term_name]}}

                Example:
                ````python
                
                "creators": {
                    "nameIdentifier": ["nameIdentifierScheme"],
                    "affiliation": {
                            "affiliationIdentifier": ["affiliationIdentifierScheme"]
                        }
                    }
                ````
                """
                dc_object_name_list = list(DC_JSON_OBJECT.keys())
                dc_object_idx_list = [DC_JSON_OBJECT[key]["id"] for key in dc_object_name_list]
                req_induced_dict = {}
                i = 0
                for dc_term in dc_object_idx_list:
                    required_term_dict, _ = process_item(dc_term, DC_TERMS)
                    for key, req_if_key in required_term_dict.items():
                        if  DC_TERMS[key].get("required") == 0 and req_if_key:
                            if req_induced_dict.get(dc_object_name_list[i]) is None:
                                req_induced_dict[dc_object_name_list[i]] = {}
                            is_nested_sub = re.match("\d\.[a-zA-Z0-9]\.", key)
                            if is_nested_sub:
                                ancestor_name = DC_ID_NAME_PAIRS[is_nested_sub.group()[:-1]]
                                if req_induced_dict[dc_object_name_list[i]].get(ancestor_name) is None:
                                    req_induced_dict[dc_object_name_list[i]][ancestor_name] = {}
                                req_induced_dict[dc_object_name_list[i]][ancestor_name].update({DC_ID_NAME_PAIRS[key]: [DC_ID_NAME_PAIRS[i] for i in req_if_key]})
                            else:
                                req_induced_dict[dc_object_name_list[i]].update({DC_ID_NAME_PAIRS[key]: [DC_ID_NAME_PAIRS[i] for i in req_if_key]})
                    i += 1
                
                return req_induced_dict
        
            req_induced_dict = get_req_induced_dict()

            def get_missing_req_induced_from(req_induced_dict):
                missing_induced_req = []
                for object_name, req_induced in req_induced_dict.items():
                    # object_name correspond to DC_JSON_OBJECT (creators, publisher...)
                    for term, value in req_induced.items():
                        # term is a DC_TERM term_name (nameIdentifier, affiliation)
                    
                        dc_object = meta_ref["data"]["attributes"][object_name]
                        match dc_object:
                            case list():
                                # dc_object has occurrence 1-n, ex: creators
                                for entity in dc_object:
                                    # check for each creators for instance
                                    if isinstance(value, list):
                                        for sub_req in value:
                                            try:
                                                entity[term]
                                                if entity[term] is not None and entity[sub_req] is None:
                                                    missing_induced_req.append(sub_req)
                                            except:
                                                # term not found because has several occurrences 
                                                # ex: nameIdentifier, in this case the key is term+s like nameIdentifiers
                                                for sub_item in entity[term+"s"]:
                                                    if sub_item[term] is not None and sub_item[sub_req] is None:
                                                        missing_induced_req.append(sub_req)
                                                                        
                                    elif isinstance(value, dict):
                                        for sub_term, sub_req_list in  value.items():
                                            for sub_req in sub_req_list:
                                                for sub_item in entity[term+"s"]:
                                                    if sub_item[term] is not None and sub_item[sub_req] is None:
                                                        missing_induced_req.append(sub_req)
                                                        
                            case dict():
                                for sub_req in value:
                                    if dc_object[term] is not None and dc_object[sub_req] is None:
                                        missing_induced_req.append(sub_req)

                            case _:
                                pass
                return missing_induced_req

            missing_req_induced = get_missing_req_induced_from(req_induced_dict)

            return missing_req_induced

        missing_req_induced = check_induced_req(meta_ref)

        if missing_req:
            raise MissingMetadataTermError(missing_req, missing_req_induced)
            

                
    def check_infos(self):
        """
            Raise error for unknown or missing fields in tables_infos
        """
        errors = []
        attr_oi = [INFO_ATT["table"], INFO_ATT["attribute"]]
        merged_df = self.sheets_dict[INFO][attr_oi].merge(
            GenerateMeta(self.sheets_dict).generate_tables_info(inplace=False)[attr_oi],
            how="outer",
            on=["table", "attribute"],
            indicator=True
        )
        left_only = merged_df[merged_df["_merge"]=="left_only"]
        right_only = merged_df[merged_df["_merge"]=="right_only"]

        if not left_only.empty:
            errors.append(AttributeNotFoundError(
                left_only.drop("_merge", axis=1).to_string(index=False)
            ))
        if not right_only.empty:
            errors.append(AttributeMissingError(
                right_only.drop("_merge", axis=1).to_string(index=False)
            ))

        if errors:
            raise InvalidInformationSchema(errors)

    def check_attributes(self):
        """
            Raise error for missing attributes in DDict_Attributes
        """
        errors = []
        attr_oi = DDICT_A_ATT["attribute"]
        left = self.sheets_dict[DDICT_A][attr_oi].tolist()      # what datadict_attribute contains
        right = (
            GenerateMeta(self.sheets_dict)
            .generate_ddict_attr(inplace=False)[attr_oi]
            .tolist()
        )                                                       # what datadict_attribute should contain
        left_only = [x for x in left if x not in right]         # attribute not found
        right_only = [x for x in right if x not in left]        # attribute missing

        if left_only:
            errors.append(AttributeNotFoundError(left_only))
        if right_only:
            errors.append(AttributeMissingError(right_only))

        if errors:
            raise InvalidDataDictAttribute(errors)
    
    def check_tables(self):
        """
            Raise error for missing tables in DDict_tables
        """
        errors = []
        attr_oi = DDICT_T_ATT["table"]
        left = self.sheets_dict[DDICT_T][attr_oi].tolist()      # what datadict_table contains
        right = (
            GenerateMeta(self.sheets_dict)
            .generate_ddict_tables(inplace=False)[attr_oi]
            .tolist()
        )                                                       # what datadict_table should contain
        left_only = [x for x in left if x not in right]         # table not found
        right_only = [x for x in right if x not in left]        # table missing

        if left_only:
            errors.append(TableNotFoundError(left_only))
        if right_only:
            errors.append(TableMissingError(right_only))

        if errors:
            raise InvalidDataDictTable(errors)
        pass
            
    def check_pk_uniqueness(self) -> None:
        """
        Raise error if fields defined as Primary Key does not
        respect uniqueness criteria
        """
        pk_constraint = self.tables_info[self.tables_info[INFO_ATT["isPK"]] == "Y"][[INFO_ATT["table"],INFO_ATT["attribute"]]]
        pk_groupedby_table = pk_constraint.groupby(by=INFO_ATT["table"])
        for table_name, pk_info in pk_groupedby_table:
            pk_info = pk_info[INFO_ATT["attribute"]].tolist()

            if check_uniqueness(fields=pk_info,table=self.sheets_dict[table_name]) != True :
                raise PrimaryKeyNonUniqueError(table_name, pk_info)

        return

    def check_fk_existence(self) -> None:
        """
        Raise error if FK is not present in Reference Table
        """

        isFK_condition = self.tables_info[INFO_ATT["isFK"]]=="Y"
        fk_by_table_and_ref = (
            self.tables_info[isFK_condition][[
                INFO_ATT["table"],
                INFO_ATT["attribute"],
                INFO_ATT["refTable"]
            ]]
            .groupby(by=[INFO_ATT["table"],INFO_ATT["refTable"]])
        )

        existence_issues = []

        for (table_name, ref_table_name), fk_info in fk_by_table_and_ref:
            exist_in_ref = (
                col in self.sheets_dict[ref_table_name].columns
                for col in fk_info[INFO_ATT["attribute"]]
            )
            
            # check that the attribute exist in reference table
            if not all(exist_in_ref):
                existence_issues.append({
                    "table": table_name,
                    "attribute": fk_info["attribute"].tolist(),
                    "reference_Table": ref_table_name
                })
            
        if existence_issues:
            issues_df = pd.DataFrame(existence_issues)
            issues_summary = issues_df.to_string(index=False)
            raise ForeignKeyNotFoundError(issues_summary)
        
        return
    
    def check_fk_uniqueness(self) -> None:
        """
        Raise error if the reference attribute does not respect unicity
        """
        isFK_condition = self.tables_info[INFO_ATT["isFK"]]=="Y"
        fk_by_table_and_ref = (
            self.tables_info[isFK_condition][[
                INFO_ATT["table"],
                INFO_ATT["attribute"],
                INFO_ATT["refTable"]
            ]]
            .groupby(by=[INFO_ATT["table"],INFO_ATT["refTable"]])
        )

        unicity_issues = []

        for (table_name, ref_table_name), fk_info in fk_by_table_and_ref:
            if not check_uniqueness(fields=fk_info["attribute"].tolist(),table=self.sheets_dict[ref_table_name]):
                unicity_issues.append({
                    "table": table_name,
                    "attribute": fk_info["attribute"].tolist(),
                    "reference_Table": ref_table_name
                })
            
        if unicity_issues:
            issues_df = pd.DataFrame(unicity_issues)
            issues_summary = issues_df.to_string(index=False)
            raise ForeignKeyNonUniqueError(issues_summary)
        return

    def check_pk_defined(self) -> None:
        """Raise AssertionError if a table has no Primary Key defined"""

        for table, table_info in self.tables_info.groupby(by=INFO_ATT["table"]):
            if not ("Y" in table_info[INFO_ATT["isPK"]].values) :
                raise PrimaryKeyMissingError(table)
        
        return
    

    def check_fk_get_ref(self) -> None:
        """
        Raise AssertionError if a field is defined as FK 
        but has empty ReferenceTable field
        """

        isFK_condition = self.tables_info[INFO_ATT["isFK"]]=="Y"
        fk_constraint = self.tables_info[isFK_condition]

        if (fk_constraint[INFO_ATT["refTable"]] == "").any() != False:
            fk_without_ref = fk_constraint[(fk_constraint[INFO_ATT["refTable"]] == "")==True]
            raise ReferenceUndefinedError(fk_without_ref.to_string(index=False))
        
        return
    
    def check_no_shared_name(self) -> None:
        """
        Raise AssertionError if fields that belong to different 
        tables have the same name, except for foreign keys (for which
        it could be normal to share the same name as their reference)
        """

        notFK_condition = self.tables_info[INFO_ATT["isFK"]] != "Y"
        attr_no_FK = self.tables_info[notFK_condition]

        group_by_attribute = attr_no_FK.groupby(INFO_ATT["attribute"])
        duplicates_list =  [group for _, group in group_by_attribute if len(group) > 1]
        if duplicates_list:
            duplicates = pd.concat(duplicates_list)
            raise AttributesDuplicateError(duplicates.to_string(index=False))
    
    def _get_tables_info(self):
        datatables_list = get_datatables_list(self.sheets_dict)

        tables_info = self.sheets_dict[INFO][self.sheets_dict[INFO][INFO_ATT["table"]]
                                        .isin(datatables_list)] \
                                        .iloc[:,:7]
        return tables_info

class CheckSpreadsheetError(Exception):
    """Base class for all exceptions raised by CheckData"""
    pass

class InvalidData(CheckSpreadsheetError):
    """Raised when one or several errors are found in spreadsheet data"""

    def __init__(self, errors):
        self.errors = errors
        error_message = "\n\n".join(f"{type(e).__name__}: {str(e)}" for e in errors)
        super().__init__(f"Data validation failed with {len(errors)} errors:\n{error_message}")

class InvalidTemplate(CheckSpreadsheetError):
    """Raised when one or several errors are found in spreadsheet template"""

    def __init__(self, errors):
        self.errors = errors
        error_message = "\n\n".join(f"{type(e).__name__}: {str(e)}" for e in errors)
        super().__init__(f"Template validation failed with {len(errors)} errors:\n{error_message}")

class PrimaryKeyMissingError(CheckSpreadsheetError):
    """Raised whan a table lacks a Primary Key"""
    def __init__(self, table):
        super().__init__(f"Table {table} has no Primary Key defined")
    
class PrimaryKeyNonUniqueError(CheckSpreadsheetError):
    """Raised if a Primary Key is not unique,
    ie: PK field/s contain duplicates
    """
    def __init__(self, table, pk_field):
        super().__init__(
            f"invalid primary key constraint {pk_field} for table {table}\n"
            "Primary must be unique"
        )

class ForeignKeyNotFoundError(CheckSpreadsheetError):
    """Raised if a field defined as a Foreign Key is missing from 
    its reference table
    """
    def __init__(self, issues_summary) -> None:
        super().__init__(
            f"invalid Foreign key, FK attributes must be present in reference table"
            f"\nSee invalid Foreing key below\n{issues_summary}"
        )

class ForeignKeyNonUniqueError(CheckSpreadsheetError):
    """Raised if a Foreign Key is based on non unique field
    ie: attribute/s in the reference table contain duplicates
    """
    def __init__(self, issues_summary) -> None:
        super().__init__(
            f"invalid Foreign key, Foreign Key attribute should be unique"
            f"\nSee invalid Foreing key below\n{issues_summary}"
        )

class ReferenceUndefinedError(CheckSpreadsheetError):
    """Raised if a Foreign key has no reference table defined"""
    def __init__(self, fk_without_ref) -> None:
        super().__init__(
            "Every FK should have a reference table defined. See Foreign key with no reference below\n"
            f"{fk_without_ref}"
        )

class AttributesDuplicateError(CheckSpreadsheetError):
    """Raised if two attributes have the same name
    without one being defined as a Foreign key based
    on the other
    """
    def __init__(self, duplicates) -> None:
        super().__init__(
            "Except for Foreign keys, different attributes should not"
            " have the same names\nSee duplicates infos:\n"
            f"{duplicates}"
        )

class MissingMetadataError(CheckSpreadsheetError):
    """Raised if mandatory metadata tables do not exist"""

    def __init__(self, missing_tables) -> None:
        super().__init__(
            "The following metadata tables are missing:\n"
            f"{missing_tables}\n"
            "Please check your spreadsheet"
        )

class InvalidInformationSchema(CheckSpreadsheetError):
    """Custom Exception group, raised if invalid fields are detected 
    in tables_infos metadata table ie: missing or unknown field
    """

    def __init__(self, errors) -> None:
        self.error_msg = "\n\n".join(f"{type(e).__name__}: {str(e)}" for e in errors)
        super().__init__(
            f"{INFO} contains errors:\n{self.error_msg}"
        )

class InvalidDataDictAttribute(CheckSpreadsheetError):
    """Custom Exception group, raised if invalid fields are detected 
    in datadict_attribute metadata table ie: missing or unknown field
    """

    def __init__(self, errors) -> None:
        self.error_msg = "\n\n".join(f"{type(e).__name__}: {str(e)}" for e in errors)
        super().__init__(
            f"{DDICT_A} contains errors:\n{self.error_msg}"
        )

class InvalidDataDictTable(CheckSpreadsheetError):
    """Custom Exception group, raised if invalid fields are detected 
    in datadict_table metadata table ie: missing or unknown field
    """

    def __init__(self, errors) -> None:
        self.error_msg = "\n\n".join(f"{type(e).__name__}: {str(e)}" for e in errors)
        super().__init__(
            f"{DDICT_T} contains errors:\n{self.error_msg}"
        )

class AttributeNotFoundError(CheckSpreadsheetError):
    """Raised if attributes in metadata table do not exist in database"""
    def __init__(self, unknown_attributes) -> None:
        self.unknown_attributes = unknown_attributes
        super().__init__(
            "The following attributes are not found in spreadsheet:\n"
            f"{self.unknown_attributes}\n"
            "Please check your spreadsheet"
        )

class AttributeMissingError(CheckSpreadsheetError):
    """Raised if attributes in database are not present in metadata table"""
    def __init__(self, missing_attributes) -> None:
        self.missing_attributes = missing_attributes
        super().__init__(
            f"The following attributes are not found in metadata table:\n"
            f"{self.missing_attributes}\n"
            "Please check your spreadsheet"
        )

class TableNotFoundError(CheckSpreadsheetError):
    """Raised if tables in metadata table do not exist in database"""
    def __init__(self, unknown_tables) -> None:
        self.unknown_tables = unknown_tables
        super().__init__(
            "The following tables are not found in spreadsheet:\n"
            f"{self.unknown_tables}\n"
            "Please check your spreadsheet"
        )

class TableMissingError(CheckSpreadsheetError):
    """Raised if tables in database are not present in metadata table"""
    def __init__(self, missing_table) -> None:
        self.missing_table = missing_table
        super().__init__(
            f"The following tables are not found in metadata table:\n"
            f"{self.missing_table}\n"
            "Please check your spreadsheet"
        )

class MissingMetadataTermError(CheckSpreadsheetError):
    """Raised if mandatory metadata terms is empty"""
    def __init__(self, req_attr, req_if_attr) -> None:
        super().__init__(
            "The following metadata terms are mandatory and have not been"
            f"filled: {req_attr}\n"
            "Some attributes are mandatory if another has been completed,"
            "see the dictionnary of attribute: mandatory_if_attribute:"
            f"{req_if_attr}"
        )