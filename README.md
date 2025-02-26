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
* app.py-> contains the code for analyzing and the pdf files and obtain the analysis data in json format usually naming "result_new<FileName>.json
* testapp.py-> contains python code for testing the output obtained form the app.py .All testing code will be updated here .
* TestPdfs-> contains randoms pdfs that were used for initial testing
* originalResults-> contains the json data about each of the pdfs containing the list of actual styles used in them 
* obtainedResults-> contains the results obtained after running app.py


## Installation

1. Ensure you have Python installed (version 3.6 or higher).
2. Clone the repository:
    ```sh
    git clone <repository-url>
    cd <repository-directory>
    ```

3. Run the fallowing command to install all the required packages
    ```sh
    pip install -r requirements.txt
    ```

### Installation Using virtual environment
Incase there are conflicts with package versions try with the virtual environment setup 
 1.  Install the virtual environment package:
    ```sh
    pip install virtualenv
    ```
 2.  Create a virtual environment:
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

* For running on the pdfs already provided in the repository as examples just run the fallowing command in the project directory
    ```sh
    python app.py
    ```
* For running the test on the provided example pdf run the fallowing command in the project directory
    ```sh 
    python testapp.py
    ```

### Using on custom pdfs

* For running the application on custom pdf save the pdf with name "TESTPDF<NO OF PDF>" in the current directory and run the command.
    ```sh
    python app.py
    ```
* For running the test scripts on the current pdf 
   1. create a .json file naming "Original_result_TESTPDF<NO OF PDF>" inside the originalResults folder
   2. Inside the json file create a json object as
        ```json
          {
        "usedStyles": [
         <Names of all styles used in current pdf>
                    ]
           }
       ```
    3. put the result obtained after running the pdf using app.py under the obtainedResults folder
    4. Run the fallowing command in the current directory.
        ```sh
    python testapp.py
    ```

   
 
## Key results of the analysis

* currently test for the verifying the frequency of styles has not being added . It requires a basic clarification of the factor how we are categorizing the usage of styles in a PDF, whether based on no of characters on which it has been applied , or on number of words it has been used or in the sections it  has been used.

The current library uses the count of style in each characters,a criteria needs to be defined and the code hence forth will be modified .For eg if the criteria is considered as the sections in which the a particular style has been used , the current code may not work. There may be a case where there is section which is having large characters count utilizing only a single unique style , and on the other hand there are many sections which are having fewer character count but are using a different style. Here if the the current library is directly used , it will affect the frequency count drastically and may not give the actually popular style

* Some times extra styles are being recognized by the library ,but even after using characters wise count the frequency of those styles are minimum, so they may not affect the functionality significantly






