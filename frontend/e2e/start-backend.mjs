// Arranca el backend para los tests E2E: base propia (asistenteia_e2e), migraciones y uvicorn con LLM_FAKE=1.
// Variables opcionales: E2E_PYTHON (intérprete con las dependencias del backend), E2E_DATABASE_URL.
import { spawn, spawnSync } from 'node:child_process'
import path from 'node:path'
import { fileURLToPath } from 'node:url'

const here = path.dirname(fileURLToPath(import.meta.url))
const backendDir = path.resolve(here, '../../backend')
const python =
  process.env.E2E_PYTHON ??
  (process.platform === 'win32'
    ? path.join(backendDir, 'venv', 'Scripts', 'python.exe')
    : path.join(backendDir, 'venv', 'bin', 'python'))

const databaseUrl =
  process.env.E2E_DATABASE_URL ?? 'postgresql+psycopg2://postgres:postgres@localhost:5434/asistenteia_e2e'

const env = {
  ...process.env,
  DATABASE_URL: databaseUrl,
  SECRET_KEY: process.env.SECRET_KEY ?? 'clave-solo-para-e2e-0123456789abcdef',
  GEMINI_API_KEY: '',
  LLM_FAKE: '1',
  SIMILARITY_THRESHOLD: '',
  CORS_ORIGINS: 'http://127.0.0.1:5174',
}

function run(args, input) {
  const result = spawnSync(python, args, { cwd: backendDir, env, input, stdio: ['pipe', 'inherit', 'inherit'] })
  if (result.status !== 0) process.exit(result.status ?? 1)
}

// 1. crea la base si no existe (se conecta a la base "postgres" del mismo servidor)
run(
  ['-I', '-c', `
import os
from sqlalchemy import create_engine, text
from sqlalchemy.engine import make_url
url = make_url(os.environ["DATABASE_URL"])
admin = create_engine(url.set(database="postgres"), isolation_level="AUTOCOMMIT")
with admin.connect() as conn:
    exists = conn.scalar(text("select 1 from pg_database where datname = :n"), {"n": url.database})
    if not exists:
        conn.execute(text('create database "' + url.database + '"'))
`],
)
// 2. migraciones
run(['-m', 'alembic', 'upgrade', 'head'])

// 3. servidor
const server = spawn(python, ['-m', 'uvicorn', 'app.main:app', '--host', '127.0.0.1', '--port', '8001'], {
  cwd: backendDir,
  env,
  stdio: 'inherit',
})
for (const signal of ['SIGINT', 'SIGTERM']) process.on(signal, () => server.kill())
server.on('exit', (code) => process.exit(code ?? 0))
