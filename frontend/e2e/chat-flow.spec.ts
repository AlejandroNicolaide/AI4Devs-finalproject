import { expect, test, type Page } from '@playwright/test'

// Flujo principal de AsistenteIA de extremo a extremo (navegador real, backend real, BD real,
// embeddings reales; Gemini sustituido por LLM_FAKE=1):
// docente sube material -> estudiante pregunta -> respuesta con fuentes -> historial -> borrado (GDPR).

const MATERIAL = `La mitosis es el proceso de división celular que da lugar a dos células hijas genéticamente idénticas.
Sus fases son profase, metafase, anafase y telofase.

La fotosíntesis convierte la energía de la luz solar en energía química dentro de los cloroplastos.`

const FAKE_ANSWER = 'Respuesta de prueba generada a partir del material de la asignatura.'

async function register(page: Page, name: string, email: string, role: 'Docente' | 'Estudiante') {
  await page.goto('/register')
  await page.getByLabel('Nombre').fill(name)
  await page.getByLabel('Email').fill(email)
  await page.getByLabel(/Contraseña/).fill('Password123!')
  await page.getByLabel('Rol').selectOption({ label: role })
  await page.getByRole('button', { name: 'Registrarme' }).click()
  await expect(page.getByRole('heading', { name: 'Asignaturas' })).toBeVisible()
}

test('docente sube material, estudiante pregunta y recibe respuesta con fuentes; luego borra su historial', async ({
  page,
}) => {
  const run = Date.now()
  const subjectName = `Biología E2E ${run}`

  // --- Docente: crea la asignatura y sube el material ---
  await register(page, 'Docente E2E', `docente.${run}@e2e-test.com`, 'Docente')
  await page.getByRole('button', { name: 'Crear asignatura' }).click()
  await page.getByPlaceholder('Nombre').fill(subjectName)
  await page.getByRole('button', { name: 'Guardar' }).click()
  await page.getByRole('link', { name: new RegExp(subjectName) }).click()

  await page.locator('input[type=file]').setInputFiles({
    name: 'unidad1.txt',
    mimeType: 'text/plain',
    buffer: Buffer.from(MATERIAL),
  })
  await expect(page.getByRole('status')).toContainText('«unidad1.txt» subido correctamente')
  await expect(page.getByRole('listitem').filter({ hasText: 'unidad1.txt' })).toBeVisible()

  // --- Estudiante: pregunta ---
  await page.getByRole('button', { name: 'Salir' }).click()
  await register(page, 'Estudiante E2E', `estudiante.${run}@e2e-test.com`, 'Estudiante')
  await page.getByRole('link', { name: new RegExp(subjectName) }).click()
  await page.getByRole('link', { name: 'Preguntar al asistente' }).click()

  await page.getByPlaceholder('Escribe tu pregunta…').fill('¿Cuáles son las fases de la mitosis?')
  await page.getByRole('button', { name: 'Enviar' }).click()

  // --- Respuesta con fuente citada ---
  await expect(page.getByText(FAKE_ANSWER)).toBeVisible()
  await expect(page.getByText('Fuentes')).toBeVisible()
  const chip = page.getByRole('button', { name: /unidad1\.txt/ })
  await expect(chip).toBeVisible()
  await chip.click()
  await expect(chip).toHaveAttribute('aria-expanded', 'true')
  await expect(page.getByText(/profase, metafase, anafase y telofase/)).toBeVisible()

  // --- Seguimiento en la misma conversación: debe aparecer sin recargar ---
  await page.getByPlaceholder('Escribe tu pregunta…').fill('¿Y qué es la fotosíntesis?')
  await page.getByRole('button', { name: 'Enviar' }).click()
  await expect(page.getByText('¿Y qué es la fotosíntesis?')).toBeVisible()
  await expect(page.getByText(FAKE_ANSWER)).toHaveCount(2)

  // --- Historial y derecho al olvido ---
  await page.getByRole('link', { name: 'Historial' }).click()
  await expect(page.getByRole('heading', { name: 'Historial de conversaciones' })).toBeVisible()
  await expect(page.getByText(subjectName)).toBeVisible()

  page.once('dialog', (dialog) => dialog.accept())
  await page.getByRole('button', { name: 'Eliminar' }).click()
  await expect(page.getByText('No tienes conversaciones.')).toBeVisible()
})
