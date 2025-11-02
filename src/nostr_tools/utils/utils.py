"""
Utility functions for Nostr protocol operations.

This module provides various utility functions for working with the Nostr
protocol, including URL parsing, cryptographic operations, data sanitization,
and encoding/decoding utilities.

The main categories of utilities include:

WebSocket Relay Discovery:
    - find_ws_urls: Extract and validate WebSocket URLs from text

Data Sanitization:
    - sanitize: Remove null bytes and clean data structures recursively

Cryptographic Operations:
    - calc_event_id: Calculate Nostr event IDs according to NIP-01
    - verify_sig: Verify Schnorr signatures for events
    - sig_event_id: Create Schnorr signatures for event IDs
    - generate_event: Create complete signed events with optional proof-of-work
    - validate_keypair: Validate private/public key pairs
    - generate_keypair: Generate new secp256k1 key pairs

Encoding Utilities:
    - to_bech32: Convert hex strings to Bech32 format (npub, nsec, etc.)
    - to_hex: Convert Bech32 strings back to hex format

Constants:
    - TLDS: List of valid top-level domains for URL validation
    - URI_GENERIC_REGEX: Comprehensive URI regex pattern following RFC 3986

All cryptographic functions use the secp256k1 elliptic curve and Schnorr
signatures as specified in the Nostr protocol. URL validation supports
both clearnet and Tor (.onion) domains.

Example:
    Basic usage of key utility functions:

    >>> # Generate a new key pair
    >>> private_key, public_key = generate_keypair()

    >>> # Create a signed event
    >>> event = generate_event(
    ...     private_key, public_key,
    ...     kind=1, tags=[], content="Hello Nostr!"
    ... )

    >>> # Verify the event signature
    >>> is_valid = verify_sig(event['id'], event['pubkey'], event['sig'])

    >>> # Convert keys to Bech32 format
    >>> npub = to_bech32('npub', public_key)
    >>> nsec = to_bech32('nsec', private_key)

    >>> # Find relay URLs in text
    >>> text = "Connect to wss://relay.damus.io"
    >>> relays = find_ws_urls(text)
"""

import hashlib
import json
import os
import re
import time
from typing import Any
from typing import Optional

import bech32
import secp256k1

# https://data.iana.org/TLD/tlds-alpha-by-domain.txt
TLDS = [
    "AAA",
    "AARP",
    "ABB",
    "ABBOTT",
    "ABBVIE",
    "ABC",
    "ABLE",
    "ABOGADO",
    "ABUDHABI",
    "AC",
    "ACADEMY",
    "ACCENTURE",
    "ACCOUNTANT",
    "ACCOUNTANTS",
    "ACO",
    "ACTOR",
    "AD",
    "ADS",
    "ADULT",
    "AE",
    "AEG",
    "AERO",
    "AETNA",
    "AF",
    "AFL",
    "AFRICA",
    "AG",
    "AGAKHAN",
    "AGENCY",
    "AI",
    "AIG",
    "AIRBUS",
    "AIRFORCE",
    "AIRTEL",
    "AKDN",
    "AL",
    "ALIBABA",
    "ALIPAY",
    "ALLFINANZ",
    "ALLSTATE",
    "ALLY",
    "ALSACE",
    "ALSTOM",
    "AM",
    "AMAZON",
    "AMERICANEXPRESS",
    "AMERICANFAMILY",
    "AMEX",
    "AMFAM",
    "AMICA",
    "AMSTERDAM",
    "ANALYTICS",
    "ANDROID",
    "ANQUAN",
    "ANZ",
    "AO",
    "AOL",
    "APARTMENTS",
    "APP",
    "APPLE",
    "AQ",
    "AQUARELLE",
    "AR",
    "ARAB",
    "ARAMCO",
    "ARCHI",
    "ARMY",
    "ARPA",
    "ART",
    "ARTE",
    "AS",
    "ASDA",
    "ASIA",
    "ASSOCIATES",
    "AT",
    "ATHLETA",
    "ATTORNEY",
    "AU",
    "AUCTION",
    "AUDI",
    "AUDIBLE",
    "AUDIO",
    "AUSPOST",
    "AUTHOR",
    "AUTO",
    "AUTOS",
    "AW",
    "AWS",
    "AX",
    "AXA",
    "AZ",
    "AZURE",
    "BA",
    "BABY",
    "BAIDU",
    "BANAMEX",
    "BAND",
    "BANK",
    "BAR",
    "BARCELONA",
    "BARCLAYCARD",
    "BARCLAYS",
    "BAREFOOT",
    "BARGAINS",
    "BASEBALL",
    "BASKETBALL",
    "BAUHAUS",
    "BAYERN",
    "BB",
    "BBC",
    "BBT",
    "BBVA",
    "BCG",
    "BCN",
    "BD",
    "BE",
    "BEATS",
    "BEAUTY",
    "BEER",
    "BERLIN",
    "BEST",
    "BESTBUY",
    "BET",
    "BF",
    "BG",
    "BH",
    "BHARTI",
    "BI",
    "BIBLE",
    "BID",
    "BIKE",
    "BING",
    "BINGO",
    "BIO",
    "BIZ",
    "BJ",
    "BLACK",
    "BLACKFRIDAY",
    "BLOCKBUSTER",
    "BLOG",
    "BLOOMBERG",
    "BLUE",
    "BM",
    "BMS",
    "BMW",
    "BN",
    "BNPPARIBAS",
    "BO",
    "BOATS",
    "BOEHRINGER",
    "BOFA",
    "BOM",
    "BOND",
    "BOO",
    "BOOK",
    "BOOKING",
    "BOSCH",
    "BOSTIK",
    "BOSTON",
    "BOT",
    "BOUTIQUE",
    "BOX",
    "BR",
    "BRADESCO",
    "BRIDGESTONE",
    "BROADWAY",
    "BROKER",
    "BROTHER",
    "BRUSSELS",
    "BS",
    "BT",
    "BUILD",
    "BUILDERS",
    "BUSINESS",
    "BUY",
    "BUZZ",
    "BV",
    "BW",
    "BY",
    "BZ",
    "BZH",
    "CA",
    "CAB",
    "CAFE",
    "CAL",
    "CALL",
    "CALVINKLEIN",
    "CAM",
    "CAMERA",
    "CAMP",
    "CANON",
    "CAPETOWN",
    "CAPITAL",
    "CAPITALONE",
    "CAR",
    "CARAVAN",
    "CARDS",
    "CARE",
    "CAREER",
    "CAREERS",
    "CARS",
    "CASA",
    "CASE",
    "CASH",
    "CASINO",
    "CAT",
    "CATERING",
    "CATHOLIC",
    "CBA",
    "CBN",
    "CBRE",
    "CC",
    "CD",
    "CENTER",
    "CEO",
    "CERN",
    "CF",
    "CFA",
    "CFD",
    "CG",
    "CH",
    "CHANNEL",
    "CHANNEL",
    "CHARITY",
    "CHASE",
    "CHAT",
    "CHEAP",
    "CHINTAI",
    "CHRISTMAS",
    "CHROME",
    "CHURCH",
    "CI",
    "CIPRIANI",
    "CIRCLE",
    "CISCO",
    "CITADEL",
    "CITI",
    "CITIC",
    "CITY",
    "CK",
    "CL",
    "CLAIMS",
    "CLEANING",
    "CLICK",
    "CLINIC",
    "CLINIQUE",
    "CLOTHING",
    "CLOUD",
    "CLUB",
    "CLUBMED",
    "CM",
    "CN",
    "CO",
    "COACH",
    "CODES",
    "COFFEE",
    "COLLEGE",
    "COLOGNE",
    "COM",
    "COMMBANK",
    "COMMUNITY",
    "COMPANY",
    "COMPARE",
    "COMPUTER",
    "COMSEC",
    "CONDOS",
    "CONSTRUCTION",
    "CONSULTING",
    "CONTACT",
    "CONTRACTORS",
    "COOKING",
    "COOL",
    "COOP",
    "CORSICA",
    "COUNTRY",
    "COUPON",
    "COUPONS",
    "COURSES",
    "CPA",
    "CR",
    "CREDIT",
    "CREDITCARD",
    "CREDITUNION",
    "CRICKET",
    "CROWN",
    "CRS",
    "CRUISE",
    "CRUISES",
    "CU",
    "CUISINELLA",
    "CV",
    "CW",
    "CX",
    "CY",
    "CYMRU",
    "CYOU",
    "CZ",
    "DAD",
    "DANCE",
    "DATA",
    "DATE",
    "DATING",
    "DATSUN",
    "DAY",
    "DCLK",
    "DDS",
    "DE",
    "DEAL",
    "DEALER",
    "DEALS",
    "DEGREE",
    "DELIVERY",
    "DELL",
    "DELOITTE",
    "DELTA",
    "DEMOCRAT",
    "DENTAL",
    "DENTIST",
    "DESI",
    "DESIGN",
    "DEV",
    "DHL",
    "DIAMONDS",
    "DIET",
    "DIGITAL",
    "DIRECT",
    "DIRECTORY",
    "DISCOUNT",
    "DISCOVER",
    "DISH",
    "DIY",
    "DJ",
    "DK",
    "DM",
    "DNP",
    "DO",
    "DOCS",
    "DOCTOR",
    "DOG",
    "DOMAINS",
    "DOT",
    "DOWNLOAD",
    "DRIVE",
    "DTV",
    "DUBAI",
    "DUNLOP",
    "DUPONT",
    "DURBAN",
    "DVAG",
    "DVR",
    "DZ",
    "EARTH",
    "EAT",
    "EC",
    "ECO",
    "EDEKA",
    "EDU",
    "EDUCATION",
    "EE",
    "EG",
    "EMAIL",
    "EMERCK",
    "ENERGY",
    "ENGINEER",
    "ENGINEERING",
    "ENTERPRISES",
    "EPSON",
    "EQUIPMENT",
    "ER",
    "ERICSSON",
    "ERNI",
    "ES",
    "ESQ",
    "ESTATE",
    "ET",
    "EU",
    "EUROVISION",
    "EUS",
    "EVENTS",
    "EXCHANGE",
    "EXPERT",
    "EXPOSED",
    "EXPRESS",
    "EXTRASPACE",
    "FAGE",
    "FAIL",
    "FAIRWINDS",
    "FAITH",
    "FAMILY",
    "FAN",
    "FANS",
    "FARM",
    "FARMERS",
    "FASHION",
    "FAST",
    "FEDEX",
    "FEEDBACK",
    "FERRARI",
    "FERRERO",
    "FI",
    "FIDELITY",
    "FIDO",
    "FILM",
    "FINAL",
    "FINANCE",
    "FINANCIAL",
    "FIRE",
    "FIRESTONE",
    "FIRMDALE",
    "FISH",
    "FISHING",
    "FIT",
    "FITNESS",
    "FJ",
    "FK",
    "FLICKR",
    "FLIGHTS",
    "FLIR",
    "FLORIST",
    "FLOWERS",
    "FLY",
    "FM",
    "FO",
    "FOO",
    "FOOD",
    "FOOTBALL",
    "FORD",
    "FOREX",
    "FORSALE",
    "FORUM",
    "FOUNDATION",
    "FOX",
    "FR",
    "FREE",
    "FRESENIUS",
    "FRL",
    "FROGANS",
    "FRONTIER",
    "FTR",
    "FUJITSU",
    "FUN",
    "FUND",
    "FURNITURE",
    "FUTBOL",
    "FYI",
    "GA",
    "GAL",
    "GALLERY",
    "GALLO",
    "GALLUP",
    "GAME",
    "GAMES",
    "GAP",
    "GARDEN",
    "GAY",
    "GB",
    "GBIZ",
    "GD",
    "GDN",
    "GE",
    "GEA",
    "GENT",
    "GENTING",
    "GEORGE",
    "GF",
    "GG",
    "GGEE",
    "GH",
    "GI",
    "GIFT",
    "GIFTS",
    "GIVES",
    "GIVING",
    "GL",
    "GLASS",
    "GLE",
    "GLOBAL",
    "GLOBO",
    "GM",
    "GMAIL",
    "GMBH",
    "GMO",
    "GMX",
    "GN",
    "GODADDY",
    "GOLD",
    "GOLDPOINT",
    "GOLF",
    "GOO",
    "GOODYEAR",
    "GOOG",
    "GOOGLE",
    "GOP",
    "GOT",
    "GOV",
    "GP",
    "GQ",
    "GR",
    "GRAINGER",
    "GRAPHICS",
    "GRATIS",
    "GREEN",
    "GRIPE",
    "GROCERY",
    "GROUP",
    "GS",
    "GT",
    "GU",
    "GUCCI",
    "GUGE",
    "GUIDE",
    "GUITARS",
    "GURU",
    "GW",
    "GY",
    "HAIR",
    "HAMBURG",
    "HANGOUT",
    "HAUS",
    "HBO",
    "HDFC",
    "HDFCBANK",
    "HEALTH",
    "HEALTHCARE",
    "HELP",
    "HELSINKI",
    "HERE",
    "HERMES",
    "HIPHOP",
    "HISAMITSU",
    "HITACHI",
    "HIV",
    "HK",
    "HKT",
    "HM",
    "HN",
    "HOCKEY",
    "HOLDINGS",
    "HOLIDAY",
    "HOMEDEPOT",
    "HOMEGOODS",
    "HOMES",
    "HOMESENSE",
    "HONDA",
    "HORSE",
    "HOSPITAL",
    "HOST",
    "HOSTING",
    "HOT",
    "HOTELS",
    "HOTMAIL",
    "HOUSE",
    "HOW",
    "HR",
    "HSBC",
    "HT",
    "HU",
    "HUGHES",
    "HYATT",
    "HYUNDAI",
    "IBM",
    "ICBC",
    "ICE",
    "ICU",
    "ID",
    "IE",
    "IEEE",
    "IFM",
    "IKANO",
    "IL",
    "IM",
    "IMAMAT",
    "IMDB",
    "IMMO",
    "IMMOBILE",
    "IN",
    "INC",
    "INDUSTRIES",
    "INFINITI",
    "INFO",
    "ING",
    "INK",
    "INSTITUTE",
    "INSURANCE",
    "INSURE",
    "INT",
    "INTERNATIONAL",
    "INTUIT",
    "INVESTMENTS",
    "IO",
    "IPIRANGA",
    "IQ",
    "IR",
    "IRISH",
    "IS",
    "ISMAILI",
    "IST",
    "ISTANBUL",
    "IT",
    "ITAU",
    "ITV",
    "JAGUAR",
    "JAVA",
    "JCB",
    "JE",
    "JEEP",
    "JETZT",
    "JEWELRY",
    "JIO",
    "JLL",
    "JM",
    "JMP",
    "JNJ",
    "JO",
    "JOBS",
    "JOBURG",
    "JOT",
    "JOY",
    "JP",
    "JPMORGAN",
    "JPRS",
    "JUEGOS",
    "JUNIPER",
    "KAUFEN",
    "KDDI",
    "KE",
    "KERRYHOTELS",
    "KERRYPROPERTIES",
    "KFH",
    "KG",
    "KH",
    "KI",
    "KIA",
    "KIDS",
    "KIM",
    "KINDLE",
    "KITCHEN",
    "KIWI",
    "KM",
    "KN",
    "KOELN",
    "KOMATSU",
    "KOSHER",
    "KP",
    "KPMG",
    "KPN",
    "KR",
    "KRD",
    "KRED",
    "KUOKGROUP",
    "KW",
    "KY",
    "KYOTO",
    "KZ",
    "LA",
    "LACAIXA",
    "LAMBORGHINI",
    "LAMER",
    "LAND",
    "LANDROVER",
    "LANXESS",
    "LASALLE",
    "LAT",
    "LATINO",
    "LATROBE",
    "LAW",
    "LAWYER",
    "LB",
    "LC",
    "LDS",
    "LEASE",
    "LECLERC",
    "LEFRAK",
    "LEGAL",
    "LEGO",
    "LEXUS",
    "LGBT",
    "LI",
    "LIDL",
    "LIFE",
    "LIFEINSURANCE",
    "LIFESTYLE",
    "LIGHTING",
    "LIKE",
    "LILLY",
    "LIMITED",
    "LIMO",
    "LINCOLN",
    "LINK",
    "LIVE",
    "LIVING",
    "LK",
    "LLC",
    "LLP",
    "LOAN",
    "LOANS",
    "LOCKER",
    "LOCUS",
    "LOL",
    "LONDON",
    "LOTTE",
    "LOTTO",
    "LOVE",
    "LPL",
    "LPLFINANCIAL",
    "LR",
    "LS",
    "LT",
    "LTD",
    "LTDA",
    "LU",
    "LUNDBECK",
    "LUXE",
    "LUXURY",
    "LV",
    "LY",
    "MA",
    "MADRID",
    "MAIF",
    "MAISON",
    "MAKEUP",
    "MAN",
    "MANAGEMENT",
    "MANGO",
    "MAP",
    "MARKET",
    "MARKETING",
    "MARKETS",
    "MARRIOTT",
    "MARSHALS",
    "MATTEL",
    "MBA",
    "MC",
    "MCKINSEY",
    "MD",
    "ME",
    "MED",
    "MEDIA",
    "MEET",
    "MELBOURNE",
    "MEME",
    "MEMORIAL",
    "MEN",
    "MENU",
    "MERCKMSD",
    "MG",
    "MH",
    "MIAMI",
    "MICROSOFT",
    "MIL",
    "MINI",
    "MINT",
    "MIT",
    "MITSUBISHI",
    "MK",
    "ML",
    "MLB",
    "MLS",
    "MM",
    "MMA",
    "MN",
    "MO",
    "MOBI",
    "MOBILE",
    "MODA",
    "MOE",
    "MOI",
    "MOM",
    "MONASH",
    "MONEY",
    "MONSTER",
    "MORMON",
    "MORTGAGE",
    "MOSCOW",
    "MOTO",
    "MOTORCYCLES",
    "MOV",
    "MOVIE",
    "MP",
    "MQ",
    "MR",
    "MS",
    "MSD",
    "MT",
    "MTN",
    "MTR",
    "MU",
    "MUSEUM",
    "MUSIC",
    "MV",
    "MW",
    "MX",
    "MY",
    "MZ",
    "NA",
    "NAB",
    "NAGOYA",
    "NAME",
    "NAVY",
    "NBA",
    "NC",
    "NE",
    "NEC",
    "NET",
    "NETBANK",
    "NETFLIX",
    "NETWORK",
    "NEUSTAR",
    "NEW",
    "NEWS",
    "NEXT",
    "NEXTDIRECT",
    "NEXUS",
    "NF",
    "NFL",
    "NG",
    "NGO",
    "NHK",
    "NI",
    "NICO",
    "NIKE",
    "NIKON",
    "NINJA",
    "NISSAN",
    "NISSAY",
    "NL",
    "NO",
    "NOKIA",
    "NORTON",
    "NOW",
    "NOWRUZ",
    "NOWTV",
    "NP",
    "NR",
    "NRA",
    "NRW",
    "NTT",
    "NU",
    "NYC",
    "NZ",
    "OBI",
    "OBSERVER",
    "OFFICE",
    "OKINAWA",
    "OLAYAN",
    "OLAYANGROUP",
    "OLLO",
    "OM",
    "OMEGA",
    "ONE",
    "ONG",
    "ONLY",
    "ONLINE",
    "OOO",
    "OPEN",
    "ORACLE",
    "ORANGE",
    "ORG",
    "ORGANIC",
    "ORIGINS",
    "OSAKA",
    "OTSUKA",
    "OTT",
    "OVH",
    "PA",
    "PAGE",
    "PANASONIC",
    "PARIS",
    "PARS",
    "PARTNERS",
    "PARTS",
    "PARTY",
    "PAY",
    "PCCW",
    "PE",
    "PET",
    "PF",
    "PFIZER",
    "PG",
    "PH",
    "PHARMACY",
    "PHD",
    "PHILIPS",
    "PHONE",
    "PHOTO",
    "PHOTOGRAPHY",
    "PHOTOS",
    "PHYSIO",
    "PICS",
    "PICTET",
    "PICTURES",
    "PID",
    "PIN",
    "PING",
    "PINK",
    "PIONEER",
    "PIZZA",
    "PK",
    "PL",
    "PLACE",
    "PLAY",
    "PLAYSTATION",
    "PLUMBING",
    "PLUS",
    "PM",
    "ON",
    "PNC",
    "POHL",
    "POKER",
    "POLITIE",
    "PORN",
    "POST",
    "PR",
    "PRAXI",
    "PRESS",
    "PRIME",
    "PRO",
    "PROD",
    "PRODUCTIONS",
    "PROF",
    "PROGRESSIVE",
    "PROMO",
    "PROPERTIES",
    "PROPERTY",
    "PROTECTION",
    "PRU",
    "PRUDENTIAL",
    "PS",
    "PT",
    "PUB",
    "PW",
    "PWC",
    "PY",
    "QA",
    "QPON",
    "QUEBEC",
    "QUEST",
    "RACING",
    "RADIO",
    "RE",
    "READ",
    "REALESTATE",
    "REALTOR",
    "REALTY",
    "RECIPES",
    "RED",
    "REDUMBRELLA",
    "REHAB",
    "REISE",
    "REISEN",
    "REIT",
    "RELIANCE",
    "REN",
    "RENT",
    "RENTALS",
    "REPAIR",
    "REPORT",
    "REPUBLICAN",
    "REST",
    "RESTAURANT",
    "REVIEW",
    "REVIEWS",
    "REXROTH",
    "RICH",
    "RICHARDLI",
    "RICOH",
    "RIL",
    "RIO",
    "RIP",
    "RO",
    "ROCKS",
    "RODEO",
    "ROGERS",
    "ROOM",
    "RS",
    "RSVP",
    "RU",
    "RUGBY",
    "RUHR",
    "RUN",
    "RW",
    "RWE",
    "RYUKYU",
    "SA",
    "SAARLAND",
    "SAFE",
    "SAFETY",
    "SAKURA",
    "SALE",
    "SALON",
    "SAMSCLUB",
    "SAMSUNG",
    "SANDVIK",
    "SANDVIKCOROMANT",
    "SANOFI",
    "SAP",
    "SARL",
    "SAS",
    "SAVE",
    "SAXO",
    "SB",
    "SBI",
    "SBS",
    "SC",
    "SCB",
    "SCHAEFFLER",
    "SCHMIDT",
    "SCHOLARSHIPS",
    "SCHOOL",
    "SCHULE",
    "SCHWARZ",
    "SCIENCE",
    "SCOT",
    "SD",
    "SE",
    "SEARCH",
    "SEAT",
    "SECURE",
    "SECURITY",
    "SEEK",
    "SELECT",
    "SENER",
    "SERVICES",
    "SEVEN",
    "SEW",
    "SEX",
    "SEXY",
    "SFR",
    "SG",
    "SH",
    "SHANGRILA",
    "SHARP",
    "SHELL",
    "SHIA",
    "SHIKSHA",
    "SHOES",
    "SHOP",
    "SHOPPING",
    "SHOUJI",
    "SHOW",
    "SI",
    "SILK",
    "SINA",
    "SINGLES",
    "SITE",
    "SJ",
    "SK",
    "SKI",
    "SKIN",
    "SKY",
    "SKYPE",
    "SL",
    "SLING",
    "SM",
    "SMART",
    "SMILE",
    "SN",
    "SNCF",
    "SO",
    "SOCCER",
    "SOCIAL",
    "SOFTBANK",
    "SOFTWARE",
    "SOHU",
    "SOLAR",
    "SOLUTIONS",
    "SONG",
    "SONY",
    "SOY",
    "SPA",
    "SPACE",
    "SPORT",
    "SPOT",
    "SR",
    "SRL",
    "SS",
    "ST",
    "STADA",
    "STAPLES",
    "STAR",
    "STATEBANK",
    "STATEFARM",
    "STC",
    "STCGROUP",
    "STOCKHOLM",
    "STORAGE",
    "STORE",
    "STREAM",
    "STUDIO",
    "STUDY",
    "STYLE",
    "SU",
    "SUCKS",
    "SUPPLIES",
    "SUPPLY",
    "SUPPORT",
    "SURF",
    "SURGERY",
    "SUZUKI",
    "SV",
    "SWATCH",
    "SWISS",
    "SX",
    "SY",
    "SYDNEY",
    "SYSTEMS",
    "SZ",
    "TAB",
    "TAIPEI",
    "TALK",
    "TAOBAO",
    "TARGET",
    "TATAMOTORS",
    "TATAR",
    "TATTOO",
    "TAX",
    "TAXI",
    "TC",
    "TCI",
    "TD",
    "TDK",
    "TEAM",
    "TECH",
    "TECHNOLOGY",
    "TEL",
    "TEMASEK",
    "TENNIS",
    "TEVA",
    "TF",
    "TG",
    "TH",
    "THD",
    "THEATER",
    "THEATRE",
    "TIAA",
    "TICKETS",
    "TIENDA",
    "TIPS",
    "TIRES",
    "TIROL",
    "TJ",
    "TJMAXX",
    "TJX",
    "TK",
    "TKMAXX",
    "TL",
    "TM",
    "TMALL",
    "TN",
    "TO",
    "TODAY",
    "TOKYO",
    "TOOLS",
    "TOP",
    "TORAY",
    "TOSHIBA",
    "TOTAL",
    "TOURS",
    "TOWN",
    "TOYOTA",
    "TOYS",
    "TR",
    "TRADE",
    "TRADING",
    "TRAINING",
    "TRAVEL",
    "TRAVELERS",
    "TRAVELERSINSURANCE",
    "TRUST",
    "TRV",
    "TT",
    "TUBE",
    "TUI",
    "TUNES",
    "TUSHU",
    "TV",
    "TVS",
    "TW",
    "TZ",
    "UA",
    "UBANK",
    "UBS",
    "UG",
    "UK",
    "UNICOM",
    "UNIVERSITY",
    "UNO",
    "UOL",
    "UPS",
    "US",
    "UY",
    "UZ",
    "VA",
    "VACATIONS",
    "VANA",
    "VANGUARD",
    "VC",
    "VE",
    "VEGAS",
    "VENTURES",
    "VERISIGN",
    "VERSICHERUNG",
    "VET",
    "VG",
    "VI",
    "VIAJES",
    "VIDEO",
    "VIG",
    "VIKING",
    "VILLAS",
    "VIN",
    "VIP",
    "VIRGIN",
    "VISA",
    "VISION",
    "VIVA",
    "VIVO",
    "VLAANDEREN",
    "VN",
    "VODKA",
    "VOLVO",
    "VOTE",
    "VOTING",
    "VOTO",
    "VOYAGE",
    "VU",
    "WALES",
    "WALMART",
    "WALTER",
    "WANG",
    "WANGGOU",
    "WATCH",
    "WATCHES",
    "WEATHER",
    "WEATHERCHANNEL",
    "WEBCAM",
    "WEBER",
    "WEBSITE",
    "WED",
    "WEDDING",
    "WEIBO",
    "WEIR",
    "WF",
    "WHOSWHO",
    "WIEN",
    "WIKI",
    "WILLIAMHILL",
    "WIN",
    "WINDOWS",
    "WINE",
    "WINNERS",
    "WME",
    "WOLTERSKLUWER",
    "WOODSIDE",
    "WORK",
    "WORKS",
    "WORLD",
    "WOW",
    "WS",
    "WTC",
    "WTF",
    "XBOX",
    "XEROX",
    "XIHUAN",
    "XIN",
    "XN--11B4C3D",
    "XN--1CK2E1B",
    "XN--1QQW23A",
    "XN--2SCRJ9C",
    "XN--30RR7Y",
    "XN--3BST00M",
    "XN--3DS443G",
    "XN--3E0B707E",
    "XN--3HCRJ9C",
    "XN--3PXU8K",
    "XN--42C2D9A",
    "XN--45BR5CYL",
    "XN--45BRJ9C",
    "XN--45Q11C",
    "XN--4DBRK0CE",
    "XN--4GBRIM",
    "XN--54B7FTA0CC",
    "XN--55QW42G",
    "XN--55QX5D",
    "XN--5SU34J936BGSG",
    "XN--5TZM5G",
    "XN--6FRZ82G",
    "XN--6QQ986B3XL",
    "XN--80ADXHKS",
    "XN--80AO21A",
    "XN--80AQECDR1A",
    "XN--80ASEHDB",
    "XN--80ASWG",
    "XN--8Y0A063A",
    "XN--90A3AC",
    "XN--90AE",
    "XN--90AIS",
    "XN--9DBQ2A",
    "XN--9ET52U",
    "XN--9KRT00A",
    "XN--B4W605FERD",
    "XN--BACK1B9A5DRE4C",
    "XN--C1AVG",
    "XN--C2BR7G",
    "XN--CCK2B3B",
    "XN--CCKWCXETD",
    "XN--CG4BKI",
    "XN--CLCHC0EA0B2G2A9GCD",
    "XN--CZR694B",
    "XN--CZRS0T",
    "XN--CZRU2D",
    "XN--D1ACJ3B",
    "XN--D1ALF",
    "XN--E1A4C",
    "XN--ECKVDTC9D",
    "XN--EFVY88H",
    "XN--FCT429K",
    "XN--FHBEI",
    "XN--FIQ228C5HS",
    "XN--FIQ64B",
    "XN--FIQS8S",
    "XN--FIQZ9S",
    "XN--FJQ720A",
    "XN--FLW351E",
    "XN--FPCRJ9C3D",
    "XN--FZC2C9E2C",
    "XN--FZYS8D69UVGM",
    "XN--G2XX48C",
    "XN--GCKR3F0F",
    "XN--GECRJ9C",
    "XN--GK3AT1E",
    "XN--H2BREG3EVE",
    "XN--H2BRJ9C",
    "XN--H2BRJ9C8C",
    "XN--HXT814E",
    "XN--I1B6B1A6A2E",
    "XN--IMR513N",
    "XN--IO0A7I",
    "XN--J1AEF",
    "XN--J1AMH",
    "XN--J6W193G",
    "XN--JLQ480N2RG",
    "XN--JVR189M",
    "XN--KCRX77D1X4A",
    "XN--KPRW13D",
    "XN--KPRY57D",
    "XN--KPUT3I",
    "XN--L1ACC",
    "XN--LGBBAT1AD8J",
    "XN--MGB9AWBF",
    "XN--MGBA3A3EJT",
    "XN--MGBA3A4F16A",
    "XN--MGBA7C0BBN0A",
    "XN--MGBAAM7A8H",
    "XN--MGBAB2BD",
    "XN--MGBAH1A3HJKRD",
    "XN--MGBAI9AZGQP6J",
    "XN--MGBAYH7GPA",
    "XN--MGBBH1A",
    "XN--MGBBH1A71E",
    "XN--MGBC0A9AZCG",
    "XN--MGBCA7DZDO",
    "XN--MGBCPQ6GPA1A",
    "XN--MGBERP4A5D4AR",
    "XN--MGBGU82A",
    "XN--MGBI4ECEXP",
    "XN--MGBPL2FH",
    "XN--MGBT3DHD",
    "XN--MGBTX2B",
    "XN--MGBX4CD0AB",
    "XN--MIX891F",
    "XN--MK1BU44C",
    "XN--MXTQ1M",
    "XN--NGBC5AZD",
    "XN--NGBE9E0A",
    "XN--NGBRX",
    "XN--NODE",
    "XN--NQV7F",
    "XN--NQV7FS00EMA",
    "XN--NYQY26A",
    "XN--O3CW4H",
    "XN--OGBPF8FL",
    "XN--OUT796D",
    "XN--P1ACF",
    "XN--P1AI",
    "XN--PGBS0DH",
    "XN--PSSY2U",
    "XN--Q7CE6A",
    "XN--Q9JYB4C",
    "XN--QCKA1PMC",
    "XN--QXA6A",
    "XN--QXAM",
    "XN--RHQV96G",
    "XN--ROVU88B",
    "XN--RVC1E0AM3E",
    "XN--S9BRJ9C",
    "XN--SES554G",
    "XN--T60B56A",
    "XN--TCKWE",
    "XN--TIQ49XQYJ",
    "XN--UNUP4Y",
    "XN--VERMGENSBERATER-CTB",
    "XN--VERMGENSBERATUNG-PWB",
    "XN--VHQUV",
    "XN--VUQ861B",
    "XN--W4R85EL8FHU5DNRA",
    "XN--W4RS40L",
    "XN--WGBH1C",
    "XN--WGBL6A",
    "XN--XHQ521B",
    "XN--XKC2AL3HYE2A",
    "XN--XKC2DL3A5EE0H",
    "XN--Y9A3AQ",
    "XN--YFRO4I67O",
    "XN--YGBI2AMMX",
    "XN--ZFR164B",
    "XXX",
    "XYZ",
    "YACHTS",
    "YAHOO",
    "YAMAXUN",
    "YANDEX",
    "YE",
    "YODOBASHI",
    "YOGA",
    "YOKOHAMA",
    "YOU",
    "YOUTUBE",
    "YT",
    "YUN",
    "ZA",
    "ZAPPOS",
    "ZARA",
    "ZERO",
    "ZIP",
    "ZM",
    "ZONE",
    "ZUERICH",
    "ZW",
]


# https://www.rfc-editor.org/rfc/rfc3986
# URI = scheme ":" hier-part [ "?" query ] [ "#" fragment ]
# scheme      = ALPHA *( ALPHA / DIGIT / "+" / "-" / "." )
# hier-part   = "//" authority path-abempty
#               / path-absolute
#               / path-rootless / path-empty
# authority   = [ userinfo "@" ] host [ ":" port ]
# userinfo    = *( unreserved / pct-encoded / sub-delims / ":" )
# host        = IP-literal / IPv4address / reg-name
# port        = *DIGIT
# path-abempty = *( "/" segment )

# scheme:    https
# hier-part: //user:pass@www.example.com:443/path/to/resource
# authority: user:pass@www.example.com:443
#     userinfo: user:pass
#     host: www.example.com
#     port: 443
# path: /path/to/resource
# query: query=value
# fragment: fragment
URI_GENERIC_REGEX = r"""
    # ==== Scheme ====
    (?P<scheme>[a-zA-Z][a-zA-Z0-9+\-.]*):       # Group 1 for the scheme:
                                               # - Starts with a letter
                                               # - Followed by letters, digits, '+', '-', or '.'
                                               # - Ends with a colon ':'

    \/\/                                       # Double forward slashes '//' separating scheme and authority

    # ==== Optional User Info ====
    (?P<userinfo>                              # Group 2 for optional userinfo group
        [A-Za-z0-9\-\._~!$&'()*+,;=:%]*@       # Userinfo (username[:password]) part, ending with '@'
                                               # - Includes unreserved, sub-delims, ':' and '%'
    )?                                         # Entire userinfo is optional

    # ==== Host (IPv6, IPv4, or Domain) ====
    (?P<host>                                  # Group 3 for host group
        # --- IPv6 Address ---
        \[                                     # Opening square bracket
            (?P<ipv6>([0-9a-fA-F]{1,4}:){7}     # Group 4 for IPv6 address part
                ([0-9a-fA-F]{1,4}))             # Final 1-4 hex digits (total 8 groups)
        \]                                     # Closing square bracket

        |                                      # OR

        # --- IPv4 Address ---
        (?P<ipv4>(\d{1,3}\.){3}                 # Group 5 for IPv4 address part
            \d{1,3})                            # Final group of 1 to 3 digits (e.g., 192.168.0.1)

        |                                      # OR

        # --- Registered Domain Name ---
        (?P<domain>                             # Group 6 for domain part
            (?:                                 # Non-capturing group for domain labels:
                [a-zA-Z0-9]                     # Label must start with a letter or digit
                (?:[a-zA-Z0-9-]{0,61}           # Label can contain letters, digits, and hyphens
                [a-zA-Z0-9])?                   # Label must end with a letter or digit
                \.                              # Dot separating labels
            )+                                    # Repeat for each subdomain
            [a-zA-Z]{2,}                         # TLD must be at least 2 alphabetic characters
        )                                        # End of domain group

        # |                                       # OR

        # (?P<localhost>localhost)                 # Group 7 Special case for 'localhost'
    )                                          # End of host group

    # ==== Optional Port ====
    (?P<port>:\d+)?                             # Group 8 for optional port number prefixed by a colon (e.g., :80)

    # ==== Path ====
    (?P<path>                                  # Group 9 for the path group
        /?                                      # Optional leading slash
        (?:                                     # Non-capturing group for path segments
            [a-zA-Z0-9\-_~!$&'()*+,;=:%]+       # Path segments (e.g., '/files', '/images', etc.)
            (?:/[a-zA-Z0-9\-_~!$&'()*+,;=:%]+)* # Optional repeated path segments
            (?:\.[a-zA-Z0-9\-]+)*                # Allow a file extension (e.g., '.txt', '.jpg', '.html')
        )?
    )                                          # End of path group

    # ==== Optional Query ====
    (?P<query>\?                                 # Group 10 for query starts with '?'
        [a-zA-Z0-9\-_~!$&'()*+,;=:%/?]*         # Query parameters (key=value pairs or just data)
    )?                                         # Entire query is optional

    # ==== Optional Fragment ====
    (?P<fragment>\#                             # Group 11 for fragment starts with '#'
        [a-zA-Z0-9\-_~!$&'()*+,;=:%/?]*         # Fragment identifier (can include same characters as query)
    )?                                         # Entire fragment is optional
"""


def find_ws_urls(text: str) -> list[str]:
    """
    Find and validate all WebSocket URLs in the given text.

    This function searches for valid WebSocket URLs (ws:// or wss://) in text,
    validates them according to RFC 3986 URI standards, and returns normalized
    URLs. It supports both clearnet domains and Tor .onion hidden services.
    All URLs are normalized to use the wss:// (secure WebSocket) scheme.

    Validation includes:
    - WebSocket scheme (ws:// or wss://)
    - Valid domain name or IP address
    - Valid port range (0-65535) if specified
    - Proper .onion address format for Tor (16 or 56 char base32)
    - Valid TLD for clearnet domains

    Args:
        text (str): The text to search for WebSocket relay URLs.
            Can contain multiple URLs mixed with other text.

    Returns:
        list[str]: List of valid WebSocket URLs found in the text.
            All URLs are normalized to use wss:// scheme and lowercase domains.
            Returns empty list if no valid URLs found.

    Examples:
        Extract relay URLs from text:

        >>> text = "Connect to wss://relay.damus.io or ws://relay.nostr.band"
        >>> urls = find_ws_urls(text)
        >>> print(urls)
        ['wss://relay.damus.io', 'wss://relay.nostr.band']

        Normalize URLs to wss:

        >>> text = "Use ws://relay.example.com:8080"
        >>> urls = find_ws_urls(text)
        >>> print(urls)
        ['wss://relay.example.com:8080']

        Extract Tor relay:

        >>> text = "Tor relay: wss://somevalidonionaddress.onion"
        >>> urls = find_ws_urls(text)

        Filter invalid URLs:

        >>> text = "wss://relay.damus.io https://example.com ws://invalid..domain"
        >>> urls = find_ws_urls(text)
        >>> print(urls)
        ['wss://relay.damus.io']  # Only WebSocket URLs with valid format

        Parse relay configuration:

        >>> config_text = '''
        ... Primary: wss://relay.damus.io
        ... Backup: wss://nostr.wine
        ... '''
        >>> relays = find_ws_urls(config_text)
        >>> for url in relays:
        ...     relay = Relay(url)
    """
    result = []
    matches = re.finditer(URI_GENERIC_REGEX, text, re.VERBOSE)

    for match in matches:
        scheme = match.group("scheme")
        host = match.group("host")
        port = match.group("port")
        port = int(port[1:]) if port else None
        path = match.group("path")
        path = "" if path in ["", "/", None] else "/" + path.strip("/")
        domain = match.group("domain")

        # Only process WebSocket schemes
        if scheme not in ["ws", "wss"]:
            continue

        # Validate port range (0-65535)
        if port and (port < 0 or port > 65535):
            continue

        # Validate .onion domains for Tor relays
        if (
            domain
            and domain.lower().endswith(".onion")
            and not re.match(r"^([a-z2-7]{16}|[a-z2-7]{56})\.onion$", domain.lower())
        ):
            continue

        # Validate TLD for clearnet domains
        if domain and (domain.split(".")[-1].upper() not in [*TLDS, "ONION"]):
            continue

        # Construct final URL (normalize to wss://)
        port_str = ":" + str(port) if port else ""
        url = "wss://" + host.lower() + port_str + path
        result.append(url)

    return result


def sanitize(value: Any) -> Any:
    r"""
    Sanitize values by removing null bytes and recursively cleaning data structures.

    This function removes null bytes (\x00) from strings and recursively processes
    lists and dictionaries to ensure all contained data is sanitized. Null bytes
    can cause issues with event validation and relay communication.

    The function handles:
    - Strings: Removes \x00 null bytes
    - Lists: Recursively sanitizes all elements
    - Dictionaries: Recursively sanitizes both keys and values
    - Other types: Returns unchanged

    Args:
        value (Any): Value to sanitize. Can be str, list, dict, or any other type.

    Returns:
        Any: Sanitized value with null bytes removed from all strings.
            Type is preserved (str returns str, list returns list, etc.).

    Examples:
        Sanitize a string:

        >>> text = "Hello\x00World"
        >>> clean = sanitize(text)
        >>> print(clean)
        HelloWorld

        Sanitize nested structures:

        >>> data = {
        ...     "content": "Test\x00message",
        ...     "tags": [["e", "id\x00123"], ["p", "abc"]]
        ... }
        >>> clean_data = sanitize(data)
        >>> print(clean_data)
        {'content': 'Testmessage', 'tags': [['e', 'id123'], ['p', 'abc']]}

        Use with event data:

        >>> event_dict = {
        ...     "content": user_input,  # May contain null bytes
        ...     "tags": user_tags
        ... }
        >>> sanitized = sanitize(event_dict)
        >>> event = Event.from_dict(sanitized)  # Now safe to validate
    """
    if isinstance(value, str):
        return value.replace("\x00", "")
    elif isinstance(value, list):
        return [sanitize(item) for item in value]
    elif isinstance(value, dict):
        return {sanitize(key): sanitize(val) for key, val in value.items()}
    else:
        return value


def calc_event_id(
    pubkey: str, created_at: int, kind: int, tags: list[list[str]], content: str
) -> str:
    """
    Calculate the event ID for a Nostr event according to NIP-01 specification.

    The event ID is calculated as the SHA-256 hash of the UTF-8 encoded JSON
    serialization of the event data array: [0, pubkey, created_at, kind, tags, content].
    The JSON is serialized with minimal formatting (no spaces, compact separators).

    Args:
        pubkey (str): Public key in lowercase hex format (64 characters).
        created_at (int): Unix timestamp (seconds since epoch) of event creation.
        kind (int): Event kind number (0-65535).
        tags (list[list[str]]): List of event tags. Each tag is a list of strings.
        content (str): Event content as a string.

    Returns:
        str: Event ID as lowercase hexadecimal string (64 characters).
            This is the SHA-256 hash of the serialized event data.

    Examples:
        Calculate event ID:

        >>> pubkey = "abc123..." # 64-char hex
        >>> created_at = 1234567890
        >>> kind = 1
        >>> tags = [["p", "def456..."], ["e", "789abc..."]]
        >>> content = "Hello Nostr!"
        >>> event_id = calc_event_id(pubkey, created_at, kind, tags, content)
        >>> len(event_id)
        64

        Use in event creation:

        >>> event_id = calc_event_id(
        ...     public_key, timestamp, kind, tags, content
        ... )
        >>> signature = sig_event_id(event_id, private_key)
        >>> event = {
        ...     "id": event_id,
        ...     "pubkey": public_key,
        ...     "created_at": timestamp,
        ...     "kind": kind,
        ...     "tags": tags,
        ...     "content": content,
        ...     "sig": signature
        ... }

        Verify event ID matches:

        >>> recalculated_id = calc_event_id(
        ...     event['pubkey'], event['created_at'],
        ...     event['kind'], event['tags'], event['content']
        ... )
        >>> assert recalculated_id == event['id']
    """
    event_data = [0, pubkey, created_at, kind, tags, content]
    event_json = json.dumps(event_data, separators=(",", ":"), ensure_ascii=False)
    event_bytes = event_json.encode("utf-8")
    event_hash = hashlib.sha256(event_bytes).digest()
    return event_hash.hex()


def verify_sig(event_id: str, pubkey: str, signature: str) -> bool:
    """
    Verify an event signature using Schnorr verification (secp256k1).

    This function verifies that the given Schnorr signature was created by the
    private key corresponding to the public key for the given event ID. Uses
    the secp256k1 elliptic curve as specified in the Nostr protocol.

    Args:
        event_id (str): Event ID in hexadecimal format (64 characters).
            This is the SHA-256 hash of the serialized event.
        pubkey (str): Public key in hexadecimal format (64 characters).
            This is the x-only public key (Schnorr format).
        signature (str): Schnorr signature in hexadecimal format (128 characters).

    Returns:
        bool: True if signature is valid and matches the event ID and public key.
            False if signature is invalid, or if there's any error during verification.

    Examples:
        Verify event signature:

        >>> event_id = "abc123..."  # 64-char hex
        >>> pubkey = "def456..."    # 64-char hex
        >>> signature = "789ghi..."  # 128-char hex
        >>> is_valid = verify_sig(event_id, pubkey, signature)
        >>> if is_valid:
        ...     print("Signature is valid!")

        Validate event from relay:

        >>> event_dict = {
        ...     "id": "...",
        ...     "pubkey": "...",
        ...     "sig": "...",
        ...     # ... other fields
        ... }
        >>> if verify_sig(event_dict['id'], event_dict['pubkey'], event_dict['sig']):
        ...     event = Event.from_dict(event_dict)

        Handle invalid signatures:

        >>> if not verify_sig(event_id, pubkey, signature):
        ...     print("Invalid signature - event may be forged")
        ...     return None
    """
    try:
        pub_key = secp256k1.PublicKey(bytes.fromhex("02" + pubkey), True)
        result = pub_key.schnorr_verify(
            bytes.fromhex(event_id), bytes.fromhex(signature), None, raw=True
        )
        return bool(result)
    except (ValueError, TypeError):
        return False


def sig_event_id(event_id: str, private_key: str) -> str:
    """
    Sign an event ID with a private key using Schnorr signatures (secp256k1).

    This function creates a Schnorr signature of the event ID using the provided
    private key. The signature can be verified using verify_sig() with the
    corresponding public key.

    Args:
        event_id (str): Event ID in hexadecimal format (64 characters).
            This is the SHA-256 hash of the serialized event.
        private_key (str): Private key in hexadecimal format (64 characters).
            Must be a valid secp256k1 private key.

    Returns:
        str: Schnorr signature as hexadecimal string (128 characters).

    Examples:
        Sign an event:

        >>> event_id = calc_event_id(pubkey, timestamp, kind, tags, content)
        >>> signature = sig_event_id(event_id, private_key)
        >>> len(signature)
        128

        Create complete signed event:

        >>> event_id = calc_event_id(public_key, timestamp, kind, tags, content)
        >>> signature = sig_event_id(event_id, private_key)
        >>> event = {
        ...     "id": event_id,
        ...     "pubkey": public_key,
        ...     "created_at": timestamp,
        ...     "kind": kind,
        ...     "tags": tags,
        ...     "content": content,
        ...     "sig": signature
        ... }

        Verify your own signature:

        >>> sig = sig_event_id(event_id, private_key)
        >>> assert verify_sig(event_id, public_key, sig)
    """
    priv_key = secp256k1.PrivateKey(bytes.fromhex(private_key), raw=True)
    signature = priv_key.schnorr_sign(bytes.fromhex(event_id), bip340tag=None, raw=True)
    return str(signature.hex())


def generate_event(
    private_key: str,
    public_key: str,
    kind: int,
    tags: list[list[str]],
    content: str,
    created_at: Optional[int] = None,
    target_difficulty: Optional[int] = None,
    timeout: int = 20,
) -> dict[str, Any]:
    """
    Generate a signed Nostr event with optional proof-of-work.

    This function creates a complete Nostr event with proper ID calculation,
    signature generation, and optional proof-of-work nonce mining.

    Args:
        private_key (str): Private key in hex format (64 characters)
        public_key (str): Public key in hex format (64 characters)
        kind (int): Event kind (0-65535)
        tags (List[List[str]]): List of event tags
        content (str): Event content
        created_at (Optional[int]): Unix timestamp (defaults to current time)
        target_difficulty (Optional[int]): Proof of work difficulty target (leading zero bits)
        timeout (int): Timeout for proof of work mining in seconds (default: 20)

    Returns:
        Dict[str, Any]: Complete signed event dictionary with keys:
                       id, pubkey, created_at, kind, tags, content, sig
    """

    def count_leading_zero_bits(hex_str: str) -> int:
        """
        Count leading zero bits in a hex string for proof-of-work validation.

        This internal function calculates the difficulty of a proof-of-work hash
        by counting consecutive zero bits from the start of the hex string. Used
        to verify that an event ID meets the required proof-of-work difficulty.

        Args:
            hex_str (str): Hexadecimal string to analyze (typically event ID).

        Returns:
            int: Number of consecutive zero bits from the start of the string.

        Examples:
            >>> count_leading_zero_bits("0000abc")  # 16 zero bits
            16
            >>> count_leading_zero_bits("00001abc")  # 19 zero bits (0000 = 16, 1xxx = 3)
            19
            >>> count_leading_zero_bits("1abc")  # 0 zero bits
            0
        """
        bits = 0
        for char in hex_str:
            val = int(char, 16)
            if val == 0:
                bits += 4
            else:
                bits += 4 - val.bit_length()
                break
        return bits

    original_tags = tags.copy()
    created_at = created_at if created_at is not None else int(time.time())

    if target_difficulty is None:
        # No proof of work required
        tags = original_tags
        event_id = calc_event_id(public_key, created_at, kind, tags, content)
    else:
        # Mine proof of work
        nonce = 0
        non_nonce_tags = [tag for tag in original_tags if tag[0] != "nonce"]
        start_time = time.time()

        while True:
            tags = [*non_nonce_tags, ["nonce", str(nonce), str(target_difficulty)]]
            event_id = calc_event_id(public_key, created_at, kind, tags, content)
            difficulty = count_leading_zero_bits(event_id)

            if difficulty >= target_difficulty:
                break
            if (time.time() - start_time) >= timeout:
                # Timeout reached, use original tags without nonce
                tags = original_tags
                event_id = calc_event_id(public_key, created_at, kind, tags, content)
                break
            nonce += 1

    # Sign the event
    sig = sig_event_id(event_id, private_key)

    return {
        "id": event_id,
        "pubkey": public_key,
        "created_at": created_at,
        "kind": kind,
        "tags": tags,
        "content": content,
        "sig": sig,
    }


def validate_keypair(private_key: str, public_key: str) -> bool:
    """
    Test if a private/public key pair is valid and matches.

    This function verifies that the given private key generates the
    corresponding public key using secp256k1 elliptic curve cryptography.

    Args:
        private_key (str): Private key in hex format (64 characters)
        public_key (str): Public key in hex format (64 characters)

    Returns:
        bool: True if the key pair is valid and matches, False otherwise
    """
    if len(private_key) != 64 or len(public_key) != 64:
        return False

    try:
        private_key_bytes = bytes.fromhex(private_key)
        private_key_obj = secp256k1.PrivateKey(private_key_bytes)
        generated_public_key = private_key_obj.pubkey.serialize(compressed=True)[1:].hex()
        return bool(generated_public_key == public_key)
    except Exception:
        return False


def to_bech32(prefix: str, hex_str: str) -> str:
    """
    Convert a hexadecimal string to Bech32 encoded format.

    This function converts hexadecimal data to Bech32 encoding with the
    specified prefix. Bech32 is commonly used for Nostr keys and identifiers
    as it provides better error detection and is more user-friendly than raw hex.

    Common Nostr prefixes:
    - 'npub': Public key (nostr public key)
    - 'nsec': Private key (nostr secret key)
    - 'note': Event ID
    - 'nprofile': Profile identifier
    - 'nevent': Event identifier

    Args:
        prefix (str): The Bech32 prefix to use (e.g., 'nsec', 'npub', 'note').
        hex_str (str): The hexadecimal string to convert (typically 64 characters).

    Returns:
        str: The Bech32 encoded string with the specified prefix.
            Returns empty string if encoding fails.

    Examples:
        Encode public key:

        >>> pubkey_hex = "abc123..."  # 64-char hex
        >>> npub = to_bech32('npub', pubkey_hex)
        >>> print(npub)
        npub1...

        Encode private key:

        >>> privkey_hex = "def456..."  # 64-char hex
        >>> nsec = to_bech32('nsec', privkey_hex)
        >>> print(nsec)
        nsec1...

        Encode event ID:

        >>> event_id = "789ghi..."  # 64-char hex
        >>> note_id = to_bech32('note', event_id)
        >>> print(note_id)
        note1...

        Convert keys for display:

        >>> priv, pub = generate_keypair()
        >>> nsec = to_bech32('nsec', priv)
        >>> npub = to_bech32('npub', pub)
        >>> print(f"Your public key: {npub}")
        >>> print(f"Your private key (keep secret!): {nsec}")

        Share event reference:

        >>> event_id = event.id
        >>> shareable_id = to_bech32('note', event_id)
        >>> print(f"View event: nostr:{shareable_id}")
    """
    byte_data = bytes.fromhex(hex_str)
    data = bech32.convertbits(byte_data, 8, 5, True)
    if data is None:
        return ""
    result = bech32.bech32_encode(prefix, data)
    return str(result) if result is not None else ""


def to_hex(bech32_str: str) -> str:
    """
    Convert a Bech32 encoded string to hexadecimal format.

    This function decodes a Bech32 string (npub, nsec, note, etc.) and returns
    the underlying data as a hexadecimal string. Useful for converting
    user-friendly Bech32 identifiers back to hex format for protocol use.

    Args:
        bech32_str (str): The Bech32 encoded string to convert.
            Examples: npub1..., nsec1..., note1...

    Returns:
        str: The hexadecimal encoded string (typically 64 characters).
            Returns empty string if decoding fails.

    Examples:
        Decode public key:

        >>> npub = "npub1..."
        >>> pubkey_hex = to_hex(npub)
        >>> len(pubkey_hex)
        64

        Decode private key:

        >>> nsec = "nsec1..."
        >>> privkey_hex = to_hex(nsec)
        >>> # Use privkey_hex for signing

        Decode event ID:

        >>> note_id = "note1..."
        >>> event_id_hex = to_hex(note_id)
        >>> # Use event_id_hex to fetch event

        Convert user input:

        >>> user_input = input("Enter npub: ")  # User enters npub1...
        >>> pubkey = to_hex(user_input)
        >>> if pubkey:
        ...     filter = Filter(authors=[pubkey])

        Round-trip conversion:

        >>> original_hex = "abc123..."  # 64-char hex
        >>> bech32 = to_bech32('npub', original_hex)
        >>> decoded_hex = to_hex(bech32)
        >>> assert original_hex == decoded_hex

        Handle invalid input:

        >>> result = to_hex("invalid-bech32")
        >>> if not result:
        ...     print("Invalid Bech32 string")
    """
    _, data = bech32.bech32_decode(bech32_str)
    if data is None:
        return ""
    byte_data = bech32.convertbits(data, 5, 8, False)
    if byte_data is None:
        return ""
    return str(bytes(byte_data).hex())


def generate_keypair() -> tuple[str, str]:
    """
    Generate a new cryptographically secure private/public key pair for Nostr.

    This function creates a new secp256k1 key pair using cryptographically
    secure random number generation. The keys are suitable for use with the
    Nostr protocol and can be used to create and sign events.

    Returns:
        tuple[str, str]: Tuple of (private_key_hex, public_key_hex).
            - private_key_hex: 64-character lowercase hexadecimal string
            - public_key_hex: 64-character lowercase hexadecimal string (x-only pubkey)

            Both keys are suitable for Nostr protocol use.

    Examples:
        Generate new identity:

        >>> private_key, public_key = generate_keypair()
        >>> len(private_key), len(public_key)
        (64, 64)

        Create and sign an event:

        >>> priv, pub = generate_keypair()
        >>> event_dict = generate_event(
        ...     priv, pub,
        ...     kind=1,
        ...     tags=[],
        ...     content="Hello from my new identity!"
        ... )
        >>> event = Event.from_dict(event_dict)

        Convert to bech32 format:

        >>> priv, pub = generate_keypair()
        >>> nsec = to_bech32('nsec', priv)
        >>> npub = to_bech32('npub', pub)
        >>> print(f"Public key (npub): {npub}")
        >>> print(f"Private key (nsec): {nsec}")

        Validate generated keypair:

        >>> priv, pub = generate_keypair()
        >>> assert validate_keypair(priv, pub)  # Always True for fresh keys

        Store securely:

        >>> priv, pub = generate_keypair()
        >>> # IMPORTANT: Store private key securely!
        >>> # Never share or expose private_key
        >>> save_to_secure_storage(priv)
        >>> # Public key can be shared freely
        >>> publish_public_key(pub)
    """
    private_key = os.urandom(32)
    private_key_obj = secp256k1.PrivateKey(private_key)
    public_key = private_key_obj.pubkey.serialize(compressed=True)[1:]
    private_key_hex = private_key.hex()
    public_key_hex = public_key.hex()
    return private_key_hex, public_key_hex
