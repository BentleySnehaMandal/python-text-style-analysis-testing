# PDF Text Styles Analysis Tool

The repository utilizes pdfplumber library to analysis the text styles used in Drawing Sheets in pdfplumber. The code performs two major functionalities being font and size analysis and also extracting additional information like information about the dimension of pages , words per pages ,images per pages and  most popular words

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

<!-- ## Headers

# This is a Heading h1
## This is a Heading h2
###### This is a Heading h6 -->
<!-- 
## Emphasis

*This text will be italic*  
_This will also be italic_

**This text will be bold**  
__This will also be bold__

_You **can** combine them_

## Lists

### Unordered

* Item 1
* Item 2
* Item 2a
* Item 2b
    * Item 3a
    * Item 3b

### Ordered

1. Item 1
2. Item 2
3. Item 3
    1. Item 3a
    2. Item 3b

## Images

![This is an alt text.](/image/sample.webp "This is a sample image.")

## Links

You may be using [Markdown Live Preview](https://markdownlivepreview.com/). -->

## Code Organisation

├──preccode  │ 

        ├── app.py │ 
        ├── testapp.py │ 
        └── ... 
├── UTILS │

        ├── findscale.py │ 
        ├── alingmentcheck.py │ 
        └── ... 
├── proximityskewapp.py

├── multiplepdf.py

├── singlepdf.py

├──modifiedmoreinfo.py

├──jsonreportdata.py

├──JSONTOUI.py

└── README.md


> 1. **UTILS:**  folders contains baisc utility functins to test and implement fragments of code
> 2. **prevcode:** folders contian previous iteration and implemtation of the functionality that has been improvised.
<!-- >> Markdown is often used to format readme files, for writing messages in online discussion forums, and to create rich text using a plain text editor. -->

## Tables

| File/Folder      | Purpose                                                                 |
|------------------|-------------------------------------------------------------------------|
| `proximityskewapp.py`         | Extracts the info about styles used in pdf and also upon selection of a style draws a bounding box for the places it is present |
| `multiplepdf.py`     | Analyses font and size distribution of text for multiple pdfs at a time                 |
| `singlepdf.py`      | Analyses font and size distribution of text for a single  pdf at a time |
| `modifiedmoreinfo.py` | Analyses addition pdf data like  word count,image count and dimensions                       |
| `jsonreportdata.py` | Uses json report to provide font analysis for the drawing sheets                               |
| `JSONTOUI.py` | Uses json report to provide additional data analysis for the drawing sheets                            |

## Application Walkthrough

The code has the fallowing functionalities
1. Generate bounding box at page locations to visualise the actual page styles
2. Analyis of fonts and sizes for text
3. Analysis of other information like the page dimentions , words per page, images per page, most common vacab used in pdfs etc.

### Visualization of styles using bounding boxes on page images walkthrough

1. Navigate to directory with the code.

```
cd <repository-directory>
```
2. Run the proximityskewapp.py using the fallowing command.

 ```
python proximityskewapp.py
```

3. After the above step a UI window will popup. Click the select file option and then a chose the file that is needed to be analyzed for style .
<!-- C:\Users\Sneha.Mandal\python-test-folder\images\proximity04POINT.png -->
![Walkthrough Image.](/images/proximity04POINT.png "walkthroughimage001.") 

4. It will take a little while for the program to run and after that the styles with there charecter frequency will be visible at the bottom part of the UI. When the drop down is selected to chose a style ,it will show the detailed description of the style as well a produce screen shots of the location of usage of the those styles inside the Drawing Sheet.
<!-- C:\Users\Sneha.Mandal\python-test-folder\images\proximity02.png -->
![Walkthrough Image.](/images/proximity02.png "walkthroughimage001.")

<!-- C:\Users\Sneha.Mandal\python-test-folder\images\jsonfileinfo.png -->
5. The json output for the data is automatically saved in the local device
![Walkthrough Image.](/images/jsonfileinfo.png "walkthroughimage001.")

### Analysis of fonts and text sizes for single pdf  walkthrough
1. navigate to directory with the code.

```
cd <repository-directory>
```
2. Run the single.py using the fallowing command.

 ```
python single.py
```

3. After the above step a UI window will popup. Click the `Open PDF` option and then a chose the file that is needed to be analysed for fonts and text sizes.

![Walkthrough Image.](/images/single01.png "walkthroughimage001.") 

4. Upon selection of the desired file it the program will take some time to run and then various data tables and graph for obtained after the font analysis of the pdf will appear. Swithing the tabs will enable the style wise and charecterwise distribution of the fonts will be visible in bar graph and and piechart format.

![Walkthrough Image.](/images/single02.png "walkthroughimage001.") 

5. The dropdown option at the lower portion of the UI provides option to view the distribution of the font sizes within the particular font selected. The data is available in pie chart, bar-graph and tabular form.
<!-- C:\Users\Sneha.Mandal\python-test-folder\images\single03.png -->
![Walkthrough Image.](/images/single03.png "walkthroughimage001.") 

6. The json output for the data is automatically saved in the local device.
![Walkthrough Image.](/images/single04.png "walkthroughimage001.")

### Analysis of fonts and text sizes for multiple pdfs walkthrough
1. Navigate to directory with the code.

```
cd <repository-directory>
```
2. Run the single.py using the fallowing command.

 ```
python multiple.py
```
3. After the above step a UI window will popup. Click the `Select Folder` option and then a chose the folder that contains all the files that are needed to be analysed for fonts and text sizes.
<!-- C:\Users\Sneha.Mandal\python-test-folder\images\multiple00.png -->
![Walkthrough Image.](/images/multiple00.png "walkthroughimage001.")

4. Upon selection of the desired folder the program will take some time to run and then various data tables and graph for obtained after the font analysis of the pdfs will appear.This shows the cumulative of all the fonts present across all the pdfs. Swithing the tabs will enable the style wise and charecterwise destribution of the fonts will be visible in bar graph and and piechart format.
![Walkthrough Image.](/images/single02.png "walkthroughimage001.") 

5. The dropdown option at the lower portion of the UI provides option to view the distribution of the font sizes within the particular font selected.The dropdown provides all the fonts used across all the drawing/sheets pdfs present in the provided files. The data is available in pie chart, bargraph and tabular form.
![Walkthrough Image.](/images/single03.png "walkthroughimage001.") 

6. The json output for the data is automatically saved in the local device.
![Walkthrough Image.](/images/single04.png "walkthroughimage001.")

### Analysis of additonal information for multiple pdfs walkthrough.

1. Navigate to directory with the code.

```
cd <repository-directory>
```
2. Run the single.py using the fallowing command.

 ```
python modifiedmoreinfo.py
```
3. After the above step a UI window will popup. Click the `Select Folder` option and then a chose the folder that contains all the files that are needed to be analysed for fonts and text sizes.
![Walkthrough Image.](/images/modified00.png "walkthroughimage001.")

4. Once the desired folder is selected then the UI application will load for some time. After the loading completes, upon clicking the `Cumulative Analysis` button , a separate UI window will pop up showing cumulative the analysis for all the pdfs and extracting information of dimensions, page counts,words per page, images per page,most popular words used across the pdfs.
![Walkthrough Image.](/images/modified01.png "walkthroughimage001.")

5. In the bottom portion of the UI there is a separate dropdown provided for analysis of individual pdfs. Dropdown options includes the name of the pdfs which are present in the previousy provided folder for cumulative analysis. Upon selection of any of the options  of the dropdown  and then selecting the `Analyze PDF`, a separate UI window will open and show the analysis for the  that particlular pdf.
![Walkthrough Image.](/images/modified02.png "walkthroughimage001.")

6. The json output for the data is automatically saved in the local device.
![Walkthrough Image.](/images/modified03.png "walkthroughimage001.")


### Using json data to generate font and additional info analysis walkthrough
> Running code for multiple pdf files anf folders can be timeconsuming everytime there is a requirement to analyse the data. Instead once the json report is generated once it can be utilized to perform the visualisation and analysis of data in less time. In that case , the code to perform analysis form the Json data comes in handy

#### Using Json data for font analysis.

1. Navigate to directory with the code.

```
cd <repository-directory>
```
2. Run the single.py using the fallowing command.

 ```
python jsonreportdata.py
```
3. After the above step a UI window will popup. Click the `Load JSON` option and then a chose the json file that contains data for all the files that are needed to be analysed for fonts and text sizes. These json files are automatically generated and saved in the local device while running `multiplepdf.py` ,`singlepdf.py` and `modifiedmoreinfo.py`.

<!-- C:\Users\Sneha.Mandal\python-test-folder\images\jsonfont00.png -->
![Walkthrough Image.](/images/jsonfont00.png "walkthroughimage001.")


4. Upon selection of the desired json file it the program will take some time to run and then various data tables and graph for obtained after the font analysis  will appear. Swithing the tabs will enable the style wise and charecter-wise distribution of the fonts will be visible in bar graph and and piechart format.
![Walkthrough Image.](/images/jsonfont01.png "walkthroughimage001.")

5. The dropdown option at the lower portion of the UI provides option to view the distribution of the font sizes within the particular font selected. The data is available in pie chart, bargraph and tabular form.
![Walkthrough Image.](/images/jsonfont02.png "walkthroughimage001.")

6. A pdf file naming `Font_Analysis_Report0001` will automatically generate and download in the local device will contain the report of data present in the UI .
![Walkthrough Image.](/images/jsonfont03.png "walkthroughimage001.")

#### Using Json data for additional data analysis

1. Navigate to directory with the code.

```
cd <repository-directory>
```
2. In the `JSONTOUI.py` file on the code line `25` change the json file name with the path of the json file that contains the required data for analysis

```
  try:
    with open("Replace with your file name", "r") as json_file:
            return json.load(json_file)
```

3. Run the single.py using the fallowing command.

 ```
python JSONTOUI.py
```
4. Once the desired json file is selected then the UI application will load for some time. After the loading completes, upon clicking the `Cumulative Analysis` button , a seperate UI window will pop up showing cumulative the analysis for all the pdfs and extracting information of dimensions, page counts,words per page, images per page,most pupular words used across the pdfs.
![Walkthrough Image.](/images/jsonmodified00.png "walkthroughimage001.")
5. ON scolling down on clicking the  `Download report` button , a report in pdf format will be downloaded via the name `JSON_Cumulative_PDF_report` .
![Walkthrough Image.](/images/jsonmodified01.png "walkthroughimage001.")

6. In the bottom portion of the UI there is a separate dropdown provided for analysis of indidividual pdfs. Dropdown options includes the name of the pdfs which are present in the previousy provided folder for cumulative analysis. Upon selection of any of the options  of the dropdown  and then selecting the `Analyze PDF`, a separate UI window will open and show the analysis for the  that particlular pdf.
![Walkthrough Image.](/images/jsonmodified02.png "walkthroughimage001.")



## Analysis Result  Examples

<!-- You may be using [Markdown Live Preview](https://markdownlivepreview.com/). -->
1. A sample analysis has been performed on 100 pdfs obtaine form [Texas Transpotation department online website](https://www.txdot.gov/business/plans-online-bid-lettings.html). The sample dataset can be viewed [here](https://bentley-my.sharepoint.com/:f:/p/sneha_mandal/ErouezgkOO1Eo9r-6kt7vH0BLDcixeE-nb5v4dQJ-N5gmw?e=CBzJKj).
2. The sample report generated  via code is different formt the final r eport as it contains some alingment issues. The raw report generated from the code can be viewed [here](https://bentley-my.sharepoint.com/:f:/p/sneha_mandal/EgKQbBySVGlJr4hAjYfTVjMBbZvED_5YA-eRYDrlvNYc-A?e=90XYAO).
3. The modifie the pdfs can be found [here](https://bentley-my.sharepoint.com/:f:/p/sneha_mandal/Egp8bYBhp3JNn4U0S5n2FSYBb1pcZbi3CY-ICYcg7ApKVQ?e=gNFrTG)



<!-- ## Inline code
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
└── README.md -->