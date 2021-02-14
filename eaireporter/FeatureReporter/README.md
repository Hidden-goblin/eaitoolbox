# Feature reporter

## Installation 


```
pip install eaiscenarioreporter
```

## Usage

### From a python shell

```python
from featurereporter import ExportUtilities

my_export = ExportUtilities()

my_export.feature_repository = "path/to/the/feature/files/folder"

my_export.create_application_documentation()

# Create the demo.docx document in the current folder.
```

### From the command line

#### GUI (experimental)

```commandline
python3 -m featurereporter
```

#### CLI 

```
# Display help
> python3 -m featurereporter -h

usage: featurereporter.py [-h] [--tag TAG] [--title TITLE] [--repository REPOSITORY] [--output OUTPUT] [--execution EXECUTION] [--license]

optional arguments:
  -h, --help            show this help message and exit
  --tag TAG             Invariant pointing to a user story
  --title TITLE         The document's title
  --repository REPOSITORY
                        The folder where the feature files are
  --output OUTPUT
  --execution EXECUTION
                        Behave plain test output in order to also print the last execution result
  --license             Display the license.

```
 
```commandline
python3 -m featurereporter --repository path/to/the/feature/files/folder
```