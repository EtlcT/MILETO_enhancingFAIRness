from src.utils import json2dict

TEMP_CONF = json2dict("conf/template_conf.json")

METAREF = TEMP_CONF["meta_references"]["tab_name"]
METAREF_ATT = TEMP_CONF["meta_references"]["tab_attr"]

INFO = TEMP_CONF["tables_info"]["tab_name"]
INFO_ATT = TEMP_CONF["tables_info"]["tab_attr"]

DDICT_T = TEMP_CONF["DDict_tables"]["tab_name"]
DDICT_T_ATT = TEMP_CONF["DDict_tables"]["tab_attr"]

DDICT_A = TEMP_CONF["DDict_attributes"]["tab_name"]
DDICT_A_ATT = TEMP_CONF["DDict_attributes"]["tab_attr"]

DDICT_S = TEMP_CONF["DDict_schema"]["tab_name"]
DDICT_S_ATT = TEMP_CONF["DDict_schema"]["tab_attr"]

METAEXTRA = TEMP_CONF["meta_extra"]["tab_name"]
METAEXTRA_ATT = TEMP_CONF["meta_extra"]["tab_attr"]
METAEXTRA_PROP = TEMP_CONF["meta_extra"]["properties"]