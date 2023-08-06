
def parse_3C(wa2):
    # Work Area 2 (COW) - Function 3C
    regular = {
        # "Internal Use": wa2[0:20],
        "Duplicate Key Flag or Continuous Parity": wa2[21],
        "Locational Status of Segment": wa2[22],
        "County Boundary Indicator": wa2[23],
        "DCP-Preferred LGC for Street 1": wa2[24:26],  # 'On' Street
        "DCP-Preferred LGC for Street 2": wa2[26:28],  # Input Cross Street with Lower B5SC value
        "DCP-Preferred LGC for Street 3": wa2[28:30],  # Input Cross Street with Higher B5SC value
        "No. of Cross Streets at Low Addr End": wa2[30],
        "List of Cross Streets at Low Address End (Up to five B5SCs, 6 bytes each)": wa2[31:61],  # Blank Filled
        "No. of Cross Streets at High Addr End": wa2[61],
        "List of Cross Streets at High Address End (Up to five B5SCs, 6 bytes each)": wa2[62:92],  # Blank Filled
        "Cross Street Reversal Flag": wa2[92],
        "LION KEY": {
            "LION Borough Code": wa2[93],
            "LION Face Code": wa2[94:97],
            "LION Sequence Number": wa2[98:103]},
        "Generated Record Flag": wa2[103],
        "Length of Segment in Feet": wa2[104:109],
        "Segment Azimuth": wa2[109:112],
        "Segment Orientation": wa2[112],
        "Marble Hill/Rikers Island Alternative Borough Flag": wa2[113],
        "From Node": wa2[114:121],
        "To Node": wa2[121:128],
        "DSNY Snow Priority Code": wa2[128],  # Dept. of Sanitation
        # "Filler": wa2[129:132],
        "Segment Identifier": wa2[133:140],
        "DOT Street Light Contractor Area": wa2[140],
        "Side-of-Street Indicator": wa2[141],
        "Curve Flag": wa2[142],
        "Feature Type Code": wa2[143],
        "Segment Type Code": wa2[144],
        "Coincident Segment Count": wa2[145],
        # "Filler": wa2[146:149],
        "COMMUNITY DISTRICT": {
            "Community District Borough Code": wa2[150],
            "Community District Number": wa2[151:153]},
        "Low House Number": wa2[153:168],  # Display Format
        "High House Number": wa2[169:185],  # Display Format
        "Future Use": wa2[185:217],
        "Community Development Eligibility Indicator": wa2[217],
        "ZIP Code": wa2[218:223],
        "Health Area": wa2[223:227],
        "Police Patrol Borough Command": wa2[227],
        "Police Precinct": wa2[228:231],
        "Fire Division": wa2[231:233],
        "Fire Battalion": wa2[233:235],
        "Fire Company Type": wa2[235],
        "Fire Company Number": wa2[236:239],
        "Community School District": wa2[239:241],
        "Atomic Polygon": wa2[241:244],  # Was Dynamic Block
        "Election District (ED)": wa2[244:247],
        "Assembly District (AD)": wa2[247:249],
        "Police Patrol Borough": wa2[249:251],
        # "Filler": wa2[251],
        # "Borough Code": wa2[252],  # Internal Use
        "1990 Census Tract": wa2[253:259],
        "2010 Census Tract": wa2[259:265],
        "2010 Census Block": wa2[265:269],
        # "2010 Census Block Suffix": wa2[269],  # Not Implemented
        "2000 Census Tract": wa2[270:276],
        "2000 Census Block": wa2[276:280],
        "2000 Census Block Suffix": wa2[280],
        # "Filler": wa2[281:287],  # Was Blockface ID See Function 3C Extended
        "Neighborhood Tabulation Area (NTA)": wa2[288:292],
        # "Filler": wa2[292:299],
    }
    # Get extended results
    regular = regular.copy()
    regular.update(parse_3C_ext(wa2))
    return regular


def parse_C_aux_seg(wa2):
    # Work Area 2 (COW) - Function 3C with Auxiliary Segment List
    return{
        # "Filler": wa2[300:305],
        "Segment Count": wa2[306:310],  # Number of Segments
        "Segment IDs": wa2[310:800],  # Up to 70 Segment IDs; 7 bytes each 7 x 70 = 490
    }

def parse_3C_ext(wa2):
    # Work Area 2 (COW) - Function 3C Extended
    return{
        # "Same as Regular Work Area 2 Function 3C": wa2[0:299],
        "List of 4 LGCs for Street 1": wa2[300:308],  # 'On' Street
        "List of 4 LGCs for Street 2": wa2[308:316],  # Input Cross Street with Lower B5SC
        "List of 4 LGCs for Street 3": wa2[316:324],  # Input Cross Street with Higher B5SC
        "Left Health Center District": wa2[324:326],
        "Right Health Center District": wa2[326:328],
        "Filler": wa2[328],  # Was Split Community School District Flag
        "Traffic Direction": wa2[329],
        "Roadway Type": wa2[330:332],
        "Physical ID": wa2[332:339],
        "Generic ID": wa2[339:346],
        "NYPD ID": wa2[346:353],
        "FDNY ID": wa2[353:360],
        "Street Status": wa2[360],
        "Street Width": wa2[361:364],
        "Street Width Irregular": wa2[364],  # Not Implemented
        "Bike Lane": wa2[365],  # Will be retired See Bike Lane 2
        "Federal Classification Code": wa2[366:368],  # Not Implemented
        "Right Of Way Type": wa2[368],
        "List of 5 Additional LGCs for Street 1": wa2[369:379],  # Not Implemented
        "Legacy ID": wa2[379:386],
        "NTA Name": wa2[386:461],
        "FROM SPATIAL COORDINATES": {  # From Node
            "From X Coordinate": wa2[461:468],
            "From Y Coordinate": wa2[468:475]},
        "TO SPATIAL COORDINATES": {  # To Node
            "To X Coordinate": wa2[475:482],
            "To Y Coordinate": wa2[482:489]},
        "Latitude of From Intersection": wa2[489:498],  # From Node
        "Longitude of From Intersection": wa2[498:509],
        "Latitude of To Intersection": wa2[509:518],  # To Node
        "Longitude of To Intersection": wa2[518:529],
        "Blockface ID": wa2[529:539],
        "Number of Travel Lanes on the Street": wa2[539:541],
        "Number of Parking Lanes on the Street": wa2[541:543],
        "Number of Total Lanes on the Street": wa2[543:545],
        "Bike Lane 2": wa2[545:547],
        "Street Width Maximum": wa2[547:550],
        "Bike Traffic Direction": wa2[550:552],
        # "Filler": wa2[552:849],
    }


def parse_3C_ext_aux_seg(wa2):
    # Work Area 2 (COW) - Function 3C Extended with Auxiliary Segment List
    return {
        # "Same as Work Area 2 for Function 3C Extended": wa2[0:849],
        "Filler": wa2[850:856],
        "Segment Count": wa2[856:860],  # Number of Segments
        "Segment IDs": wa2[860:1350],  # Up to 70 Segment IDs 7 bytes each 7 x 70 = 490
    }