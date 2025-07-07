from datetime import datetime

def convert_to_datetime(date_str: str, date_format: str="%Y-%m-%d") -> datetime:
    """Convert date string to datetime object"""
    try:
        date_obj = datetime.strptime(date_str, date_format)
        return date_obj
    except ValueError as e:
        return False
