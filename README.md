## TODO
### Utils
Create classes for all LabView data files

Create custom functions

## Setup Instructions for virtual environments (not mandatory)
To do only if you don't have the required libraries and don't want to add them to you path.

See `requirements.txt` to see needed libraries for the project

1. Create a virtual environment in head directory of this project:
   ```bash
   python -m venv venv
   ```

2. Activate the virtual environment:
   - **Windows cmd**: `venv\Scripts\activate`
   - **Windows git bash (or equivalent)**: `source venv/Scripts/activate`
   - **macOS/Linux**: `source venv/bin/activate`

3. Install the dependencies:
   ```bash
   pip install -r requirements.txt
   ```