// Los mensajes nativos dependen del idioma del navegador, no de <html lang>.
// Mantener la validacion HTML y presentar sus errores en el idioma del CRM.
document.addEventListener('invalid', (event) => {
  const field = event.target
  if (!(field instanceof HTMLInputElement || field instanceof HTMLSelectElement || field instanceof HTMLTextAreaElement)) return
  field.setCustomValidity('')
  const validity = field.validity
  let message = ''
  if (validity.valueMissing) message = 'Completa este campo.'
  else if (validity.typeMismatch) message = field.type === 'email' ? 'Ingresa un correo electrónico válido.' : 'Ingresa un valor válido.'
  else if (validity.patternMismatch) message = field.title || 'El valor no tiene el formato requerido.'
  else if (validity.tooShort) message = `Ingresa al menos ${field.minLength} caracteres.`
  else if (validity.tooLong) message = `Ingresa como máximo ${field.maxLength} caracteres.`
  else if (validity.rangeUnderflow) message = `El valor mínimo es ${field.min}.`
  else if (validity.rangeOverflow) message = `El valor máximo es ${field.max}.`
  else if (validity.badInput || validity.stepMismatch) message = 'Ingresa un número válido.'
  field.setCustomValidity(message)
}, true)

for (const event of ['input', 'change']) {
  document.addEventListener(event, ({ target }) => {
    if (typeof target.setCustomValidity === 'function') target.setCustomValidity('')
  }, true)
}
