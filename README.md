# PDF Text Styles Analysis Tool

the repository utilizes pdfplumber library to analysis the text styles used in PDF


## Directory Structure
├── obtainedResults │ 

        ├── result_newTESTPDF01.json │ 
        ├── result_newTESTPDF02.json │ 
        └── ... 
├── originalResults │

        ├── Original_result_TESTPDF01.json │ 
        ├── Original_result_TESTPDF02.json │ 
        └── ... 
├── TestPdfs │

        ├── 2502GNDPR00.pdf │ 
        ├── ... 
├── app.py 

├── testapp.py

└── README.md



## Functionality

* `app.py` - Contains the code for analyzing the PDF files and obtaining the analysis data in JSON format, usually naming the files as `result_new<FileName>.json`.
* `testapp.py` - Contains Python code for testing the output obtained from `app.py`. All testing code will be updated here.
* `TestPdfs` - Contains random PDFs that were used for initial testing.
* `originalResults` - Contains the JSON data about each of the PDFs, including the list of actual styles used in them.
* `obtainedResults` - Contains the results obtained after running `app.py`.

## Installation

1. Ensure you have Python installed (version 3.6 or higher).
2. Clone the repository:
    ```sh
    git clone <repository-url>
    cd <repository-directory>
    ```
3. Run the following command to install all the required packages:
    ```sh
    pip install -r requirements.txt
    ```

### Installation Using Virtual Environment

In case there are conflicts with package versions, try with the virtual environment setup:

1. Install the virtual environment package:
    ```sh
    pip install virtualenv
    ```
2. Create a virtual environment:
    ```sh
    python -m venv <Virtual env name>
    ```
3. Activate the virtual environment:

    - On Windows:
        ```sh
        <Virtual env name>\Scripts\activate
        ```

    - On macOS and Linux:
        ```sh
        source <Virtual env name>/bin/activate
        ```
4. Install the required packages:
    ```sh
    pip install -r requirements.txt
    ```

## Usage

* For running on the PDFs already provided in the repository as examples, just run the following command in the project directory:
    ```sh
    python app.py
    ```
* For running the test on the provided example PDFs, run the following command in the project directory:
    ```sh 
    python testapp.py
    ```

### Using on Custom PDFs

* For running the application on custom PDFs, save the PDF with the name "TESTPDF<NO OF PDF>" in the current directory and run the command:
    ```sh
    python app.py
    ```
* For running the test scripts on the current PDF:
   1. Create a .json file naming "Original_result_TESTPDF<NO OF PDF>" inside the originalResults folder.
   2. Inside the JSON file, create a JSON object as:
        ```json
        {
            "usedStyles": [
                <Names of all styles used in the current PDF>
            ]
        }
        ```
   3. Put the result obtained after running the PDF using [app.py](http://_vscodecontentref_/4) under the obtainedResults folder.
   4. Run the following command in the current directory:
        ```sh
        python testapp.py
        ```

## Key Results of the Analysis

* Currently, tests for verifying the frequency of styles have not been added. It requires a basic clarification of the factor of how we are categorizing the usage of styles in a PDF, whether based on the number of characters on which it has been applied, or on the number of words it has been used, or in the sections it has been used.

The current library uses the count of style in each character. A criteria needs to be defined and the code henceforth will be modified. For example, if the criteria is considered as the sections in which a particular style has been used, the current code may not work. There may be a case where there is a section that has a large character count utilizing only a single unique style, and on the other hand, there are many sections that have fewer character counts but are using a different style. Here, if the current library is directly used, it will affect the frequency count drastically and may not give the actual popular style.

* Sometimes extra styles are being recognized by the library, but even after using character-wise count, the frequency of those styles is minimal, so they may not affect the functionality significantly.