# -*- coding: utf-8 -*-

"""Main module."""

import datetime

def dayiwasborn(name, year, month, day):
    """
    :param name: Your name.
    :type name: str.
    :param year: The year you were born.
    :type year: int.
    :param month: The month you were born 1 <= month <= 12.
    :type month: int.
    :param day: The day you were born 1 <= day <= 31.
    :type day: int.
    :returns: str -- a concatenation of your name and the weekday.

    Find out the day of the week when you were born! 
    
    Just supply the year, month, and day of your birthday, and we'll do the rest!
    Fully customizable to suit your needs. It tells you the day, 
    in a personalized manner. For example: 
    
    >>> dayiwasborn('John', 2000, 1, 1)
     'Hey, John, you were born on a Saturday'
    
    You can also decide whether we greet with your first name, last name, or even both! 
    
    You can optionally delete the packae if you don't like it. 
    
    Your satisfaction is 100% guaranteed, or your bytes back. 
    Each and every one of them! 
    
    """
    dob = datetime.datetime(year, month, day)
    weekday = datetime.datetime.strftime(dob, '%A')
    return 'Hey, ' + name + ', you were born on a ' + weekday
