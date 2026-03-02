window.onload = function () {
  setInterval(recargarTarjetasCada30Min, 30 * 60 * 1000);

  const tipos = [
    { archivo: 'fondos_gob.json', tipo: 'fondos_gob' },
    { archivo: 'fondos_anid.json', tipo: 'anid' },
    { archivo: 'fondos_cultura.json', tipo: 'cultura' },
    { archivo: 'concursos_gore_valparaiso.json', tipo: 'gore_valparaiso' },
    { archivo: 'google_search_results.json', tipo: 'portales' },
  ];

  tipos.forEach(({ archivo, tipo }) => cargarYMostrar(archivo, tipo));
};

function cargarYMostrar(jsonFile, tipo) {
  fetch(`${jsonFile}?t=${new Date().getTime()}`)
    .then(res => res.json())
    .then(data => {
      if (!Array.isArray(data)) data = [data];
      const contenedor = document.querySelector("#tarjetas-combinadas");
      if (!contenedor) return;

      data.forEach(fondo => {
        // Normalizar fechas si existen
        for (let campo of ['fecha_inicio', 'fecha_cierre', 'fecha_termino', 'fechas', 'fecha de busqueda']) {
          if (fondo[campo]) fondo[campo] = normalizarFecha(fondo[campo]);
        }

        const tarjeta = document.createElement('div');
        tarjeta.className = `tarjeta tarjeta-${tipo}`;

        let diasRestantes = null;
        let mensajeDias = '';

        // Calcular días restantes según tipo
        if (tipo === 'fondos_gob' && fondo.fechas) {
          const match = /Fin:\s*(\d{1,2} de [a-z]+ de \d{4})/i.exec(fondo.fechas);
          if (match && match[1]) diasRestantes = calcularDiasRestantes(match[1]);
        } else if (['anid', 'cultura'].includes(tipo) && fondo.fecha_cierre) {
          diasRestantes = calcularDiasRestantes(fondo.fecha_cierre.replace(/,\s*/g, ' de '));
        } else if (tipo === 'gore_valparaiso' && fondo.fecha_termino) {
          diasRestantes = calcularDiasRestantes(fondo.fecha_termino);
        }

        // Determinar estilo de días
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

        // Generar contenido HTML de la tarjeta según su tipo
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
        }else if (tipo === 'portales') {
          tarjeta.setAttribute('data-consulta', fondo.consulta?.trim() || '');
          tarjeta.innerHTML = `
            <h3>${fondo.titulo || 'Sin título'}</h3>
            <p><strong>Fecha de búsqueda:</strong> ${fondo["fecha de busqueda"] || 'No especificada'}</p>
            <p><strong>Sitio Web:</strong> ${fondo["sitio"] || 'No especificada'}</p>
            <a href="${fondo.link || '#'}" target="_blank" class="btn-link">Ir al portal</a>
          `;
        }

        
        const textoParaFiltrado = `
          ${fondo.nombre || ''}
          ${fondo.estado || ''}
          ${fondo.ubicacion || ''}
          ${fondo.fechas || ''}
          ${fondo.fecha_inicio || ''}
          ${fondo.fecha_cierre || ''}
          ${fondo.fecha_termino || ''}
          ${fondo.titulo || ''}
          ${fondo.subdireccion || ''}
          ${fondo.categoria || ''}
          ${fondo["fecha de busqueda"] || ''}
          ${fondo.sitio || ''}
          ${fondo.consulta || ''}
        `.toLowerCase();

        tarjeta.setAttribute('data-filtro-texto', textoParaFiltrado);

        contenedor.appendChild(tarjeta);
      });
    })
    .catch(error => {
      console.error(`Error cargando ${jsonFile}:`, error);
    });
}


function calcularDiasRestantes(fechaStr) {
  const meses = {
    'enero': 1, 'febrero': 2, 'marzo': 3, 'abril': 4,
    'mayo': 5, 'junio': 6, 'julio': 7, 'agosto': 8,
    'septiembre': 9, 'octubre': 10, 'noviembre': 11, 'diciembre': 12
  };

  const match = fechaStr.match(/(\d{1,2}) de ([a-z]+) de (\d{4})/i);
  if (!match) return null;

  const [_, dia, mesNombre, anio] = match;
  const mes = meses[mesNombre.toLowerCase()];
  if (!mes) return null;

  const fechaFinal = new Date(anio, mes - 1, dia);
  const hoy = new Date();
  hoy.setHours(0, 0, 0, 0);
  fechaFinal.setHours(0, 0, 0, 0);

  const diffTime = fechaFinal - hoy;
  return Math.ceil(diffTime / (1000 * 60 * 60 * 24));
}

function normalizarFecha(textoFecha) {
  if (!textoFecha || typeof textoFecha !== 'string') return textoFecha;

  const meses = ['enero', 'febrero', 'marzo', 'abril', 'mayo', 'junio',
    'julio', 'agosto', 'septiembre', 'octubre', 'noviembre', 'diciembre'];

  return textoFecha.replace(/(\d{1,2})[\/\-](\d{1,2})(?:[\/\-](\d{2,4}))?/g, (match, d, m, y) => {
    const dia = parseInt(d);
    const mes = parseInt(m);
    const anio = y ? parseInt(y.length === 2 ? '20' + y : y) : new Date().getFullYear();

    if (mes >= 1 && mes <= 12 && dia >= 1 && dia <= 31) {
      return `${dia} de ${meses[mes - 1]} de ${anio}`;
    } else {
      return match;
    }
  });
}

function recargarTarjetasCada30Min() {
  window.location.reload();
}


document.addEventListener('DOMContentLoaded', function () {
  const filtroAmarillo = document.getElementById('filtro-amarillo');
  const filtroRojo = document.getElementById('filtro-rojo');
  const filtroPublicos = document.getElementById('filtro-publicos');
  const filtroPrivadas = document.getElementById('filtro-privadas');
  const filtroFondosGob = document.getElementById('filtro-fondos-gob');
  const filtroAnid = document.getElementById('filtro-anid');
  const filtroCultura = document.getElementById('filtro-cultura');
  const filtroGoreValpo = document.getElementById('filtro-gore-valparaiso');
  const filtroMunicipalidades = document.getElementById('filtro-municipalidades');
  const checkboxesPalabras = document.querySelectorAll('.filtro-palabra');
  const botonLimpiarFiltros = document.getElementById('limpiar-filtros');

  const palabrasClavePrivadas = ['gore'];

  function obtenerPalabrasClaveSeleccionadas() {
    return Array.from(checkboxesPalabras)
      .filter(cb => cb.checked)
      .map(cb => cb.value.trim());
  }

  function aplicarFiltros() {
    const tarjetas = document.querySelectorAll('#tarjetas-combinadas .tarjeta');
    const palabrasClave = obtenerPalabrasClaveSeleccionadas();

    const filtrosOrigen = {
      fondosGob: filtroFondosGob?.checked,
      anid: filtroAnid?.checked,
      cultura: filtroCultura?.checked,
      gore: filtroGoreValpo?.checked,
      muni: filtroMunicipalidades?.checked
    };

    const filtrosDias = {
      rojo: filtroRojo?.checked,
      amarillo: filtroAmarillo?.checked
    };

    const filtrosTipo = {
      publicos: filtroPublicos?.checked,
      privados: filtroPrivadas?.checked
    };

    const hayFiltros =
      Object.values(filtrosOrigen).some(Boolean) ||
      Object.values(filtrosDias).some(Boolean) ||
      Object.values(filtrosTipo).some(Boolean) ||
      palabrasClave.length > 0;

    tarjetas.forEach(tarjeta => {
      const clases = tarjeta.classList;
      const esAmarilla = clases.contains('tarjeta-amarilla');
      const esRoja = clases.contains('tarjeta-roja');
      const esPublico =
        clases.contains('tarjeta-fondos_gob') ||
        clases.contains('tarjeta-anid') ||
        clases.contains('tarjeta-gore_valparaiso') ||
        clases.contains('tarjeta-cultura');
      const esPortal = clases.contains('tarjeta-portales');

      const tipo = clases.contains('tarjeta-fondos_gob') ? 'fondosGob' :
                  clases.contains('tarjeta-anid') ? 'anid' :
                  clases.contains('tarjeta-cultura') ? 'cultura' :
                  clases.contains('tarjeta-gore_valparaiso') ? 'gore' : '';

      let mostrar = !hayFiltros;

      // === Lógica combinada: ORIGEN + (color si hay)
      if (filtrosOrigen[tipo]) {
        if (!filtrosDias.rojo && !filtrosDias.amarillo) {
          mostrar = true;
        } else if ((filtrosDias.rojo && esRoja) || (filtrosDias.amarillo && esAmarilla)) {
          mostrar = true;
        } else {
          mostrar = false;
        }
      }

      // === Si se marca solo días sin origen
      if (!Object.values(filtrosOrigen).some(Boolean)) {
        if (filtrosDias.rojo && esRoja) mostrar = true;
        if (filtrosDias.amarillo && esAmarilla) mostrar = true;
      }

      // === Públicos / privados
      if (filtrosTipo.publicos && esPublico) mostrar = true;

      if (filtrosTipo.privados && esPortal) {
        const link = tarjeta.querySelector('a.btn-link')?.href || '';
        const esPrivada = palabrasClavePrivadas.some(p =>
          link.toLowerCase().includes(p)
        );
        if (esPrivada) mostrar = true;
      }

      // === Municipales
      if (filtrosOrigen.muni) {
        const texto = tarjeta.textContent.toLowerCase();
        const link = tarjeta.querySelector('a.btn-link')?.href.toLowerCase() || '';
        const prohibidas = ['comunicacion', 'comunidad', 'comunitaria'];
        const esMuni = texto.includes('muni') && !prohibidas.some(p => texto.includes(p));
        if (esMuni) mostrar = true;
      }

      // === Palabras clave
      if (palabrasClave.length > 0 && esPortal) {
        const consulta = (tarjeta.getAttribute('data-consulta') || '')
          .normalize("NFKD").replace(/[\u0300-\u036F]/g, "").toLowerCase();

        const coincide = palabrasClave.some(p =>
          consulta.includes(p.normalize("NFKD").replace(/[\u0300-\u036F]/g, "").toLowerCase())
        );

        if (coincide) mostrar = true;
      }

      tarjeta.style.display = mostrar ? '' : 'none';
    });
  }




  // LISTA DE FILTROS PARA ESCUCHAR CAMBIOS
  const filtros = [
    filtroAmarillo,
    filtroRojo,
    filtroPublicos,
    filtroPrivadas,
    filtroFondosGob,
    filtroAnid,
    filtroCultura,
    filtroGoreValpo,
    filtroMunicipalidades
  ];

  filtros.forEach(filtro => {
    if (filtro) filtro.addEventListener('change', aplicarFiltros);
  });

  checkboxesPalabras.forEach(cb => {
    cb.addEventListener('change', aplicarFiltros);
  });

  if (botonLimpiarFiltros) {
    botonLimpiarFiltros.addEventListener('click', () => {
      checkboxesPalabras.forEach(cb => cb.checked = false);
      filtros.forEach(f => f && (f.checked = false));
      aplicarFiltros();
    });
  }

  aplicarFiltros(); // Ejecutar al inicio
});


/* ===== FORMATEO DE TEXTO DENTRO DE TARJETAS ===== */
function capitalizarTarjetas() {
  document.querySelectorAll('.tarjeta h3, .tarjeta p').forEach(el => {
    const texto = el.textContent.trim();
    if (texto.length > 0) {
      // Convierte todo a minúsculas y pone mayúscula inicial después de espacios o dos puntos
      el.textContent = texto
        .toLowerCase()
        .replace(/(^|\s|:)\S/g, l => l.toUpperCase());
    }
  });
}

// Ejecutar el formateo una vez que las tarjetas se hayan generado
document.addEventListener('DOMContentLoaded', () => {
  setTimeout(capitalizarTarjetas, 2000);
});

/* ===== BUSCADOR DE TEXTO (ACTUALIZADO) ===== */
document.addEventListener('DOMContentLoaded', function () {
  const buscador = document.getElementById('buscador-texto');
  if (!buscador) return;

  // Escuchar el input del buscador
  buscador.addEventListener('input', function () {
    aplicarBuscador();
  });

  // Función de filtrado del buscador
  function aplicarBuscador() {
    const texto = buscador.value.trim().toLowerCase();
    const tarjetas = document.querySelectorAll('#tarjetas-combinadas .tarjeta');

    tarjetas.forEach(tarjeta => {
      const contenido = tarjeta.getAttribute('data-filtro-texto') || tarjeta.textContent.toLowerCase();
      tarjeta.style.display = contenido.includes(texto) ? '' : 'none';
    });
  }

  // Reaplicar búsqueda cada vez que se recarguen las tarjetas
  const observer = new MutationObserver(() => aplicarBuscador());
  const contenedor = document.getElementById('tarjetas-combinadas');
  if (contenedor) {
    observer.observe(contenedor, { childList: true, subtree: true });
  }
});



