# lominova
# Prototype Service

This repository contains a prototype service that processes files in a watch folder by simulating AWS API calls, performing validation, and writing output to a CSS file.

## Prerequisites

- Python 3.6 or later installed on your machine.
- Basic understanding of Python and virtual environments.

## Getting Started

### 1. Clone the Repository
Clone this repository to your local machine:
```bash
git clone https://github.com/azarian/lominova
cd lominova
```

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

### 3. Install Dependencies
Install the required Python packages:
```bash
pip install -r requirements.txt
```

### 4. Run the Script
Run the script to start the service:
```bash
python3 main.py
```

### 5. Add Files to the Watch Folder
Once the service is running, it will monitor the `watch_folder` directory. Add files to this folder for processing:

```bash
mv <your-file> watch_folder/
```

The service will simulate the following steps for each file:
1. Call the AWS `analyzeExpense` API.
2. Validate extracted data.
3. Write output to `output.css`.

### 6. Stop the Service
To stop the service, use `Ctrl+C` in the terminal.

## Notes

- The script includes placeholders for AWS API integration and custom validation logic. You can modify the script to include real API calls and additional processing as needed.
- Ensure the `watch_folder` directory exists before running the script. It will be automatically created if it doesn't.

## License
This project is licensed under the MIT License.
