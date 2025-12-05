import sys
from flask import Flask, request
from flask import render_template
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))
from components.data_cleaner import SQLCleaner
from components.sql_parser import SQLConverter

app = Flask(__name__)
converter = SQLConverter()
cleaner = SQLCleaner()

@app.route("/", methods=["GET", "POST"])
def index():
    tableau_sql = ""
    fabric_sql = ""
    errors = []

    if request.method == "POST":
        tableau_sql = request.form.get("tableau_sql", "").strip()
        
        if tableau_sql:
            try:
                cleaned_sql = cleaner.clean_query(tableau_sql)
                no_comments_sql, _ = cleaner.extract_comments(cleaned_sql)
                statements = cleaner.split_statements(no_comments_sql)

                converted_statements = []
                errors = []
                
                for statement in statements:
                    fabric_sql, metrics, flagged = converter.convert_query(statement)
                    converted_statements.append(fabric_sql)
                    errors.append(flagged)
                '''
                fabric_sql, metrics, flagged = converter.convert_query(statements)
                errors.append(flagged)
                '''

            except Exception as e:
                fabric_sql = ""
                errors = [(0, f"Error: {str(e)}")]

    return render_template("base.html", 
                          tableau_sql=tableau_sql,
                          fabric_sql=fabric_sql,
                          errors=errors)





if __name__ == "__main__":
    app.run(debug=True)