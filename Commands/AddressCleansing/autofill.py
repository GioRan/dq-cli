from typing import List

import pandas

class Autofill:

    def __init__(self):
        self.conditions = self.get_conditions()

    def apply_autofill(self, row: pandas.Series) -> pandas.Series:
        if row['Cleansing Status'] == 'Cleansed': return row

        row_with_lookups: List[dict] = [{**row, **condition} for condition in self.conditions if self.init_condition(row, condition['conditions'])]

        if len(row_with_lookups) == 1:
            row = self.attach_lookups(row, row_with_lookups[0])
            row['Script Tagging'] = 'Autofill'
            row['Cleansing Status'] = 'Cleansed'

        return row

    def attach_lookups(self, row: pandas.Series, row_with_lookups: dict) -> pandas.Series:
        for lookup in row_with_lookups['lookup_values']:
            row[lookup] = row_with_lookups['lookup_values'][lookup]

        del row_with_lookups['lookup_values']
        del row_with_lookups['conditions']

        return row

    def init_condition(self, row: pandas.Series, conditionary: dict, condition: str = '') -> bool:
        is_truthy: bool = None
        truthy_list: List[bool] = []

        for key in conditionary:
            if key in ['and', 'or']:
                condition = key
                truthy_list.append(self.init_condition(row, conditionary[key], condition))
            elif isinstance(key, dict):
                truthy_list.append(self.init_condition(row, key))
            else:
                if condition == 'or' and '||' in conditionary[key]:
                    truthy_list.extend([s.upper() in row[key].upper() for s in conditionary[key].split('||')])
                else:
                    truthy_list.append(conditionary[key].upper() in row[key].upper())

        if condition == 'or': is_truthy = any(truthy_list)
        elif condition == 'and': is_truthy = all(truthy_list)

        return is_truthy

    def get_conditions(self) -> List[dict]:
        return [
            {
                "conditions": {
                    "and": [
                        {
                            "or": {
                                "bldg_name": "88 CORPORATE CE",
                                "street_name": "88 CORPORATE CE"
                            }
                        },
                        {
                            "or": {
                                "town": "MAKATI||NCR",
                                "street_name": "SEDENO||MAKATI"
                            }
                        }
                    ]
                },
                "lookup_values": {
                    "postal_cd_NEW": "1209",
                    "bldg_name_NEW": "88 CORPORATE CENTER",
                    "street_name_NEW": "SEDENO COR. VALERO",
                    "town_NEW": "CITY OF MAKATI",
                    "province_NEW": "NCR, FOURTH DISTRICT (Not a Province)",
                    "area_name_NEW": "Bel-Air"
                }
            },
            {
                "conditions": {
                    "and": [
                        {
                            "or": {
                                "bldg_name": "ABREEZA",
                                "street_name": "ABREEZA"
                            }
                        },
                        {
                            "or": {
                                "town": "DAVAO",
                                "street_name": "LAUREL",
                                "province": "DAVAO"
                            }
                        }
                    ]
                },
                "lookup_values": {
                    "postal_cd_NEW": "8000",
                    "bldg_name_NEW": "ABREEZA MALL",
                    "street_name_NEW": "J.P. Laurel Ave",
                    "town_NEW": "CITY OF DAVAO",
                    "province_NEW": "DAVAO DEL SUR",
                    "area_name_NEW": "Barangay 20-B (Pob.)"
                }
            },
            {
                "conditions": {
                    "or": {
                        "bldg_name": "ACCRALAW",
                        "street_name": "ACCRALAW",
                        "rm_flr_no": "ACCRALAW"
                    }
                },
                "lookup_values": {
                    "postal_cd_NEW": "1634",
                    "bldg_name_NEW": "ACCRALAW TOWER",
                    "street_name_NEW": "2ND AVE. COR. 30TH ST.",
                    "town_NEW": "CITY OF TAGUIG",
                    "province_NEW": "NCR, FOURTH DISTRICT (Not a Province)",
                    "area_name_NEW": "Fort Bonifacio"
                }
            },
            {
                "conditions": {
                    "or": {
                        "bldg_name": "ASIAN STAR",
                        "street_name": "ASIAN STAR",
                        "rm_flr_no": "ASIAN STAR"
                    }
                },
                "lookup_values": {
                    "postal_cd_NEW": "1780",
                    "bldg_name_NEW": "ASIAN STAR BLDG.",
                    "street_name_NEW": "ASEAN",
                    "town_NEW": "CITY OF MUNTINLUPA",
                    "province_NEW": "NCR, FOURTH DISTRICT (Not a Province)",
                    "area_name_NEW": "Alabang"
                }
            },
            {
                "conditions": {
                    "or": {
                        "bldg_name": "AYALA CEB",
                        "street_name": "AYALA CEB",
                        "rm_flr_no": "AYALA CEB"
                    }
                },
                "lookup_values": {
                    "postal_cd_NEW": "6000",
                    "bldg_name_NEW": "AYALA CENTER CEBU",
                    "street_name_NEW": "ARCHBISHOP REYES AVENUE",
                    "town_NEW": "CITY OF CEBU (Capital)",
                    "province_NEW": "CEBU",
                    "area_name_NEW": "Luz"
                }
            },
            {
                "conditions": {
                    "and": [
                        {
                            "or": {
                                "bldg_name": "TOWER one",
                                "street_name": "TOWER one",
                                "rm_flr_no": "ASIAN STAR"
                            }
                        },
                        {
                            "or": {
                                "bldg_name": "AYALA",
                                "street_name": "AYALA",
                                "town": "AYALA",
                                "province": "MAKATI"
                            }
                        }
                    ]
                },
                "lookup_values": {
                    "postal_cd_NEW": "1209",
                    "bldg_name_NEW": "AYALA TOWER ONE",
                    "street_name_NEW": "AYALA AVE. COR. PASEO DE ROXAS",
                    "town_NEW": "CITY OF MAKATI",
                    "province_NEW": "NCR, FOURTH DISTRICT (Not a Province)",
                    "area_name_NEW": "Bel-Air"
                }
            },
            {
                "conditions": {
                    "and": [
                        {
                            "or": {
                                "bldg_name": "BAYANTEL",
                                "street_name": "BAYANTEL"
                            }
                        },
                        {
                            "or": {
                                "street_name": "Quezon",
                                "town": "Quezon"
                            }
                        }
                    ]
                },
                "lookup_values": {
                    "postal_cd_NEW": "1101",
                    "bldg_name_NEW": "BAYAN CORPORATE CENTER",
                    "street_name_NEW": "MAGINHAWA COR. MALINGAP ST.",
                    "town_NEW": "QUEZON CITY",
                    "province_NEW": "NCR, SECOND DISTRICT (Not a Province)",
                    "area_name_NEW": "Teachers Village East"
                }
            },
            {
                "conditions": {
                    "or": {
                        "bldg_name": "BURGUNDY CORPORATE",
                        "street_name": "BURGUNDY CORPORATE",
                        "rm_flr_no": "BURGUNDY CORPORATE"
                    }
                },
                "lookup_values": {
                    "postal_cd_NEW": "1223",
                    "bldg_name_NEW": "BURGUNDY CORPORATE TOWER",
                    "street_name_NEW": "252 SEN. GIL PUYAT AVE.",
                    "town_NEW": "CITY OF MAKATI",
                    "province_NEW": "NCR, FOURTH DISTRICT (Not a Province)",
                    "area_name_NEW": "San Lorenzo"
                }
            },
            {
                "conditions": {
                    "and": [
                        {
                            "or": {
                                "bldg_name": "CBC B",
                                "street_name": "CBC B",
                                "rm_flr_no": "CBC B"
                            }
                        },
                        {
                            "or": {
                                "town": "quezon",
                                "street_name": "VISAYAS"
                            }
                        }
                    ]
                },
                "lookup_values": {
                    "postal_cd_NEW": "1128",
                    "bldg_name_NEW": "CBC BLDG",
                    "street_name_NEW": "VISAYAS AVE.",
                    "town_NEW": "QUEZON CITY",
                    "province_NEW": "NCR, SECOND DISTRICT (Not a Province)",
                    "area_name_NEW": "Culiat"
                }
            },
            {
                "conditions": {
                    "and": [
                        {
                            "or": {
                                "bldg_name": "CHINA BANK",
                                "street_name": "CHINA BANK",
                                "rm_flr_no": "CHINA BANK"
                            }
                        },
                        {
                            "or": {
                                "town": "makati",
                                "province": "makati",
                                "postal_cd": "makati"
                            }
                        }
                    ]
                },
                "lookup_values": {
                    "postal_cd_NEW": "1209",
                    "bldg_name_NEW": "CHINA BANK BLDG",
                    "street_name_NEW": "8745 PASEO DE ROXAS AVE",
                    "town_NEW": "CITY OF MAKATI",
                    "province_NEW": "NCR, FOURTH DISTRICT (Not a Province)",
                    "area_name_NEW": "Bel-Air"
                }
            },
            {
                "conditions": {
                    "and": [
                        {
                            "or": {
                                "bldg_name": "CITIBANK",
                                "street_name": "CITIBANK",
                                "rm_flr_no": "CITIBANK"
                            }
                        },
                        {
                            "or": {
                                "town": "makati",
                                "province": "makati",
                                "street_name": "makati",
                                "postal_cd": "makati"
                            }
                        }
                    ]
                },
                "lookup_values": {
                    "postal_cd_NEW": "1209",
                    "bldg_name_NEW": "Citibank Tower",
                    "street_name_NEW": "8741 Paseo de Roxas",
                    "town_NEW": "CITY OF MAKATI",
                    "province_NEW": "NCR, FOURTH DISTRICT (Not a Province)",
                    "area_name_NEW": "Bel-Air"
                }
            },
            {
                "conditions": {
                    "and": [
                        {
                            "or": {
                                "bldg_name": "CITIBANK",
                                "street_name": "CITIBANK",
                                "rm_flr_no": "CITIBANK"
                            }
                        },
                        {
                            "or": {
                                "town": "Quezon city",
                                "province": "Quezon city",
                                "street_name": "Quezon city",
                                "postal_cd": "Quezon city"
                            }
                        }
                    ]
                },
                "lookup_values": {
                    "postal_cd_NEW": "1110",
                    "bldg_name_NEW": "CITIBANK SQUARE I",
                    "street_name_NEW": "EASTWOOD AVE., EASTWOOD CITY, LIBIS",
                    "town_NEW": "QUEZON CITY",
                    "province_NEW": "NCR, SECOND DISTRICT (Not a Province)",
                    "area_name_NEW": "BAGUMBAYAN"
                }
            },
            {
                "conditions": {
                    "and": [
                        {
                            "or": {
                                "bldg_name": "DISCOVERY",
                                "street_name": "DISCOVERY",
                                "rm_flr_no": "DISCOVERY"
                            }
                        },
                        {
                            "or": {
                                "town": "PASIG",
                                "province": "PASIG",
                                "street_name": "PASIG",
                                "bldg_name": "PASIG"
                            }
                        }
                    ]
                },
                "lookup_values": {
                    "postal_cd_NEW": "1600",
                    "bldg_name_NEW": "DISCOVERY CENTER",
                    "street_name_NEW": "25 ADB AVE., ORTIGAS COMPLEX",
                    "town_NEW": "CITY OF PASIG",
                    "province_NEW": "NCR, SECOND DISTRICT (Not a Province)",
                    "area_name_NEW": "San Antonio"
                }
            },
            {
                "conditions": {
                    "or": {
                        "bldg_name": "FARMERST MARKET",
                        "street_name": "FARMERST MARKET",
                        "rm_flr_no": "FARMERST MARKET"
                    }
                },
                "lookup_values": {
                    "postal_cd_NEW": "1109",
                    "bldg_name_NEW": "FARMERS MARKET",
                    "street_name_NEW": "11 GENERAL ARANETA AVE.",
                    "town_NEW": "QUEZON CITY",
                    "province_NEW": "NCR, SECOND DISTRICT (Not a Province)",
                    "area_name_NEW": "Socorro"
                }
            },
            {
                "conditions": {
                    "or": {
                        "bldg_name": "GLORIETTA 3",
                        "street_name": "GLORIETTA 3",
                        "rm_flr_no": "GLORIETTA 3"
                    }
                },
                "lookup_values": {
                    "postal_cd_NEW": "1223",
                    "bldg_name_NEW": "GLORIETTA 3",
                    "street_name_NEW": "AYALA AVE.",
                    "town_NEW": "CITY OF MAKATI",
                    "province_NEW": "NCR, FOURTH DISTRICT (Not a Province)",
                    "area_name_NEW": "San Lorenzo"
                }
            },
            {
                "conditions": {
                    "or": {
                        "bldg_name": "GREENBELT 5",
                        "street_name": "GREENBELT 5",
                        "rm_flr_no": "GREENBELT 5"
                    }
                },
                "lookup_values": {
                    "postal_cd_NEW": "1223",
                    "bldg_name_NEW": "GREENBELT 5",
                    "street_name_NEW": "AYALA AVE.",
                    "town_NEW": "CITY OF MAKATI",
                    "province_NEW": "NCR, FOURTH DISTRICT (Not a Province)",
                    "area_name_NEW": "San Lorenzo"
                }
            },
            {
                "conditions": {
                    "or": {
                        "bldg_name": "GT TOWER",
                        "street_name": "GT TOWER",
                        "rm_flr_no": "GT TOWER"
                    }
                },
                "lookup_values": {
                    "postal_cd_NEW": "1209",
                    "bldg_name_NEW": "GT TOWER",
                    "street_name_NEW": "6813 AYALA AVE. COR. H.V. DELA COSTA ST.",
                    "town_NEW": "CITY OF MAKATI",
                    "province_NEW": "NCR, FOURTH DISTRICT (Not a Province)",
                    "area_name_NEW": "Bel-Air"
                }
            },
            {
                "conditions": {
                    "or": {
                        "bldg_name": "IBM PL",
                        "street_name": "IBM PL",
                        "rm_flr_no": "IBM PL"
                    }
                },
                "lookup_values": {
                    "postal_cd_NEW": "1110",
                    "bldg_name_NEW": "IBM PLAZA",
                    "street_name_NEW": "E RODRIQUEZ JUNIOR AVE.",
                    "town_NEW": "QUEZON CITY",
                    "province_NEW": "NCR, SECOND DISTRICT (Not a Province)",
                    "area_name_NEW": "Libis"
                }
            },
            {
                "conditions": {
                    "or": {
                        "bldg_name": "IBM PL",
                        "street_name": "IBM PL",
                        "rm_flr_no": "IBM PL"
                    }
                },
                "lookup_values": {
                    "postal_cd_NEW": "1103",
                    "bldg_name_NEW": "KAMUNING PUBLIC MARKET",
                    "street_name_NEW": "K-5th St.",
                    "town_NEW": "QUEZON CITY",
                    "province_NEW": "NCR, SECOND DISTRICT (Not a Province)",
                    "area_name_NEW": "Kamuning"
                }
            },
            {
                "conditions": {
                    "and": [
                        {
                            "or": {
                                "bldg_name": "KAMUNING",
                                "street_name": "PUBLIC MARKET",
                                "rm_flr_no": "PUBLIC MARKET"
                            }
                        },
                        {
                            "or": {
                                "town": "quezon city",
                                "street_name": "K FIFTH||K 5TH"
                            }
                        },
                        {
                            "or": {
                                "province": "METRO MANILA"
                            }
                        }
                    ]
                },
                "lookup_values": {
                    "postal_cd_NEW": "1103",
                    "bldg_name_NEW": "KAMUNING PUBLIC MARKET",
                    "street_name_NEW": "K-5th St.",
                    "town_NEW": "QUEZON CITY",
                    "province_NEW": "NCR, SECOND DISTRICT (Not a Province)",
                    "area_name_NEW": "Kamuning"
                }
            },
            {
                "conditions": {
                    "and": [
                        {
                            "or": {
                                "bldg_name": "PBCOM",
                                "street_name": "PBCOM",
                                "rm_flr_no": "PBCOM"
                            }
                        },
                        {
                            "or": {
                                "town": "makati||SALCEDO||RUFINO||BEL",
                                "province": "makati||salcedo||rufino"
                            }
                        }
                    ]
                },
                "lookup_values": {
                    "postal_cd_NEW": "1209",
                    "bldg_name_NEW": "PBCOM TOWER",
                    "street_name_NEW": "6795 V.A. Rufino St.",
                    "town_NEW": "CITY OF MAKATI",
                    "province_NEW": "NCR, FOURTH DISTRICT (Not a Province)",
                    "area_name_NEW": "Bel-Air"
                }
            },
            {
                "conditions": {
                    "and": [
                        {
                            "or": {
                                "bldg_name": "FARMERS MARKET||FARMERS M||FARMERS",
                                "street_name": "FARMERS MARKET||FARMERS M||FARMERS"
                            }
                        },
                        {
                            "or": {
                                "town": "QUEZON CITY",
                                "street_name": "QUEZON CITY",
                                "province": "QUEZON CITY"
                            }
                        }
                    ]
                },
                "lookup_values": {
                    "postal_cd_NEW": "1109",
                    "bldg_name_NEW": "FARMERS MARKET",
                    "street_name_NEW": "11 General Araneta",
                    "town_NEW": "QUEZON CITY",
                    "province_NEW": "NCR, SECOND DISTRICT (Not a Province)",
                    "area_name_NEW": "Socorro"
                }
            },
            {
                "conditions": {
                    "and": [
                        {
                            "or": {
                                "bldg_name": "GLOBE TELECOM",
                                "street_name": "GLOBE TELECOM"
                            }
                        },
                        {
                            "or": {
                                "town": "VILLAGE||salcedo||makati",
                                "province": "makati||salcedo"
                            }
                        }
                    ]
                },
                "lookup_values": {
                    "postal_cd_NEW": "1209",
                    "bldg_name_NEW": "Globe Telepark-Valero",
                    "street_name_NEW": "111, 1227 Valero",
                    "town_NEW": "CITY OF MAKATI",
                    "province_NEW": "NCR, FOURTH DISTRICT (Not a Province)",
                    "area_name_NEW": "Bel-Air"
                }
            },
            {
                "conditions": {
                    "and": [
                        {
                            "or": {
                                "bldg_name": "GLOBE TELECOM",
                                "street_name": "GLOBE TELECOM"
                            }
                        },
                        {
                            "or": {
                                "town": "mandaluyong||salcedo",
                                "province": "mandaluyong||salcedo"
                            }
                        }
                    ]
                },
                "lookup_values": {
                    "postal_cd_NEW": "1550",
                    "bldg_name_NEW": "Globe Telecom Plaza",
                    "street_name_NEW": "Pioneer Highlands, Madison",
                    "town_NEW": "CITY OF MANDALUYONG",
                    "province_NEW": "NCR, SECOND DISTRICT (Not a Province)",
                    "area_name_NEW": "Barangka Ilaya"
                }
            },
            {
                "conditions": {
                    "or": {
                        "bldg_name": "CITIBANK TOWER",
                        "street_name": "GLOBE TELECOM"
                    }
                },
                "lookup_values": {
                    "postal_cd_NEW": "1209",
                    "bldg_name_NEW": "Citibank Tower",
                    "street_name_NEW": "8741 Paseo de Roxas",
                    "town_NEW": "CITY OF MAKATI",
                    "province_NEW": "NCR, FOURTH DISTRICT (Not a Province)",
                    "area_name_NEW": "Bel-Air"
                }
            }
        ]