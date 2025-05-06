# Jenkins helper

Use this as command line program to:
- check if your build is done and how many tests are failed
- save console output to file
- get job host

## Installation

You need to have python (3.11 or greater). 

As a recommendation create virtual environment for you dependencies and activate it:
```bash
python -m venv venv
# below is script for powershell. 
.\venv\Scripts\activate.ps1

# for bash
source venv/bin/activate
```

Install dependencies:
```bash
pip install -r requirements.txt
```
To test it check help:
```bash
python main.py --help
```

## Authentication
To use this tool you need to generate API token. Go to Jenkins and i right top corner you will see your user. Click on it and on Configure. In section **API Token** add new token.
Create new file called `.env` and add your token and user name as
```
JENKINS_USER=user
JENKINS_TOKEN=supersecrettoken1234
```

## Checking if last build is done 

To check if job is finished use `build_done` action and parameter `-b` (`--branch`). Name of branch is not exact as in bitbucket because Jenkins has it's own pipelines. 
Depending what you want to see:
- if you want to check multibranch f.ex: feature/important-thing you need to get full name of job: folder_name/feature%2Fimportant-thing because this job is inside `folder_name` folder
```bash
python main.py build_done -b folder_name/feature%2Fimportant-thing
```
- if you use job that is not in folder use it's own name f.ex: my-branch
```bash
python main.py build_done -b my-branch
```
where `-b` is branch name and `build_done` is functionality to check if build is done.

Bellow is simple result of done job:
```
INFO - Hello User
INFO - Found job folder_name/feature%2Fimportant-thing:33
Done: UNSTABLE. https://jenkins.com/job/folder_name/job/feature%252important-thing/33/
INFO - Tests: failed: 1/3144, skipped: 0
```

If build will be not done then it will be checked every 60 seconds as default. If you want to change it use `--sleep` with number of seconds.