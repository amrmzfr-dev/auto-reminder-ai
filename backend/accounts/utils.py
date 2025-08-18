from .models import State

def get_customer_state_obj(customer_state_str):
    """
    Convert a Customer.state string to the corresponding State model instance.
    """
    state_mapping = {
        'Selangor': 'Central 2',
        'Kuala Lumpur': 'Central 1',
        'Putrajaya': 'Central 1',
        'Perak': 'Northern',
        'Kedah': 'Northern',
        'Perlis': 'Northern',
        'Penang': 'Northern',
        'Negeri Sembilan': 'Southern',
        'Melaka': 'Southern',
        'Johor': 'Southern',
        'Pahang': 'East Coast',
        'Terengganu': 'East Coast',
        'Kelantan': 'East Coast',
        'Sabah': "East M'sia",
        'Sarawak': "East M'sia",
    }
    state_code = state_mapping.get(customer_state_str)
    if not state_code:
        return None
    try:
        return State.objects.get(code=state_code)
    except State.DoesNotExist:
        return None
