# Lominova - Prototype Service

This repository contains a prototype service that allows users to upload files, configure processing jobs via a web interface, and monitor their progress in real-time.

## Features
- Beautiful web interface for seamless interaction.
- Upload files and define configurations in JSON format.
- Monitor job progress and outcomes directly from the interface.
- Async REST API for job submission and status tracking.

---

## Prerequisites
- Python 3.6 or later installed on your machine.
- Basic understanding of Python virtual environments and web development.

---

## Getting Started

### 1. Clone the Repository
Clone this repository to your local machine:
```bash
git clone https://github.com/azarian/lominova
cd lominova
```

---

### 2. Create a Virtual Environment
Set up a Python virtual environment to manage dependencies:
```bash
python3 -m venv env
```

Activate the virtual environment:
- On macOS/Linux:
  ```bash
  source env/bin/activate
  ```
- On Windows:
  ```bash
  env\Scripts\activate
  ```

---

### 3. Install Dependencies
Install the required Python packages:
```bash
pip install -r requirements.txt
```

---

### 4. Start the Service
Run the Flask application:
```bash
python3 main.py
```

By default, the service will be available at `http://127.0.0.1:5000/`.

---

### 5. Use the Web Interface
1. Open your browser and navigate to `http://127.0.0.1:5000/`.
2. On the **Lominova** interface:
   - Upload a file using the "Select File" field.
   - Define the job configuration in JSON format in the text box.
   - Click the "Run Job" button to submit the job.
3. Monitor the job's progress and outcomes in the "Job Output" section.

---

### Example Configuration JSON
Here is an example of what you can enter in the configuration field:
```json
{
  "validation": {
    "field_name": {
      ">": 0
    }
  },
  "load": {
    "output": "https://docs.google.com/spreadsheets/d/example"
  }
}
```

---

### 6. Stop the Service
To stop the service, press `Ctrl+C` in the terminal where it is running.

---

## Notes
- The service currently simulates the processing steps (e.g., AWS API calls, validations, Google Sheets updates).
- Ensure valid JSON is provided in the configuration field on the web interface.
- Use a modern web browser for the best experience.

---

## License
This project is licensed under the MIT License.

---

Enjoy using **Lominova** to simplify your workflow!
