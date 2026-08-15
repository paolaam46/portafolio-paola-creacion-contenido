/**
 * gallery.js — Motor de Galerías, Collages Scrapbook y Visor Lightbox
 * Portafolio Paola Andrea Muelas Núñez
 */

(function () {
  'use strict';

  // ─── ESTADO DEL LIGHTBOX ──────────────────────────────────────────────────
  let activeGallery = [];
  let currentIndex = 0;
  let touchStartX = 0;
  let touchEndX = 0;

  // ─── FUNCIONES DEL LIGHTBOX ───────────────────────────────────────────────

  /**
   * Abre el Lightbox con una lista específica de elementos multimedia
   * @param {Array<{url: string, title?: string, caption?: string}>} items Lista de imágenes
   * @param {number} startIndex Índice inicial
   */
  function openLightbox(items, startIndex = 0) {
    if (!items || !items.length) return;

    activeGallery = items;
    currentIndex = Math.max(0, Math.min(startIndex, items.length - 1));

    const lightbox = document.getElementById('lightbox');
    if (!lightbox) return;

    lightbox.classList.remove('hidden');
    lightbox.setAttribute('aria-hidden', 'false');
    document.body.classList.add('lightbox-active');

    renderLightboxContent();
  }

  /**
   * Renderiza la imagen actual, el contador y los textos explicativos
   */
  function renderLightboxContent() {
    const imgEl = document.getElementById('lightbox-img');
    const counterEl = document.getElementById('lightbox-counter');
    const titleEl = document.getElementById('lightbox-title');
    const captionEl = document.getElementById('lightbox-caption');

    if (!imgEl || !activeGallery.length) return;

    const currentItem = activeGallery[currentIndex];

    // Animación suave de transición
    imgEl.classList.add('lb-fade-out');

    setTimeout(() => {
      imgEl.src = currentItem.url;
      imgEl.alt = currentItem.title || 'Fotografía Paola Andrea Muelas';

      if (counterEl) {
        counterEl.textContent = `${currentIndex + 1} / ${activeGallery.length}`;
      }

      if (titleEl) {
        titleEl.textContent = currentItem.title || '';
        titleEl.style.display = currentItem.title ? 'block' : 'none';
      }

      if (captionEl) {
        captionEl.textContent = currentItem.caption || '';
        captionEl.style.display = currentItem.caption ? 'block' : 'none';
      }

      imgEl.classList.remove('lb-fade-out');
    }, 120);
  }

  /**
   * Cambia de imagen en el visor
   * @param {number} direction (+1 para siguiente, -1 para anterior)
   */
  function navigateLightbox(direction) {
    if (!activeGallery.length) return;
    currentIndex = (currentIndex + direction + activeGallery.length) % activeGallery.length;
    renderLightboxContent();
  }

  /**
   * Cierra el visor modal
   */
  function closeLightbox() {
    const lightbox = document.getElementById('lightbox');
    if (!lightbox) return;

    lightbox.classList.add('hidden');
    lightbox.setAttribute('aria-hidden', 'true');
    document.body.classList.remove('lightbox-active');
  }

  // ─── GESTIÓN DE EVENTOS DE TECLADO Y TOUCH ────────────────────────────────

  function setupLightboxListeners() {
    // Teclado
    document.addEventListener('keydown', (e) => {
      const lightbox = document.getElementById('lightbox');
      if (!lightbox || lightbox.classList.contains('hidden')) return;

      if (e.key === 'Escape') closeLightbox();
      if (e.key === 'ArrowRight') navigateLightbox(1);
      if (e.key === 'ArrowLeft') navigateLightbox(-1);
    });

    // Clic fuera del contenido
    const lightbox = document.getElementById('lightbox');
    if (lightbox) {
      lightbox.addEventListener('click', (e) => {
        if (e.target === lightbox || e.target.classList.contains('lightbox__overlay')) {
          closeLightbox();
        }
      });
    }

    // Touch Swipe en dispositivos móviles
    if (lightbox) {
      lightbox.addEventListener('touchstart', (e) => {
        touchStartX = e.changedTouches[0].screenX;
      }, { passive: true });

      lightbox.addEventListener('touchend', (e) => {
        touchEndX = e.changedTouches[0].screenX;
        handleSwipe();
      }, { passive: true });
    }
  }

  function handleSwipe() {
    const diff = touchEndX - touchStartX;
    if (Math.abs(diff) > 45) {
      if (diff > 0) {
        navigateLightbox(-1); // Deslizar a la derecha -> anterior
      } else {
        navigateLightbox(1);  // Deslizar a la izquierda -> siguiente
      }
    }
  }

  // ─── DISPARADORES DE GALERÍAS ESPECÍFICAS ─────────────────────────────────

  /**
   * Abre colecciones multimedia predefinidas desde el objeto PORTFOLIO_RESOURCES
   * @param {string} categoryKey ('disenoDigital' o 'fotografia')
   * @param {string} subCategoryKey ('carrusel', 'posts', 'velaton', 'acreditacion', 'ocaso')
   * @param {number} index
   */
  function openResourceCollection(categoryKey, subCategoryKey, index = 0) {
    if (
      window.PORTFOLIO_RESOURCES &&
      window.PORTFOLIO_RESOURCES[categoryKey] &&
      window.PORTFOLIO_RESOURCES[categoryKey][subCategoryKey]
    ) {
      const collection = window.PORTFOLIO_RESOURCES[categoryKey][subCategoryKey];
      openLightbox(collection.items, index);
    }
  }

  // ─── EXPORTACIONES GLOBALES ───────────────────────────────────────────────
  window.openLightbox = openLightbox;
  window.closeLightbox = closeLightbox;
  window.navigateLightbox = navigateLightbox;
  window.openResourceCollection = openResourceCollection;

  // Inicializar listeners cuando el DOM esté listo
  if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', setupLightboxListeners);
  } else {
    setupLightboxListeners();
  }

})();
