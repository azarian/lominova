from flask import Flask, request, jsonify, render_template
import threading
import uuid
import time
import json

# Placeholder for AWS SDK imports (e.g., boto3 for AWS API calls)

app = Flask(__name__)
jobs = {}

def evaluate_execution_plan(config):
    """Simulates evaluating the JSON configuration and generates an execution plan."""
    print("Evaluating execution plan:")
    print("- Using AWS API: analyzeExpense")
    print("- Validating fields")
    print("- Writing to Google Sheets")

def process_job(job_id, file, config):
    jobs[job_id]['step'] = 'Prepareing Execution Plan'
    time.sleep(5)  # Simulate preparing execution plan
    jobs[job_id]['step'] = 'Execution Plan Ready'
    jobs[job_id]['outcomes']['Execution Plan'] = "[file]->[analyzeExpense]->[validate]->[write_to_google_sheets]"
    jobs[job_id]['step'] = 'Processing file'
    time.sleep(5) 
    try:
        # Simulate calling AWS API
        jobs[job_id]['outcomes']['aws_api'] = "Calling AWS API: analyzeExpense"
        print(jobs[job_id]['outcomes']['aws_api'])
        time.sleep(5) 

        # Placeholder for AWS analyzeExpense logic
        extracted_data = {"placeholder_field": 1}  # Simulated extracted data

        # Perform validation
        jobs[job_id]['step'] = 'Validating data'
        print("Performing validation")
        time.sleep(5) 
        validation_passed = True
        for field, constraints in config['validation'].items():
            if field in extracted_data:
                value = extracted_data[field]
                if constraints.get('>') is not None and value <= constraints['>']:
                    validation_passed = False
                    error_message = f"Validation failed for {field}: value must be > {constraints['>']}"
                    jobs[job_id]['outcomes']['validation'] = error_message
                    print(error_message)

        if not validation_passed:
            jobs[job_id]['step'] = 'Validation failed'
            return
        time.sleep(5) 
        # Simulate writing to Google Sheets
        jobs[job_id]['step'] = 'Writing to Google Sheets'
        google_sheet_url = config['load']['output']
        print(f"Writing to Google Sheets at {google_sheet_url}")
        jobs[job_id]['outcomes']['google_sheets'] = f"Written to Google Sheets at {google_sheet_url}"

        # Finalize job
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
    data = request.json
    file = data.get('file')
    config = data.get('config')

    if not file or not config:
        return jsonify({"error": "File and config are required."}), 400

    job_id = str(uuid.uuid4())
    jobs[job_id] = {
        'step': 'Queued',
        'outcomes': {}
    }

    threading.Thread(target=process_job, args=(job_id, file, config)).start()

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
