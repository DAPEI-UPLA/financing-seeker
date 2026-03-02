<!DOCTYPE html>
<html lang="es">
<head>
  <meta charset="UTF-8">
  <title>Filtros</title>
  <link rel="stylesheet" href="estilos_filtro.css">
</head>
<body>
  <!-- Encabezado -->
  <div class="encabezado">
    <div class="barra-superior">
      <a href="index.php" class="btn-volver">← Volver a la página principal</a>
      <h1>Buscador de Financiamiento</h1>
    </div>
  </div>

  <!-- Contenido principal -->
  <div class="contenido">
    <div class="layout">
      
      <!-- Filtros laterales -->
      <div class="filtros-laterales">
        <h2>Filtros</h2>

        <!-- 🔍 Buscador de texto -->
        <div class="buscador">
          <input type="text" id="buscador-texto" placeholder="Buscar fondos o palabras clave...">
        </div>

        <form id="filtro-form">
          <h3>Urgencia:</h3>
          <label><input type="checkbox" id="filtro-amarillo"> 5–7 días</label><br>
          <label><input type="checkbox" id="filtro-rojo"> 0–4 días</label><br>

          <h3>Origen:</h3>
          <label><input type="checkbox" id="filtro-privadas"> Gore Regional</label><br>
          <label><input type="checkbox" id="filtro-fondos-gob"> Fondos Gob</label><br>
          <label><input type="checkbox" id="filtro-anid"> ANID</label><br>
          <label><input type="checkbox" id="filtro-cultura"> Cultura</label><br>
          <label><input type="checkbox" id="filtro-gore-valparaiso"> Gore Valparaíso</label><br>
          <label><input type="checkbox" id="filtro-municipalidades"> Municipalidades</label><br>

          <h3>General:</h3>
          <label><input type="checkbox" id="filtro-publicos"> Públicos</label><br>

          <h2>Palabras Clave:</h2>
          <label><input type="checkbox" class="filtro-palabra" value="Fondos concursable"> FONDOS CONCURSABLE</label><br>
          <label><input type="checkbox" class="filtro-palabra" value="Concurso"> CONCURSO</label><br>
          <label><input type="checkbox" class="filtro-palabra" value="Llamado"> LLAMADO</label><br>
          <label><input type="checkbox" class="filtro-palabra" value="Postulaciones"> POSTULACIONES</label><br>
          <label><input type="checkbox" class="filtro-palabra" value="Iniciativas"> INICIATIVAS</label><br>
          <label><input type="checkbox" class="filtro-palabra" value="Lanzamientos"> LANZAMIENTOS</label><br>
          <label><input type="checkbox" class="filtro-palabra" value="Fondos concursables publicos"> FONDOS CONCURSABLES PÚBLICOS</label><br>
          <label><input type="checkbox" class="filtro-palabra" value="Fondos concursables privados"> FONDOS CONCURSABLES PRIVADOS</label><br>
          <label><input type="checkbox" class="filtro-palabra" value="Desafío"> DESAFÍO</label><br>
          <label><input type="checkbox" class="filtro-palabra" value="Convocatoria"> CONVOCATORIA</label><br>
          <button type="button" id="limpiar-filtros">Limpiar filtros</button>
        </form>
      </div>

      <!-- Contenido principal: Tarjetas -->
      <div class="contenido-principal">
        <div class="contenedor-tarjetas" id="tarjetas-combinadas"></div>
      </div>
    </div>
  </div>

  <!-- Pie de página -->
  <div class="footer">
    &copy; 2025 Universidad de Playa Ancha - Todos los derechos reservados.
  </div>

  <script src="filtros.js"></script>
</body>
</html>
