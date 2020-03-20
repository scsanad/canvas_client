# AC_grader
A python client for grading canvas submissions.

## Setup
1. Create a conda environment with the dependencies (conda is required): 

    `conda env create -f environment.yml`
2. Activate the environment:
    
    Linux: `source activate canvas_api`
    
    Windows: `activate canvas_api`
3. Generate an access token. Open canvas2.cs.ubbcluj.ro. Go to `Settings` -> `New access token` -> copy
4. Create a `config.json` file:
   1. For grading AC submissions:
    ```
   {
        "access_token": "<access token>",
        "course_id": <course id here>,
        "labs": {
            "W1": {
                "nr_files": <nr files>,
                "files_to_test": <list of file names. e.g: ["L1a", "L1b", "L1c"]>,
                "lib": <list of libraries. e.g: ["io", "mio"]>,
                "assignment_id": <assignment id>
            },
            "L2": {
                ...
            }
        }
    }
    ```
   1. To other courses (only to download submissions and upload grades:
   ```
   {
        "access_token": "<access token here>",
        "course_id": <course id here>,
        "labs": {
            "W1": {
                "assignment_id": <assignment id here>
            },
            "L2": {
                "assignment_id": <assignment id here>
            }
        }
    }
    ```
## Usage
1. Download the submissions:

    `python ac.py -d L1`

    This command creates an `L1_grades.json` file with the comments, grades, etc.

2. Test the submission with actest:

    `python ac.py -t L1`

    This command executes the actest on the submissions, and adds the necessary comments and grades to the `L1_grades.json`.

3. To upload the grades and comments:
    
    `python ac.py -u L1`

    This command uploads the content of the `L1_grades.json`.