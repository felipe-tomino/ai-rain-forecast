from orator import DatabaseManager

db_params = {
    'postgresql': {
        'driver': 'postgresql',
        'host': 'localhost',
        'database': 'tccfelipetomino',
        'user': 'felipe',
        'password': 'tomino',
        'prefix': ''
    }
}

db = DatabaseManager(db_params)
