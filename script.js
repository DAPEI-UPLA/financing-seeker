window.onload = function () {
  setInterval(recargarTarjetasCada30Min, 30 * 60 * 1000);

  cargarYMostrar('fondos_gob.json', 'fondos_gob');
  cargarYMostrar('fondos_anid.json', 'anid');
  cargarYMostrar('fondos_cultura.json', 'cultura');
  cargarYMostrar('concursos_gore_valparaiso.json', 'gore_valparaiso');
  cargarYMostrar('google_search_results.json', 'portales');

  // NUEVA COLUMNA → USANDO resultado.json
  cargarYMostrar('resultado.json', 'licitaciones');
};


function cargarYMostrar(jsonFile, tipo) {
  fetch(`${jsonFile}?t=${new Date().getTime()}`)
    .then(res => res.json())
    .then(data => {

      if (!Array.isArray(data)) data = [data];

      const contenedor = document.querySelector(`#${tipo} .tarjetas`);
      if (!contenedor) return;

      contenedor.innerHTML = '';

      data.forEach(fondo => {

        // Normalización general
        if (fondo.fecha_inicio) fondo.fecha_inicio = normalizarFecha(fondo.fecha_inicio);
        if (fondo.fecha_cierre) fondo.fecha_cierre = normalizarFecha(fondo.fecha_cierre);
        if (fondo.fecha_termino) fondo.fecha_termino = normalizarFecha(fondo.fecha_termino);
        if (fondo.fechas) fondo.fechas = normalizarFecha(fondo.fechas);
        if (fondo["fecha de busqueda"]) fondo["fecha de busqueda"] = normalizarFecha(fondo["fecha de busqueda"]);

        const tarjeta = document.createElement('div');
        tarjeta.className = `tarjeta tarjeta-${tipo}`;

        let diasRestantes = null;
        let mensajeDias = '';

        //-----------------------------
        // CÁLCULO DE DÍAS RESTANTES
        //-----------------------------
        if (tipo === 'fondos_gob' && fondo.fechas) {

          const match = /Fin:\s*(\d{1,2} de [a-z]+ de \d{4})/i.exec(fondo.fechas);
          if (match && match[1]) diasRestantes = calcularDiasRestantes(match[1]);

        } else if (tipo === 'anid' && fondo.fecha_cierre) {

          const fecha = fondo.fecha_cierre.replace(/,\s*/g, ' de ');
          diasRestantes = calcularDiasRestantes(fecha);

        } else if (tipo === 'cultura' && fondo.fecha_cierre) {

          const fecha = fondo.fecha_cierre.replace(/,\s*/g, ' de ');
          diasRestantes = calcularDiasRestantes(fecha);

        } else if (tipo === 'gore_valparaiso' && fondo.fecha_termino) {

          diasRestantes = calcularDiasRestantes(fondo.fecha_termino);

        } else if (tipo === 'licitaciones' && fondo.FechaCierre) {

          const fecha = new Date(fondo.FechaCierre);
          const meses = ['enero','febrero','marzo','abril','mayo','junio','julio','agosto','septiembre','octubre','noviembre','diciembre'];

          fondo._fechaCierreFormateada = `${fecha.getDate()} de ${meses[fecha.getMonth()]} de ${fecha.getFullYear()}`;
          diasRestantes = calcularDiasRestantes(fondo._fechaCierreFormateada);
        }

        //-----------------------------
        // COLORES / MENSAJE DE DÍAS
        //-----------------------------
        if (diasRestantes !== null) {
          if (diasRestantes >= 5 && diasRestantes <= 7) {
            tarjeta.classList.add('tarjeta-amarilla');
            mensajeDias = `<p class="dias-restantes amarillo"><strong>¡Quedan ${diasRestantes} días!</strong></p>`;
          } else if (diasRestantes >= 0 && diasRestantes <= 4) {
            tarjeta.classList.add('tarjeta-roja');
            mensajeDias = `<p class="dias-restantes rojo"><strong>¡Últimos ${diasRestantes} días!</strong></p>`;
          } else if (diasRestantes < 0) {
            mensajeDias = `<p class="dias-restantes cerrado"><strong>Plazo cerrado</strong></p>`;
          }
        }

        //-----------------------------
        // TARJETAS ESPECÍFICAS
        //-----------------------------

        if (tipo === 'fondos_gob') {
          tarjeta.innerHTML = `
            <h3>${fondo.nombre || 'Sin nombre'}</h3>
            <p><strong>Estado:</strong> ${fondo.estado || 'No especificado'}</p>
            <p><strong>Ubicación:</strong> ${fondo.ubicacion || 'No especificada'}</p>
            <p><strong>Fechas:</strong> ${fondo.fechas || 'No especificadas'}</p>
            ${mensajeDias}
            <a href="${fondo.link || '#'}" target="_blank" class="btn-link">Ver más</a>
          `;

        } else if (tipo === 'anid') {
          tarjeta.innerHTML = `
            <h3>${fondo.titulo || 'Sin título'}</h3>
            <p><strong>Subdirección:</strong> ${fondo.subdireccion || 'No especificada'}</p>
            <p><strong>Inicio:</strong> ${fondo.fecha_inicio || 'No especificado'}</p>
            <p><strong>Cierre:</strong> ${fondo.fecha_cierre || 'No especificado'}</p>
            ${mensajeDias}
            <a href="${fondo.enlace_ver_mas || '#'}" target="_blank" class="btn-link">Ver más</a>
          `;

        } else if (tipo === 'cultura') {
          tarjeta.innerHTML = `
            <h3>${fondo.titulo || 'Sin título'}</h3>
            <p><strong>Categoría:</strong> ${fondo.categoria || 'No especificada'}</p>
            <p><strong>Cierre:</strong> ${fondo.fecha_cierre || 'No especificado'}</p>
            ${mensajeDias}
            <a href="${fondo.enlace || '#'}" target="_blank" class="btn-link">Ver más</a>
          `;

        } else if (tipo === 'gore_valparaiso') {
          tarjeta.innerHTML = `
            <h3>${fondo.titulo || 'Sin título'}</h3>
            <p><strong>Inicio:</strong> ${fondo.fecha_inicio || 'No especificado'}</p>
            <p><strong>Término:</strong> ${fondo.fecha_termino || 'No especificado'}</p>
            ${mensajeDias}
          `;

        } else if (tipo === 'portales') {
          tarjeta.innerHTML = `
            <h3>${fondo.titulo || 'Sin título'}</h3>
            <p><strong>Fecha búsqueda:</strong> ${fondo["fecha de busqueda"] || 'No especificada'}</p>
            <p><strong>Sitio Web:</strong> ${fondo["sitio"] || 'No especificada'}</p>
            <a href="${fondo.link || '#'}" target="_blank" class="btn-link">Ir al portal</a>
          `;

        //-----------------------------
        // NUEVA TARJETA → LICITACIONES
        //-----------------------------
        } else if (tipo === 'licitaciones') {
          tarjeta.innerHTML = `
            <h3>${fondo.Nombre || 'Sin nombre'}</h3>
            <p><strong>Código:</strong> ${fondo.CodigoExterno || 'No especificado'}</p>
            <p><strong>Cierre:</strong> ${fondo._fechaCierreFormateada || 'No especificada'}</p>
            ${mensajeDias}
            <a href="${fondo.UrlPublica || '#'}" target="_blank" class="btn-link">Ver licitación</a>
          `;
        }

        contenedor.appendChild(tarjeta);
      });
    })
    .catch(error => {
      console.error(`Error cargando ${jsonFile}:`, error);
      const cont = document.querySelector(`#${tipo} .tarjetas`);
      if (cont) cont.innerHTML = `<p>Error al cargar ${jsonFile}</p>`;
    });
}



// =======================================================
//   AUTO-SCROLL GLOBAL
// =======================================================
function iniciarScrollGlobal() {
  const scrollContainers = Array.from(document.querySelectorAll(".tarjetas"));
  const btnScroll = document.getElementById("btn-scroll-toggle");

  let isScrolling = false;
  let scrollInterval;

  function startScroll() {
    if (scrollInterval) return;
    scrollInterval = setInterval(() => {
      scrollContainers.forEach(container => {
        container.scrollTop += 1;
        if (container.scrollTop >= container.scrollHeight - container.clientHeight) {
          container.scrollTop = 0;
        }
      });
    }, 40);
  }

  function stopScroll() {
    clearInterval(scrollInterval);
    scrollInterval = null;
  }

  btnScroll.addEventListener("click", () => {
    if (!isScrolling) {
      startScroll();
      isScrolling = true;
      btnScroll.textContent = "⏸️";
    } else {
      stopScroll();
      isScrolling = false;
      btnScroll.textContent = "▶️";
    }
  });
}

document.addEventListener("DOMContentLoaded", () => {
  setTimeout(iniciarScrollGlobal, 1500);
});



// =======================================================
//   FUNCIONES DE APOYO
// =======================================================

function calcularDiasRestantes(fechaStr) {
  if (!fechaStr) return null;

  const meses = {
    'enero': 1,'febrero': 2,'marzo': 3,'abril': 4,
    'mayo': 5,'junio': 6,'julio': 7,'agosto': 8,
    'septiembre': 9,'octubre': 10,'noviembre': 11,'diciembre': 12
  };

  const regex = /(\d{1,2}) de ([a-z]+) de (\d{4})/i;
  const match = fechaStr.match(regex);
  if (!match) return null;

  const dia = parseInt(match[1]);
  const mes = meses[match[2]];
  const anio = parseInt(match[3]);

  const fechaFinal = new Date(anio, mes - 1, dia);
  const hoy = new Date();
  hoy.setHours(0,0,0,0);
  fechaFinal.setHours(0,0,0,0);

  const diffTime = fechaFinal - hoy;
  return Math.ceil(diffTime / (1000 * 60 * 60 * 24));
}


function normalizarFecha(textoFecha) {
  if (!textoFecha || typeof textoFecha !== 'string') return textoFecha;

  const meses = ['enero','febrero','marzo','abril','mayo','junio','julio','agosto',
                 'septiembre','octubre','noviembre','diciembre'];

  return textoFecha.replace(
    /(\d{1,2})[\/\-](\d{1,2})(?:[\/\-](\d{2,4}))?/g,
    (match, d, m, y) => {
      const dia = parseInt(d);
      const mes = parseInt(m);
      const anio =
        y ? parseInt(y.length === 2 ? '20' + y : y) : new Date().getFullYear();

      if (mes >= 1 && mes <= 12 && dia >= 1 && dia <= 31) {
        return `${dia} de ${meses[mes - 1]} de ${anio}`;
      }
      return match;
    }
  );
}



function capitalizarTarjetas() {
  document.querySelectorAll('.tarjeta h3, .tarjeta p').forEach(el => {
    const texto = el.textContent.trim();
    if (texto.length > 0) {
      el.textContent = texto
        .toLowerCase()
        .replace(/(^|\s|:)\S/g, l => l.toUpperCase());
    }
  });
}

document.addEventListener('DOMContentLoaded', () => {
  setTimeout(capitalizarTarjetas, 2000);
});



// =======================================================
//   RECARGA CADA 30 MIN
// =======================================================

function recargarTarjetasCada30Min() {
  const tipos = [
    'fondos_gob',
    'anid',
    'cultura',
    'gore_valparaiso',
    'portales',
    'licitaciones'  // ← NUEVO
  ];

  tipos.forEach(tipo => {
    let archivo = '';

    switch (tipo) {
      case 'fondos_gob': archivo = 'fondos_gob.json'; break;
      case 'anid': archivo = 'fondos_anid.json'; break;
      case 'cultura': archivo = 'fondos_cultura.json'; break;
      case 'gore_valparaiso': archivo = 'concursos_gore_valparaiso.json'; break;
      case 'portales': archivo = 'google_search_results.json'; break;
      case 'licitaciones': archivo = 'resultado.json'; break; // ← NUEVO
    }

    cargarYMostrar(archivo, tipo);
  });
}
