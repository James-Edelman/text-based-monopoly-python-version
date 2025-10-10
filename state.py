"""global variables, and instances of classes from other modules"""

players_playing = 0
dev_mode = False
house_total = 32
hotel_total = 12
time_played = 0
game_version = 0.96
player_turn = None
player: dict = None
current_screen = "homescreen"

globals().update({"skibidi skibidi hawk tuah": 67}) # this variable serves no purpose

# player icons can only appear in certain points here
# default space is blank but some special cases specified individually
player_display = [["          ", True] for i in range(41)]

player_display[7] = ["    ()    ", False] # False = irregular
player_display[22] = ["    / /   ", False]
player_display[36] = [ "  \\_|    ", False]
player_display[40] = [" ║ ║ ║ ║ ", False]

property_data = [{} for i in range(28)]

# colour set rent is double normal rent, mortgage/unmortgage value
# based on street value; none of these values are recorded
property_data[0]  = {"name": "Old Kent Road"        , "type": "property", "street value": 60 , "owner": None, "upgrade state": 0, "colour set": 0, "rent": 2 , "h1 rent": 10 , "h2 rent": 30 , "h3 rent": 90  , "h4 rent": 160 , "h5 rent": 250 , "house cost": 50 }
property_data[1]  = {"name": "Whitechapel"          , "type": "property", "street value": 60 , "owner": None, "upgrade state": 0, "colour set": 0, "rent": 4 , "h1 rent": 20 , "h2 rent": 60 , "h3 rent": 180 , "h4 rent": 320 , "h5 rent": 450 , "house cost": 50 }
property_data[2]  = {"name": "Kings Cross Station"  , "type": "station" , "street value": 200, "owner": None, "upgrade state": 0}
property_data[3]  = {"name": "The Angel Islington"  , "type": "property", "street value": 100, "owner": None, "upgrade state": 0, "colour set": 1, "rent": 6 , "h1 rent": 30 , "h2 rent": 90 , "h3 rent": 270 , "h4 rent": 400 , "h5 rent": 550 , "house cost": 50 }
property_data[4]  = {"name": "Euston Road"          , "type": "property", "street value": 100, "owner": None, "upgrade state": 0, "colour set": 1, "rent": 6 , "h1 rent": 30 , "h2 rent": 90 , "h3 rent": 270 , "h4 rent": 400 , "h5 rent": 550 , "house cost": 50 }
property_data[5]  = {"name": "Pentonville Road"     , "type": "property", "street value": 120, "owner": None, "upgrade state": 0, "colour set": 1, "rent": 8 , "h1 rent": 40 , "h2 rent": 100, "h3 rent": 300 , "h4 rent": 450 , "h5 rent": 600 , "house cost": 50 }
property_data[6]  = {"name": "Pall Mall"            , "type": "property", "street value": 140, "owner": None, "upgrade state": 0, "colour set": 2, "rent": 10, "h1 rent": 50 , "h2 rent": 150, "h3 rent": 450 , "h4 rent": 625 , "h5 rent": 750 , "house cost": 100}
property_data[7]  = {"name": "Electric Company"     , "type": "utility" , "street value": 150, "owner": None, "upgrade state": 0}
property_data[8]  = {"name": "Whitehall"            , "type": "property", "street value": 140, "owner": None, "upgrade state": 0, "colour set": 2, "rent": 10, "h1 rent": 50 , "h2 rent": 150, "h3 rent": 450 , "h4 rent": 625 , "h5 rent": 750 , "house cost": 100}
property_data[9]  = {"name": "Northumberland Avenue", "type": "property", "street value": 160, "owner": None, "upgrade state": 0, "colour set": 2, "rent": 12, "h1 rent": 60 , "h2 rent": 180, "h3 rent": 500 , "h4 rent": 700 , "h5 rent": 900 , "house cost": 100}
property_data[10] = {"name": "Marylebone Station"   , "type": "station" , "street value": 200, "owner": None, "upgrade state": 0}
property_data[11] = {"name": "Bow Street"           , "type": "property", "street value": 180, "owner": None, "upgrade state": 0, "colour set": 3, "rent": 14, "h1 rent": 70 , "h2 rent": 200, "h3 rent": 550 , "h4 rent": 750 , "h5 rent": 950 , "house cost": 100}
property_data[12] = {"name": "Marlborough Street"   , "type": "property", "street value": 180, "owner": None, "upgrade state": 0, "colour set": 3, "rent": 14, "h1 rent": 70 , "h2 rent": 200, "h3 rent": 550 , "h4 rent": 750 , "h5 rent": 950 , "house cost": 100}
property_data[13] = {"name": "Vine Street"          , "type": "property", "street value": 200, "owner": None, "upgrade state": 0, "colour set": 3, "rent": 16, "h1 rent": 80 , "h2 rent": 220, "h3 rent": 600 , "h4 rent": 800 , "h5 rent": 1000, "house cost": 100}
property_data[14] = {"name": "Strand"               , "type": "property", "street value": 220, "owner": None, "upgrade state": 0, "colour set": 4, "rent": 18, "h1 rent": 90 , "h2 rent": 250, "h3 rent": 700 , "h4 rent": 875 , "h5 rent": 1050, "house cost": 150}
property_data[15] = {"name": "Fleet Street"         , "type": "property", "street value": 220, "owner": None, "upgrade state": 0, "colour set": 4, "rent": 18, "h1 rent": 90 , "h2 rent": 250, "h3 rent": 700 , "h4 rent": 875 , "h5 rent": 1050, "house cost": 150}
property_data[16] = {"name": "Trafalgar Square"     , "type": "property", "street value": 240, "owner": None, "upgrade state": 0, "colour set": 4, "rent": 18, "h1 rent": 90 , "h2 rent": 250, "h3 rent": 700 , "h4 rent": 875 , "h5 rent": 1050, "house cost": 150}
property_data[17] = {"name": "Fenchurch St. Station", "type": "station" , "street value": 200, "owner": None, "upgrade state": 0}
property_data[18] = {"name": "Leicester Square"     , "type": "property", "street value": 260, "owner": None, "upgrade state": 0, "colour set": 5, "rent": 22, "h1 rent": 110, "h2 rent": 330, "h3 rent": 800 , "h4 rent": 975 , "h5 rent": 1150, "house cost": 150}
property_data[19] = {"name": "Coventry Street"      , "type": "property", "street value": 260, "owner": None, "upgrade state": 0, "colour set": 5, "rent": 22, "h1 rent": 110, "h2 rent": 330, "h3 rent": 800 , "h4 rent": 975 , "h5 rent": 1150, "house cost": 150}
property_data[20] = {"name": "Water Works"          , "type": "utility" , "street value": 150, "owner": None, "upgrade state": 0}
property_data[21] = {"name": "Piccadilly"           , "type": "property", "street value": 280, "owner": None, "upgrade state": 0, "colour set": 5, "rent": 24, "h1 rent": 120, "h2 rent": 360, "h3 rent": 850 , "h4 rent": 1025, "h5 rent": 1200, "house cost": 150}
property_data[22] = {"name": "Regent Street"        , "type": "property", "street value": 300, "owner": None, "upgrade state": 0, "colour set": 6, "rent": 26, "h1 rent": 130, "h2 rent": 390, "h3 rent": 900 , "h4 rent": 1100, "h5 rent": 1275, "house cost": 200}
property_data[23] = {"name": "Oxford Street"        , "type": "property", "street value": 300, "owner": None, "upgrade state": 0, "colour set": 6, "rent": 26, "h1 rent": 130, "h2 rent": 390, "h3 rent": 900 , "h4 rent": 1100, "h5 rent": 1275, "house cost": 200}
property_data[24] = {"name": "Bond Street"          , "type": "property", "street value": 320, "owner": None, "upgrade state": 0, "colour set": 6, "rent": 28, "h1 rent": 150, "h2 rent": 450, "h3 rent": 1000, "h4 rent": 1200, "h5 rent": 1400, "house cost": 200}
property_data[25] = {"name": "Liverpool St. Station", "type": "station" , "street value": 200, "owner": None, "upgrade state": 0}
property_data[26] = {"name": "Park Lane"            , "type": "property", "street value": 350, "owner": None, "upgrade state": 0, "colour set": 7, "rent": 35, "h1 rent": 175, "h2 rent": 500, "h3 rent": 1100, "h4 rent": 1300, "h5 rent": 1500, "house cost": 200}
property_data[27] = {"name": "Mayfair"              , "type": "property", "street value": 400, "owner": None, "upgrade state": 0, "colour set": 7, "rent": 50, "h1 rent": 200, "h2 rent": 600, "h3 rent": 1400, "h4 rent": 1700, "h5 rent": 2000, "house cost": 200}

# index = number of stations
station_rent = [0, 25, 50, 100, 200]

# this converts the player's position into the corresponding property
prop_from_pos = {
    1:0, 3:1, 5:2, 6:3, 8:4, 9:5, 11:6, 12:7, 13:8, 14:9, 15:10,
    16:11, 18:12, 19:13, 21:14, 23:15, 24:16, 25:17, 26:18, 27:19, 
    28:20, 29:21, 31:22, 32:23, 34:24, 35:25, 37:26, 39:27
}