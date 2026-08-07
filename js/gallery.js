/**
 * gallery.js — Motor de distribución de galería fotográfica
 * Portafolio · Paola Andrea Muelas Núñez
 *
 * Funcionalidades:
 *  · Distribución tipo Pinterest usando CSS Grid de múltiples columnas
 *  · Cálculo dinámico de column-span / row-span en base a la relación de aspecto real
 *  · Sub-sección "UnicaUCA" con su propio motor (escala reducida)
 *  · Array unificado para el Lightbox (sub-sección + galería principal)
 *  · Swipe táctil y teclado en el Lightbox
 *  · Re-cálculo de spans en resize (sin reconstruir el DOM)
 */

function initGallery (_resources) {
  'use strict';
  /*
  Resource {
    type: string;
    title?: string;
    data: {
      url: string;
      tag?: string;
      caption?: string;
      footer?: string;
    }[];
  }
  */


  // ─── Constantes ───────────────────────────────────────────────────────────────

  const MAIN_GAP = 12; // px — gap del grid principal (debe coincidir con CSS)
  const SUB_GAP  = 6;  // px — gap del grid interno de sub-sección

  /**
   * Array unificado para el Lightbox.
   * Orden: imágenes de UnicaUCA primero (índices 0-8),
   * luego las de la galería principal (9 en adelante).
   */
  const ALL_URLS = [
    ...(_resources[0] && _resources[0].data ? _resources[0].data.map(d => d.url) : []),
    ..._resources.filter(r => r.type !== "gallery").flatMap(r => r.data ? r.data.map(d => d.url) : [])
  ];

  // ─── Estado ───────────────────────────────────────────────────────────────────

  let currentIdx   = 0;
  let touchStartX  = 0;
  let lbFadeTimer  = null;
  let resizeTimer  = null;

  // Referencias al DOM (se construyen una sola vez)
  let galleryGrid = null;
  let subSection  = null;
  let subGrid     = null;
  let mainItems   = []; // [{ el, url }]
  let subItems    = []; // [{ el, url }]
  let domReady    = false;

  // ─── Lectura de config desde CSS custom properties ────────────────────────────

  /**
   * Las propiedades CSS definen los parámetros del grid para cada breakpoint.
   * parseInt('20px') → 20  ✓   parseInt('20') → 20  ✓
   */
  function readCfg() {
    const s = getComputedStyle(document.documentElement);
    const v = (k) => parseInt(s.getPropertyValue('--' + k).trim()) || 0;
    return {
      cols:    v('gcols')    || 20,
      rowUnit: v('grow')     || 20,
      subCols: v('gsubcols') || 12,
      subRow:  v('gsubrow')  || 10,
      subH:    v('g-sub-h')  || 440,
    };
  }

  // ─── Utilidades ───────────────────────────────────────────────────────────────

  const dimCache = {};
  /** Carga las dimensiones naturales de una imagen (con caché). */
  function loadDims(url) {
    if (dimCache[url]) return Promise.resolve(dimCache[url]);
    return new Promise(resolve => {
      const img = new Image();
      img.onload  = () => { dimCache[url] = { w: img.naturalWidth, h: img.naturalHeight }; resolve(dimCache[url]); };
      img.onerror = () => { dimCache[url] = { w: 3, h: 2 }; resolve(dimCache[url]); };
      img.src = url;
    });
  }

  /**
   * Devuelve el column-span adecuado para una relación de aspecto dada.
   * La base está calibrada para 20 columnas y se escala proporcionalmente.
   */
  function computeColSpan(ar, totalCols) {
    const scale = totalCols / 20;
    let base;
    if      (ar >= 2.2)  base = 9;
    else if (ar >= 1.65) base = 8;
    else if (ar >= 1.25) base = 7;
    else if (ar >= 0.88) base = 6;
    else if (ar >= 0.62) base = 5;
    else                 base = 4;
    return Math.min(Math.max(Math.round(base * scale), 1), totalCols);
  }

  /**
   * Convierte una altura de contenido en número de filas del grid.
   *
   * Con grid-auto-rows = U y gap = G, un item de N filas tiene:
   *   altura = N·U + (N−1)·G
   * Despejando N:
   *   N = ceil( (h + G) / (U + G) )
   */
  function computeRowSpan(contentH, gap, rowUnit) {
    return Math.max(2, Math.ceil((contentH + gap) / (rowUnit + gap)));
  }

  // ─── Motor de layout (Packer con recortes para evitar espacios) ───────────────

  async function applyLayout(container, items, totalCols, rowUnitPx, gapPx, fixedFirstItem = null) {
    const containerW = container.clientWidth;
    if (!containerW || !items.length) return;

    const cellW = (containerW - gapPx * (totalCols - 1)) / totalCols;

    const measuredItems = await Promise.all(items.map(async (item, index) => {
      const { el, url } = item;
      const { w, h } = await loadDims(url);
      return { el, ar: w / h, index };
    }));

    let placements = [];
    let currentRowOffset = 0;
    let itemsCopy = [...measuredItems];

    // Si hay un item fijo (la sub-sección), se coloca primero y se rellena el espacio a su derecha
    if (fixedFirstItem) {
      placements.push({
        el: fixedFirstItem.el,
        c: 0,
        r: currentRowOffset,
        w: fixedFirstItem.w,
        h: fixedFirstItem.h
      });

      let remainingW = totalCols - fixedFirstItem.w;
      
      // Si hay espacio a la derecha (ej. en desktop es la mitad del ancho)
      if (remainingW > 0 && itemsCopy.length > 0) {
        // Cuántas imágenes caben bien en ese espacio
        let numItems = remainingW >= (totalCols * 0.5) ? 2 : 1;
        numItems = Math.min(numItems, itemsCopy.length);
        
        let rowItems = itemsCopy.splice(0, numItems);
        let totalAR = rowItems.reduce((sum, item) => sum + item.ar, 0);
        
        let currentC = fixedFirstItem.w;
        for (let i = 0; i < rowItems.length; i++) {
          let w = (i === rowItems.length - 1) 
            ? remainingW 
            : Math.max(2, Math.round(remainingW * (rowItems[i].ar / totalAR)));
          
          if (remainingW - w < (rowItems.length - 1 - i) * 2) {
            w = remainingW - (rowItems.length - 1 - i) * 2;
          }

          placements.push({
            el: rowItems[i].el,
            c: currentC,
            r: currentRowOffset,
            w: w,
            // Forzamos a que tengan EXACTAMENTE la misma altura que la sub-sección
            h: fixedFirstItem.h 
          });
          currentC += w;
          remainingW -= w;
        }
      }
      // La siguiente fila empieza después de la sub-sección
      currentRowOffset += fixedFirstItem.h; 
    }

    // Para el resto de los items, creamos filas completas
    while (itemsCopy.length > 0) {
      let rowItems = [];
      let totalAR = 0;
      
      // Agrupamos imágenes para formar una fila (2 o 3 imágenes por fila funciona muy bien)
      while (itemsCopy.length > 0) {
        let item = itemsCopy.shift();
        rowItems.push(item);
        totalAR += item.ar;
        // Cortar la fila si ya tenemos suficientes proporciones o máximo 3 items
        if (totalAR >= 2.5 && rowItems.length >= 2) break; 
        if (rowItems.length >= 3) break;
      }
      
      let remainingW = totalCols;
      let currentC = 0;
      let rowWidths = [];
      
      // Repartimos las columnas según el aspect ratio de cada imagen
      for (let i = 0; i < rowItems.length; i++) {
        let w = (i === rowItems.length - 1) 
          ? remainingW 
          : Math.max(2, Math.round(totalCols * (rowItems[i].ar / totalAR)));
        
        if (remainingW - w < (rowItems.length - 1 - i) * 2) {
          w = remainingW - (rowItems.length - 1 - i) * 2;
        }
        
        rowWidths.push(w);
        remainingW -= w;
      }
      
      // Calculamos qué altura debería tener esta fila basándonos en el tamaño de las imágenes
      let maxTotalH = 0;
      for (let i = 0; i < rowItems.length; i++) {
        let w = rowWidths[i];
        let dispW = cellW * w + gapPx * (w - 1);
        let dispH = dispW / rowItems[i].ar;
        
        const captionEl = rowItems[i].el.querySelector('.g-caption-container');
        const captionH = captionEl ? captionEl.offsetHeight : 0;
        
        let totalH = dispH + captionH + 4;
        if (totalH > maxTotalH) maxTotalH = totalH;
      }
      
      // Todas las imágenes de ESTA FILA tendrán EXACTAMENTE esta altura en grid-rows
      let rs = Math.max(2, Math.ceil((maxTotalH + gapPx) / (rowUnitPx + gapPx)));
      
      for (let i = 0; i < rowItems.length; i++) {
        placements.push({
          el: rowItems[i].el,
          c: currentC,
          r: currentRowOffset,
          w: rowWidths[i],
          h: rs
        });
        currentC += rowWidths[i];
      }
      // La siguiente fila empieza limpiamente debajo de esta
      currentRowOffset += rs;
    }

    // Aplicar las posiciones absolutas en el DOM
    for (let p of placements) {
      p.el.style.gridColumn = `${p.c + 1} / span ${p.w}`;
      p.el.style.gridRow = `${p.r + 1} / span ${p.h}`;
    }
  }

  // ─── Constructores del DOM ────────────────────────────────────────────────────

  /**
   * Crea una tarjeta de imagen (usada tanto para galería principal como sub-sección).
   * @param {Object}  imgData    { url, caption }
   * @param {number}  lbIndex    Índice en ALL_URLS para el lightbox
   * @param {boolean} isSub      true si pertenece a la sub-sección
   */
  function makeCard(imgData, lbIndex, isSub) {
    const el = document.createElement('div');
    el.className = 'g-item' + (isSub ? ' g-item--sub' : '');
    el.addEventListener('click', () => openLightbox(lbIndex));

    // Wrapper de imagen (ocupa flex:1 para llenar el espacio disponible)
    const wrap = document.createElement('div');
    wrap.className = 'g-img-wrap';

    const img = document.createElement('img');
    img.src      = imgData.url;
    img.alt      = imgData.caption || 'Fotografía Paola Andrea Muelas';
    img.loading  = 'lazy';
    img.className = 'g-img';
    wrap.appendChild(img);

    // Overlay de hover
    const ov = document.createElement('div');
    ov.className = 'g-overlay';
    ov.innerHTML = '<span>Ver Ampliado</span>';
    wrap.appendChild(ov);

    el.appendChild(wrap);

    // Caption estructurado en galería principal
    if (imgData.caption && !isSub) {
      const container = document.createElement('div');
      container.className = 'g-caption-container p-5 flex-grow flex flex-col justify-between space-y-4 bg-brand-bg relative z-10';
      
      const topContent = document.createElement('div');
      topContent.className = 'space-y-2';
      
      const tagSpan = document.createElement('span');
      tagSpan.className = 'block text-[10px] font-semibold tracking-widest text-brand-dusty uppercase';
      tagSpan.textContent = imgData.tag;
      
      const descP = document.createElement('p');
      descP.className = 'text-brand-gray text-xs leading-relaxed font-light';
      descP.textContent = imgData.caption;
      
      topContent.appendChild(tagSpan);
      topContent.appendChild(descP);
      
      const footerDiv = document.createElement('div');
      footerDiv.className = 'text-[10px] font-semibold text-brand-dark tracking-wider';
      footerDiv.textContent = imgData.footer;
      
      container.appendChild(topContent);
      container.appendChild(footerDiv);
      
      el.appendChild(container);
    }

    return el;
  }

  /**
   * Crea el bloque completo de la sub-sección UnicaUCA:
   * · Un grid interno con las 9 imágenes
   * · Un label "UnicaUCA" con degradado en la parte inferior
   */
  function makeSubsection() {
    const outer = document.createElement('div');
    outer.className = 'g-subsection';

    const grid = document.createElement('div');
    grid.className = 'g-sub-grid';
    outer.appendChild(grid);

    // Añadir imágenes UnicaUCA; lbIndex = i (están al inicio de ALL_URLS)
    _resources[0].data.forEach((d, i) => {
      grid.appendChild(makeCard(d, i, true));
    });

    // Label con degradado
    const lbl = document.createElement('div');
    lbl.className = 'g-sub-label';
    lbl.innerHTML = '<span>UNICAUCA</span>';
    outer.appendChild(lbl);

    return outer;
  }

  // ─── Construcción del DOM (una sola vez) ──────────────────────────────────────

  function buildDom() {
    galleryGrid = document.getElementById('gallery-grid');
    if (!galleryGrid) return false;

    // 1. Sub-sección en primera posición
    subSection = makeSubsection();
    galleryGrid.appendChild(subSection);
    subGrid = subSection.querySelector('.g-sub-grid');

    // 2. Imágenes de la galería principal
    mainItems = _resources.filter(r => r.type !== "gallery").map((r, idx) => r.data).flat(2).map((d, i) => {
      const card = makeCard(d, _resources[0].data.length + i, false);
      galleryGrid.appendChild(card);
      return { el: card, url: d.url };
    });

    // 3. Referencias a los items de la sub-sección
    subItems = _resources[0].data.map((d, i) => ({
      el:  subGrid.children[i],
      url: d.url,
    }));

    domReady = true;
    return true;
  }

  // ─── Aplicar spans (llamable en init y en resize) ─────────────────────────────

  async function applySpans() {
    if (!domReady) return;
    const c = readCfg();

    // Span de la sub-sección en el grid principal
    const subColSpan = window.innerWidth <= 600
      ? c.cols                    // móvil: ancho completo
      : Math.floor(c.cols / 2);   // tablet/desktop: mitad
    const subRowSpan = computeRowSpan(c.subH, MAIN_GAP, c.rowUnit);

    const fixedSubSection = {
      el: subSection,
      w: subColSpan,
      h: subRowSpan
    };

    // Aplicar layout al grid principal y al grid interno en paralelo
    await Promise.all([
      applyLayout(galleryGrid, mainItems, c.cols, c.rowUnit, MAIN_GAP, fixedSubSection),
      applyLayout(subGrid,     subItems,  c.subCols, c.subRow, SUB_GAP, null),
    ]);
  }

  // ─── Inicialización ───────────────────────────────────────────────────────────

  async function init() {
    if (!buildDom()) return;
    await applySpans();
  }

  // Re-calcular spans en resize sin reconstruir el DOM
  window.addEventListener('resize', () => {
    clearTimeout(resizeTimer);
    resizeTimer = setTimeout(applySpans, 280);
  });

  // ─── Lightbox (unificado: galería + secciones) ──────────────────────────────

  let lbIsSection = false;
  let secUrls = [];
  let secIdx  = 0;

  function activeUrls() { return lbIsSection ? secUrls : ALL_URLS; }
  function activeIdx()  { return lbIsSection ? secIdx  : currentIdx; }
  function setActiveIdx(v) { if (lbIsSection) secIdx = v; else currentIdx = v; }

  function renderLightbox() {
    const img = document.getElementById('lightbox-img');
    const ctr = document.getElementById('lightbox-counter');
    if (!img || !ctr) return;
    const urls = activeUrls();
    const idx  = activeIdx();
    ctr.textContent = `${idx + 1} / ${urls.length}`;
    clearTimeout(lbFadeTimer);
    img.classList.add('lb-fade');
    lbFadeTimer = setTimeout(() => {
      img.src = urls[idx];
      img.classList.remove('lb-fade');
    }, 180);
  }

  function openLightbox(index) {
    lbIsSection = false;
    currentIdx = index;
    renderLightbox();
    const lb = document.getElementById('lightbox');
    if (lb) { lb.classList.remove('hidden'); document.body.classList.add('lightbox-active'); }
  }

  function openSectionLightbox(urls, index) {
    lbIsSection = true;
    secUrls = urls;
    secIdx  = index;
    renderLightbox();
    const lb = document.getElementById('lightbox');
    if (lb) { lb.classList.remove('hidden'); document.body.classList.add('lightbox-active'); }
  }

  function closeLightbox() {
    const lb = document.getElementById('lightbox');
    if (lb) { lb.classList.add('hidden'); document.body.classList.remove('lightbox-active'); }
  }

  function changeLightboxImage(dir) {
    const urls = activeUrls();
    setActiveIdx((activeIdx() + dir + urls.length) % urls.length);
    renderLightbox();
  }

  window.openLightbox          = openLightbox;
  window.openSectionLightbox   = openSectionLightbox;
  window.closeLightbox         = closeLightbox;
  window.changeLightboxImage   = changeLightboxImage;

  document.addEventListener('keydown', e => {
    const lb = document.getElementById('lightbox');
    if (!lb || lb.classList.contains('hidden')) return;
    if (e.key === 'Escape')     closeLightbox();
    if (e.key === 'ArrowRight') changeLightboxImage(1);
    if (e.key === 'ArrowLeft')  changeLightboxImage(-1);
  });

  document.addEventListener('touchstart', e => {
    const lb = document.getElementById('lightbox');
    if (!lb || lb.classList.contains('hidden')) return;
    touchStartX = e.touches[0].clientX;
  }, { passive: true });

  document.addEventListener('touchend', e => {
    const lb = document.getElementById('lightbox');
    if (!lb || lb.classList.contains('hidden')) return;
    const dx = touchStartX - e.changedTouches[0].clientX;
    if (Math.abs(dx) > 50) changeLightboxImage(dx > 0 ? 1 : -1);
  });

  // ─── Boot ────────────────────────────────────────────────────────────────────

  if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', init);
  } else {
    init();
  }

}
