import sqlite3

DB_NAME = "taller.db"

def get_db():
    conn = sqlite3.connect(DB_NAME)
    conn.row_factory = sqlite3.Row
    return conn

def init_db():
    conn = get_db()
    cursor = conn.cursor()
    
    # 1. Clientes
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS clientes (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            nombre TEXT NOT NULL,
            tipo_doc TEXT,
            nro_doc TEXT,
            condicion_iva TEXT,
            telefono TEXT NOT NULL,
            email TEXT,
            direccion TEXT,
            localidad TEXT
        )
    ''')
    
    # 2. Vehículos
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS vehiculos (
            patente TEXT PRIMARY KEY,
            cliente_id INTEGER,
            marca TEXT,
            modelo TEXT,
            anio INTEGER,
            tipo_propulsion TEXT DEFAULT 'Combustión (Nafta/Diésel)',
            motor TEXT,
            km_actuales INTEGER,
            km_promedio_mes INTEGER DEFAULT 1200,
            intervalo_aceite_km INTEGER DEFAULT 10000,
            intervalo_distribucion_km INTEGER DEFAULT 60000,
            intervalo_bujias_km INTEGER DEFAULT 30000,
            FOREIGN KEY (cliente_id) REFERENCES clientes (id)
        )
    ''')
    
    # Migración de columnas para vehiculos
    cursor.execute("PRAGMA table_info(vehiculos)")
    cols_veh = [row[1] for row in cursor.fetchall()]
    cols_veh_nuevas = [
        ("tipo_propulsion", "TEXT DEFAULT 'Combustión (Nafta/Diésel)'"),
        ("km_promedio_mes", "INTEGER DEFAULT 1200"),
        ("intervalo_aceite_km", "INTEGER DEFAULT 10000"),
        ("intervalo_distribucion_km", "INTEGER DEFAULT 60000"),
        ("intervalo_bujias_km", "INTEGER DEFAULT 30000")
    ]
    for c_nom, c_tipo in cols_veh_nuevas:
        if c_nom not in cols_veh:
            cursor.execute(f"ALTER TABLE vehiculos ADD COLUMN {c_nom} {c_tipo}")
    
    # 3. Intervenciones Técnicas Oficiales (Taller)
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS servicios_taller (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            patente TEXT,
            fecha TEXT,
            km_servicio INTEGER,
            categoria TEXT,
            diagnostico_dtc TEXT,
            estado_dtc TEXT DEFAULT 'Resuelto',
            trabajo_realizado TEXT,
            repuestos_utilizados TEXT,
            parametros_tecnicos TEXT,
            software_version TEXT,
            garantia TEXT,
            proximo_km INTEGER,
            proxima_fecha TEXT,
            costo_total REAL DEFAULT 0,
            FOREIGN KEY (patente) REFERENCES vehiculos (patente)
        )
    ''')
    
    # Migración de columnas para servicios_taller
    cursor.execute("PRAGMA table_info(servicios_taller)")
    cols_serv = [row[1] for row in cursor.fetchall()]
    cols_serv_nuevas = [
        ("estado_dtc", "TEXT DEFAULT 'Resuelto'"),
        ("parametros_tecnicos", "TEXT"),
        ("software_version", "TEXT")
    ]
    for cs_nom, cs_tipo in cols_serv_nuevas:
        if cs_nom not in cols_serv:
            cursor.execute(f"ALTER TABLE servicios_taller ADD COLUMN {cs_nom} {cs_tipo}")

    # 4. Mantenimientos Externos (Cargados por el Cliente)
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS servicios_externos (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            patente TEXT,
            fecha TEXT,
            km_servicio INTEGER,
            tipo_mantenimiento TEXT,
            establecimiento TEXT,
            detalle_materiales TEXT,
            FOREIGN KEY (patente) REFERENCES vehiculos (patente)
        )
    ''')
    
    # 5. Presupuestos
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS presupuestos (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            patente TEXT,
            fecha_emision TEXT,
            categoria TEXT,
            validez_dias INTEGER DEFAULT 15,
            estado TEXT DEFAULT 'Pendiente',
            detalle_trabajo TEXT,
            repuestos TEXT,
            total REAL,
            FOREIGN KEY (patente) REFERENCES vehiculos (patente)
        )
    ''')
    
    conn.commit()
    conn.close()

if __name__ == "__main__":
    init_db()