<script setup>
import { computed, onBeforeUnmount, onMounted, ref } from 'vue'
import { ArrowRight, BadgeCheck, BookOpen, CalendarDays, Clock3, Coins, FileText, Layers, Search } from '@lucide/vue'
import { listOfertas, registrarInteres } from '../services/api'

const ofertas = ref([])
const buscar = ref('')
const loading = ref(true)
const selected = ref(null)
const message = ref('')
const error = ref('')
const form = ref({ nombre: '', apellido: '', documento: '', correo: '', telefono: '', profesion: '', ubicacion: '' })
const notice = ref('')
let noticeTimeout = null

const step = computed(() => {
  if (selected.value) return 2
  return 1
})
const filteredOfertas = computed(() => {
  const term = buscar.value.trim().toLowerCase()

  return [...ofertas.value]
    .filter((oferta) => {
      const matchesSearch = !term || [oferta.titulo, oferta.descripcion, oferta.modulo?.nombre, oferta.programa?.nombre, oferta.modulo?.programa?.nombre].some((value) => String(value || '').toLowerCase().includes(term))

      return matchesSearch
    })
    .sort((a, b) => new Date(b.created_at) - new Date(a.created_at))
})

async function load() {
  loading.value = true
  error.value = ''
  try {
    ofertas.value = await listOfertas({ buscar: buscar.value })
  } catch (exception) {
    ofertas.value = []
    error.value = exception.response?.data?.mensaje || exception.response?.data?.message || 'No se pudieron cargar los anuncios.'
  } finally {
    loading.value = false
  }
}

function selectOffer(oferta) {
  selected.value = oferta
  message.value = ''
  error.value = ''
}

function offerImage(oferta) {
  return oferta.imagen_publica || oferta.imagen || oferta.modulo?.imagen || ''
}

function handleOfferImageError(event) {
  event.currentTarget.style.display = 'none'
  event.currentTarget.closest('.offer-image-wrap')?.classList.add('image-failed')
}

function priceNumber(value) {
  return Number(value || 0)
}

function hasDiscount(oferta) {
  return priceNumber(oferta.modulo?.precio) > priceNumber(oferta.precio)
}

function discountPercent(oferta) {
  const original = priceNumber(oferta.modulo?.precio)
  const current = priceNumber(oferta.precio)

  if (!original || current >= original) return 0

  return Math.round(((original - current) / original) * 100)
}

function isOpen(oferta) {
  const today = new Date()
  today.setHours(0, 0, 0, 0)

  return new Date(`${oferta.fecha_limite_inscripcion}T00:00:00`) >= today
}

function backToList() {
  resetFlow()
}

async function submitInterest() {
  message.value = ''
  error.value = ''
  try {
    const payload = {
      ...form.value,
      anuncio_id: selected.value.external_anuncio_id || selected.value.id,
      modulo_id: selected.value.external_modulo_id,
    }

    const response = await registrarInteres(payload)
    form.value = { nombre: '', apellido: '', documento: '', correo: '', telefono: '', profesion: '', ubicacion: '' }
    showTemporaryNotice(response.mensaje || 'Interes registrado. Un vendedor se comunicara por WhatsApp.')
    resetFlow()
    await load()
  } catch (exception) {
    error.value = exception.response?.data?.mensaje || exception.response?.data?.message || 'No se pudo registrar el interes.'
  }
}

function resetFlow() {
  selected.value = null
  message.value = ''
  error.value = ''
}

function showTemporaryNotice(text) {
  notice.value = text

  if (noticeTimeout) {
    clearTimeout(noticeTimeout)
  }

  noticeTimeout = setTimeout(() => {
    notice.value = ''
  }, 4500)
}

function handleHeaderBack(event) {
  if (!selected.value) return

  event.detail.handled = true
  backToList()
}

onMounted(() => {
  window.addEventListener('crm:go-back', handleHeaderBack)
  load()
})

onBeforeUnmount(() => {
  window.removeEventListener('crm:go-back', handleHeaderBack)
})
</script>

<template>
  <section class="public-board">
    <div v-if="notice" class="temporary-toast success-message">{{ notice }}</div>

    <div v-if="!selected" class="board-heading">
      <div class="visitor-filters">
        <label class="visitor-search">
          <Search :size="22" />
          <input v-model="buscar" placeholder="Buscar modulo, programa o palabra clave..." />
        </label>
        <div class="visitor-stepper compact" aria-label="Proceso de solicitud">
          <div class="visitor-step" :class="{ active: step >= 1 }">
            <strong>1</strong>
            <div>
              <h3>Elegir modulo</h3>
              <p>Explora y selecciona el modulo de tu interes</p>
            </div>
          </div>
          <div class="visitor-step" :class="{ active: step >= 2 }">
            <strong>2</strong>
            <div>
              <h3>Registrar interes</h3>
              <p>Completa tus datos de contacto</p>
            </div>
          </div>
          <div class="visitor-step" :class="{ active: step >= 3 }">
            <strong>3</strong>
            <div>
              <h3>Atencion por WhatsApp</h3>
              <p>Un vendedor continua por WhatsApp</p>
            </div>
          </div>
        </div>
      </div>
    </div>

    <p v-if="!selected && error" class="error-message">{{ error }}</p>
    <div v-if="!selected && loading" class="muted">Cargando anuncios...</div>
    <div v-else-if="!selected" class="offer-grid">
      <article v-for="oferta in filteredOfertas" :key="oferta.id" class="offer-card">
        <div class="offer-image-wrap">
          <img v-if="offerImage(oferta)" :src="offerImage(oferta)" alt="" @error="handleOfferImageError" />
          <span class="offer-state-pill" :class="{ closed: !isOpen(oferta) }">{{ isOpen(oferta) ? 'Inscripciones abiertas' : 'Inscripciones cerradas' }}</span>
        </div>
        <div class="offer-body">
          <span>{{ oferta.modulo?.programa?.nombre }}</span>
          <h3>{{ oferta.modulo?.nombre || oferta.titulo }}</h3>
          <p>{{ oferta.descripcion }}</p>
          <div class="offer-meta">
            <span v-if="hasDiscount(oferta)" class="discount-badge">-{{ discountPercent(oferta) }}%</span>
            <small v-if="hasDiscount(oferta)" class="old-price">{{ oferta.modulo?.precio }} Bs</small>
            <small><Clock3 :size="16" /> {{ oferta.modulo?.duracion }}</small>
            <small><Coins :size="16" /> {{ oferta.precio }} Bs</small>
            <small><CalendarDays :size="16" /> Hasta {{ oferta.fecha_limite_inscripcion }}</small>
          </div>
          <button class="primary-inline" type="button" :disabled="!isOpen(oferta)" @click="selectOffer(oferta)">
            Solicitar modulo
            <ArrowRight :size="18" />
          </button>
        </div>
      </article>
      <section v-if="filteredOfertas.length === 0" class="empty-offers-state">
        <h3>No hay anuncios disponibles</h3>
        <p>Cuando existan modulos publicados con inscripcion vigente apareceran aqui.</p>
      </section>
      <div v-if="filteredOfertas.length" class="visitor-pagination">
        <p>Mostrando 1 a {{ filteredOfertas.length }} de {{ filteredOfertas.length }} modulos</p>
        <div>
          <button disabled>&lsaquo;</button>
          <button class="active">1</button>
          <button disabled>&rsaquo;</button>
        </div>
      </div>
    </div>

    <section v-if="selected" class="visitor-enrollment-flow">
      <div class="visitor-stepper selected-flow" aria-label="Proceso de solicitud">
        <div class="visitor-step active done">
          <strong><BadgeCheck :size="24" /></strong>
          <div>
            <h3>1. Elegir modulo</h3>
            <p>Modulo seleccionado</p>
          </div>
        </div>
        <span></span>
        <div class="visitor-step" :class="{ active: step === 2, done: step > 2 }">
          <strong><BadgeCheck v-if="step > 2" :size="24" /><template v-else>2</template></strong>
          <div>
            <h3>Registrar interes</h3>
            <p>{{ step > 2 ? 'Datos registrados' : 'Completa tus datos de contacto' }}</p>
          </div>
        </div>
        <span></span>
        <div class="visitor-step" :class="{ active: step >= 3 }">
          <strong>3</strong>
          <div>
            <h3>Atencion por WhatsApp</h3>
            <p>Recibe seguimiento por WhatsApp</p>
          </div>
        </div>
      </div>

      <section class="enrollment-screen">
        <section class="course-detail-panel visitor-detail-card">
          <div class="visitor-detail-image">
            <img v-if="offerImage(selected)" :src="offerImage(selected)" alt="" @error="handleOfferImageError" />
            <span class="offer-state-pill">Inscripciones abiertas</span>
          </div>
          <div class="course-detail-body">
            <p class="eyebrow">{{ selected.modulo?.programa?.nombre }}</p>
            <h2>{{ selected.modulo?.nombre }}</h2>
            <p class="muted">{{ selected.modulo?.descripcion || 'Modulo de prueba' }}</p>

            <dl class="course-detail-list visitor-detail-list">
              <div>
                <BookOpen :size="30" />
                <dt>Programa</dt>
                <dd>{{ selected.modulo?.programa?.nombre }}</dd>
              </div>
              <div>
                <Layers :size="30" />
                <dt>Duracion</dt>
                <dd>{{ selected.modulo?.duracion }}</dd>
              </div>
              <div>
                <Coins :size="30" />
                <dt>Inversion</dt>
                <dd>
                  <span v-if="hasDiscount(selected)" class="old-price">{{ selected.modulo?.precio }} Bs</span>
                  {{ selected.precio }} Bs
                </dd>
              </div>
              <div>
                <CalendarDays :size="30" />
                <dt>Inscripcion hasta</dt>
                <dd>{{ selected.fecha_limite_inscripcion }}</dd>
              </div>
            </dl>

            <section class="module-description">
              <div class="module-description-title">
                <CalendarDays :size="22" />
                <p class="eyebrow">Descripcion del modulo</p>
              </div>
              <p>{{ selected.modulo?.descripcion || selected.descripcion }}</p>
            </section>
          </div>
        </section>

        <aside class="enrollment-panel visitor-interest-panel">
          <form class="visitor-interest-card" @submit.prevent="submitInterest">
            <div class="visitor-interest-header">
              <div class="catalog-modal-icon">
                <FileText :size="38" />
              </div>
              <div>
                <h2>Registrar interes</h2>
                <p>Completa tus datos para continuar con el proceso de inscripcion.</p>
              </div>
            </div>
            <div class="selected-module-box">
              <span>Modulo seleccionado</span>
              <strong>{{ selected.modulo?.nombre }}</strong>
            </div>
            <div class="contact-section-title">
              <FileText :size="20" />
              <h3>Datos de contacto</h3>
            </div>
            <div class="visitor-contact-grid">
              <label>
                <span>Nombre <strong>*</strong></span>
                <input v-model="form.nombre" name="given-name" autocomplete="given-name" required placeholder="Ingresa tu nombre" />
              </label>
              <label>
                <span>Apellido <strong>*</strong></span>
                <input v-model="form.apellido" name="family-name" autocomplete="family-name" required placeholder="Ingresa tu apellido" />
              </label>
              <label>
                <span>Documento <strong>*</strong></span>
                <div class="split-input">
                  <select aria-label="Tipo de documento">
                    <option>CI</option>
                  </select>
                  <input v-model="form.documento" name="documento" autocomplete="off" required placeholder="Nro. de documento" />
                </div>
              </label>
              <label>
                <span>Telefono <strong>*</strong></span>
                <div class="split-input phone">
                  <strong>+591</strong>
                  <input v-model="form.telefono" name="tel-national" type="tel" inputmode="numeric" autocomplete="tel-national" required placeholder="Ej. 71234567" />
                </div>
              </label>
              <label>
                <span>Profesion <strong>*</strong></span>
                <input v-model="form.profesion" name="organization-title" autocomplete="organization-title" required placeholder="Ej. Ingeniero de sistemas" />
              </label>
              <label>
                <span>Ubicacion <strong>*</strong></span>
                <input v-model="form.ubicacion" name="address-level2" autocomplete="address-level2" required placeholder="Ej. Santa Cruz" />
              </label>
              <label class="visitor-email-field">
                <span>Correo electronico <strong>*</strong></span>
                <input v-model="form.correo" name="email" type="email" autocomplete="email" required placeholder="tu@email.com" />
              </label>
            </div>
            <p v-if="hasDiscount(selected)" class="success-message">Precio promocional: {{ selected.precio }} Bs. Precio regular: {{ selected.modulo?.precio }} Bs.</p>
            <p v-if="error" class="error-message">{{ error }}</p>
            <button class="primary-inline visitor-pay-action" type="submit">
              Enviar interes
              <ArrowRight :size="20" />
            </button>
          </form>
        </aside>
      </section>
    </section>
  </section>
</template>
