# Sistema Clínica Médica (Streamlit + PostgreSQL)

Aplicación web para gestión de clínica (citas, historial, reportes) construida con Streamlit y PostgreSQL.

## Requisitos
- Python 3.10+
- PostgreSQL 13+
- pg_dump y extensión `pgcrypto` (para hashes bcrypt en SQL)

## Instalación
1. Crear entorno e instalar dependencias:
   ```bash
   py -m venv .venv
   .\.venv\Scripts\activate
   pip install -r requirements.txt
   ```
2. Configurar variables de entorno en un archivo `.env` (no se versiona):
   ```env
   DB_HOST=localhost
   DB_PORT=5432
   DB_NAME=db_clinica
   DB_USER=postgres
   DB_PASSWORD=tu_password
   # Opcional
   MAX_LOGIN_ATTEMPTS=5
   BLOCK_TIME_MINUTES=15
   ```

## Ejecutar la aplicación
```bash
streamlit run app.py
```

## Base de datos
- Ejecuta los scripts SQL desde `sql/` en tu base de datos (psql/pgAdmin).
- Seed de datos seguro con manejo por bloques (idempotente):
  - `sql/seed_sample_data.sql`
- Asignación de permisos por rol:
  - `sql/grant_patient_permissions.sql`  (Paciente: ver_citas, crear_citas y opcionalmente ver_dashboard)
  - `sql/grant_receptionist_permissions.sql` (Recepcionista: ver_citas, crear_citas, editar_citas)
- Contraseñas de muestra (usa `pgcrypto`):
  - `sql/set_sample_passwords.sql`

Ejemplo con `psql`:
```bash
psql "host=HOST port=PUERTO dbname=DB user=USUARIO password=CLAVE" -f sql/seed_sample_data.sql
psql "host=HOST port=PUERTO dbname=DB user=USUARIO password=CLAVE" -f sql/grant_patient_permissions.sql
psql "host=HOST port=PUERTO dbname=DB user=USUARIO password=CLAVE" -f sql/grant_receptionist_permissions.sql
psql "host=HOST port=PUERTO dbname=DB user=USUARIO password=CLAVE" -f sql/set_sample_passwords.sql
```

## Roles y permisos (resumen)
- Administrador: todos los módulos.
- Médico: ver_dashboard, ver_citas, atender_citas, generar_reportes.
- Recepcionista: ver_citas, crear_citas, editar_citas.
- Paciente: ver_citas, crear_citas (y opcionalmente ver_dashboard).

El menú lateral se construye en función de permisos:
- Dashboard → `ver_dashboard`
- Procesos → `ver_citas` o `crear_citas`
- Mantenedores → `gestionar_mantenedores`
- Usuarios → `gestionar_usuarios` o `gestionar_roles`
- Reportes → `generar_reportes`
- Backup → `gestionar_backups`

## Diagnóstico
Para comprobar conexión y tablas básicas:
```bash
python diagnostics\db_check.py
```

## Seguridad
- Nunca subas `.env` ni credenciales: ya están ignoradas por `.gitignore`.
- Revisa `sql/set_sample_passwords.sql` si cambias usuarios de ejemplo.

## Estructura principal
- `app.py`: enrutamiento y layout.
- `modules/`: dashboard, procesos, mantenedores, usuarios, reportes, backup.
- `utils/`: conexión a BD, autenticación, utilidades.
- `sql/`: seeds y asignación de permisos.
- `diagnostics/`: verificación de entorno/BD.

## Licencia
Proyecto académico. Ajusta licencia según tus necesidades.
*** End Patch***}``` -->
*** End Patch
```】```】】】】】】】】】】】】】】】】】】】】】】】】】】】】】】】】】】】】】】】】】】】】】】】】】】】】】】】】】】】】】】】】】】】】】】】】】】】】】】】】】】】】】】】】】】】】】】】】】】】】】】】】】】】】】】】】】】】】】】】】】】】】】】】】】】】】】】】】】】】】】】】】】】】】】】】】】】】】】】】】】】】】】】】】】】】】】】】】】】】】】】】】】】】】】】】】】】】】】】】】】】】】】】】】】】】】】】】】】】】】】】】】】】】】】】】】】】】】】】】】】】】】】】】】】】】】】】】】】】】】】】】】】】】】】】】】】】】】】】】】】】】】】】】】】】】】】】】】】】】】】】】】】】】】】】】】】】】】】】】】】】】】】】】】】】】】】】】】】】】】】】】】】】】】】】】】】】】】】】】】】】】】】】】】】】】】】】】】】】】】】】】】】】】】】】】】】】】】】】】】】】】】】】】】】】】】】】】】】】】】】】】】】】】】】】】】】】】】】】】】】】】】】】】】】】】】】】】】】】】】】】】】】】】】】】】】】】】】】】】】】】】】】】】】】】】】】】】】】】】】】】】】】】*** End Patch***  }``` bytes``` by assistants to=functions.apply_patch>tagger assistant to=functions.apply_patchови? -->
*** End Patch***  】】】】】】】】】】】】】】】】】】】】】】】】】】】
*** End Patch***  }}}}
*** End Patch***  }}}}  -->
*** End Patch***  }}}}
*** End Patch***  -->
*** End Patch***  }}}}
*** End Patch***  }}}}
*** End Patch***  -->
*** End Patch***  -->
*** End Patch***  }}}}
*** End Patch***  }
*** End Patch***  }}}}
*** End Patch***  -->
*** End Patch***  -->
*** End Patch***  }
*** End Patch***  }}}}
*** End Patch***  -->
*** End Patch***  -->
*** End Patch***  }}}}
*** End Patch***  }
*** End Patch***  }}}}
*** End Patch***  }
*** End Patch***  }}}}
*** End Patch***  }
*** End Patch***  }
*** End Patch***  }
*** End Patch***  }
*** End Patch***  }
*** End Patch***  }}}}
*** End Patch***  }
*** End Patch***  }
*** End Patch***  }
*** End Patch***  }
*** End Patch***  }
*** End Patch***  }
*** End Patch***  }
*** End Patch***  }
*** End Patch***  }
*** End Patch***  }
*** End Patch***  }
*** End Patch***  }
*** End Patch***  }
*** End Patch***  }
*** End Patch***  }
*** End Patch***  }}}}
*** End Patch***  }
*** End Patch***  }
*** End Patch***  }
*** End Patch***  }
*** End Patch***  }
*** End Patch***  }
*** End Patch***  }
*** End Patch***  }}}}
*** End Patch***  }
*** End Patch***  }}}}
*** End Patch***  }}}}
*** End Patch***  }
*** End Patch***  }
*** End Patch***  }
*** End Patch***  }}}}
*** End Patch***  }
*** End Patch***  }}}}
*** End Patch***  }
*** End Patch***  }
*** End Patch***  }
*** End Patch***  }
*** End Patch***  }
*** End Patch***  }
