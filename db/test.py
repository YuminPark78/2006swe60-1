import requests
import sqlite3
import time
from tqdm import tqdm

# OneMap API endpoint and database connection
API_URL = "https://www.onemap.gov.sg/api/common/elastic/search"
DB_PATH = "data.db"  # Replace with your actual database path

# List of postal codes
dataset = [
    {"name": "SHELL ALEXANDRA", "address": "358 ALEXANDRA ROAD 159950", "latitude": 1.290661046, "longitude": 103.806843695, "e-waste accepted": "Non-regulated products only; E.g. Small household appliances, gaming consoles, audio systems, power supplies"},
    {"name": "SHELL ANG MO KIO", "address": "3535 ANG MO KIO AVENUE 6 569839", "latitude": 1.367837492, "longitude": 103.844671566, "e-waste accepted": "Non-regulated products only; E.g. Small household appliances, gaming consoles, audio systems, power supplies"},
    {"name": "SHELL BOON LAY", "address": "2 BOON LAY AVENUE 649960", "latitude": 1.344003409, "longitude": 103.707710355, "e-waste accepted": "Non-regulated products only; E.g. Small household appliances, gaming consoles, audio systems, power supplies"},
    {"name": "SHELL BRADDELL", "address": "110 BRADDELL ROAD 359914", "latitude": 1.344583526, "longitude": 103.864557912, "e-waste accepted": "Non-regulated products only; E.g. Small household appliances, gaming consoles, audio systems, power supplies"},
    {"name": "SHELL BUKIT BATOK (AVE 3)", "address": "11 BUKIT BATOK WEST AVENUE 3 659166", "latitude": 1.350227423, "longitude": 103.738433116, "e-waste accepted": "Non-regulated products only; E.g. Small household appliances, gaming consoles, audio systems, power supplies"},
    {"name": "SHELL BUKIT BATOK (AVE 6)", "address": "28 BUKIT BATOK EAST AVENUE 6 659760", "latitude": 1.34762672, "longitude": 103.764888537, "e-waste accepted": "Non-regulated products only; E.g. Small household appliances, gaming consoles, audio systems, power supplies"},
    {"name": "SHELL CHOA CHU KANG", "address": "20 CHOA CHU KANG DRIVE 689717", "latitude": 1.385605519, "longitude": 103.746481837, "e-waste accepted": "Non-regulated products only; E.g. Small household appliances, gaming consoles, audio systems, power supplies"},
    {"name": "SHELL EAST COAST", "address": "338 EAST COAST ROAD 428961", "latitude": 1.308211823, "longitude": 103.909783038, "e-waste accepted": "Non-regulated products only; E.g. Small household appliances, gaming consoles, audio systems, power supplies"},
    {"name": "SHELL HAVELOCK", "address": "548 HAVELOCK ROAD 169637", "latitude": 1.2899369098838, "longitude": 103.832409397132, "e-waste accepted": "Non-regulated products only; E.g. Small household appliances, gaming consoles, audio systems, power supplies"},
    {"name": "SHELL JURONG WEST", "address": "21 JURONG WEST AVENUE 5 649481", "latitude": 1.350092212, "longitude": 103.701211186, "e-waste accepted": "Non-regulated products only; E.g. Small household appliances, gaming consoles, audio systems, power supplies"},
    {"name": "SHELL MARSILING", "address": "10 MARSILING ROAD 739109", "latitude": 1.438325333, "longitude": 103.775415745, "e-waste accepted": "Non-regulated products only; E.g. Small household appliances, gaming consoles, audio systems, power supplies"},
    {"name": "SHELL NEWTON HOOPER", "address": "150 BUKIT TIMAH ROAD 229846", "latitude": 1.311342945, "longitude": 103.843097938, "e-waste accepted": "Non-regulated products only; E.g. Small household appliances, gaming consoles, audio systems, power supplies"},
    {"name": "SHELL PASIR RIS", "address": "1 NEW LOYANG LINK 506931", "latitude": 1.365794134, "longitude": 103.967222284, "e-waste accepted": "Non-regulated products only; E.g. Small household appliances, gaming consoles, audio systems, power supplies"},
    {"name": "SHELL PAYA LEBAR", "address": "98 PAYA LEBAR ROAD 409008", "latitude": 1.321754989, "longitude": 103.891649083, "e-waste accepted": "Non-regulated products only; E.g. Small household appliances, gaming consoles, audio systems, power supplies"},
    {"name": "SHELL PAYA LEBAR MACPHERSON", "address": "255 PAYA LEBAR ROAD 409037", "latitude": 1.33178863606529, "longitude": 103.888725333216, "e-waste accepted": "Non-regulated products only; E.g. Small household appliances, gaming consoles, audio systems, power supplies"},
    {"name": "SHELL SERANGOON GARDEN", "address": "49 SERANGOON GARDEN WAY 555944", "latitude": 1.36322447321201, "longitude": 103.867359768798, "e-waste accepted": "Non-regulated products only; E.g. Small household appliances, gaming consoles, audio systems, power supplies"},
    {"name": "SHELL SIGLAP", "address": "40 UPPER EAST COAST ROAD 455212", "latitude": 1.312552973, "longitude": 103.926540994, "e-waste accepted": "Non-regulated products only; E.g. Small household appliances, gaming consoles, audio systems, power supplies"},
    {"name": "SHELL SIMPANG BEDOK", "address": "331 BEDOK ROAD 469504", "latitude": 1.330890018, "longitude": 103.947576317, "e-waste accepted": "Non-regulated products only; E.g. Small household appliances, gaming consoles, audio systems, power supplies"},
    {"name": "SHELL TAMPINES", "address": "9 TAMPINES AVENUE 2 529731", "latitude": 1.349208775, "longitude": 103.947630247, "e-waste accepted": "Non-regulated products only; E.g. Small household appliances, gaming consoles, audio systems, power supplies"},
    {"name": "SHELL THOMSON", "address": "324 THOMSON ROAD 307672", "latitude": 1.324191507, "longitude": 103.842166355, "e-waste accepted": "Non-regulated products only; E.g. Small household appliances, gaming consoles, audio systems, power supplies"},
    {"name": "SHELL TIONG BAHRU", "address": "603 TIONG BAHRU ROAD 158788", "latitude": 1.28848416886655, "longitude": 103.819631176469, "e-waste accepted": "Non-regulated products only; E.g. Small household appliances, gaming consoles, audio systems, power supplies"},
    {"name": "SHELL TOA PAYOH", "address": "248 TOA PAYOH LORONG 1 319755", "latitude": 1.341087645, "longitude": 103.848878826, "e-waste accepted": "Non-regulated products only; E.g. Small household appliances, gaming consoles, audio systems, power supplies"},
    {"name": "SHELL WOODLANDS", "address": "20 WOODLANDS AVENUE 9 738954", "latitude": 1.444329267, "longitude": 103.790059164, "e-waste accepted": "Non-regulated products only; E.g. Small household appliances, gaming consoles, audio systems, power supplies"},
    {"name": "SHELL YISHUN", "address": "1 YISHUN STREET 11 768642", "latitude": 1.43080205, "longitude": 103.83301117, "e-waste accepted": "Non-regulated products only; E.g. Small household appliances, gaming consoles, audio systems, power supplies"},
    {"name": "ANG MO KIO HUB", "address": "53 ANG MO KIO AVENUE 3, AMK HUB, #03-13 569933", "latitude": 1.369248913, "longitude": 103.8483992, "e-waste accepted": "Non-regulated products only; E.g. Small household appliances, gaming consoles, audio systems, power supplies"},
    {"name": "ONE MARINA", "address": "1 MARINA BOULEVARD, ONE MARINA BOULEVARD, B1 18989", "latitude": 1.282287657, "longitude": 103.8524287, "e-waste accepted": "Non-regulated products only; E.g. Small household appliances, gaming consoles, audio systems, power supplies"},
    {"name": "JURONG POINT", "address": "1 JURONG WEST CENTRAL 2, JURONG POINT, BESIDES SKECHERS #01-16H/J 648886", "latitude": 1.339830153, "longitude": 103.7064609, "e-waste accepted": "Non-regulated products only; E.g. Small household appliances, gaming consoles, audio systems, power supplies"},
    {"name": "WISMA ATRIA", "address": "435 ORCHARD ROAD, WISMA ATRIA, LEVEL 6 BESIDE CARPARK 238877", "latitude": 1.303698902, "longitude": 103.8331896, "e-waste accepted": "Non-regulated products only; E.g. Small household appliances, gaming consoles, audio systems, power supplies"},
    {"name": "SENGKANG GENERAL HOSPITAL", "address": "110 SENGKANG EAST WAY, SENGKANG GENERAL HOSPITAL, LEVEL 8 544886", "latitude": 1.394299412, "longitude": 103.8930013, "e-waste accepted": "Non-regulated products only; E.g. Small household appliances, gaming consoles, audio systems, power supplies"},
    {"name": "CHANGI GENERAL HOSPITAL", "address": "2 SIMEI STREET 3, CHANGI GENERAL HOSPITAL 529889", "latitude": 1.34068474, "longitude": 103.9492944, "e-waste accepted": "Non-regulated products only; E.g. Small household appliances, gaming consoles, audio systems, power supplies"},
    {"name": "ESR BIZPARK@CHANGI", "address": "8 CHANGI BUSINESS PARK AVENUE 1, ESR BIZPARK #01-51 486018", "latitude": 1.334919773, "longitude": 103.9636539, "e-waste accepted": "Non-regulated products only; E.g. Small household appliances, gaming consoles, audio systems, power supplies"},
    {"name": "SEMBAWANG SHOPPING CENTRE", "address": "604 SEMBAWANG ROAD, SEMBAWANG SHOPPING CENTRE, 2F 758459", "latitude": 1.441767148, "longitude": 103.8244951, "e-waste accepted": "Non-regulated products only; E.g. Small household appliances, gaming consoles, audio systems, power supplies"},
    {"name": "23 GHIM MOH LINK", "address": "23 GHIM MOH LINK 271023", "latitude": 1.308635626, "longitude": 103.786332, "e-waste accepted": "Non-regulated products only; E.g. Small household appliances, gaming consoles, audio systems, power supplies"},
    {"name": "SINGPOST CENTRE", "address": "10 EUNOS ROAD 8, SINGPOST CENTRE 408600", "latitude": 1.318856103, "longitude": 103.8940672, "e-waste accepted": "Non-regulated products only; E.g. Small household appliances, gaming consoles, audio systems, power supplies"},
    {"name": "SINGAPORE GENERAL HOSPITAL", "address": "20 COLLEGE ROAD, ACADEMIA BUILDING 169856", "latitude": 1.281670377, "longitude": 103.8355855, "e-waste accepted": "Non-regulated products only; E.g. Small household appliances, gaming consoles, audio systems, power supplies"},
    {"name": "SOUTH BEACH AVENUE", "address": "26 BEACH ROAD, SOUTH BEACH AVENUE 189768", "latitude": 1.294431711, "longitude": 103.8560109, "e-waste accepted": "Non-regulated products only; E.g. Small household appliances, gaming consoles, audio systems, power supplies"},
    {"name": "TZU CHI HUMANISTIC YOUTH CENTRE", "address": "30A YISHUN CENTRAL 1, TZU CHI HUMANISTIC YOUTH CENTRE 768796", "latitude": 1.426537511, "longitude": 103.8383334, "e-waste accepted": "Non-regulated products only; E.g. Small household appliances, gaming consoles, audio systems, power supplies"},
    {"name": "MARINA ONE", "address": "5 STRAITS VIEW, MARINA ONE, #B2-79 18935", "latitude": 1.277372343, "longitude": 103.8528448, "e-waste accepted": "Non-regulated products only; E.g. Small household appliances, gaming consoles, audio systems, power supplies"},
    {"name": "336A SEMBAWANG CRESCENT MSCP", "address": "336A SEMBAWANG CRESCENT 751336", "latitude": 1.446638619, "longitude": 103.8150105, "e-waste accepted": "Non-regulated products only; E.g. Small household appliances, gaming consoles, audio systems, power supplies"}
] + [
    {"name": "406A SEMBAWANG DRIVE MSCP", "address": "406A SEMBAWANG DRIVE 751406", "latitude": 1.452736242, "longitude": 103.8172493, "e-waste accepted": "Non-regulated products only; E.g. Small household appliances, gaming consoles, audio systems, power supplies"},
    {"name": "NORTHPOINT CITY", "address": "930 YISHUN AVENUE 2, NORTHPOINT CITY, SOUTH WING, LEVEL 2 769098", "latitude": 1.42969848, "longitude": 103.8357765, "e-waste accepted": "Non-regulated products only; E.g. Small household appliances, gaming consoles, audio systems, power supplies"},
    {"name": "CHENG SAN COMMUNITY CENTRE", "address": "6 ANG MO KIO STREET 53, CHENG SAN COMMUNITY CENTRE, LEVEL 1 569205", "latitude": 1.371780447, "longitude": 103.84957, "e-waste accepted": "Non-regulated products only; E.g. Small household appliances, gaming consoles, audio systems, power supplies"},
    {"name": "BISHAN COMMUNITY CLUB", "address": "51 BISHAN STREET 13, LEVEL 1 579799", "latitude": 1.349022435, "longitude": 103.8491227, "e-waste accepted": "Non-regulated products only; E.g. Small household appliances, gaming consoles, audio systems, power supplies"},
    {"name": "BRADDELL HEIGHTS COMMUNITY CLUB", "address": "50 SERANGOON AVENUE 2, LEVEL 1 556129", "latitude": 1.3497831, "longitude": 103.869184, "e-waste accepted": "Non-regulated products only; E.g. Small household appliances, gaming consoles, audio systems, power supplies"},
    {"name": "FUCHUN COMMUNITY CLUB", "address": "1 WOODLANDS STREET 81, LEVEL 1 738526", "latitude": 1.436335238, "longitude": 103.7905551, "e-waste accepted": "Non-regulated products only; E.g. Small household appliances, gaming consoles, audio systems, power supplies"},
    {"name": "GAMBAS COMMUNITY CLUB", "address": "525 WELLINGTON CIRCLE, LEVEL 1 757991", "latitude": 1.4266841, "longitude": 103.823822, "e-waste accepted": "Non-regulated products only; E.g. Small household appliances, gaming consoles, audio systems, power supplies"},
    {"name": "HOUGANG COMMUNITY CLUB", "address": "35 HOUGANG AVENUE 3, LEVEL 1 538840", "latitude": 1.365106, "longitude": 103.8911, "e-waste accepted": "Non-regulated products only; E.g. Small household appliances, gaming consoles, audio systems, power supplies"},
    {"name": "HWI YOH VILLE COMMUNITY CENTRE", "address": "535 SERANGOON NORTH AVENUE 4, LEVEL 1 550535", "latitude": 1.3715435, "longitude": 103.8775, "e-waste accepted": "Non-regulated products only; E.g. Small household appliances, gaming consoles, audio systems, power supplies"},
    {"name": "JALAN BESAR COMMUNITY CLUB", "address": "69A JALAN BESAR 208814", "latitude": 1.307169, "longitude": 103.856776, "e-waste accepted": "Non-regulated products only; E.g. Small household appliances, gaming consoles, audio systems, power supplies"},
    {"name": "KAMPONG CHAI CHEE COMMUNITY CENTRE", "address": "11 BEDOK NORTH STREET 1, LEVEL 1 469659", "latitude": 1.326543, "longitude": 103.934445, "e-waste accepted": "Non-regulated products only; E.g. Small household appliances, gaming consoles, audio systems, power supplies"},
    {"name": "KAMPONG KEMBANGAN COMMUNITY CENTRE", "address": "5 LENGKONG TIGA, LEVEL 1 417408", "latitude": 1.321823, "longitude": 103.911, "e-waste accepted": "Non-regulated products only; E.g. Small household appliances, gaming consoles, audio systems, power supplies"},
    {"name": "KAMPONG UBI COMMUNITY CENTRE", "address": "10 EUNOS ROAD 5, LEVEL 1 408600", "latitude": 1.3185, "longitude": 103.8945, "e-waste accepted": "Non-regulated products only; E.g. Small household appliances, gaming consoles, audio systems, power supplies"},
    {"name": "KEBUN BARU COMMUNITY CLUB", "address": "216 ANG MO KIO AVENUE 4, LEVEL 1 569881", "latitude": 1.3682, "longitude": 103.8332, "e-waste accepted": "Non-regulated products only; E.g. Small household appliances, gaming consoles, audio systems, power supplies"},
    {"name": "KRETA AYER COMMUNITY CLUB", "address": "28A KEONG SAIK ROAD, LEVEL 1 089135", "latitude": 1.280556, "longitude": 103.841667, "e-waste accepted": "Non-regulated products only; E.g. Small household appliances, gaming consoles, audio systems, power supplies"},
    {"name": "LIM CHU KANG COMMUNITY CLUB", "address": "211 CHOA CHU KANG STREET 53, LEVEL 1 689278", "latitude": 1.3924, "longitude": 103.7464, "e-waste accepted": "Non-regulated products only; E.g. Small household appliances, gaming consoles, audio systems, power supplies"},
    {"name": "MACPHERSON COMMUNITY CLUB", "address": "400 PAYA LEBAR WAY, LEVEL 1 379131", "latitude": 1.329384, "longitude": 103.88966, "e-waste accepted": "Non-regulated products only; E.g. Small household appliances, gaming consoles, audio systems, power supplies"},
    {"name": "MARINE PARADE COMMUNITY CLUB", "address": "278 MARINE PARADE ROAD, LEVEL 1 449282", "latitude": 1.302321, "longitude": 103.9028, "e-waste accepted": "Non-regulated products only; E.g. Small household appliances, gaming consoles, audio systems, power supplies"},
    {"name": "NANYANG COMMUNITY CLUB", "address": "60 JURONG WEST STREET 91, LEVEL 1 649040", "latitude": 1.339883, "longitude": 103.706, "e-waste accepted": "Non-regulated products only; E.g. Small household appliances, gaming consoles, audio systems, power supplies"},
    {"name": "PASIR RIS EAST COMMUNITY CLUB", "address": "1 PASIR RIS DRIVE 4, LEVEL 1 519457", "latitude": 1.3725, "longitude": 103.9442, "e-waste accepted": "Non-regulated products only; E.g. Small household appliances, gaming consoles, audio systems, power supplies"},
    {"name": "PAYA LEBAR COMMUNITY CLUB", "address": "11 HOUGANG AVENUE 6, LEVEL 1 538789", "latitude": 1.372038, "longitude": 103.8916, "e-waste accepted": "Non-regulated products only; E.g. Small household appliances, gaming consoles, audio systems, power supplies"},
    {"name": "POTONG PASIR COMMUNITY CLUB", "address": "6 POTONG PASIR AVENUE 2, LEVEL 1 358361", "latitude": 1.3318, "longitude": 103.8687, "e-waste accepted": "Non-regulated products only; E.g. Small household appliances, gaming consoles, audio systems, power supplies"},
    {"name": "QUEENSTOWN COMMUNITY CLUB", "address": "365 COMMONWEALTH AVENUE, LEVEL 1 149732", "latitude": 1.2996, "longitude": 103.8051, "e-waste accepted": "Non-regulated products only; E.g. Small household appliances, gaming consoles, audio systems, power supplies"},
    {"name": "SENGKANG COMMUNITY CLUB", "address": "2 SENGKANG SQUARE, LEVEL 1 545025", "latitude": 1.391935, "longitude": 103.892644, "e-waste accepted": "Non-regulated products only; E.g. Small household appliances, gaming consoles, audio systems, power supplies"},
    {"name": "TAMPINES EAST COMMUNITY CLUB", "address": "10 TAMPINES STREET 32, LEVEL 1 529287", "latitude": 1.35344, "longitude": 103.94802, "e-waste accepted": "Non-regulated products only; E.g. Small household appliances, gaming consoles, audio systems, power supplies"},
    {"name": "TAMPINES NORTH COMMUNITY CLUB", "address": "120 TAMPINES AVENUE 5, LEVEL 1 529753", "latitude": 1.353839, "longitude": 103.94126, "e-waste accepted": "Non-regulated products only; E.g. Small household appliances, gaming consoles, audio systems, power supplies"},
    {"name": "TECK GHEE COMMUNITY CLUB", "address": "861 ANG MO KIO AVENUE 10, LEVEL 1 569733", "latitude": 1.3772, "longitude": 103.8538, "e-waste accepted": "Non-regulated products only; E.g. Small household appliances, gaming consoles, audio systems, power supplies"},
    {"name": "TOA PAYOH CENTRAL COMMUNITY CLUB", "address": "93 TOA PAYOH CENTRAL, LEVEL 1 319194", "latitude": 1.334933, "longitude": 103.852, "e-waste accepted": "Non-regulated products only; E.g. Small household appliances, gaming consoles, audio systems, power supplies"},
    {"name": "WEST COAST COMMUNITY CLUB", "address": "2 CLEMENTI WEST STREET 2, LEVEL 1 129605", "latitude": 1.304742, "longitude": 103.7642, "e-waste accepted": "Non-regulated products only; E.g. Small household appliances, gaming consoles, audio systems, power supplies"},
    {"name": "WOODLANDS COMMUNITY CLUB", "address": "1 WOODLANDS STREET 81, LEVEL 1 738526", "latitude": 1.436355, "longitude": 103.7908, "e-waste accepted": "Non-regulated products only; E.g. Small household appliances, gaming consoles, audio systems, power supplies"},
    {"name": "WOODLANDS EAST COMMUNITY CLUB", "address": "1 WOODLANDS STREET 83, LEVEL 1 738507", "latitude": 1.43861, "longitude": 103.7954, "e-waste accepted": "Non-regulated products only; E.g. Small household appliances, gaming consoles, audio systems, power supplies"},
    {"name": "YIO CHU KANG COMMUNITY CLUB", "address": "50 ANG MO KIO STREET 61, LEVEL 1 569163", "latitude": 1.3826, "longitude": 103.8442, "e-waste accepted": "Non-regulated products only; E.g. Small household appliances, gaming consoles, audio systems, power supplies"},
    {"name": "YISHUN COMMUNITY CLUB", "address": "2 YISHUN AVENUE 9, LEVEL 1 768993", "latitude": 1.4259, "longitude": 103.8474, "e-waste accepted": "Non-regulated products only; E.g. Small household appliances, gaming consoles, audio systems, power supplies"},
    {"name": "YUHUA COMMUNITY CLUB", "address": "90 BOON LAY WAY, LEVEL 1 609958", "latitude": 1.332, "longitude": 103.744, "e-waste accepted": "Non-regulated products only; E.g. Small household appliances, gaming consoles, audio systems, power supplies"},
    {"name": "BOON LAY COMMUNITY CENTRE", "address": "10 BOON LAY PLACE, LEVEL 1 649882", "latitude": 1.34446, "longitude": 103.7054, "e-waste accepted": "Non-regulated products only; E.g. Small household appliances, gaming consoles, audio systems, power supplies"},
    {"name": "BUKIT BATOK COMMUNITY CLUB", "address": "21 BUKIT BATOK CENTRAL, LEVEL 1 659858", "latitude": 1.34896, "longitude": 103.7494, "e-waste accepted": "Non-regulated products only; E.g. Small household appliances, gaming consoles, audio systems, power supplies"},
    {"name": "CLEMENTI COMMUNITY CLUB", "address": "220 CLEMENTI AVENUE 4, LEVEL 1 129880", "latitude": 1.3132, "longitude": 103.7655, "e-waste accepted": "Non-regulated products only; E.g. Small household appliances, gaming consoles, audio systems, power supplies"},
    {"name": "CHONG PANG COMMUNITY CLUB", "address": "21 YISHUN RING ROAD, LEVEL 1 768677", "latitude": 1.43241, "longitude": 103.8356, "e-waste accepted": "Non-regulated products only; E.g. Small household appliances, gaming consoles, audio systems, power supplies"}
] + [
    {"name": "NANYANG POLYTECHNIC", "address": "180 ANG MO KIO AVENUE 8 569830", "latitude": 1.37965, "longitude": 103.849724, "e-waste accepted": "Non-regulated products only; E.g. Small household appliances, gaming consoles, audio systems, power supplies"},
    {"name": "NGEE ANN POLYTECHNIC", "address": "535 CLEMENTI ROAD 599489", "latitude": 1.332318, "longitude": 103.776818, "e-waste accepted": "Non-regulated products only; E.g. Small household appliances, gaming consoles, audio systems, power supplies"},
    {"name": "REPUBLIC POLYTECHNIC", "address": "9 WOODLANDS AVENUE 9 738964", "latitude": 1.443758, "longitude": 103.784454, "e-waste accepted": "Non-regulated products only; E.g. Small household appliances, gaming consoles, audio systems, power supplies"},
    {"name": "SINGAPORE POLYTECHNIC", "address": "500 DOVER ROAD 139651", "latitude": 1.307792, "longitude": 103.778356, "e-waste accepted": "Non-regulated products only; E.g. Small household appliances, gaming consoles, audio systems, power supplies"},
    {"name": "TEMASEK POLYTECHNIC", "address": "21 TAMPINES AVENUE 1 529757", "latitude": 1.345221, "longitude": 103.932373, "e-waste accepted": "Non-regulated products only; E.g. Small household appliances, gaming consoles, audio systems, power supplies"},
    {"name": "ITE COLLEGE CENTRAL", "address": "2 ANG MO KIO DRIVE 567720", "latitude": 1.3779, "longitude": 103.84943, "e-waste accepted": "Non-regulated products only; E.g. Small household appliances, gaming consoles, audio systems, power supplies"},
    {"name": "ITE COLLEGE EAST", "address": "10 SIMEI AVENUE 486047", "latitude": 1.345233, "longitude": 103.953598, "e-waste accepted": "Non-regulated products only; E.g. Small household appliances, gaming consoles, audio systems, power supplies"},
    {"name": "ITE COLLEGE WEST", "address": "1 CHOA CHU KANG GROVE 688236", "latitude": 1.347823, "longitude": 103.746778, "e-waste accepted": "Non-regulated products only; E.g. Small household appliances, gaming consoles, audio systems, power supplies"},
    {"name": "BISHAN PUBLIC LIBRARY", "address": "5 BISHAN PLACE, LEVEL 2 579841", "latitude": 1.351733, "longitude": 103.848269, "e-waste accepted": "Non-regulated products only; E.g. Small household appliances, gaming consoles, audio systems, power supplies"},
    {"name": "BUKIT BATOK PUBLIC LIBRARY", "address": "1 BUKIT BATOK CENTRAL LINK, #03-01 WEST MALL 658713", "latitude": 1.352582, "longitude": 103.749826, "e-waste accepted": "Non-regulated products only; E.g. Small household appliances, gaming consoles, audio systems, power supplies"},
    {"name": "BUKIT MERAH PUBLIC LIBRARY", "address": "3779 JALAN BUKIT MERAH 159462", "latitude": 1.285439, "longitude": 103.811947, "e-waste accepted": "Non-regulated products only; E.g. Small household appliances, gaming consoles, audio systems, power supplies"},
    {"name": "CLEMENTI PUBLIC LIBRARY", "address": "3155 COMMONWEALTH AVENUE WEST, #05-13/14 129588", "latitude": 1.314868, "longitude": 103.764965, "e-waste accepted": "Non-regulated products only; E.g. Small household appliances, gaming consoles, audio systems, power supplies"},
    {"name": "GEYLANG EAST PUBLIC LIBRARY", "address": "50 GEYLANG EAST AVENUE 1 389777", "latitude": 1.320654, "longitude": 103.888293, "e-waste accepted": "Non-regulated products only; E.g. Small household appliances, gaming consoles, audio systems, power supplies"},
    {"name": "JURONG REGIONAL LIBRARY", "address": "21 JURONG EAST CENTRAL 1 609732", "latitude": 1.329184, "longitude": 103.739482, "e-waste accepted": "Non-regulated products only; E.g. Small household appliances, gaming consoles, audio systems, power supplies"},
    {"name": "LIBRARY@HARBOURFRONT", "address": "1 HARBOURFRONT WALK, VIVOCITY, #03-05 098585", "latitude": 1.2642, "longitude": 103.8224, "e-waste accepted": "Non-regulated products only; E.g. Small household appliances, gaming consoles, audio systems, power supplies"},
    {"name": "LIBRARY@ORCHARD", "address": "277 ORCHARD ROAD, #03-12/13 238858", "latitude": 1.3047, "longitude": 103.8314, "e-waste accepted": "Non-regulated products only; E.g. Small household appliances, gaming consoles, audio systems, power supplies"},
    {"name": "LIBRARY@CHINATOWN", "address": "133 NEW BRIDGE ROAD, #04-12 CHINATOWN POINT 059413", "latitude": 1.2859, "longitude": 103.8457, "e-waste accepted": "Non-regulated products only; E.g. Small household appliances, gaming consoles, audio systems, power supplies"},
    {"name": "MARINE PARADE PUBLIC LIBRARY", "address": "278 MARINE PARADE ROAD, #02-02 449282", "latitude": 1.302678, "longitude": 103.902953, "e-waste accepted": "Non-regulated products only; E.g. Small household appliances, gaming consoles, audio systems, power supplies"},
    {"name": "PASIR RIS PUBLIC LIBRARY", "address": "1 PASIR RIS CENTRAL STREET 3, #04-01 WHITE SANDS 518457", "latitude": 1.3725, "longitude": 103.9478, "e-waste accepted": "Non-regulated products only; E.g. Small household appliances, gaming consoles, audio systems, power supplies"},
    {"name": "PUNGGOL REGIONAL LIBRARY", "address": "83 PUNGGOL CENTRAL, #02-15 828761", "latitude": 1.404228, "longitude": 103.902777, "e-waste accepted": "Non-regulated products only; E.g. Small household appliances, gaming consoles, audio systems, power supplies"},
    {"name": "QUEENSTOWN PUBLIC LIBRARY", "address": "53 MARGARET DRIVE 149297", "latitude": 1.30034, "longitude": 103.806859, "e-waste accepted": "Non-regulated products only; E.g. Small household appliances, gaming consoles, audio systems, power supplies"},
    {"name": "SENGKANG PUBLIC LIBRARY", "address": "1 COMPASSVALE DRIVE, #03-11 545078", "latitude": 1.3929, "longitude": 103.8935, "e-waste accepted": "Non-regulated products only; E.g. Small household appliances, gaming consoles, audio systems, power supplies"},
    {"name": "TAMPINES REGIONAL LIBRARY", "address": "1 TAMPINES WALK, #02-01 529684", "latitude": 1.3535, "longitude": 103.9448, "e-waste accepted": "Non-regulated products only; E.g. Small household appliances, gaming consoles, audio systems, power supplies"},
    {"name": "TOA PAYOH PUBLIC LIBRARY", "address": "6 TOA PAYOH CENTRAL 319191", "latitude": 1.3340, "longitude": 103.8495, "e-waste accepted": "Non-regulated products only; E.g. Small household appliances, gaming consoles, audio systems, power supplies"},
    {"name": "WOODLANDS REGIONAL LIBRARY", "address": "900 SOUTH WOODLANDS DRIVE, #01-03 730900", "latitude": 1.436332, "longitude": 103.7867, "e-waste accepted": "Non-regulated products only; E.g. Small household appliances, gaming consoles, audio systems, power supplies"},
    {"name": "YISHUN PUBLIC LIBRARY", "address": "930 YISHUN AVENUE 2, #04-01 NORTHPOINT CITY, NORTH WING 769098", "latitude": 1.4298, "longitude": 103.8364, "e-waste accepted": "Non-regulated products only; E.g. Small household appliances, gaming consoles, audio systems, power supplies"},
    {"name": "ANG MO KIO CENTRAL MARKET", "address": "628 ANG MO KIO AVENUE 4 560628", "latitude": 1.3750, "longitude": 103.8499, "e-waste accepted": "Non-regulated products only; E.g. Small household appliances, gaming consoles, audio systems, power supplies"},
    {"name": "BEDOK MARKET PLACE", "address": "348 BEDOK ROAD 469560", "latitude": 1.3286, "longitude": 103.9451, "e-waste accepted": "Non-regulated products only; E.g. Small household appliances, gaming consoles, audio systems, power supplies"},
    {"name": "BISHAN NORTH SHOPPING MALL", "address": "282 BISHAN STREET 22 570282", "latitude": 1.3569, "longitude": 103.8471, "e-waste accepted": "Non-regulated products only; E.g. Small household appliances, gaming consoles, audio systems, power supplies"},
    {"name": "BLOODBANK@WOODLANDS", "address": "900 SOUTH WOODLANDS DRIVE, LEVEL 1 730900", "latitude": 1.4371, "longitude": 103.7856, "e-waste accepted": "Non-regulated products only; E.g. Small household appliances, gaming consoles, audio systems, power supplies"},
    {"name": "CENTRAL @ CLARKE QUAY", "address": "6 EU TONG SEN STREET, #B1-01 059817", "latitude": 1.2882, "longitude": 103.8467, "e-waste accepted": "Non-regulated products only; E.g. Small household appliances, gaming consoles, audio systems, power supplies"},
    {"name": "CITY SQUARE MALL", "address": "180 KITCHENER ROAD 208539", "latitude": 1.3111, "longitude": 103.8565, "e-waste accepted": "Non-regulated products only; E.g. Small household appliances, gaming consoles, audio systems, power supplies"},
    {"name": "FAIRPRICE @ HOUGANG", "address": "90 HOUGANG AVENUE 10 538766", "latitude": 1.3683, "longitude": 103.8922, "e-waste accepted": "Non-regulated products only; E.g. Small household appliances, gaming consoles, audio systems, power supplies"},
    {"name": "FAIRPRICE @ WOODLANDS", "address": "30 WOODLANDS AVENUE 1 739065", "latitude": 1.4372, "longitude": 103.7862, "e-waste accepted": "Non-regulated products only; E.g. Small household appliances, gaming consoles, audio systems, power supplies"},
    {"name": "FAIRPRICE @ BEDOK MALL", "address": "311 NEW UPPER CHANGI ROAD, BEDOK MALL, #B2-23 467360", "latitude": 1.3245, "longitude": 103.9297, "e-waste accepted": "Non-regulated products only; E.g. Small household appliances, gaming consoles, audio systems, power supplies"},
    {"name": "FAIRPRICE @ JURONG EAST", "address": "2 JURONG EAST STREET 21 609601", "latitude": 1.3359, "longitude": 103.7446, "e-waste accepted": "Non-regulated products only; E.g. Small household appliances, gaming consoles, audio systems, power supplies"},
    {"name": "FAIRPRICE @ SERANGOON", "address": "253 SERANGOON CENTRAL DRIVE, #B2-20 550253", "latitude": 1.3524, "longitude": 103.8704, "e-waste accepted": "Non-regulated products only; E.g. Small household appliances, gaming consoles, audio systems, power supplies"}
] + [
    {"name": "FAIRPRICE @ NEX MALL", "address": "23 SERANGOON CENTRAL, #03-42 556083", "latitude": 1.3508, "longitude": 103.8739, "e-waste accepted": "Non-regulated products only; E.g. Small household appliances, gaming consoles, audio systems, power supplies"},
    {"name": "FAIRPRICE @ ANG MO KIO", "address": "712 ANG MO KIO AVENUE 6 560712", "latitude": 1.3719, "longitude": 103.8488, "e-waste accepted": "Non-regulated products only; E.g. Small household appliances, gaming consoles, audio systems, power supplies"},
    {"name": "FAIRPRICE @ TAMAN JURONG", "address": "399 YUNG SHENG ROAD 610399", "latitude": 1.3307, "longitude": 103.7245, "e-waste accepted": "Non-regulated products only; E.g. Small household appliances, gaming consoles, audio systems, power supplies"},
    {"name": "FAIRPRICE @ TOA PAYOH HUB", "address": "530 LORONG 6 TOA PAYOH, #B1-01 310530", "latitude": 1.3328, "longitude": 103.8477, "e-waste accepted": "Non-regulated products only; E.g. Small household appliances, gaming consoles, audio systems, power supplies"},
    {"name": "FAIRPRICE @ VIVO CITY", "address": "1 HARBOURFRONT WALK, #B2-23 098585", "latitude": 1.2643, "longitude": 103.8222, "e-waste accepted": "Non-regulated products only; E.g. Small household appliances, gaming consoles, audio systems, power supplies"},
    {"name": "FAIRPRICE @ WATERWAY POINT", "address": "83 PUNGGOL CENTRAL, #B1-01 828761", "latitude": 1.4055, "longitude": 103.9029, "e-waste accepted": "Non-regulated products only; E.g. Small household appliances, gaming consoles, audio systems, power supplies"},
    {"name": "FAIRPRICE @ WOODLANDS", "address": "30 WOODLANDS AVENUE 1 739065", "latitude": 1.4374, "longitude": 103.7865, "e-waste accepted": "Non-regulated products only; E.g. Small household appliances, gaming consoles, audio systems, power supplies"},
    {"name": "FAIRPRICE @ YEW TEE", "address": "21 CHOA CHU KANG NORTH 6, #01-26 689578", "latitude": 1.3973, "longitude": 103.7476, "e-waste accepted": "Non-regulated products only; E.g. Small household appliances, gaming consoles, audio systems, power supplies"},
    {"name": "GIANT @ IMM", "address": "2 JURONG EAST STREET 21, #03-01 609601", "latitude": 1.3356, "longitude": 103.7439, "e-waste accepted": "Non-regulated products only; E.g. Small household appliances, gaming consoles, audio systems, power supplies"},
    {"name": "GIANT @ PIONEER MALL", "address": "63 JURONG WEST CENTRAL 3, #03-01 648331", "latitude": 1.3401, "longitude": 103.7053, "e-waste accepted": "Non-regulated products only; E.g. Small household appliances, gaming consoles, audio systems, power supplies"},
    {"name": "GIANT @ TAMPINES", "address": "21 TAMPINES NORTH DRIVE 2 528765", "latitude": 1.3826, "longitude": 103.9435, "e-waste accepted": "Non-regulated products only; E.g. Small household appliances, gaming consoles, audio systems, power supplies"},
    {"name": "HARVEY NORMAN @ MILLENNIA WALK", "address": "9 RAFFLES BOULEVARD, #01-59/60 039596", "latitude": 1.2930, "longitude": 103.8572, "e-waste accepted": "Non-regulated products only; E.g. Small household appliances, gaming consoles, audio systems, power supplies"},
    {"name": "HARVEY NORMAN @ NORTHPOINT CITY", "address": "930 YISHUN AVENUE 2, #03-10 769098", "latitude": 1.4301, "longitude": 103.8356, "e-waste accepted": "Non-regulated products only; E.g. Small household appliances, gaming consoles, audio systems, power supplies"},
    {"name": "IKEA @ ALEXANDRA", "address": "317 ALEXANDRA ROAD 159965", "latitude": 1.2882, "longitude": 103.8055, "e-waste accepted": "Non-regulated products only; E.g. Small household appliances, gaming consoles, audio systems, power supplies"},
    {"name": "IKEA @ TAMPINES", "address": "60 TAMPINES NORTH DRIVE 2 528764", "latitude": 1.3724, "longitude": 103.9307, "e-waste accepted": "Non-regulated products only; E.g. Small household appliances, gaming consoles, audio systems, power supplies"},
    {"name": "POPULAR @ CAUSEWAY POINT", "address": "1 WOODLANDS SQUARE, #03-07 738099", "latitude": 1.4361, "longitude": 103.7866, "e-waste accepted": "Non-regulated products only; E.g. Small household appliances, gaming consoles, audio systems, power supplies"},
    {"name": "POPULAR @ CITY SQUARE MALL", "address": "180 KITCHENER ROAD, #03-17/18 208539", "latitude": 1.3113, "longitude": 103.8577, "e-waste accepted": "Non-regulated products only; E.g. Small household appliances, gaming consoles, audio systems, power supplies"},
    {"name": "POPULAR @ JEM", "address": "50 JURONG GATEWAY ROAD, #04-26 608549", "latitude": 1.3332, "longitude": 103.7439, "e-waste accepted": "Non-regulated products only; E.g. Small household appliances, gaming consoles, audio systems, power supplies"},
    {"name": "POPULAR @ NEX", "address": "23 SERANGOON CENTRAL, #04-40 556083", "latitude": 1.3517, "longitude": 103.8721, "e-waste accepted": "Non-regulated products only; E.g. Small household appliances, gaming consoles, audio systems, power supplies"},
    {"name": "POPULAR @ WATERWAY POINT", "address": "83 PUNGGOL CENTRAL, #B2-32 828761", "latitude": 1.4056, "longitude": 103.9019, "e-waste accepted": "Non-regulated products only; E.g. Small household appliances, gaming consoles, audio systems, power supplies"},
    {"name": "POPULAR @ BEDOK MALL", "address": "311 NEW UPPER CHANGI ROAD, #B2-01 467360", "latitude": 1.3257, "longitude": 103.9309, "e-waste accepted": "Non-regulated products only; E.g. Small household appliances, gaming consoles, audio systems, power supplies"},
    {"name": "SHENG SIONG @ BUKIT BATOK", "address": "7 BUKIT BATOK STREET 33, #01-20 659033", "latitude": 1.3554, "longitude": 103.7555, "e-waste accepted": "Non-regulated products only; E.g. Small household appliances, gaming consoles, audio systems, power supplies"},
    {"name": "SHENG SIONG @ CHIN SWEE", "address": "52 CHIN SWEE ROAD, #01-35 160052", "latitude": 1.2878, "longitude": 103.8405, "e-waste accepted": "Non-regulated products only; E.g. Small household appliances, gaming consoles, audio systems, power supplies"},
    {"name": "SHENG SIONG @ CLEMENTI", "address": "720 CLEMENTI WEST STREET 2, #01-144 120720", "latitude": 1.3025, "longitude": 103.7635, "e-waste accepted": "Non-regulated products only; E.g. Small household appliances, gaming consoles, audio systems, power supplies"},
    {"name": "SHENG SIONG @ GEYLANG", "address": "301 GEYLANG ROAD, #01-01 389338", "latitude": 1.3154, "longitude": 103.8888, "e-waste accepted": "Non-regulated products only; E.g. Small household appliances, gaming consoles, audio systems, power supplies"},
    {"name": "SHENG SIONG @ JURONG WEST", "address": "3 JURONG WEST AVENUE 1 649213", "latitude": 1.3532, "longitude": 103.7243, "e-waste accepted": "Non-regulated products only; E.g. Small household appliances, gaming consoles, audio systems, power supplies"},
    {"name": "SHENG SIONG @ LENGKONG TIGA", "address": "25A LENGKONG TIGA, #01-10 417443", "latitude": 1.3232, "longitude": 103.9128, "e-waste accepted": "Non-regulated products only; E.g. Small household appliances, gaming consoles, audio systems, power supplies"},
    {"name": "SHENG SIONG @ TECK WHYE", "address": "21 CHOA CHU KANG AVENUE 4, #B1-01 689812", "latitude": 1.3784, "longitude": 103.7456, "e-waste accepted": "Non-regulated products only; E.g. Small household appliances, gaming consoles, audio systems, power supplies"},
    {"name": "SHENG SIONG @ WOODLANDS", "address": "6A WOODLANDS CENTRE ROAD 731006", "latitude": 1.4381, "longitude": 103.7702, "e-waste accepted": "Non-regulated products only; E.g. Small household appliances, gaming consoles, audio systems, power supplies"},
    {"name": "SHENG SIONG @ YISHUN", "address": "301 YISHUN AVENUE 2, #01-01 760301", "latitude": 1.4315, "longitude": 103.8379, "e-waste accepted": "Non-regulated products only; E.g. Small household appliances, gaming consoles, audio systems, power supplies"},
    {"name": "TANGLIN MALL", "address": "163 TANGLIN ROAD, #B1-01 247933", "latitude": 1.3055, "longitude": 103.8221, "e-waste accepted": "Non-regulated products only; E.g. Small household appliances, gaming consoles, audio systems, power supplies"},
    {"name": "TAMPINES MALL", "address": "4 TAMPINES CENTRAL 5, #B1-01 529510", "latitude": 1.3532, "longitude": 103.9446, "e-waste accepted": "Non-regulated products only; E.g. Small household appliances, gaming consoles, audio systems, power supplies"},
    {"name": "TIONG BAHRU PLAZA", "address": "302 TIONG BAHRU ROAD, #02-101 168732", "latitude": 1.2869, "longitude": 103.8274, "e-waste accepted": "Non-regulated products only; E.g. Small household appliances, gaming consoles, audio systems, power supplies"},
    {"name": "WEST COAST PLAZA", "address": "154 WEST COAST ROAD, #02-01 127371", "latitude": 1.3041, "longitude": 103.7656, "e-waste accepted": "Non-regulated products only; E.g. Small household appliances, gaming consoles, audio systems, power supplies"},
    {"name": "WHAMPOA COMMUNITY CLUB", "address": "300 WHAMPOA DRIVE, LEVEL 1 327737", "latitude": 1.3265, "longitude": 103.8551, "e-waste accepted": "Non-regulated products only; E.g. Small household appliances, gaming consoles, audio systems, power supplies"},
    {"name": "YISHUN COMMUNITY HOSPITAL", "address": "2 YISHUN CENTRAL 1 768876", "latitude": 1.4244, "longitude": 103.8369, "e-waste accepted": "Non-regulated products only; E.g. Small household appliances, gaming consoles, audio systems, power supplies"},
    {"name": "ZALEA BEAUTY", "address": "9 RAFFLES BOULEVARD, #02-03/04 039596", "latitude": 1.2937, "longitude": 103.8578, "e-waste accepted": "Non-regulated products only; E.g. Small household appliances, gaming consoles, audio systems, power supplies"}
] + [
    {"name": "ADAM ROAD FOOD CENTRE", "address": "2 ADAM ROAD 289876", "latitude": 1.3248, "longitude": 103.8141, "e-waste accepted": "Non-regulated products only; E.g. Small household appliances, gaming consoles, audio systems, power supplies"},
    {"name": "ALJUNIED COMMUNITY CLUB", "address": "110 HOUGANG AVENUE 1 538884", "latitude": 1.3598, "longitude": 103.8867, "e-waste accepted": "Non-regulated products only; E.g. Small household appliances, gaming consoles, audio systems, power supplies"},
    {"name": "BEDOK COMMUNITY CENTRE", "address": "850 NEW UPPER CHANGI ROAD 467352", "latitude": 1.3268, "longitude": 103.9277, "e-waste accepted": "Non-regulated products only; E.g. Small household appliances, gaming consoles, audio systems, power supplies"},
    {"name": "BUKIT BATOK EAST COMMUNITY CENTRE", "address": "23 BUKIT BATOK EAST AVENUE 4 659841", "latitude": 1.3492, "longitude": 103.7536, "e-waste accepted": "Non-regulated products only; E.g. Small household appliances, gaming consoles, audio systems, power supplies"},
    {"name": "BUKIT GOMBAK COMMUNITY CLUB", "address": "81 BUKIT BATOK WEST AVENUE 3 659207", "latitude": 1.3565, "longitude": 103.7512, "e-waste accepted": "Non-regulated products only; E.g. Small household appliances, gaming consoles, audio systems, power supplies"},
    {"name": "CAIRNHILL COMMUNITY CLUB", "address": "1 ANTHONY ROAD 229944", "latitude": 1.3109, "longitude": 103.8396, "e-waste accepted": "Non-regulated products only; E.g. Small household appliances, gaming consoles, audio systems, power supplies"},
    {"name": "CHANGI COMMUNITY CLUB", "address": "4 CHANGI VILLAGE ROAD 509124", "latitude": 1.3906, "longitude": 103.9876, "e-waste accepted": "Non-regulated products only; E.g. Small household appliances, gaming consoles, audio systems, power supplies"},
    {"name": "CHONG BOON COMMUNITY CLUB", "address": "180 ANG MO KIO AVENUE 6 569830", "latitude": 1.3761, "longitude": 103.8492, "e-waste accepted": "Non-regulated products only; E.g. Small household appliances, gaming consoles, audio systems, power supplies"},
    {"name": "CI YUAN COMMUNITY CLUB", "address": "51 HOUGANG AVENUE 9 538776", "latitude": 1.3617, "longitude": 103.8863, "e-waste accepted": "Non-regulated products only; E.g. Small household appliances, gaming consoles, audio systems, power supplies"},
    {"name": "CLEMENTI COMMUNITY CLUB", "address": "220 CLEMENTI AVENUE 4 129880", "latitude": 1.3147, "longitude": 103.7657, "e-waste accepted": "Non-regulated products only; E.g. Small household appliances, gaming consoles, audio systems, power supplies"},
    {"name": "DARUL GHUFRAAN MOSQUE", "address": "503 TAMPINES AVENUE 5 529651", "latitude": 1.3541, "longitude": 103.9387, "e-waste accepted": "Non-regulated products only; E.g. Small household appliances, gaming consoles, audio systems, power supplies"},
    {"name": "DAWSON PLACE", "address": "57 DAWSON ROAD 142061", "latitude": 1.2958, "longitude": 103.8104, "e-waste accepted": "Non-regulated products only; E.g. Small household appliances, gaming consoles, audio systems, power supplies"},
    {"name": "EUNOS COMMUNITY CLUB", "address": "180 BEDOK RESERVOIR ROAD 479220", "latitude": 1.3333, "longitude": 103.9062, "e-waste accepted": "Non-regulated products only; E.g. Small household appliances, gaming consoles, audio systems, power supplies"},
    {"name": "FUCHUN COMMUNITY CLUB", "address": "1 WOODLANDS STREET 81 738526", "latitude": 1.4354, "longitude": 103.7908, "e-waste accepted": "Non-regulated products only; E.g. Small household appliances, gaming consoles, audio systems, power supplies"},
    {"name": "GEYLANG EAST COMMUNITY CLUB", "address": "45 GEYLANG EAST AVENUE 3 389716", "latitude": 1.3207, "longitude": 103.8845, "e-waste accepted": "Non-regulated products only; E.g. Small household appliances, gaming consoles, audio systems, power supplies"},
    {"name": "HOLLAND-BUKIT TIMAH COMMUNITY CLUB", "address": "170 GHIM MOH ROAD 279621", "latitude": 1.3124, "longitude": 103.7895, "e-waste accepted": "Non-regulated products only; E.g. Small household appliances, gaming consoles, audio systems, power supplies"},
    {"name": "HOUGANG COMMUNITY CLUB", "address": "35 HOUGANG AVENUE 3 538840", "latitude": 1.3650, "longitude": 103.8909, "e-waste accepted": "Non-regulated products only; E.g. Small household appliances, gaming consoles, audio systems, power supplies"},
    {"name": "JURONG GREEN COMMUNITY CLUB", "address": "6 JURONG WEST AVENUE 1 649295", "latitude": 1.3386, "longitude": 103.7219, "e-waste accepted": "Non-regulated products only; E.g. Small household appliances, gaming consoles, audio systems, power supplies"},
    {"name": "KEBUN BARU COMMUNITY CLUB", "address": "216 ANG MO KIO AVENUE 4 569897", "latitude": 1.3666, "longitude": 103.8345, "e-waste accepted": "Non-regulated products only; E.g. Small household appliances, gaming consoles, audio systems, power supplies"},
    {"name": "KEMBANGAN-CHAI CHEE COMMUNITY CLUB", "address": "200 BEDOK NORTH AVENUE 1 469752", "latitude": 1.3288, "longitude": 103.9306, "e-waste accepted": "Non-regulated products only; E.g. Small household appliances, gaming consoles, audio systems, power supplies"},
    {"name": "LENG KEE COMMUNITY CLUB", "address": "400 COMMONWEALTH AVENUE 149604", "latitude": 1.3002, "longitude": 103.7981, "e-waste accepted": "Non-regulated products only; E.g. Small household appliances, gaming consoles, audio systems, power supplies"},
    {"name": "MACPHERSON COMMUNITY CLUB", "address": "400 PAYA LEBAR WAY 379131", "latitude": 1.3298, "longitude": 103.8888, "e-waste accepted": "Non-regulated products only; E.g. Small household appliances, gaming consoles, audio systems, power supplies"},
    {"name": "MARSILING COMMUNITY CLUB", "address": "100A ADMIRALTY ROAD 759936", "latitude": 1.4325, "longitude": 103.7744, "e-waste accepted": "Non-regulated products only; E.g. Small household appliances, gaming consoles, audio systems, power supplies"},
    {"name": "NANYANG COMMUNITY CLUB", "address": "60 JURONG WEST STREET 91 649040", "latitude": 1.3387, "longitude": 103.7044, "e-waste accepted": "Non-regulated products only; E.g. Small household appliances, gaming consoles, audio systems, power supplies"},
    {"name": "PASIR RIS EAST COMMUNITY CLUB", "address": "1 PASIR RIS DRIVE 4 519457", "latitude": 1.3726, "longitude": 103.9444, "e-waste accepted": "Non-regulated products only; E.g. Small household appliances, gaming consoles, audio systems, power supplies"},
    {"name": "QUEENSTOWN COMMUNITY CLUB", "address": "365 COMMONWEALTH AVENUE 149732", "latitude": 1.3023, "longitude": 103.7984, "e-waste accepted": "Non-regulated products only; E.g. Small household appliances, gaming consoles, audio systems, power supplies"},
    {"name": "SERANGOON GARDENS COMMUNITY CLUB", "address": "2 MENG SUAN ROAD 779217", "latitude": 1.3618, "longitude": 103.8695, "e-waste accepted": "Non-regulated products only; E.g. Small household appliances, gaming consoles, audio systems, power supplies"},
    {"name": "TAMPINES EAST COMMUNITY CLUB", "address": "10 TAMPINES STREET 32 529287", "latitude": 1.3538, "longitude": 103.9472, "e-waste accepted": "Non-regulated products only; E.g. Small household appliances, gaming consoles, audio systems, power supplies"},
    {"name": "TANGLIN COMMUNITY CLUB", "address": "245 WHITLEY ROAD 297829", "latitude": 1.3243, "longitude": 103.8363, "e-waste accepted": "Non-regulated products only; E.g. Small household appliances, gaming consoles, audio systems, power supplies"},
    {"name": "TECK GHEE COMMUNITY CLUB", "address": "861 ANG MO KIO AVENUE 10 569733", "latitude": 1.3734, "longitude": 103.8565, "e-waste accepted": "Non-regulated products only; E.g. Small household appliances, gaming consoles, audio systems, power supplies"},
    {"name": "TELOK BLANGAH COMMUNITY CLUB", "address": "450 TELOK BLANGAH STREET 31 108943", "latitude": 1.2726, "longitude": 103.8135, "e-waste accepted": "Non-regulated products only; E.g. Small household appliances, gaming consoles, audio systems, power supplies"},
    {"name": "TOA PAYOH EAST COMMUNITY CLUB", "address": "7 LORONG 6 TOA PAYOH 319387", "latitude": 1.3326, "longitude": 103.8522, "e-waste accepted": "Non-regulated products only; E.g. Small household appliances, gaming consoles, audio systems, power supplies"},
    {"name": "TOA PAYOH WEST COMMUNITY CLUB", "address": "200 LORONG 2 TOA PAYOH 319642", "latitude": 1.3335, "longitude": 103.8499, "e-waste accepted": "Non-regulated products only; E.g. Small household appliances, gaming consoles, audio systems, power supplies"},
    {"name": "WHAMPOA COMMUNITY CENTRE", "address": "300 WHAMPOA DRIVE 327737", "latitude": 1.3263, "longitude": 103.8575, "e-waste accepted": "Non-regulated products only; E.g. Small household appliances, gaming consoles, audio systems, power supplies"},
    {"name": "WOODLANDS COMMUNITY CLUB", "address": "1 WOODLANDS STREET 81 738526", "latitude": 1.4378, "longitude": 103.7867, "e-waste accepted": "Non-regulated products only; E.g. Small household appliances, gaming consoles, audio systems, power supplies"},
    {"name": "YIO CHU KANG COMMUNITY CLUB", "address": "50 ANG MO KIO STREET 61 569163", "latitude": 1.3821, "longitude": 103.8449, "e-waste accepted": "Non-regulated products only; E.g. Small household appliances, gaming consoles, audio systems, power supplies"},
    {"name": "YUHUA COMMUNITY CLUB", "address": "90 BOON LAY WAY 609958", "latitude": 1.3340, "longitude": 103.7455, "e-waste accepted": "Non-regulated products only; E.g. Small household appliances, gaming consoles, audio systems, power supplies"},
    {"name": "ZHUJIAO CENTRE (TEKKA CENTRE)", "address": "665 BUFFALO ROAD 210665", "latitude": 1.3067, "longitude": 103.8512, "e-waste accepted": "Non-regulated products only; E.g. Small household appliances, gaming consoles, audio systems, power supplies"}
]

# Connect to SQLite database
conn = sqlite3.connect(DB_PATH)
cursor = conn.cursor()

# Loop through each entry in the dataset and insert into both tables
for entry in dataset:
    name = f"{entry['name']} E-waste Bin"
    address = entry["address"]
    latitude = entry["latitude"]
    longitude = entry["longitude"]
    opening_hours = "All time year round"
    recycle_category = "others"

    # Insert or replace in Locations table
    cursor.execute("""
        SELECT COUNT(*) FROM Locations WHERE Latitude = ? AND Longitude = ?
    """, (latitude, longitude))
    exists_location = cursor.fetchone()[0] > 0

    if exists_location:
        # Update existing entry
        cursor.execute("""
            UPDATE Locations
            SET Name = ?, "Opening Hours" = ?, Address = ?
            WHERE Latitude = ? AND Longitude = ?
        """, (name, opening_hours, address, latitude, longitude))
        print(f"Entry for {entry['name']} at ({latitude}, {longitude}) has been replaced in Locations.")
    else:
        # Insert new entry
        cursor.execute("""
            INSERT INTO Locations (Name, "Opening Hours", Address, Latitude, Longitude)
            VALUES (?, ?, ?, ?, ?)
        """, (name, opening_hours, address, latitude, longitude))
        print(f"Entry for {entry['name']} at ({latitude}, {longitude}) has been added to Locations.")

    # Insert or replace in RecycleCategory table
    cursor.execute("""
        SELECT COUNT(*) FROM RecycleCategory 
        WHERE Latitude = ? AND Longitude = ? AND RecycleItemCategory = ?
    """, (latitude, longitude, recycle_category))
    exists_recycle = cursor.fetchone()[0] > 0

    if exists_recycle:
        # Replace existing entry in RecycleCategory
        cursor.execute("""
            INSERT OR REPLACE INTO RecycleCategory (Latitude, Longitude, RecycleItemCategory)
            VALUES (?, ?, ?)
        """, (latitude, longitude, recycle_category))
        print(f"Entry for {entry['name']} at ({latitude}, {longitude}) has been replaced in RecycleCategory.")
    else:
        # Insert new entry in RecycleCategory
        cursor.execute("""
            INSERT INTO RecycleCategory (Latitude, Longitude, RecycleItemCategory)
            VALUES (?, ?, ?)
        """, (latitude, longitude, recycle_category))
        print(f"Entry for {entry['name']} at ({latitude}, {longitude}) has been added to RecycleCategory.")

# Commit and close database connection
conn.commit()
conn.close()

print("Data insertion and replacement operations are complete.")