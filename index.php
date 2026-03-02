<!DOCTYPE html>
<html lang="es">
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
  <title>Buscador de Financiamiento</title>

  <!-- Fuente Lato -->
  <link href="https://fonts.googleapis.com/css2?family=Lato:wght@300;400;700&display=swap" rel="stylesheet">

  <!-- Estilos -->
  <link rel="stylesheet" href="style.css">
</head>
<body>

  <!-- Encabezado -->
  <header class="encabezado">
    <div class="barra-superior">
      <h1>Buscador de Financiamiento</h1>
      <a href="filtro.php" class="btn-filtros">Ir a filtros avanzados →</a>
    </div>
  </header>

  <!-- Contenido principal -->
  <div class="contenido">
    <div class="container">

      <!-- Columna: Fondos.gob.cl -->
      <div class="columna" id="fondos_gob">
        <h2>Fondos Gob</h2>
        <div class="tarjetas"></div>
      </div>

      <!-- Columna: ANID -->
      <div class="columna" id="anid">
        <h2>Fondos ANID</h2>
        <div class="tarjetas"></div>
      </div>

      <!-- Columna: Cultura -->
      <div class="columna" id="cultura">
        <h2>Fondos Cultura</h2>
        <div class="tarjetas"></div>
      </div>

      <!-- Columna: GORE Valparaíso -->
      <div class="columna" id="gore_valparaiso">
        <h2>GORE Valparaíso</h2>
        <div class="tarjetas"></div>
      </div>

      <!-- Columna: Portales -->
      <div class="columna" id="portales">
        <h2>Portales de Financiamiento</h2>
        <div class="tarjetas"></div>
      </div>

      <!-- Columna: Licitaciones -->
      <div class="columna" id="licitaciones">
        <h2>Licitaciones</h2>
        <div class="tarjetas"></div>
      </div>

    </div>
  </div>

  <!-- Botón flotante Play/Pause -->
  <button id="btn-scroll-toggle" class="btn-scroll-fab" title="">▶️</button>

  <!-- Pie de página -->
  <footer class="footer">
    <p>© Universidad De Playa Ancha - 2025</p>
  </footer>

  <!-- Script principal -->
  <script src="script.js"></script>
</body>
</html>
