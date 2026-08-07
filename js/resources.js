

const TEST_IMG_PATH = 'assets/images/img_test';

/** Imágenes de la galería de prueba */
const resources = [
  {
    type: "gallery",
    title: "UNICAUCA",
    data: [
      { url: `${TEST_IMG_PATH}/1.jpg` },
      { url: `${TEST_IMG_PATH}/2.jpg` },
      { url: `${TEST_IMG_PATH}/3.jpg` },
      { url: `${TEST_IMG_PATH}/4.jpg` },
      { url: `${TEST_IMG_PATH}/5.jpg` },
      { url: `${TEST_IMG_PATH}/6.jpg` },
    ]
  },
  {
    type: 'image',
    data: [{  
      url: `${TEST_IMG_PATH}/1.jpg`,
      tag: 'Fotoperiodismo',
      caption: 'Cobertura periodística en tiempo real. Análisis visual de coyunturas políticas y sociales.',
      footer: 'Prensa'
    }]
  },
  {
    type: 'image',
    data: [{  
      url: `${TEST_IMG_PATH}/2.jpg`,
      tag: 'Composición',
      caption: 'Composición fotográfica con ojo de autor. Exploración de luces, sombras y geometría.',
      footer: 'Fotografía Artística'
    }]
  },
  {
    type: 'image',
    data: [{  
      url: `${TEST_IMG_PATH}/3.jpg`,
      tag: 'Naturaleza & Entorno',
      caption: 'El paisaje caucano como protagonista. Registro de la riqueza natural.',
      footer: 'Paisajismo'
    }]
  },
  {
    type: 'image',
    data: [{  
      url: `${TEST_IMG_PATH}/4.jpg`,
      tag: 'Identidad Local',
      caption: 'Registro de identidad territorial en el Cauca. Una mirada profunda a los oficios tradicionales.',
      footer: 'Patrimonio Visual'
    }]
  },
  {
    type: 'image',
    data: [{  
      url: `${TEST_IMG_PATH}/5.jpg`,
      tag: 'Vida Cotidiana',
      caption: 'Escenas del día a día en el Cauca. El ritmo de la ciudad y el campo capturados con sensibilidad.',
      footer: 'Street Photography'
    }]
  },
  {
    type: 'image',
    data: [{  
      url: `${TEST_IMG_PATH}/6.jpg`,
      tag: 'Retrato & Autor',
      caption: 'Exploración de retratos expresivos e historias humanas en el territorio.',
      footer: 'Retrato'
    }]
  }
];

