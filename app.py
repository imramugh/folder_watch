from flask import Flask, render_template, jsonify
from utils.setup_db import setup_database, File
from utils.logger import system_logger

app = Flask(__name__)
Session = setup_database()

@app.route('/')
def index():
    return render_template('database_viewer_ui.html')

@app.route('/all_records')
def all_records():
    session = Session()
    files = session.query(File).all()
    return jsonify([{
        'id': f.id,
        'file_name': f.file_name,
        'date_modified': f.date_modified.isoformat(),
        'embedded': f.embedded
    } for f in files])

@app.route('/delete/<int:file_id>', methods=['DELETE'])
def delete_file(file_id):
    session = Session()
    file = session.query(File).get(file_id)
    if file:
        session.delete(file)
        session.commit()
        system_logger.info(f"Record deleted from database: {file.file_name}")
        return '', 204
    return 'File not found', 404

if __name__ == '__main__':
    system_logger.info("Database viewer UI started")
    app.run(debug=True)
    system_logger.info("Database viewer UI stopped")