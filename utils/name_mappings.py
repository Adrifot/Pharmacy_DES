def get_name_mappings():
    """Return a dictionary that maps the performance measure
    variable names in the simulation model to a user-friendly version
    with units of measurement.
    
    Returns
    ----------
    dict{str:{"name":str, "units":str}}
    """
    name_mappings = {
        "mean_queue_waiting_time": {
            "name": "Queue Waiting Time",
            "units": "minutes"
        },
        
        "counter_util": {
            "name": "Pharmacist Utilization",
            "units": "%"
        },
        
        "reneging_rate": {
            "name": "Reneging Rate",
            "units": "%"
        }
    }
    
    return name_mappings
    
    