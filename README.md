<h1 style="text-align: center">Enhancing FAIRness: a spreadsheet to sqlite database converter</h1>
<div style="text-align: center"><a href="">Scotti Roberto</a><sup>1</sup>&emsp;<a href="">Giadrossich Filippo</a><sup>1</sup>&emsp;<a href="https://github.com/EtlcT" target="_blank" >Casalta-Badetti Agathe</a><sup>2</sup></div>

<br>
<sup>1</sup> Instigators&emsp;<sup>2</sup> Data engineer - Developper
<br>

## Introduction
<p style="text-align: justify; font-weight: bold">The Enhancing FAIRness project is born from the MILETO research project that focuses on the detection and analysis of so-called
'protection' forests.
Enhancing FAIRness project aims, as its name suggest, to improve data FAIRness by facilitating the sharing of researchers' datasets.
This project begets to NFS-FAIR-DDP python software, that allows to easily convert a spreadsheet that respects a specific template into a sqlite database with a documentation and an Entity Relationship Diagram (ERD).</p>
<p>
CSV is a widespread open format for sharing but it presents limitations in terms of reuse. Ss2db offers to convert spreadsheets with 'one sheets per table' into corresponding database. Mains benefits of Ss2db regarding FAIRness are the following:</p>
<ul>
    <li>Findable</li>
    <ul>
        <li>Support the use of data repositories and the insertion of DOI</li>
    </ul>
    <li>Accessible</li>
    <ul>
        <li>Generate metadata in JSON format (mainly to facilitate communication with data repositories' API)</li>
    </ul>
    <li>Interoperable</li>
    <ul>
        <li>Produce files in Open format (sqlite, png, svg, pdf, json)</li>
        <li>The JSON file produced from user's metadata facilitate communication through API (after mapping to fit API terms)</li>
    </ul>
    <li>Reusable</li>
    <ul>
        <li>Encourage providing rich metadata</li>
        <li>Encourage the use of data dictionnaries to facilitate reuse</li>
    </ul>
</ul>

## Tree Overview
A brief description of files and folders of interests is made ## IN UPPERCASE
```text
|   .gitignore
|   app.py ## TO RUN THE APP AND USED FOR PYINSTALLER BUILD
|   CITATION.cff
|   LICENSE
|   pyproject.toml
|   README.md
|   requirements.txt
|   
+---conf
|       template_conf.json ## TO MODIFY WHEN CHANGES APPLY TO EXCEL TEMPLATE
|       
+---data ## SOME EXCEL FILES FOR TESTING PURPOSE
|   |   ErosionExperiment_Marganai_v2024.xlsx
|   |   2024_ExampleDataSet.xlsx
|   |   db_orders.xlsx
|   |   
|   +---images ## IMAGES FOR DB_ORDERS.XLSX
|   |   
|   \---output
+---doc
|       VS Build Tool 2022 install.png
|       
+---helpers
|       autoDDict_Table.bas ## EXCEL VBA CODE TO PUT IN PESONNAL MACRO WORKBOOK
|       
+---src
|   |   utils.py
|   |   
|   +---dbcreate ## SQLITE FILE CREATION
|   |   |   dbcreate.py
|   |   |   erd_create.py
|   |   |   run.py
|   |   |   __init__.py
|   |           
|   +---doccreate ## PDF DOCUMENTAION CREATION
|   |   |   pdf_create.py
|   |   |   run.py
|   |   |   __init__.py
|   |           
|   +---extraction ## ACCESS DATA IN SPREADSHEET
|   |   |   retrieve_data.py
|   |   |   __init__.py
|   |           
|   +---gui
|   +---templates # USED FOR PDF CREATION
|           doc.css
|           doc.html
|           
+---tests 
    |   test_dbcreate.py
    |   test_extraction.py
    |   __init__.py
    |   
    +---tests_outputs
```

## Getting started

<b>Ss2db executable is available on MILETO's project website <a href="https://temp-lthzdyetwjemvdsnecmw.webadorsite.com" target="_blank">MILETO</a>. You can either clone this repository and follow the intructions on this page.</b> 

### 1. Clone repository

```bash
git clone https://github.com/EtlcT/MILETO_enhancingFAIRness.git
cd MILETO_EnhancingFAIRness
```

### 2. Create and activate virtual environment
```bash
python -m venv venv

# Windows
.\venv\Scripts\activate

# Linux / MacOS
source venv/bin/activate
```

### 3. ⚠️Pre-requisites
1. <b>Ss2db relies on Pygraphiz to generates the ERD, if you want to make full profit of Ss2db we advise you to follow the intructions in this section. If you don't the ERD will be created using another library with a worse render.</b>
<br>
For detailed intructions see <a href="https://github.com/pygraphviz/pygraphviz/blob/main/INSTALL.txt" target="_blank">PyGraphiz INTALL instructions</a>
<br>
Otherwise you can find the main steps to achieve below but as explained by PyGraphiz developpers additionnal advanced steps may be required. If you encounter issues please refers to PyGraphiz instructions directly.

2. <b>Ss2db also relies on wkhtmltopdf. You can download it <a href="https://wkhtmltopdf.org/downloads.html" target="_blank">wkhtmltopdf website</a>.</b>

#### Linux / MacOS

```bash
# Linux
sudo apt-get install graphviz graphviz-dev
sudo apt-get install python3-dev
pip install pygraphviz

sudo apt-get install libpq-dev
sudo apt-get install pkg-config
sudo apt-get install libmysqlclient-dev
sudo apt-get install wkhtmltopdf
```

```bash
# MacOS
brew install graphviz
pip install pygraphviz
```

#### Windows
On Windows Graphiz need to be intalled manually and specific tools are required.

1. Download and install graphiz 2.46.0 or greater stable version for Windows on <a href="https://graphviz.org/download/">Graphviz.org</a>
2. Dowload and install Build Tools on <a href="https://visualstudio.microsoft.com/fr/visual-cpp-build-tools/">Microsoft.com</a>
During install under "Desktop & Mobile" select "Desktop development in C++" as shown on the image below (in French 😿) 

<img src="doc/VS Build Tool 2022 install.png"></img>

Then install PyGraphiz from command-line.
```PowerShell
python -m pip install `
--config-settings="--global-option=build_ext" `
--config-settings="--global-option=-IC:\Program Files\Graphviz\include" `
--config-settings="--global-option=-LC:\Program Files\Graphviz\lib" `
pygraphviz
```

Add to system environment variables path to:
- Path\to\Graphiz\bin
- Path\to\wkhtml\bin

### 4. Install dependencies

```bash
pip install -r requirements.txt
```

### 5. Running App.py

```bash
python app.py
```

## Testing the app
You can test our app with spreadsheets present in the data folder.

## About unittest
Several unittest have been implemented using unittest and parametrized libraries. There are stored in tests folder and can be runned with unittest command from project's root folder.

<b>Before running unittest</b> please create a into tests folder a conf.json file with the following content:
```json
{
    "img_path": {
        "img_1": "absolute_path_to\\MILETO_enhancingFAIRness\\data\\images\\suitcase.jpg",
        "img_2": "absolute_path_to\\MILETO_enhancingFAIRness\\data\\images\\phone_charger.jpg",
        "img_3": "absolute_path_to\\MILETO_enhancingFAIRness\\data\\images\\lotr_dvd.jpg"
    }
}
```

```bash
python -m unittest
```

## Building the executable
The executable has been created using <a href="https://pyinstaller.org/en/stable/" target="_blank">PyInstaller</a>. To reproduce the bundled app follow the instructions below.

```bash
# Linux
python -m PyInstaller \
--name "NFS-FAIR-DDP_v1_1_0_beta" \
--add-data "/path_to/MILETO_enhancingFAIRness/conf/:conf/" \
--add-data "/path_to/MILETO_enhancingFAIRness/src/templates/:src/templates" \
--add-data "/path_to/MILETO_enhancingFAIRness/src/gui/assets/:src/gui/assets" \
--add-data "/path_to/MILETO_enhancingFAIRness/assets/logo.ico:assets/" \
--add-binary "/usr/lib/x86_64-linux-gnu/graphviz:graphviz" \
--add-binary "/usr/bin/dot:graphviz" \
--add-binary "/usr/bin/wkhtmltopdf:wkhtmltopdf" \
--add-binary "/usr/lib/x86_64-linux-gnu/qt5/plugins/platforms:qt5/plugins/platforms" \
--hidden-import tkinter \
--hidden-import PIL._tkinter_finder \
--distpath "/path_to_output_dir/dist" \
--workpath "/path_to_output_dir/build" \
--specpath "/path_to_output_dir/" \
--onedir app.py
```

```Powershell
# Windows
python -m PyInstaller `
--name "NFS-FAIR-DDP" `
--add-data "path_to\MILETO_enhancingFAIRness\conf\template_conf.json:conf\" `
--add-data "path_to\MILETO_enhancingFAIRness\conf\dc_meta_terms.json:conf\" `
--add-data "path_to\MILETO_enhancingFAIRness\conf\metadata_properties.json:conf\" `
--add-data "path_to\MILETO_enhancingFAIRness\src\templates\:src\templates" `
--add-data "path_to\MILETO_enhancingFAIRness\assets\logo.ico:assets\" `
--add-data "path_to\MILETO_enhancingFAIRness\src\gui\assets\:src\gui\assets\" `
--add-binary "C:\Program Files\Graphviz\bin\*:graphviz" `
--add-binary "C:\Program Files\wkhtmltopdf\bin\*:wkhtmltopdf" `
-i "path_to\MILETO_enhancingFAIRness\assets\logo.ico" `
--distpath "path_to_output_dir\dist" `
--workpath "path_to_output_dir\build" `
--specpath "path_to_output_dir\" `
--hide-console hide-early `
--noconfirm `
--onedir app.py
```
