# Imports for get_clan_list
import csv
import urllib.request
import codecs

"""
rs3clans.py Module

Made by: John Victor

List of functions:

# Added v0.1
get_clan_list(clan_name)
- Returns a List of Members and their info in a Clan (csv.reader)
For row As: ['user_name', 'rank', 'clan_exp', 'kills']

# Added v0.1
get_clan_exp(clan_name)
- Returns Total Clan Exp of a Clan (Int)

# Added v0.1
get_user_clan_exp(user_name, clan_name)
- Returns User Clan Exp (Int)

# Added v0.1
get_user_rank(user_name, clan_name)
- Returns a User's Rank in a Clan (Str)

# Added v0.1
get_user_info(user_name, clan_name)
- Returns All available Clan info (List)
As: ['user_name', 'rank', 'clan_exp', 'kills']

# Added v0.1
get_player_count(clan_name)
- Returns Player count of a Clan (Int)

# Added v0.1
get_average_clan_exp(clan_name)
- Returns the average Clan Exp per member in a Clan (Int)


RS3 API: http://runescape.wikia.com/wiki/Application_programming_interface
"""

# Clan List .csv format:
#
# ['user_name', 'rank', 'clan_exp', 'kills']
#
# Everything is read as a string and the single quotes are included.
# Use values explictly
#
# Example:
# - Getting clan exp from a user that has 323,142,653 Clan Exp:
#
# int(user_info[2])  # Output(int): 323142653
# user_info[2]  # Output(string): '323142653'


def get_clan_list(clan_name):
    """
    Gets a clan_list using csv.reader and returns it.
    It does NOT return a List type.

    If you wish to use it as is, you will have to iterate over it,
    you can append the list into another format for usability.
    """
    url = 'http://services.runescape.com/m=clan-hiscores/members_lite.ws?clanName='  # noqa
    url += clan_name

    read_url = urllib.request.urlopen(url)

    # errors="replace" is for names that contains spaces
    clan_list = csv.reader(codecs.iterdecode(read_url, 'utf-8',
                                             errors="replace"))

    return clan_list


def get_clan_exp(clan_name):
    """
    Gets the Total clan exp from clan_name and returns it.
    Returned Value is an Integer and can be used as such normally.

    It gets the Total clan exp adding up from every member in the clan,
    thus it's not very fast since those values are not cached somewhere.
    """
    clan_list = get_clan_list(clan_name)
    total_exp = 0
    for row in clan_list:
        try:
            if (row[2] != ' Total XP'):
                total_exp += int(row[2])
        except IndexError:
            print("Error: Invalid Clan name '{}'".format(clan_name))
            return 0
    return total_exp


def get_user_clan_exp(user_name, clan_name):
    """
    Gets the total Clan Exp from a user in clan_name and returns it.
    Returned Value is an Integer and can be used as such normally.
    """
    clan_list = get_clan_list(clan_name)
    for row in clan_list:
        try:
            if (row[0].lower() == user_name.lower()):
                return int(row[2])
        except IndexError:
            print("Error: Invalid Clan name '{}'".format(clan_name))
            return 0
    print("Error: User '{}' not found in clan '{}'".format(user_name,
                                                           clan_name))
    return 0


def get_user_rank(user_name, clan_name):
    """
    Gets a user's rank in clan_name and returns it.
    Returned Value is a String and can be used as such normally.
    """
    clan_list = get_clan_list(clan_name)
    for row in clan_list:
        try:
            if (row[0].lower() == user_name.lower()):
                return str(row[1])
        except IndexError:
            print("Error: Invalid Clan name '{}'".format(clan_name))
            return 0
    print("Error: User '{}' not found in clan '{}'".format(user_name,
                                                           clan_name))
    return 0


def get_user_info(user_name, clan_name):
    """
    Gets a user's clan info from clan_name and returns it as a List.

    Elements from the List can be accessed as you would normally with a List.

    List is formatted as:
    ['user_name', 'rank', 'clan_exp', 'kills']
    """
    clan_list = get_clan_list(clan_name)
    clan_info = []
    for row in clan_list:
        try:
            if (row[0].lower() == user_name.lower()):
                clan_info.append(row[0])  # user_name
                clan_info.append(row[1])  # rank
                clan_info.append(row[2])  # clan_exp
                clan_info.append(row[3])  # kills
                return clan_info
        except IndexError:
            print("Error: Invalid Clan name '{}'".format(clan_name))
            return 0
    print("Error: User '{}' not found in clan '{}'".format(user_name,
                                                           clan_name))
    return 0


def get_player_count(clan_name):
    """
    Gets the Total player count from clan_name and returns it.
    Returned Value is an Integer and can be used as such normally.

    Since Jagex's RS3 API takes a while to register when someone leaves a clan,
    this count may take a while to update.
    """
    clan_list = get_clan_list(clan_name)
    number_of_players = 0
    if 'Clanmate' in clan_list:
        for row in clan_list:
                print(row)
                number_of_players += 1
    else:
        print("Error: Invalid Clan name '{}'".format(clan_name))
        return 0
    return number_of_players


def get_average_clan_exp(clan_name):
    """
    Gets the Average clan exp from clan_name per Member and returns it.
    Returned Value is an Integer and can be used as such normally.
    """
    number_of_players = get_player_count(clan_name)
    total_clan_exp = get_clan_exp(clan_name)
    mean_clan_exp = total_clan_exp / number_of_players
    return mean_clan_exp
