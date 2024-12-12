from typing import List
import numpy as np
import json
from datetime import datetime
from skyfield.api import load, wgs84
from skyfield.sgp4lib import EarthSatellite


def process_tle_with_skyfield(sat_data: List[EarthSatellite]):
    """
    Process TLE data using Skyfield

    :param tle_data: List of TLE data dictionaries
    :return: List of processed satellite information
    """
    # Load time scale
    ts = load.timescale()

    # Current time
    t = ts.now()

    processed_satellites = []
    print("processing")
    for sat in sat_data:
        try:

            # Compute satellite's geocentric position
            geocentric = sat.at(t)

            # Get latitude, longitude, and altitude
            subpoint = geocentric.subpoint()

            # Compute additional information
            satellite_info = {
                "name": sat["OBJECT_NAME"],
                "norad_id": sat["NORAD_CAT_ID"],
                "epoch": sat["EPOCH"],
                "latitude": subpoint.latitude.degrees,
                "longitude": subpoint.longitude.degrees,
                "elevation_km": subpoint.elevation.kilometers,
            }

            processed_satellites.append(satellite_info)

        except Exception as e:
            print(
                f"Error processing satellite {
                  sat.get('OBJECT_NAME', 'Unknown')}: {e}"
            )

    return processed_satellites


def angular_separation(alt1: float, az1: float, alt2: float, az2: float):
    """
    Calculate angular separation between two celestial positions
    using the haversine formula, which works well for astronomical calculations
    """
    # Convert degrees to radians
    lat1, lon1 = np.radians(alt1), np.radians(az1)
    lat2, lon2 = np.radians(alt2), np.radians(az2)

    # Haversine formula
    dlat = lat2 - lat1
    dlon = lon2 - lon1
    a = np.sin(dlat / 2) ** 2 + np.cos(lat1) * np.cos(lat2) * np.sin(dlon / 2) ** 2
    angular_distance = 2 * np.arcsin(np.sqrt(a))

    return np.degrees(angular_distance)


def find_smarter_every_days_satellite(gp_data: list):
    # Create a Timescale object
    ts = load.timescale()

    # Load gp data into EarthSatellite objects
    sats = [EarthSatellite.from_omm(ts, fields) for fields in gp_data]
    print("Loaded", len(sats), "satellites")

    # Timestamps and position taken from
    # https://www.reddit.com/r/SmarterEveryDay/comments/1cwuoxc/comment/l4ysbyf/?utm_source=share&utm_medium=web3x&utm_name=web3xcss&utm_term=1&utm_content=share_button
    C3 = ts.utc(2024, 4, 8, 19, 2, 26)
    FIRST_OBJECT = ts.utc(2024, 4, 8, 19, 2, 31)
    SECOND_OBJECT = ts.utc(2024, 4, 8, 19, 2, 37)
    JACKSON = wgs84.latlon(37.42902, -89.64276)

    # Suns position at C3 obtained from US Navy
    # https://aa.usno.navy.mil/calculated/eclipse/solar?eclipse=12024&lat=37.429&lon=-89.6428&label=&height=0&submit=Get+Data
    SUN_ALT = 57.0
    SUN_AZ = 209.2

    # Alternative timestamp I found for first object
    FIRST_OBJECT_ALT = ts.ut1(2024, 4, 8, 19, 2, 27.9)

    candidates = []

    for sat in sats:
        difference = sat - JACKSON
        topocentric = difference.at(FIRST_OBJECT)
        alt, az, distance = topocentric.altaz()

        # Altitude must be greater than zero to be above horizon
        # Arbitrarily limited satellite distances so that they are less than 10,000km away
        if alt.degrees > 0 and distance.km < 10000:

            # Rank satellites based on angular seperation from sun
            sep = angular_separation(SUN_ALT, SUN_AZ, alt.degrees, az.degrees)
            candidates.append(
                {"sep": sep, "sat": sat, "alt": alt, "az": az, "distance": distance}
            )

    candidates.sort(key=lambda x: x["sep"])

    for sat in candidates[:5]:
        print(f"Satellite: {sat['sat']}")
        print(f"Degree of Seperation: {sat['sep']:.3f}°")
        print(f"Altitude: {sat['alt'].degrees:.2f} degrees")
        print(f"Azimuth: {sat['az'].degrees:.2f} degrees")
        print(f"Distance: {sat['distance'].km:.2f} km")
        print("---")


def main():
    with open("satellite_data.json") as f:
        gp_data = json.load(f)

    find_smarter_every_days_satellite(gp_data)


if __name__ == "__main__":
    main()
