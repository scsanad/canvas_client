# Canvas client
A python client for grading canvas submissions.

## Setup
1. `pip install canvas_client`

2. Generate an access token. Open canvas. Go to `Settings` -> `New access token` -> copy

4. Create a config file:
    - create an empty `config.json` file and save it in a folder where you want to downdload the submissions
    - insert the following text into the file
        
            {
                "access_token": "<access token here>",
                "course_id": <course id here>,
                "labs": {
                    "<Assignemnt name (e.g. L1)>": {
                        "assignment_id": <assignment id here>
                    },
                    "<Assignment name (e.g. L2)>": {
                        "assignment_id": <assignment id here>
                    },
                    ...
                }
            }
            
            
        **Note**: You can find the `course id` and `assingment id` by opening the approriate assingment in canvas: 
        ![alt text](doc/canvas_url.png)

    

## Usage
1. Download the submissions:

    `python -m canvas_client -d <assingment name>`
    
    e.g.:
    
    `python -m canvas_client -d L1`

    This command downloads the submissions and creates an `L1.xls` file with the submission comments.


2. To upload the grades and comments:
    
    `python ac.py -u <assingment_name>`
    e.g.:
    `python ac.py -u L1`

    This command uploads the content of the `L1.xls`.