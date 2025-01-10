## How to run

1. Create a virtual environment

    `python -m venv env`

2. Activate
    
    Windows: `.\env\Scripts\activate`

    macOS/Linux: `source env/bin/activate`

3. Install required packages

    `pip install -r requirements.txt`

4. Create a `.env` file with your mongodb uri in it:

    `MONGODB_URI=<INSERT_MONGO_URI_HERE>`

5. Create the dataset

    `python generateData.py`

6. Run the server    

    `fastapi dev main.py`


### Initialize for the DF approach:
`localhost:8000/initialize`

## Example requests:

### Un-indexed database:
`localhost:8000/top/2000?method=db`    

### Indexed database:
`localhost:8000/top/2000?method=index`

### Pandas dataframe:
`localhost:8000/top/2000?method=df`