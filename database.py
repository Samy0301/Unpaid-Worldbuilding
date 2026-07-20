"""Capa de acceso a datos SQLite"""

import sqlite3
from config import DB_PATH


class Database:
    """Gestiona la conexión y esquema de la base de datos (singleton)"""

    _instance = None

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
            cls._instance.conn = sqlite3.connect(DB_PATH)
            cls._instance.conn.execute("PRAGMA foreign_keys = ON")
            cls._instance.cursor = cls._instance.conn.cursor()
            cls._instance._crear_tablas()
        return cls._instance

    def _crear_tablas(self):
        self.cursor.executescript("""
            CREATE TABLE IF NOT EXISTS historias (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                nombre TEXT NOT NULL,
                resumen TEXT,
                plot_general TEXT,
                foto_blob BLOB,
                fecha_creacion TEXT DEFAULT CURRENT_TIMESTAMP
            );

            CREATE TABLE IF NOT EXISTS personajes (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                historia_id INTEGER,
                nombre TEXT NOT NULL,
                apodo TEXT,
                categoria TEXT DEFAULT 'principal',
                edad TEXT,
                familia TEXT,
                historia_personal TEXT,
                trauma TEXT,
                plot_rol TEXT,
                guia_trama TEXT,
                foto_blob BLOB,
                FOREIGN KEY (historia_id) REFERENCES historias(id) ON DELETE CASCADE
            );

            CREATE TABLE IF NOT EXISTS arboles_genealogicos (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                historia_id INTEGER,
                nombre_arbol TEXT,
                FOREIGN KEY (historia_id) REFERENCES historias(id) ON DELETE CASCADE
            );

            CREATE TABLE IF NOT EXISTS nodos_genealogicos (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                arbol_id INTEGER,
                personaje_id INTEGER,
                padre_id INTEGER,
                madre_id INTEGER,
                pareja_id INTEGER,
                FOREIGN KEY (arbol_id) REFERENCES arboles_genealogicos(id) ON DELETE CASCADE,
                FOREIGN KEY (personaje_id) REFERENCES personajes(id) ON DELETE CASCADE
            );

            CREATE TABLE IF NOT EXISTS relaciones (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                historia_id INTEGER,
                personaje1_id INTEGER,
                personaje2_id INTEGER,
                tipo TEXT,
                descripcion TEXT,
                FOREIGN KEY (historia_id) REFERENCES historias(id) ON DELETE CASCADE,
                FOREIGN KEY (personaje1_id) REFERENCES personajes(id) ON DELETE CASCADE,
                FOREIGN KEY (personaje2_id) REFERENCES personajes(id) ON DELETE CASCADE
            );

            CREATE TABLE IF NOT EXISTS capitulos (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                historia_id INTEGER,
                numero INTEGER,
                titulo TEXT,
                plot_guia TEXT,
                FOREIGN KEY (historia_id) REFERENCES historias(id) ON DELETE CASCADE
            );

            CREATE TABLE IF NOT EXISTS partes_capitulo (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                capitulo_id INTEGER,
                nombre_parte TEXT,
                contenido TEXT,
                orden INTEGER,
                FOREIGN KEY (capitulo_id) REFERENCES capitulos(id) ON DELETE CASCADE
            );

            CREATE TABLE IF NOT EXISTS posiciones_nodos (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                historia_id INTEGER NOT NULL,
                personaje_id INTEGER NOT NULL,
                x REAL NOT NULL,
                y REAL NOT NULL,
                UNIQUE(historia_id, personaje_id),
                FOREIGN KEY (historia_id) REFERENCES historias(id) ON DELETE CASCADE,
                FOREIGN KEY (personaje_id) REFERENCES personajes(id) ON DELETE CASCADE
            );
        """)
        self.conn.commit()
        self._migrar_personajes()

    def _migrar_personajes(self):
        """Migra la tabla personajes si tiene esquema antiguo."""
        self.cursor.execute("PRAGMA table_info(personajes)")
        cols = {row[1]: row[0] for row in self.cursor.fetchall()}

        if "apodo" not in cols:
            # Esquema antiguo sin apodo: recrear tabla
            self.cursor.execute("SELECT * FROM personajes")
            rows = self.cursor.fetchall()

            self.cursor.execute("ALTER TABLE personajes RENAME TO personajes_old")

            self.cursor.executescript("""
                CREATE TABLE personajes (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    historia_id INTEGER,
                    nombre TEXT NOT NULL,
                    apodo TEXT,
                    categoria TEXT DEFAULT 'principal',
                    edad TEXT,
                    familia TEXT,
                    historia_personal TEXT,
                    trauma TEXT,
                    plot_rol TEXT,
                    guia_trama TEXT,
                    foto_blob BLOB,
                    FOREIGN KEY (historia_id) REFERENCES historias(id) ON DELETE CASCADE
                );
            """)

            for row in rows:
                # Orden viejo: id, historia_id, nombre, categoria, edad, familia,
                #              historia_personal, trauma, plot_rol, guia_trama, foto_blob
                # Orden nuevo: id, historia_id, nombre, apodo, categoria, edad, familia,
                #              historia_personal, trauma, plot_rol, guia_trama, foto_blob
                self.cursor.execute("""
                    INSERT INTO personajes (id, historia_id, nombre, apodo, categoria, edad, familia,
                    historia_personal, trauma, plot_rol, guia_trama, foto_blob)
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                """, (row[0], row[1], row[2], None, row[3], row[4], row[5], row[6], row[7], row[8], row[9], row[10]))

            self.cursor.execute("DROP TABLE personajes_old")
            self.conn.commit()
        elif cols.get("apodo") != 3:
            # apodo existe pero en posicion incorrecta (al final por ALTER TABLE)
            self.cursor.execute("SELECT * FROM personajes")
            rows = self.cursor.fetchall()

            self.cursor.execute("ALTER TABLE personajes RENAME TO personajes_old")

            self.cursor.executescript("""
                CREATE TABLE personajes (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    historia_id INTEGER,
                    nombre TEXT NOT NULL,
                    apodo TEXT,
                    categoria TEXT DEFAULT 'principal',
                    edad TEXT,
                    familia TEXT,
                    historia_personal TEXT,
                    trauma TEXT,
                    plot_rol TEXT,
                    guia_trama TEXT,
                    foto_blob BLOB,
                    FOREIGN KEY (historia_id) REFERENCES historias(id) ON DELETE CASCADE
                );
            """)

            for row in rows:
                # Orden con apodo al final: id, historia_id, nombre, categoria, edad, familia,
                #              historia_personal, trauma, plot_rol, guia_trama, foto_blob, apodo
                # Orden nuevo: id, historia_id, nombre, apodo, categoria, edad, familia,
                #              historia_personal, trauma, plot_rol, guia_trama, foto_blob
                self.cursor.execute("""
                    INSERT INTO personajes (id, historia_id, nombre, apodo, categoria, edad, familia,
                    historia_personal, trauma, plot_rol, guia_trama, foto_blob)
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                """, (row[0], row[1], row[2], row[11], row[3], row[4], row[5], row[6], row[7], row[8], row[9], row[10]))

            self.cursor.execute("DROP TABLE personajes_old")
            self.conn.commit()

    def ejecutar(self, query: str, params=()):
        self.cursor.execute(query, params)
        self.conn.commit()
        return self.cursor

    def obtener(self, query: str, params=()):
        self.cursor.execute(query, params)
        return self.cursor.fetchall()

    def obtener_uno(self, query: str, params=()):
        self.cursor.execute(query, params)
        return self.cursor.fetchone()