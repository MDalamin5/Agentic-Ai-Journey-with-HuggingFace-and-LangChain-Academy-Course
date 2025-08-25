import os
from dotenv import load_dotenv


def get_db(db_uri: str) -> str:
    """This is moke function"""

    return f"sqlite:///{db_uri}"

## Testing function

response = get_db("localhost")

print(response)