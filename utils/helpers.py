import pandas as pd

def km_driven_cleaner(value):
    """
    Converts a string representing kilometers driven into an integer value.

    The input is expected to be a string that may end with:
    - 'L' representing 'Lakh' (1 Lakh = 100,000)
    - 'k' representing 'Thousand' (1k = 1,000)

    The function parses the numeric part of the string, converts it to a float and then multiplies it accordingly:
    - If the value ends with 'L', it multiplies the number by 1,00,000.
    - If the value ends with 'k', it multiplies the number by 1,000.

    Parameters:
        value (str): A string indicating the kilometers driven, using 'k' or 'L' notation.

    Returns:
        km_driven (int): The equivalent number of kilometers as an integer.

    Example:
        >>> km_driven_cleaner("1.5L")
        150000
        >>> km_driven_cleaner("12k")
        12000
    """
    if value.strip().endswith('L'):
        return round(float(value.replace('L',''))*100000)
    else:
        return round(float(value.replace('k',''))*1000)
    
def price_cleaner(value):
    """
    Converts a string representing a price into an integer value in Indian Rupees (INR).

    The input is expected to be a string ending with:
    - 'lakh' representing 1 Lakh = 1,00,000 INR
    - 'Crore' representing 1 Crore = 10,000,000 INR

    The function parses the numeric part of the string, converts it to a float and multiplies it by the appropriate factor:
    - If the value ends with 'lakh', it multiplies the number by 1,00,000.
    - If the value ends with 'Crore', it multiplies the number by 10,000,000.

    Parameters:
        value (str): A string indicating the price, ending with either 'lakh' or 'Crore'.

    Returns:
        price (int): The equivalent price in Indian Rupees as an integer.

    Cleans price values and converts them into integer rupees.
    
    Example:
        "5.5lakh"  -> 550000
        "1.2Crore" -> 12000000
        "550000"   -> 550000
    
    """
    if value.strip().endswith('lakh'):
        return round(float(value.replace('lakh',''))*100000)
    else:
        return round(float(value.replace('Crore',''))*10000000)

