import requests
import json
from dotenv import load_dotenv
import os

# Space-Track.org authentication and API endpoints
BASE_URL = "https://www.space-track.org"
LOGIN_URL = f"{BASE_URL}/ajaxauth/login"
QUERY_URL = f"{BASE_URL}/basicspacedata/query"
USE_FILE = True


def authenticate_space_track(username: str, password: str) -> requests.Session:
    """
    Authenticate credentials with Space-Track.org

    :param username: Space-Track.org username
    :param password: Space-Track.org password
    :return: Authenticated Session
    """

    print("Authenticating with space-track.org.")

    assert username is not None and isinstance(
        username, str
    ), "Username is not properly defined"
    assert password is not None and isinstance(
        password, str
    ), "Password is not properly defined"

    # Create session
    session = requests.Session()

    # Login to Space-Track.org
    login_data = {"identity": username, "password": password}

    try:
        # Authenticate
        login_response = session.post(LOGIN_URL, data=login_data)
        login_response.raise_for_status()

    except requests.RequestException as e:
        print(f"Error logging in with credentials: {e}")
        return None

    print("Successfully authenticated.")
    return session


def get_space_track_data(session: requests.Session, search_parameters: dict):
    """
    Retrieve TLE data from Space-Track.org

    :param search_parameters: Dictionary of search criteria
    :return: List of TLE data dictionaries
    """

    print("Retrieving space-track.org data.")

    assert session is not None and isinstance(session, requests.Session)
    assert (
        search_parameters is not None
        and isinstance(search_parameters, dict)
        and len(search_parameters.keys()) != 0
    )

    try:
        # Build query string
        query_params = "/".join([f"{k}/{v}" for k, v in search_parameters.items()])
        full_query_url = f"{QUERY_URL}/{query_params}/format/json"
        print(f"Getting {full_query_url}.")
        # Make the request
        response = session.get(full_query_url)
        response.raise_for_status()

        data = response.json()
        print(f"Recieved data of length {len(data)}.")
        # Parse and return JSON response
        return response.json()

    except requests.RequestException as e:
        print(f"Error retrieving data: {e}")
        return None


def main():
    load_dotenv()

    # Replace with your actual Space-Track.org credentials
    username = os.getenv("SPACETRACK_USERNAME")
    password = os.getenv("SPACETRACK_PASSWORD")

    # Optional search parameters
    search_params = {
        "class": "gp_history",
        "EPOCH": "2024-04-08--2024-04-09",
        "orderBy": "norad_cat_id,EPOCH",
        "distinct": "NORAD_CAT_ID",
    }

    # Authenticate with Space Track
    session = authenticate_space_track(username, password)

    # Retrieve TLE data
    gp_data = get_space_track_data(session, search_params)

    if gp_data is None:
        print("Data requet failed. Please try again.")

    else:
        with open("satellite_data.json", "w") as f:
            json.dump(gp_data, f)
            # Same thing as this
            # f.write(json.dumps(tle_data))
