class AppConfig:
    weekly_shifts = [
        'lunedi_m', 'lunedi_pr', 'lunedi_po',
        'martedi_m', 'martedi_pr', 'martedi_po',
        'mercoledi_m', 'mercoledi_pr', 'mercoledi_po',
        'giovedi_m', 'giovedi_pr', 'giovedi_po',
        'venerdi_m', 'venerdi_pr', 'venerdi_po'
    ]
    MIN_PEOPLE_PER_SHIFT = 2
    MAX_PEOPLE_PER_SHIFT = 3
    CSV_FILE_PATH = "disponibilita.csv"