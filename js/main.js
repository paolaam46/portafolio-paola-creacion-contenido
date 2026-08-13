'use strict';

document.addEventListener('DOMContentLoaded', () => {
  if (typeof initGallery === 'function' && typeof resources !== 'undefined') {
    initGallery(resources);
  }
});
