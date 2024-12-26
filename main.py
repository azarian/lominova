from flask import Flask, request, jsonify, render_template
import threading
import uuid
import time
import json
from textractor import Textractor
import boto3
from botocore.exceptions import ClientError

app = Flask(__name__)
jobs = {}

DRY_RUN = True

def initialize_textractor():
    """Initialize Textractor client with AWS credentials"""
    try:
        # Assuming AWS credentials are configured in the environment
        textract_client = boto3.client('textract')
        return Textractor(textract_client=textract_client)
    except Exception as e:
        print(f"Error initializing Textractor: {e}")
        return None

def extract_document_info(file_path, textractor_client,dry_run=False):
    """
    Extract information from document using Textractor
    Returns a dictionary of extracted fields and their values
    """
    if dry_run:
        return {
            "forms": {
                "field1": "value1",
                "field2": "value2"
            },
            "tables": [
                ["row1", "row2"],
                ["col1", "col2"]
            ],
            "raw_text": "This is a sample text"
        }
    try:
        # Process the document
        document = textractor_client.process_document(file_path)
        
        # Extract forms (key-value pairs)
        forms_dict = {}
        for field in document.forms:
            if field.key and field.value:  # Ensure both key and value exist
                forms_dict[field.key.text] = field.value.text
        
        # Extract tables
        tables_data = []
        for table in document.tables:
            table_data = []
            for row in table.rows:
                row_data = [cell.text if cell else "" for cell in row.cells]
                table_data.append(row_data)
            tables_data.append(table_data)
        
        return {
            "forms": forms_dict,
            "tables": tables_data,
            "raw_text": document.text
        }
    except Exception as e:
        raise Exception(f"Error extracting document info: {str(e)}")

def validate_extracted_data(extracted_data, validation_config):
    """Validate extracted data against configuration rules"""
    validation_results = {
        "passed": True,
        "errors": []
    }
    
    for field, constraints in validation_config.items():
        # Check in forms data
        if field in extracted_data['forms']:
            value = extracted_data['forms'][field]
            
            # Handle numeric validations
            if any(op in constraints for op in ['>', '<', '>=', '<=']):
                try:
                    value = float(value)
                    for op, threshold in constraints.items():
                        if op == '>' and not value > threshold:
                            validation_results['errors'].append(f"{field} must be greater than {threshold}")
                        elif op == '<' and not value < threshold:
                            validation_results['errors'].append(f"{field} must be less than {threshold}")
                        elif op == '>=' and not value >= threshold:
                            validation_results['errors'].append(f"{field} must be greater than or equal to {threshold}")
                        elif op == '<=' and not value <= threshold:
                            validation_results['errors'].append(f"{field} must be less than or equal to {threshold}")
                except ValueError:
                    validation_results['errors'].append(f"{field} must be a number")
            
            # Handle required fields
            if constraints.get('required', False) and not value:
                validation_results['errors'].append(f"{field} is required but empty")

    validation_results['passed'] = len(validation_results['errors']) == 0
    return validation_results

def process_job(job_id, file_path, config):
    try:
        jobs[job_id]['step'] = 'Initializing Textractor'
        textractor_client = None
        if not DRY_RUN:
            textractor_client = initialize_textractor()
            if not textractor_client:
                raise Exception("Failed to initialize Textractor client")

        jobs[job_id]['step'] = 'Extracting Document Information'
        extracted_data = extract_document_info(file_path, textractor_client,dry_run=DRY_RUN)
        jobs[job_id]['outcomes']['extraction'] = "Document processed successfully"
        
        # Validate extracted data
        jobs[job_id]['step'] = 'Validating Data'
        validation_results = validate_extracted_data(extracted_data, config.get('validation', {}))
        jobs[job_id]['outcomes']['validation'] = validation_results
        
        if not validation_results['passed']:
            jobs[job_id]['step'] = 'Validation Failed'
            return
        
        # Write to Google Sheets (placeholder - implement your Google Sheets logic)
        jobs[job_id]['step'] = 'Writing to Google Sheets'
        google_sheet_url = config['load']['output']
        # Add your Google Sheets writing logic here
        
        jobs[job_id]['outcomes']['extracted_data'] = extracted_data
        jobs[job_id]['step'] = 'Completed'
        
    except Exception as e:
        jobs[job_id]['step'] = 'Error'
        jobs[job_id]['outcomes']['error'] = str(e)
        print(f"Error processing job {job_id}: {e}")

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/submit-job', methods=['POST'])
def submit_job():
    if 'file' not in request.files:
        return jsonify({"error": "No file uploaded"}), 400
        
    file = request.files['file']
    config = request.form.get('config')
    
    if not file or not config:
        return jsonify({"error": "File and config are required."}), 400
    
    try:
        config = json.loads(config)
    except json.JSONDecodeError:
        return jsonify({"error": "Invalid JSON configuration"}), 400
    
    # Save the file temporarily
    file_path = f"/tmp/{uuid.uuid4()}_{file.filename}"
    file.save(file_path)
    
    job_id = str(uuid.uuid4())
    jobs[job_id] = {
        'step': 'Queued',
        'outcomes': {}
    }
    
    threading.Thread(target=process_job, args=(job_id, file_path, config)).start()
    return jsonify({"job_id": job_id}), 202

@app.route('/job-status/<job_id>', methods=['GET'])
def job_status(job_id):
    job = jobs.get(job_id)
    if not job:
        return jsonify({"error": "Job ID not found."}), 404
    return jsonify({
        "job_id": job_id,
        "step": job['step'],
        "outcomes": job['outcomes']
    })

if __name__ == "__main__":
    app.run(debug=True)
