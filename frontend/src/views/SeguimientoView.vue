<script setup>
import { computed, onMounted, ref } from 'vue'
import { BadgeDollarSign, CheckCircle2, Clock3, CreditCard, GraduationCap, RefreshCw, WalletCards } from '@lucide/vue'
import { getResumenComisiones, listComisiones, listOrdenesPago, pagarComisionesVendedor } from '../services/api'
import { authState } from '../services/auth'

const ordenes = ref([])
const comisiones = ref([])
const vendedores = ref([])
const ranking = ref([])
const error = ref('')
const loading = ref(true)

const ventasAprobadas = computed(() => ordenes.value.filter((orden) => orden.estado === 'Pago aprobado'))
const cursosVendidos = computed(() => ventasAprobadas.value.reduce((total, orden) => total + (orden.items?.length || 0), 0))
const ventaTotal = computed(() => ventasAprobadas.value.reduce((total, orden) => total + Number(orden.total || 0), 0))
const comisionTotal = computed(() => comisiones.value.reduce((total, comision) => total + Number(comision.monto || 0), 0))
const comisionPendiente = computed(() => comisiones.value.filter((comision) => comision.estado === 'Pendiente').reduce((total, comision) => total + Number(comision.monto || 0), 0))
const comisionRecibida = computed(() => comisiones.value.filter((comision) => comision.estado === 'Pagada').reduce((total, comision) => total + Number(comision.monto || 0), 0))
const canManageCommissions = computed(() => ['administrador', 'coordinador'].includes(authState.usuario?.rol))
const sellerRows = computed(() => {
  if (vendedores.value.length) {
    return vendedores.value.map((vendedor) => ({
      ...vendedor,
      cursos_vendidos: vendedor.comisiones_count || 0,
      comision_total: Number(vendedor.comision_total || 0),
      comision_pendiente: Number(vendedor.comision_pendiente || 0),
      comision_recibida: Number(vendedor.comision_total || 0) - Number(vendedor.comision_pendiente || 0),
    }))
  }

  const bySeller = new Map()
  comisiones.value.forEach((comision) => {
    const id = comision.vendedor_id || comision.vendedor?.id || authState.usuario?.id
    if (!bySeller.has(id)) {
      bySeller.set(id, {
        id,
        nombre: comision.vendedor?.nombre || authState.usuario?.nombre || 'Vendedor',
        apellido: comision.vendedor?.apellido || authState.usuario?.apellido || '',
        cursos_vendidos: 0,
        comision_total: 0,
        comision_pendiente: 0,
        comision_recibida: 0,
      })
    }
    const row = bySeller.get(id)
    row.cursos_vendidos += 1
    row.comision_total += Number(comision.monto || 0)
    if (comision.estado === 'Pendiente') row.comision_pendiente += Number(comision.monto || 0)
    if (comision.estado === 'Pagada') row.comision_recibida += Number(comision.monto || 0)
  })

  return [...bySeller.values()]
})

async function load() {
  loading.value = true
  error.value = ''
  try {
    const [ordenData, comisionData, resumenData] = await Promise.all([
      listOrdenesPago(),
      listComisiones(),
      canManageCommissions.value ? getResumenComisiones().catch(() => null) : Promise.resolve(null),
    ])
    ordenes.value = ordenData
    comisiones.value = comisionData
    vendedores.value = resumenData?.vendedores || []
    ranking.value = resumenData?.ranking_ventas || []
  } catch (exception) {
    error.value = exception.response?.data?.mensaje || exception.response?.data?.message || 'No se pudo cargar el seguimiento comercial.'
  } finally {
    loading.value = false
  }
}

async function markPaid(vendedor) {
  if (!canManageCommissions.value) return
  await pagarComisionesVendedor(vendedor.id)
  await load()
}

function money(value) {
  return `${Number(value || 0).toFixed(2)} Bs`
}

function prospectName(orden) {
  return [orden.prospecto?.nombre, orden.prospecto?.apellido].filter(Boolean).join(' ') || 'Sin prospecto'
}

function sellerName(orden) {
  return [orden.vendedor?.nombre, orden.vendedor?.apellido].filter(Boolean).join(' ') || 'Sin vendedor'
}

function paymentBadgeClass(estado) {
  if (estado === 'Pago aprobado') return 'success'
  if (estado === 'En revision') return 'warning'
  if (estado === 'Pago rechazado') return 'danger'
  return 'neutral'
}

function commissionBadgeClass(estado) {
  if (estado === 'Pagada') return 'success'
  if (estado === 'Pendiente') return 'warning'
  return 'neutral'
}

onMounted(load)
</script>

<template>
  <section class="public-board sales-page">
    <section class="table-surface sales-hero-panel">
      <div class="table-header">
        <div>
          <p class="eyebrow">Ventas y comisiones</p>
          <h2>Ventas, pagos y comisiones</h2>
          <p>Consulta pagos aprobados, cursos vendidos y comisiones del 2%.</p>
        </div>
        <button class="secondary-button" type="button" @click="load">
          <RefreshCw :size="17" />
          Actualizar
        </button>
      </div>
      <p v-if="error" class="error-message">{{ error }}</p>
      <p v-if="loading" class="muted">Cargando seguimiento...</p>
    </section>

    <section class="sales-metrics-grid">
      <article class="sales-metric-card">
        <div><GraduationCap :size="20" /></div>
        <span>Cursos vendidos</span>
        <strong>{{ cursosVendidos }}</strong>
        <small>Total confirmado</small>
      </article>
      <article class="sales-metric-card">
        <div><CreditCard :size="20" /></div>
        <span>Ventas aprobadas</span>
        <strong>{{ money(ventaTotal) }}</strong>
        <small>Valor vendido</small>
      </article>
      <article class="sales-metric-card">
        <div><BadgeDollarSign :size="20" /></div>
        <span>Comision total</span>
        <strong>{{ money(comisionTotal) }}</strong>
        <small>Historico generado</small>
      </article>
      <article class="sales-metric-card">
        <div><Clock3 :size="20" /></div>
        <span>Comision pendiente</span>
        <strong>{{ money(comisionPendiente) }}</strong>
        <small>Por pagar</small>
      </article>
      <article class="sales-metric-card">
        <div><WalletCards :size="20" /></div>
        <span>Comision recibida</span>
        <strong>{{ money(comisionRecibida) }}</strong>
        <small>Ya cobrada</small>
      </article>
    </section>

    <section class="table-surface sales-panel">
      <div class="table-header">
        <div>
          <p class="eyebrow">Vendedores</p>
          <h2>Resumen de ventas y comisiones</h2>
        </div>
        <span class="sales-count">{{ sellerRows.length }} vendedor(es)</span>
      </div>
      <div class="table-wrap sales-table-wrap">
        <table class="sales-table">
          <thead>
            <tr>
              <th>Vendedor</th>
              <th>Cursos vendidos</th>
              <th>Comision total</th>
              <th>Comision pendiente</th>
              <th>Comision recibida</th>
              <th v-if="canManageCommissions">Accion</th>
            </tr>
          </thead>
          <tbody>
            <tr v-for="vendedor in sellerRows" :key="vendedor.id">
              <td>{{ vendedor.nombre }} {{ vendedor.apellido }}</td>
              <td>{{ vendedor.cursos_vendidos }}</td>
              <td><strong>{{ money(vendedor.comision_total) }}</strong></td>
              <td><span class="amount-chip pending">{{ money(vendedor.comision_pendiente) }}</span></td>
              <td><span class="amount-chip paid">{{ money(vendedor.comision_recibida) }}</span></td>
              <td v-if="canManageCommissions" class="row-actions">
                <button class="commission-action" :disabled="Number(vendedor.comision_pendiente || 0) === 0" @click="markPaid(vendedor)">
                  <CheckCircle2 :size="16" />
                  Marcar recibida
                </button>
              </td>
            </tr>
            <tr v-if="sellerRows.length === 0">
              <td :colspan="canManageCommissions ? 6 : 5">Sin comisiones registradas.</td>
            </tr>
          </tbody>
        </table>
      </div>
    </section>

    <section class="sales-two-column">
      <section class="table-surface sales-panel">
      <div class="table-header">
        <div>
          <p class="eyebrow">Ordenes de pago</p>
          <h2>Pagos y cursos asociados</h2>
        </div>
      </div>
      <div class="table-wrap sales-table-wrap">
        <table class="sales-table">
          <thead>
            <tr>
              <th>Orden</th>
              <th>Prospecto</th>
              <th>Vendedor</th>
              <th>Cursos</th>
              <th>Total</th>
              <th>Pago</th>
            </tr>
          </thead>
          <tbody>
            <tr v-for="orden in ordenes" :key="orden.id">
              <td>#{{ orden.id }}</td>
              <td>{{ prospectName(orden) }}</td>
              <td>{{ sellerName(orden) }}</td>
              <td>
                <div class="stacked-cell">
                  <span v-for="item in orden.items" :key="item.id">{{ item.modulo_nombre }}</span>
                </div>
              </td>
              <td>{{ money(orden.total) }}</td>
              <td><span class="badge" :class="paymentBadgeClass(orden.pago?.estado || orden.estado)">{{ orden.pago?.estado || orden.estado }}</span></td>
            </tr>
            <tr v-if="ordenes.length === 0">
              <td colspan="6">Sin ordenes de pago registradas.</td>
            </tr>
          </tbody>
        </table>
      </div>
    </section>

    <section class="table-surface sales-panel">
      <div class="table-header">
        <div>
          <p class="eyebrow">Comisiones</p>
          <h2>Detalle por curso vendido</h2>
        </div>
        <span class="sales-count">{{ money(comisionTotal) }} historico</span>
      </div>
      <div class="table-wrap sales-table-wrap">
        <table class="sales-table">
          <thead>
            <tr>
              <th>Curso</th>
              <th>Vendedor</th>
              <th>Porcentaje</th>
              <th>Monto</th>
              <th>Estado</th>
              <th>Fecha recibida</th>
            </tr>
          </thead>
          <tbody>
            <tr v-for="comision in comisiones" :key="comision.id">
              <td>{{ comision.venta?.modulo_nombre }}</td>
              <td>{{ comision.vendedor?.nombre }} {{ comision.vendedor?.apellido }}</td>
              <td>{{ Number(comision.porcentaje || 0).toFixed(0) }}%</td>
              <td><span class="amount-chip" :class="comision.estado === 'Pagada' ? 'paid' : 'pending'">{{ money(comision.monto) }}</span></td>
              <td><span class="badge" :class="commissionBadgeClass(comision.estado)">{{ comision.estado }}</span></td>
              <td>{{ comision.fecha_pago ? new Date(comision.fecha_pago).toLocaleString('es-BO') : 'Pendiente' }}</td>
            </tr>
            <tr v-if="comisiones.length === 0">
              <td colspan="6">Sin comisiones registradas.</td>
            </tr>
          </tbody>
        </table>
      </div>
    </section>
    </section>
  </section>
</template>
