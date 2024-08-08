import logging
import pandas as pd

from conf.config import *
from src.utils.utils import check_uniqueness
from src.utils.utils_extraction import get_datatables_list

logging.basicConfig(level=logging.ERROR, 
                    format='%(asctime)s %(levelname)s %(message)s',
                    handlers=[logging.FileHandler("Ss2db.log"),
                              logging.StreamHandler()])

class CheckSpreadsheet:
    """
        This class checks that data from spreadsheet is compliant with 
        relationnal schema and template
    """

    def __init__(self, spreadsheet):
        ## GUI: spreadsheet has already been loaded and is stored as dict
        if isinstance(spreadsheet, dict):
            self.sheets_dict = spreadsheet
        ## CLI: spreadsheet is read for the first time
        else:
            self.sheets_dict = pd.read_excel(spreadsheet, sheet_name=None)
        self.tables_info = self._get_tables_info()
        self.metadata_tables = [METAREF, INFO, DDICT_T, DDICT_A]

    def validate_template(self):
        """Raise error if spreasheet is not compliant with template"""

        errors = []
        check_tasks = [
            self.check_metadata_exists,
            self.check_metadata_not_empty,
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
            raise MissingMetadataError(missing_tables)
        
        return

    def check_metadata_not_empty(self):
        """
            Raise error if mandatory fields are not completed
        """
        pass

    def check_infos(self):
        """
            Raise error for missing fields in tables_infos
        """
        pass

    def check_attributes(self):
        """
            Raise error for missing attributes in DDict_Attributes
        """
        pass

    def check_tables(self):
        """
            Raise error for missing tables in DDict_tables
        """
        pass
            
    def check_pk_uniqueness(self) -> None:
        """
        Raise error if fields defined as Primary Key does not
        respect uniqueness criteria
        """
        pk_constraint = self.tables_info[self.tables_info[INFO_ATT['isPK']] == 'Y'][[INFO_ATT['table'],INFO_ATT['attribute']]]
        pk_groupedby_table = pk_constraint.groupby(by=INFO_ATT['table'])
        for table_name, pk_info in pk_groupedby_table:
            pk_info = pk_info[INFO_ATT['attribute']].tolist()

            if check_uniqueness(fields=pk_info,table=self.sheets_dict[table_name]) != True :
                raise PrimaryKeyNonUniqueError(table_name, pk_info)

        return

    def check_fk_existence(self) -> None:
        """
        Raise error if FK is not present in Reference Table
        """

        isFK_condition = self.tables_info[INFO_ATT['isFK']]=='Y'
        fk_by_table_and_ref = (
            self.tables_info[isFK_condition][[
                INFO_ATT["table"],
                INFO_ATT['attribute'],
                INFO_ATT['refTable']
            ]]
            .groupby(by=[INFO_ATT["table"],INFO_ATT['refTable']])
        )

        existence_issues = []

        for (table_name, ref_table_name), fk_info in fk_by_table_and_ref:
            exist_in_ref = (
                col in self.sheets_dict[ref_table_name].columns
                for col in fk_info[INFO_ATT['attribute']]
            )
            
            # check that the attribute exist in reference table
            if not all(exist_in_ref):
                existence_issues.append({
                    "table": table_name,
                    "attribute": fk_info['attribute'].tolist(),
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
        isFK_condition = self.tables_info[INFO_ATT['isFK']]=='Y'
        fk_by_table_and_ref = (
            self.tables_info[isFK_condition][[
                INFO_ATT["table"],
                INFO_ATT['attribute'],
                INFO_ATT['refTable']
            ]]
            .groupby(by=[INFO_ATT["table"],INFO_ATT['refTable']])
        )

        unicity_issues = []

        for (table_name, ref_table_name), fk_info in fk_by_table_and_ref:
            if not check_uniqueness(fields=fk_info['attribute'].tolist(),table=self.sheets_dict[ref_table_name]):
                unicity_issues.append({
                    "table": table_name,
                    "attribute": fk_info['attribute'].tolist(),
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
            if not ('Y' in table_info[INFO_ATT['isPK']].values) :
                raise PrimaryKeyMissingError(table)
        
        return
    

    def check_fk_get_ref(self) -> None:
        """
        Raise AssertionError if a field is defined as FK 
        but has empty ReferenceTable field
        """

        isFK_condition = self.tables_info[INFO_ATT['isFK']]=='Y'
        fk_constraint = self.tables_info[isFK_condition]

        if fk_constraint[INFO_ATT['refTable']].isna().any() != False:
            fk_without_ref = fk_constraint[fk_constraint[INFO_ATT['refTable']].isna()==True]
            raise ReferenceUndefinedError(fk_without_ref.to_string(index=False))
        
        return
    
    def check_no_shared_name(self) -> None:
        """
        Raise AssertionError if fields that belong to different 
        tables have the same name, except for foreign keys (for which
        it could be normal to share the same name as their reference)
        """

        notFK_condition = self.tables_info[INFO_ATT['isFK']].isna()
        attr_no_FK = self.tables_info[notFK_condition]

        group_by_attribute = attr_no_FK.groupby(INFO_ATT['attribute'])
        duplicates_list =  [group for _, group in group_by_attribute if len(group) > 1]
        if duplicates_list:
            duplicates = pd.concat(duplicates_list)
            raise AttributesDuplicateError(duplicates.to_string(index=False))
    
    def _get_tables_info(self):

        datatables_list = get_datatables_list(self.sheets_dict)

        tables_info = self.sheets_dict[INFO][self.sheets_dict[INFO][INFO_ATT["table"]]
                                        .isin(datatables_list)] \
                                        .iloc[:,:5]
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
            "have the same names\nSee duplicates infos:\n"
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