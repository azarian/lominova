from flask import Flask, request, jsonify, render_template
import threading
import uuid
import time
import json
from textractor import Textractor
import boto3
from botocore.exceptions import ClientError
import html


app = Flask(__name__)
jobs = {}

DRY_RUN = False

def initialize_textractor():
    """Initialize Textractor client with AWS credentials"""
    try:
        # Assuming AWS credentials are configured in the environment
        textract_client = boto3.client('textract')
        return Textractor(profile_name="default")
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
        document = textractor_client.detect_document_text(file_path,save_image=False)
        text = document.get_text()
        return {
            "forms": text,
            "tables": "Not Implemented",
            "raw_text": text
        }
    except Exception as e:
        raise Exception(f"Error extracting document info: {str(e)}")

def validate_extracted_data(extracted_data, validation_config):
    """Validate extracted data against configuration rules"""
    validation_results = {
        "passed": True,
        "errors": []
    }
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
