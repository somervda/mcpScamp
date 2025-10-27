import time
import sqlite3
import math
import json
import os
import sys
import pytz

from datetime import datetime,timezone
from timezonefinder import TimezoneFinder
from mcp.server.fastmcp import FastMCP
from config_reader import ConfigReader



config=ConfigReader("config.json")
mcp = FastMCP("MCP Scamp",port=8100,host="0.0.0.0")



def distance_between_points(lat1, lon1, lat2, lon2):
    """
    Calculate the distance between two points on Earth using the Haversine formula.
    
    Inputs are in decimal degrees. Output is in kilometers.
    """
    # Earth radius in kilometers
    earth_radius = 6371

    # Convert degrees to radians
    lat1 = math.radians(lat1)
    lon1 = math.radians(lon1)
    lat2 = math.radians(lat2)
    lon2 = math.radians(lon2)

    # Differences in coordinates
    diff_lat = lat2 - lat1
    diff_lon = lon2 - lon1

    # Haversine formula
    a = math.sin(diff_lat / 2) ** 2 + math.cos(lat1) * math.cos(lat2) * math.sin(diff_lon / 2) ** 2
    c = 2 * math.atan2(math.sqrt(a), math.sqrt(1 - a))

    # Distance in miles
    distance = earth_radius * c * 0.62
    return distance

def lat_lon_range(latitude, longitude, distance_miles):
    """
    Calculates the latitude and longitude range based on a given point and distance.

    Args:
        latitude (float): Latitude of the center point in degrees.
        longitude (float): Longitude of the center point in degrees.
        distance_miles (float): Distance in miles to calculate the range.

    Returns:
        tuple: A tuple containing the minimum and maximum latitude and longitude
               (min_lat, max_lat, min_lon, max_lon).
    """
    earth_radius_miles = 3959  # Earth radius in miles

    # Convert latitude and longitude to radians
    lat_rad = math.radians(latitude)
    lon_rad = math.radians(longitude)

    # Angular distance in radians
    angular_distance = distance_miles / earth_radius_miles

    # Calculate minimum and maximum latitude
    min_lat = math.degrees(lat_rad - angular_distance)
    max_lat = math.degrees(lat_rad + angular_distance)

    # Calculate the change in longitude
    delta_lon = math.degrees(math.asin(math.sin(angular_distance) / math.cos(lat_rad)))

    # Calculate minimum and maximum longitude
    min_lon = longitude - delta_lon
    max_lon = longitude + delta_lon

    return (min_lat, max_lat, min_lon, max_lon)

def get_db_connection():
    scamp_db_file = config.scamp_db
    print("scamp_db_file",scamp_db_file)
    conn = sqlite3.connect(scamp_db_file)
    conn.row_factory = sqlite3.Row  # Enables dict-like access to rows
    return conn

# Tool: return location as latitude and longitude
@mcp.tool()
def get_location() -> str:
    """Return the current location as latitude and longitude. Timestamp is included 
       for information on when the location was last determined."""
    try:
        gps_file_name = config.gps_file
        with open(gps_file_name, "r") as f:
            gps_data = json.load(f)
        
        # Extract values
        latitude = round(gps_data.get("latitude"),5)
        longitude = round(gps_data.get("longitude"),5)
        altitude = gps_data.get("altitude")
        timestamp = gps_data.get("timestamp")

        return json.dumps({
            "latitude": latitude,
            "longitude": longitude,
            "altitude": altitude,
            "timestamp": timestamp
        })
    
    except FileNotFoundError:
        print(f"Error: {gps_file_name} not found.")
    except json.JSONDecodeError:
        print("Error: Invalid JSON format.")

@mcp.tool()
def get_state_parks_details_by_name(name: str ) -> str:
    """
    Gets a detailed information about a specific pennsylvania state park by name
    Args:
        name: The name of the park   
    """
    conn = get_db_connection()
    cursor = conn.cursor()
    select =   "SELECT * FROM pa_state_park where name = '" + name + "'"
    print(select)
    cursor.execute(select)
    rows = cursor.fetchall()
    conn.close()
    park = [dict(row) for row in rows]  # Convert to list of dictionaries items
    return json.dumps(park)

@mcp.tool()
def get_state_parks_by_distance(miles: int) -> str:
    """
    Gets a list of pennsylvania state parks by distance in miles from my current location. 
    Park details includes information about if the park has RV camping.
    Args:
        miles: An integer representing how many miles distance 
    """
    print(get_state_parks_by_distance,miles)
    location=json.loads(get_location())
    print("location",location)
    lat=float(location.get("latitude",0))
    long=float(location.get("longitude",0))
    print("lat",lat,"long",long)
    min_lat, max_lat, min_lon, max_lon = lat_lon_range(lat,long,miles)
    conn = get_db_connection()
    cursor = conn.cursor()
    select =   "SELECT name,longitude,latitude,hasRVCamping FROM pa_state_park where latitude>={:.4f} and latitude <={:.4f} and longitude>={:.4f} and longitude<={:.4f}".format(min_lat, max_lat, min_lon, max_lon)
    print(select)
    cursor.execute(select)
    rows = cursor.fetchall()
    conn.close()
    parks = [dict(row) for row in rows]  # Convert to list of dictionaries items
    parkAndDistance=[]
    for park in parks:
        park['distance']=round(distance_between_points(lat,long,park.get("latitude"),park.get("longitude")),2)
        del park['latitude']
        del park['longitude']
        parkAndDistance.append(park)
    return json.dumps(parkAndDistance)

@mcp.tool()
def get_rv_parks_by_distance(miles: int ) -> str:
    """
    Gets a list of all the RV parks in Pennsylvania,New York,
     Delaware and Ohio by distance in miles from my current location
    Args:
        miles: An integer representing how many miles distance 
    """

    print("get_rv_parks_by_distance:",miles)
    location=json.loads(get_location())
    lat=float(location.get("latitude",0))
    long=float(location.get("longitude",0))
    min_lat, max_lat, min_lon, max_lon = lat_lon_range(lat,long,miles)
    conn = get_db_connection()
    cursor = conn.cursor()
    select =   "SELECT name,longitude,latitude,city,st FROM rv_park where latitude>={:.4f} and latitude <={:.4f} and longitude>={:.4f} and longitude<={:.4f}".format(min_lat, max_lat, min_lon, max_lon)
    print(select)
    cursor.execute(select)
    rows = cursor.fetchall()
    conn.close()
    parks = [dict(row) for row in rows]  # Convert to list of dictionaries items
    parkAndDistance=[]
    for park in parks:
        park['distance']=distance_between_points(lat,long,park.get("latitude"),park.get("longitude"))
        parkAndDistance.append(park)
    return json.dumps(parkAndDistance)

@mcp.tool()
def get_rv_parks_details_by_name(name: str ) -> str:
    """
    Gets a detailed information about a specific RV park by name
    Args:
        name: The name of the park   
    """
    conn = get_db_connection()
    cursor = conn.cursor()
    select =   "SELECT * FROM rv_park where name = '" + name + "'"
    print(select)
    cursor.execute(select)
    rows = cursor.fetchall()
    conn.close()
    park = [dict(row) for row in rows]  # Convert to list of dictionaries items
    return json.dumps(park)

# Tool: return current UTC time
@mcp.tool()
def get_UTC_time() -> str:
    """Return the current UTC time as an ISO 8601 string."""
    print("get_UTC_time")
    return datetime.now(timezone.utc).replace(tzinfo=pytz.utc).isoformat()

# Tool: return local time by latitude & longitude
@mcp.tool()
def get_local_time() -> str:
    """
    Return the local time based on the current location timezone.
    Time is returned as an ISO 8601 string.
    """
    print("get_local_time")
    location=json.loads(get_location())
    latitude=float(location.get("latitude",0))
    longitude=float(location.get("longitude",0))
    tf = TimezoneFinder()
    tz_name = tf.timezone_at(lng=longitude, lat=latitude)

    if not tz_name:
        raise ValueError("Could not determine timezone for given coordinates")

    tz = pytz.timezone(tz_name)
    utc_now = datetime.now(timezone.utc).replace(tzinfo=pytz.utc)
    local_time = utc_now.astimezone(tz)
    return local_time.isoformat()

if __name__ == '__main__':
    # print(get_UTC_time())
    mcp.run(transport="streamable-http")
