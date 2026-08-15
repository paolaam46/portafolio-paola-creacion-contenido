/**
 * main.js — Lógica de Interacciones, Renderizado Scrapbook y Navegación
 * Portafolio Paola Andrea Muelas Núñez
 */

'use strict';

document.addEventListener('DOMContentLoaded', () => {
  initNavbarScroll();
  initMobileMenu();
  initCollageGalleries();
  initSmoothScroll();
  initCopyEmail();
});

/**
 * Control dinámico del navbar según el scroll:
 * En scroll 0 es compacto y transparente sin avatar;
 * al hacer scroll se expande con blur, avatar y estilos scrapbook completos.
 */
function initNavbarScroll() {
  const nav = document.querySelector('.scrapbook-nav');
  if (!nav) return;

  function handleScroll() {
    if (window.scrollY > 25) {
      nav.classList.add('scrapbook-nav--scrolled');
    } else {
      nav.classList.remove('scrapbook-nav--scrolled');
    }
  }

  window.addEventListener('scroll', handleScroll, { passive: true });
  handleScroll(); // Verificar estado al cargar por si la página inicia con scroll
}

/**
 * Control del menú hamburguesa en dispositivos móviles
 */
function initMobileMenu() {
  const menuBtn = document.getElementById('mobile-menu-btn');
  const mobileMenu = document.getElementById('mobile-menu');
  const menuIcon = document.getElementById('menu-icon');
  const mobileLinks = document.querySelectorAll('.mobile-nav-link');

  if (!menuBtn || !mobileMenu) return;

  function toggleMenu() {
    const isExpanded = mobileMenu.classList.toggle('is-open');
    menuBtn.setAttribute('aria-expanded', isExpanded ? 'true' : 'false');
    if (menuIcon) {
      menuIcon.className = isExpanded ? 'fa-solid fa-xmark' : 'fa-solid fa-bars';
    }
  }

  menuBtn.addEventListener('click', toggleMenu);

  mobileLinks.forEach(link => {
    link.addEventListener('click', () => {
      mobileMenu.classList.remove('is-open');
      menuBtn.setAttribute('aria-expanded', 'false');
      if (menuIcon) {
        menuIcon.className = 'fa-solid fa-bars';
      }
    });
  });
}

/**
 * Renderiza dinámicamente las tarjetas de collages interactivos para
 * Diseño Digital y las 3 series de Fotografía desde PORTFOLIO_RESOURCES.
 */
function initCollageGalleries() {
  if (!window.PORTFOLIO_RESOURCES) return;

  // 1. Carrusel Funcionario (Diseño Digital)
  renderCarruselCollage();

  // 2. Posts Redes Sociales (Diseño Digital)
  renderPostsCollage();

  // 3. Series Fotográficas (Velatón, Ruta 2027, Ocaso de los Ídolos)
  renderPhotographySeries();
}

/**
 * Renderiza la sección de Carrusel de Funcionario
 */
function renderCarruselCollage() {
  const container = document.getElementById('carrusel-gallery-container');
  if (!container || !window.PORTFOLIO_RESOURCES.disenoDigital.carrusel) return;

  const carruselData = window.PORTFOLIO_RESOURCES.disenoDigital.carrusel;
  const items = carruselData.items;

  let html = `
    <div class="scrapbook-collection-card">
      <div class="scrapbook-collection-header">
        <div class="tape-strip tape-strip--top-left"></div>
        <div class="tape-strip tape-strip--top-right"></div>
        <div class="collection-badge">
          <i class="fa-solid fa-layer-group"></i> ${carruselData.category}
        </div>
        <h4 class="collection-title">${carruselData.title}</h4>
        <p class="collection-desc">${carruselData.description}</p>
      </div>

      <div class="carrusel-strip">
        ${items.map((item, idx) => `
          <div class="polaroid-card polaroid-card--carrusel" onclick="openResourceCollection('disenoDigital', 'carrusel', ${idx})">
            <div class="washi-tape washi-tape--center"></div>
            <div class="polaroid-img-wrapper">
              <img src="${item.url}" alt="${item.title}" loading="lazy" class="polaroid-img" />
              <div class="polaroid-overlay">
                <span><i class="fa-solid fa-magnifying-glass-plus"></i> Ver lámina ${idx + 1}</span>
              </div>
            </div>
            <div class="polaroid-label">
              <span class="polaroid-num">0${idx + 1}</span>
              <p class="polaroid-text">${item.title}</p>
            </div>
          </div>
        `).join('')}
      </div>

      <div class="collection-footer-action">
        <button type="button" class="scrapbook-btn-pill" onclick="openResourceCollection('disenoDigital', 'carrusel', 0)">
          <i class="fa-solid fa-expand"></i> Ver carrusel completo (${items.length} láminas)
        </button>
      </div>
    </div>
  `;

  container.innerHTML = html;
}

/**
 * Renderiza la sección de Posts de Redes Sociales
 */
function renderPostsCollage() {
  const container = document.getElementById('posts-gallery-container');
  if (!container || !window.PORTFOLIO_RESOURCES.disenoDigital.posts) return;

  const postsData = window.PORTFOLIO_RESOURCES.disenoDigital.posts;
  const items = postsData.items;

  let html = `
    <div class="scrapbook-collection-card">
      <div class="scrapbook-collection-header">
        <div class="tape-strip tape-strip--top-center"></div>
        <div class="collection-badge">
          <i class="fa-brands fa-instagram"></i> ${postsData.category}
        </div>
        <h4 class="collection-title">${postsData.title}</h4>
        <p class="collection-desc">${postsData.description}</p>
      </div>

      <div class="posts-scrapbook-grid">
        ${items.map((item, idx) => `
          <div class="polaroid-card polaroid-card--post tilt-${(idx % 3) + 1}" onclick="openResourceCollection('disenoDigital', 'posts', ${idx})">
            <div class="washi-tape ${idx === 1 ? 'washi-tape--top-left' : 'washi-tape--top-right'}"></div>
            <div class="polaroid-img-wrapper">
              <img src="${item.url}" alt="${item.title}" loading="lazy" class="polaroid-img" />
              <div class="polaroid-overlay">
                <span><i class="fa-solid fa-magnifying-glass-plus"></i> Ampliar</span>
              </div>
            </div>
            <div class="polaroid-label">
              <p class="polaroid-text font-hand">${item.title}</p>
            </div>
          </div>
        `).join('')}
      </div>
    </div>
  `;

  container.innerHTML = html;
}

/**
 * Renderiza las 3 series de Fotografía
 */
function renderPhotographySeries() {
  const container = document.getElementById('photo-series-container');
  if (!container || !window.PORTFOLIO_RESOURCES.fotografia) return;

  const foto = window.PORTFOLIO_RESOURCES.fotografia;

  const series = [
    { key: 'velaton', data: foto.velaton, icon: 'fa-solid fa-fire-flame-curved' },
    { key: 'acreditacion', data: foto.acreditacion, icon: 'fa-solid fa-bus-simple' },
    { key: 'ocaso', data: foto.ocaso, icon: 'fa-solid fa-monument' }
  ];

  let html = series.map((serie, sIdx) => {
    const sData = serie.data;
    if (!sData) return '';

    return `
      <article class="photo-serie-block paper-sheet" id="${sData.id}">
        <div class="paper-sheet__inner">
          <div class="washi-tape washi-tape--top-left"></div>
          <div class="washi-tape washi-tape--top-right"></div>

          <div class="photo-serie-header">
            <div class="serie-meta">
              <span class="serie-badge"><i class="${serie.icon}"></i> ${sData.category}</span>
              <span class="serie-count"><i class="fa-solid fa-camera"></i> ${sData.items.length} fotografías</span>
            </div>
            <h3 class="serie-title font-hand">${sData.title}</h3>
            <p class="serie-desc">${sData.description}</p>
          </div>

          <!-- Collage Grid con estética Scrapbook -->
          <div class="photo-collage-grid photo-collage-grid--${serie.key}">
            ${sData.items.map((item, iIdx) => `
              <div class="photo-stamp photo-stamp--${serie.key}-${iIdx + 1} tilt-${((sIdx + iIdx) % 4) + 1}" 
                   onclick="openResourceCollection('fotografia', '${serie.key}', ${iIdx})">
                <div class="washi-tape washi-tape--corner"></div>
                <div class="photo-stamp__wrap">
                  <img src="${item.url}" alt="${item.title}" loading="lazy" class="photo-stamp__img" />
                  <div class="photo-stamp__overlay">
                    <span class="photo-stamp__tag"><i class="fa-solid fa-expand"></i> Ver foto ${iIdx + 1}</span>
                  </div>
                </div>
                <div class="photo-stamp__caption font-hand">
                  ${item.title}
                </div>
              </div>
            `).join('')}
          </div>

          <div class="photo-serie-action">
            <button type="button" class="scrapbook-btn-outline" onclick="openResourceCollection('fotografia', '${serie.key}', 0)">
              <i class="fa-solid fa-images"></i> Abrir galería de ${sData.title} (${sData.items.length} fotos)
            </button>
          </div>
        </div>
      </article>
    `;
  }).join('');

  container.innerHTML = html;
}

/**
 * Smooth Scroll para todos los enlaces internos
 */
function initSmoothScroll() {
  document.querySelectorAll('a[href^="#"]').forEach(anchor => {
    anchor.addEventListener('click', function (e) {
      const targetId = this.getAttribute('href');
      if (targetId === '#' || !targetId) return;

      const targetEl = document.querySelector(targetId);
      if (targetEl) {
        e.preventDefault();
        const headerOffset = 80;
        const elementPosition = targetEl.getBoundingClientRect().top;
        const offsetPosition = elementPosition + window.pageYOffset - headerOffset;

        window.scrollTo({
          top: offsetPosition,
          behavior: 'smooth'
        });
      }
    });
  });
}

/**
 * Copiar correo electrónico al portapapeles con feedback visual
 */
function initCopyEmail() {
  const copyBtn = document.getElementById('copy-email-btn');
  if (!copyBtn) return;

  copyBtn.addEventListener('click', () => {
    const email = copyBtn.getAttribute('data-email') || 'paolaandreamuelas@gmail.com';
    navigator.clipboard.writeText(email).then(() => {
      const originalText = copyBtn.innerHTML;
      copyBtn.innerHTML = '<i class="fa-solid fa-check"></i> ¡Copiado!';
      copyBtn.classList.add('btn-copied');
      setTimeout(() => {
        copyBtn.innerHTML = originalText;
        copyBtn.classList.remove('btn-copied');
      }, 2000);
    }).catch(err => {
      console.error('Error al copiar correo:', err);
    });
  });
}
