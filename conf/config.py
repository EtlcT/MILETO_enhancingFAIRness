from src.utils.utils import json2dict, get_name_id_pairs

TEMP_CONF = json2dict("conf/template_conf.json")

METAREF = TEMP_CONF["meta_terms"]["tab_name"]
METAREF_ATT = TEMP_CONF["meta_terms"]["tab_attr"]

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

META_TABLES = [METAREF, INFO, DDICT_T, DDICT_A, DDICT_S, METAEXTRA]
COLUMN_WIDTH_S = [INFO_ATT["type"], INFO_ATT["isPK"], INFO_ATT["isFK"], DDICT_A_ATT["unit"]]

# accepted regex for columm that contains image path to convert to blob
IMG_COL_REGEX = ["img_", "image_"]

# DC terms
DC_INFO = json2dict("conf/dc_meta_terms.json")
TERMS_REQ = [key for key in DC_INFO["items"]["required"].keys()]
DC_JSON_OBJECT = {**DC_INFO["items"]["required"], **DC_INFO["items"]["other"]}
DC_TERMS = DC_INFO["properties"]
DC_NAME_ID_PAIRS = get_name_id_pairs(DC_TERMS)
