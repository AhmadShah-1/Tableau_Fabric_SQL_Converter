# Tableau to Fabric SQL Converter

###### Members:

- Syed Ahmad Shah  (sshah6@gmail.com)
- James Sessions (james.sessions@prudential.com)

###### Brief Description:

As our organization migrates analytics dashboards from Tableau to Power BI (Microsoft Fabric), teams are spending significant time and resources manually converting Tableau SQL queries to Fabric-compatible SQL. This manual process is repetitive, and error-prone.

Our solution to this problem involves creating a Python application that automatically translates Tableau SQL scripts as input into its Microsoft Fabric equivalent.

More details are within /main/Assets/Engineering_Python_Proposal 

Details on program flow /main/Assets/Design.png (UML diagram)

### Initial Setup:

first ensure you are in the root directory and run: pip install -r requirements.txt  (I highly recommend seting up a venv [running on python 3.13.3])

### File Setup:

So the entire project is divided to three different implementations:

- Flask App: A route towards the main page allowing users to easily access through a website
- GUI: A gui interface utilizing tkinter (This was created using AI)
- backend_process_email: This implements notable functions from the program to show the flow of the program

##### Flask App:

To launch the flask app, navigate to the "flask_app" folder, and run the entry.py file, which contains a route to a template base.html, it will provide a localhost link to navigate to. If you are having issues launching it, make sure you are in the correct directory and have installed the requirements, and that your ports are available for port forwarding.

This does not yet support file uploads, so you must navigate to /main/sample_queries/Input/Tableau and select a file to copy over to the input box

##### GUI:

The GUI with tkinter was created using AI as there were quite a few requirements to setup to interface with the rest of the program, and a lot of styling and general app requirements. (ui_template.py)

To launch the GUI, navigate to GUI_implement.ipynb and run all of the cells.

Once in the GUI, you can select a SQL file to process by navigating to /main/sample_queries/Input/Tableau and select a file

##### Process:

To run the backend_process_email, it was named this as email support for any issues with the program will be included and wanted to remember that is a feature I would highly like to include, go to backend_process_email.ipynb and run all the cells

### Components:

data_cleaner.py: Normalizes and prepares raw SQL before conversion, removing whitespaces and empty lines, and extracting comments

file_handler.py: Input/Output operations, handles file reading, writing, and validation.

sql_parser.py: Tracks conversion metrics, handles errors as program continues, entry point for conversions.

sql_mappings.py: A dictionary of Tableau -> Fabric functions, has O(1) lookup, and identifies functions that need further handling, along with tracking mapping statistics

Regex_mapping.py: Performs the actual SQL conversion from Tableau to Fabric using regex patterns (Especially for functions that require reordering within a function), also provide flags for lines that haven't been accounted for (manual reviewal, user can edit in the view)

ui_controller.py: Provides a GUI for the application, to be packaged as an exe by pyinstaller for distribution

### Member Contribution:

Syed Ahmad Shah:

- Proposal
- UML Diagram
- Architecture
- GUI, Flask  App, Pytests
- components

James Sessions:

- Proposal
