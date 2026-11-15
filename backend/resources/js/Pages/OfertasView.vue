<script setup>
import { apiErrorMessage } from '../services/errors'
import { computed, onBeforeUnmount, onMounted, ref } from 'vue'
import { ArrowLeft, ArrowRight, BadgeCheck, BookOpen, CalendarDays, Clock3, Coins, FileText, Layers, Search } from '@lucide/vue'
import { listOfertas, registrarInteres } from '../services/api'

const ofertas = ref([])
const buscar = ref('')
const loading = ref(true)
const submitting = ref(false)
const selected = ref(null)
const programa = ref(null)
const fullProgram = ref(false)
const message = ref('')
const error = ref('')
const form = ref({ nombre: '', apellido: '', documento: '', correo: '', telefono: '', profesion: '', ubicacion: '' })
const notice = ref('')
let noticeTimeout = null

const step = computed(() => {
  if (selected.value || fullProgram.value) return 2
  return 1
})
const inDetail = computed(() => Boolean(selected.value || fullProgram.value))
// La oferta se muestra por programa: asi se interesa al visitante en la malla completa.
const programas = computed(() => {
  const groups = new Map()
  ofertas.value.forEach((oferta) => {
    const info = oferta.programa || oferta.modulo?.programa
    if (!info) return
    if (!groups.has(info.id)) groups.set(info.id, { ...info, ofertas: [] })
    groups.get(info.id).ofertas.push(oferta)
  })
  return [...groups.values()].map((group) => ({
    ...group,
    total: group.ofertas.reduce((sum, oferta) => sum + priceNumber(oferta.precio), 0),
  }))
})
const filteredProgramas = computed(() => {
  const term = buscar.value.trim().toLowerCase()
  if (!term) return programas.value

  return programas.value.filter((item) => [item.nombre, item.descripcion, ...item.ofertas.map((oferta) => oferta.modulo?.nombre)]
    .some((value) => String(value || '').toLowerCase().includes(term)))
})

async function load() {
  loading.value = true
  error.value = ''
  try {
    ofertas.value = await listOfertas()
  } catch (exception) {
    ofertas.value = []
    error.value = apiErrorMessage(exception, 'No se pudieron cargar los anuncios.')
  } finally {
    loading.value = false
  }
}

function toTop() {
  window.scrollTo({ top: 0 })
}

function selectProgram(item) {
  toTop()
  programa.value = item
  message.value = ''
  error.value = ''
}

function selectOffer(oferta) {
  toTop()
  selected.value = oferta
  fullProgram.value = false
  message.value = ''
  error.value = ''
}

function selectFullProgram() {
  toTop()
  selected.value = null
  fullProgram.value = true
  message.value = ''
  error.value = ''
}

function programOpen(item) {
  return item.ofertas.some(isOpen)
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
  toTop()
  if (inDetail.value) {
    selected.value = null
    fullProgram.value = false
  } else {
    programa.value = null
  }
  message.value = ''
  error.value = ''
}

async function submitInterest() {
  if (submitting.value) return
  submitting.value = true
  message.value = ''
  error.value = ''
  try {
    const payload = fullProgram.value
      ? { ...form.value, programa_id: programa.value.id }
      : {
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
    error.value = apiErrorMessage(exception, 'No se pudo registrar el interes.')
  } finally {
    submitting.value = false
  }
}

function resetFlow() {
  selected.value = null
  fullProgram.value = false
  programa.value = null
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
  if (!programa.value) return

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

    <div v-if="!inDetail && !programa" class="board-heading">
      <div class="visitor-filters">
        <label class="visitor-search">
          <Search :size="22" />
          <input v-model="buscar" aria-label="Buscar programa o modulo" placeholder="Buscar programa, modulo o palabra clave..." />
        </label>
        <div class="visitor-stepper compact" aria-label="Proceso de solicitud">
          <div class="visitor-step" :class="{ active: step >= 1 }">
            <strong>1</strong>
            <div>
              <h3>Elegir programa</h3>
              <p>Completo o uno de sus modulos</p>
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

    <p v-if="!inDetail && error" class="error-message">{{ error }}</p>
    <div v-if="!inDetail && loading" class="muted">Cargando programas...</div>

    <div v-else-if="!programa" class="offer-grid">
      <article v-for="item in filteredProgramas" :key="item.id" class="offer-card">
        <div class="offer-image-wrap">
          <img v-if="item.imagen" :src="item.imagen" alt="" @error="handleOfferImageError" />
          <span class="offer-state-pill" :class="{ closed: !programOpen(item) }">{{ programOpen(item) ? 'Inscripciones abiertas' : 'Inscripciones cerradas' }}</span>
        </div>
        <div class="offer-body">
          <span>{{ item.ofertas.length }} modulos</span>
          <h3>{{ item.nombre }}</h3>
          <p>{{ item.descripcion }}</p>
          <div class="offer-meta">
            <small><Layers :size="16" /> {{ item.ofertas.map((oferta) => oferta.modulo?.nombre).slice(0, 3).join(', ') }}{{ item.ofertas.length > 3 ? '...' : '' }}</small>
            <small><Coins :size="16" /> {{ item.total }} Bs el programa</small>
          </div>
          <button class="primary-inline" type="button" @click="selectProgram(item)">
            Ver programa
            <ArrowRight :size="18" />
          </button>
        </div>
      </article>
      <section v-if="filteredProgramas.length === 0" class="empty-offers-state">
        <h3>No hay programas disponibles</h3>
        <p>{{ buscar ? 'Ningun programa o modulo coincide con la busqueda.' : 'Cuando existan programas con inscripcion vigente apareceran aqui.' }}</p>
      </section>
    </div>

    <template v-else-if="!inDetail">
      <section class="table-surface program-overview">
        <div class="program-overview-copy">
          <button class="secondary-button compact-button" type="button" @click="backToList">
            <ArrowLeft :size="16" />
            Todos los programas
          </button>
          <h2>{{ programa.nombre }}</h2>
          <p>{{ programa.descripcion }}</p>
          <p class="program-overview-facts">
            <span><Layers :size="17" /> {{ programa.ofertas.length }} modulos</span>
            <span><Coins :size="17" /> {{ programa.total }} Bs el programa completo</span>
          </p>
        </div>
        <button class="primary-inline" type="button" :disabled="!programOpen(programa)" @click="selectFullProgram">
          Me interesa el programa completo
          <ArrowRight :size="18" />
        </button>
      </section>

      <div class="offer-grid">
        <article v-for="(oferta, index) in programa.ofertas" :key="oferta.id" class="offer-card">
          <div class="offer-image-wrap">
            <img v-if="offerImage(oferta)" :src="offerImage(oferta)" alt="" @error="handleOfferImageError" />
            <span class="offer-state-pill" :class="{ closed: !isOpen(oferta) }">{{ isOpen(oferta) ? 'Inscripciones abiertas' : 'Inscripciones cerradas' }}</span>
          </div>
          <div class="offer-body">
            <span>Modulo {{ index + 1 }} de {{ programa.ofertas.length }}</span>
            <h3>{{ oferta.modulo?.nombre || oferta.titulo }}</h3>
            <p>{{ oferta.descripcion }}</p>
            <div class="offer-meta">
              <span v-if="hasDiscount(oferta)" class="discount-badge">-{{ discountPercent(oferta) }}%</span>
              <small v-if="hasDiscount(oferta)" class="old-price">{{ oferta.modulo?.precio }} Bs</small>
              <small><Clock3 :size="16" /> {{ oferta.modulo?.duracion }}</small>
              <small><Coins :size="16" /> {{ oferta.precio }} Bs</small>
              <small><CalendarDays :size="16" /> Hasta {{ oferta.fecha_limite_inscripcion }}</small>
            </div>
            <button class="secondary-button" type="button" :disabled="!isOpen(oferta)" @click="selectOffer(oferta)">
              Ver detalle del modulo
              <ArrowRight :size="18" />
            </button>
          </div>
        </article>
      </div>
    </template>

    <section v-if="inDetail" class="visitor-enrollment-flow">
      <div class="visitor-stepper selected-flow" aria-label="Proceso de solicitud">
        <div class="visitor-step active done">
          <strong><BadgeCheck :size="24" /></strong>
          <div>
            <h3>1. Elegir programa</h3>
            <p>{{ fullProgram ? 'Programa completo' : 'Modulo seleccionado' }}</p>
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
        <section v-if="selected" class="course-detail-panel visitor-detail-card">
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

        <section v-else class="course-detail-panel visitor-detail-card">
          <div class="visitor-detail-image">
            <img v-if="programa.imagen" :src="programa.imagen" alt="" @error="handleOfferImageError" />
            <span class="offer-state-pill">Inscripciones abiertas</span>
          </div>
          <div class="course-detail-body">
            <h2>{{ programa.nombre }}</h2>
            <p class="muted">{{ programa.descripcion }}</p>

            <dl class="course-detail-list visitor-detail-list">
              <div>
                <Layers :size="30" />
                <dt>Modulos</dt>
                <dd>{{ programa.ofertas.length }}</dd>
              </div>
              <div>
                <Coins :size="30" />
                <dt>Inversion total</dt>
                <dd>{{ programa.total }} Bs</dd>
              </div>
            </dl>

            <section class="module-description">
              <div class="module-description-title">
                <BookOpen :size="22" />
                <h3>Modulos del programa</h3>
              </div>
              <ol class="program-module-list">
                <li v-for="oferta in programa.ofertas" :key="oferta.id">
                  <strong>{{ oferta.modulo?.nombre }}</strong>
                  <small>{{ oferta.modulo?.duracion }} · {{ oferta.precio }} Bs</small>
                </li>
              </ol>
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
              <span>{{ fullProgram ? 'Programa completo' : 'Modulo seleccionado' }}</span>
              <strong>{{ fullProgram ? `${programa.nombre} (${programa.ofertas.length} modulos)` : selected.modulo?.nombre }}</strong>
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
            <p v-if="selected && hasDiscount(selected)" class="success-message">Precio promocional: {{ selected.precio }} Bs. Precio regular: {{ selected.modulo?.precio }} Bs.</p>
            <p v-if="error" class="error-message">{{ error }}</p>
            <button class="primary-inline visitor-pay-action" type="submit" :disabled="submitting">
              Enviar interes
              <ArrowRight :size="20" />
            </button>
          </form>
        </aside>
      </section>
    </section>
  </section>
</template>
