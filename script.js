/* ============================================================
   CarffCode Portfolio — script.js
   Autor: Filipe Franco Cardoso (Carff)
   ============================================================ */

document.addEventListener('DOMContentLoaded', function () {
  initTheme();
  initHeaderScroll();
  initNavMenu();
  initActiveLinks();
  initBackToTop();
  initRevealOnScroll();
  initSkillBars();
  initProjectFilter();
  initTestimonialsSlider();
  initTypedHero();
  initContactForm();
  initQRCode();
});

/* ============================================================
   1. TEMA CLARO / ESCURO
   ============================================================ */

function initTheme() {
  var root        = document.documentElement;
  var themeToggle = document.getElementById('themeToggle');
  var themeIcon   = document.getElementById('themeIcon');

  if (!themeToggle || !themeIcon) return;

  var savedTheme = localStorage.getItem('carff_theme');
  if (savedTheme === 'light' || savedTheme === 'dark') {
    root.setAttribute('data-theme', savedTheme);
  }

  updateThemeIcon();

  themeToggle.addEventListener('click', function () {
    var current = root.getAttribute('data-theme') || 'dark';
    var next    = current === 'dark' ? 'light' : 'dark';
    root.setAttribute('data-theme', next);
    localStorage.setItem('carff_theme', next);
    updateThemeIcon();
  });

  function updateThemeIcon() {
    var theme = root.getAttribute('data-theme') || 'dark';
    if (theme === 'dark') {
      themeIcon.classList.remove('fa-sun');
      themeIcon.classList.add('fa-moon');
    } else {
      themeIcon.classList.remove('fa-moon');
      themeIcon.classList.add('fa-sun');
    }
  }
}

/* ============================================================
   2. HEADER AO ROLAR
   ============================================================ */

function initHeaderScroll() {
  var header = document.querySelector('.header');
  if (!header) return;

  function handleScroll() {
    if (window.scrollY > 30) {
      header.classList.add('scrolled');
    } else {
      header.classList.remove('scrolled');
    }
  }

  handleScroll();
  window.addEventListener('scroll', handleScroll);
}

/* ============================================================
   3. MENU MOBILE
   ============================================================ */

function initNavMenu() {
  var hamburger = document.getElementById('hamburger');
  var navMenu   = document.getElementById('navMenu');

  if (!hamburger || !navMenu) return;

  hamburger.addEventListener('click', function () {
    var isOpen = navMenu.classList.toggle('open');
    hamburger.classList.toggle('open', isOpen);
    hamburger.setAttribute('aria-expanded', String(isOpen));
    hamburger.setAttribute('aria-label', isOpen ? 'Fechar menu' : 'Abrir menu');
  });

  navMenu.addEventListener('click', function (e) {
    if (e.target.classList.contains('nav__link')) {
      navMenu.classList.remove('open');
      hamburger.classList.remove('open');
      hamburger.setAttribute('aria-expanded', 'false');
      hamburger.setAttribute('aria-label', 'Abrir menu');
    }
  });
}

/* ============================================================
   4. LINK ATIVO NO MENU
   ============================================================ */

function initActiveLinks() {
  var sections = document.querySelectorAll('section[id]');
  var navLinks = document.querySelectorAll('.nav__link');

  if (!sections.length || !navLinks.length) return;

  function handleActiveLink() {
    var scrollY = window.pageYOffset;

    sections.forEach(function (section) {
      var sectionHeight = section.offsetHeight;
      var sectionTop    = section.offsetTop - 140;
      var sectionId     = section.getAttribute('id');

      if (scrollY > sectionTop && scrollY <= sectionTop + sectionHeight) {
        navLinks.forEach(function (link) {
          link.classList.remove('active-link');
          link.removeAttribute('aria-current');

          if (link.getAttribute('href') === '#' + sectionId) {
            link.classList.add('active-link');
            link.setAttribute('aria-current', 'page');
          }
        });
      }
    });
  }

  handleActiveLink();
  window.addEventListener('scroll', handleActiveLink);
}

/* ============================================================
   5. BOTÃO VOLTAR AO TOPO
   ============================================================ */

function initBackToTop() {
  var btn = document.getElementById('backToTop');
  if (!btn) return;

  function toggleVisibility() {
    if (window.scrollY > 350) {
      btn.classList.add('visible');
    } else {
      btn.classList.remove('visible');
    }
  }

  btn.addEventListener('click', function () {
    window.scrollTo({ top: 0, behavior: 'smooth' });
  });

  toggleVisibility();
  window.addEventListener('scroll', toggleVisibility);
}

/* ============================================================
   6. ANIMAÇÃO REVEAL AO ROLAR
   ============================================================ */

function initRevealOnScroll() {
  var revealEls = document.querySelectorAll('.reveal');
  if (!revealEls.length) return;

  var observer = new IntersectionObserver(function (entries) {
    entries.forEach(function (entry) {
      if (entry.isIntersecting) {
        entry.target.classList.add('visible');

        // dispara animação das barras de skills
        if (
          entry.target.classList.contains('skill-card') ||
          entry.target.closest('.skills__grid')
        ) {
          animateSkillBars();
        }

        observer.unobserve(entry.target);
      }
    });
  }, {
    threshold: 0.15
  });

  revealEls.forEach(function (el) {
    observer.observe(el);
  });
}

/* ============================================================
   7. BARRAS DE SKILLS
   ============================================================ */

function initSkillBars() {
  // lógica disparada pelo IntersectionObserver (initRevealOnScroll)
}

function animateSkillBars() {
  var fills = document.querySelectorAll('.skill-card__bar-fill');
  fills.forEach(function (fill) {
    var targetWidth = fill.dataset.width || 0;
    requestAnimationFrame(function () {
      fill.style.width = targetWidth + '%';
    });
  });
}

/* ============================================================
   8. FILTRO DE PROJETOS
   ============================================================ */

function initProjectFilter() {
  var filterButtons = document.querySelectorAll('.filter-btn');
  var projectCards  = document.querySelectorAll('.project-card');

  if (!filterButtons.length || !projectCards.length) return;

  filterButtons.forEach(function (btn) {
    btn.addEventListener('click', function () {
      var filter = btn.dataset.filter;

      filterButtons.forEach(function (b) {
        b.classList.remove('active');
      });
      btn.classList.add('active');

      projectCards.forEach(function (card) {
        var category = card.dataset.category || '';
        if (filter === 'all' || category === filter) {
          card.classList.remove('hidden');
        } else {
          card.classList.add('hidden');
        }
      });
    });
  });
}

/* ============================================================
   9. SLIDER DE DEPOIMENTOS
   ============================================================ */

function initTestimonialsSlider() {
  var track    = document.getElementById('testimonialsTrack');
  var prevBtn  = document.getElementById('sliderPrev');
  var nextBtn  = document.getElementById('sliderNext');
  var dotsWrap = document.getElementById('sliderDots');

  if (!track || !prevBtn || !nextBtn || !dotsWrap) return;

  var slides      = Array.from(track.children);
  var totalSlides = slides.length;
  var current     = 0;
  var autoTimer   = null;
  var AUTO_TIME   = 7000;

  // criar dots
  slides.forEach(function (_, index) {
    var dot = document.createElement('button');
    dot.classList.add('dot');
    if (index === 0) dot.classList.add('active');
    dot.setAttribute('aria-label', 'Ir para o depoimento ' + (index + 1));
    dot.addEventListener('click', function () {
      goTo(index);
    });
    dotsWrap.appendChild(dot);
  });

  var dots = Array.from(dotsWrap.children);

  function update() {
    track.style.transform = 'translateX(-' + (current * 100) + '%)';
    dots.forEach(function (d, i) {
      d.classList.toggle('active', i === current);
    });
  }

  function goTo(index) {
    current = (index + totalSlides) % totalSlides;
    update();
    restartAuto();
  }

  function next() {
    goTo(current + 1);
  }

  function prev() {
    goTo(current - 1);
  }

  function startAuto() {
    if (autoTimer) return;
    autoTimer = setInterval(next, AUTO_TIME);
  }

  function restartAuto() {
    clearInterval(autoTimer);
    autoTimer = null;
    startAuto();
  }

  nextBtn.addEventListener('click', next);
  prevBtn.addEventListener('click', prev);

  // pausa no hover
  track.addEventListener('mouseenter', function () {
    clearInterval(autoTimer);
    autoTimer = null;
  });

  track.addEventListener('mouseleave', function () {
    startAuto();
  });

  // swipe em mobile
  var startX = 0;
  var endX   = 0;

  track.addEventListener('touchstart', function (e) {
    startX = e.changedTouches[0].screenX;
  }, { passive: true });

  track.addEventListener('touchend', function (e) {
    endX = e.changedTouches[0].screenX;
    var diff = startX - endX;
    if (Math.abs(diff) > 50) {
      if (diff > 0) {
        next();
      } else {
        prev();
      }
    }
  }, { passive: true });

  startAuto();
}

/* ============================================================
   10. TEXTO DIGITANDO NO HERO
   ============================================================ */

function initTypedHero() {
  var typedEl = document.getElementById('typedText');
  if (!typedEl) return;

  var phrases = [
  'Carff · Full Stack Developer (HTML, CSS & JavaScript)',
  'Full Stack · focado em boas práticas',
  'Do caos ao código · construindo interfaces modernas',
  'Transformando ideias em aplicações web funcionais',
  'Frontend & UX · código limpo, design eficiente',
  'Desenvolvendo experiências digitais simples e diretas',
  'Código organizado · interfaces rápidas · usuários felizes',
  'Do layout ao deploy · cuidado em cada detalhe',
  'Desenvolvedor Web · focado em performance e clareza',
  'Construindo páginas leves, responsivas e bem estruturadas'
];

  var phraseIndex = 0;
  var charIndex   = 0;
  var isDeleting  = false;

  function type() {
    var currentPhrase = phrases[phraseIndex];

    if (!isDeleting) {
      typedEl.textContent = currentPhrase.substring(0, charIndex + 1);
      charIndex++;

      if (charIndex === currentPhrase.length) {
        isDeleting = true;
        setTimeout(type, 2000);
        return;
      }
    } else {
      typedEl.textContent = currentPhrase.substring(0, charIndex - 1);
      charIndex--;

      if (charIndex === 0) {
        isDeleting  = false;
        phraseIndex = (phraseIndex + 1) % phrases.length;
      }
    }

    var speed = isDeleting ? 45 : 85;
    setTimeout(type, speed);
  }

  type();
}

/* ============================================================
   11. FORMULÁRIO DE CONTATO
   ============================================================ */

function initContactForm() {
  var form         = document.getElementById('contactForm');
  var nameInput    = document.getElementById('name');
  var emailInput   = document.getElementById('email');
  var subjectInput = document.getElementById('subject');
  var messageInput = document.getElementById('message');

  var nameError    = document.getElementById('nameError');
  var emailError   = document.getElementById('emailError');
  var subjectError = document.getElementById('subjectError');
  var messageError = document.getElementById('messageError');

  var feedbackEl   = document.getElementById('formFeedback');
  var submitBtn    = document.getElementById('submitBtn');
  var btnText      = document.getElementById('btnText');

  if (!form || !nameInput || !emailInput || !subjectInput || !messageInput) return;

  // usando RegExp para evitar problemas de quebra de linha
  var emailRegex = new RegExp('^[^\\s@]+@[^\\s@]+\\.[^\\s@]+$');

  form.addEventListener('submit', function (e) {
    e.preventDefault();
    clearErrors();

    var isValid = true;

    if (nameInput.value.trim().length < 3) {
      setError(nameInput, nameError, 'Informe seu nome completo.');
      isValid = false;
    }

    var emailValue = emailInput.value.trim();
    if (!emailValue || !emailRegex.test(emailValue)) {
      setError(emailInput, emailError, 'Informe um e-mail válido.');
      isValid = false;
    }

    if (subjectInput.value.trim().length < 3) {
      setError(subjectInput, subjectError, 'Informe um assunto.');
      isValid = false;
    }

    if (messageInput.value.trim().length < 10) {
      setError(messageInput, messageError, 'Escreva uma mensagem com pelo menos 10 caracteres.');
      isValid = false;
    }

    if (!isValid) {
      showFeedback('Por favor, corrija os campos destacados.', 'error');
      return;
    }

    simulateSend();
  });

  function setError(input, errorEl, message) {
    input.classList.add('error');
    if (errorEl) errorEl.textContent = message;
  }

  function clearErrors() {
    [nameInput, emailInput, subjectInput, messageInput].forEach(function (input) {
      input.classList.remove('error');
    });
    [nameError, emailError, subjectError, messageError].forEach(function (el) {
      if (el) el.textContent = '';
    });
    if (feedbackEl) {
      feedbackEl.textContent = '';
      feedbackEl.classList.remove('success', 'error');
    }
  }

  function showFeedback(message, type) {
    if (!feedbackEl) return;
    feedbackEl.textContent = message;
    feedbackEl.classList.remove('success', 'error');
    feedbackEl.classList.add(type === 'success' ? 'success' : 'error');
  }

  function simulateSend() {
    if (!submitBtn || !btnText) return;

    submitBtn.disabled  = true;
    btnText.textContent = 'Enviando...';

    var subject = encodeURIComponent(subjectInput.value.trim());
    var body    = encodeURIComponent(
      'Nome: '   + nameInput.value.trim() +
      '\nE-mail: ' + emailInput.value.trim() +
      '\n\n'     + messageInput.value.trim()
    );

    var mailto = 'mailto:filipe.carff282@gmail.com?subject=' + subject + '&body=' + body;

    setTimeout(function () {
      window.location.href = mailto;
      submitBtn.disabled  = false;
      btnText.textContent = 'Enviar mensagem';
      showFeedback('Abrindo seu cliente de e-mail. Obrigado pelo contato!', 'success');
      form.reset();
    }, 800);
  }
}

/* ============================================================
   12. QR CODE DO WHATSAPP
   ============================================================ */

function initQRCode() {
  var qrBox = document.getElementById('qrCodeBox');
  if (!qrBox) return;

  // como você já tem a imagem qrcode-whatsapp.png, apenas garantimos que ela esteja ali
  if (!qrBox.querySelector('img')) {
    var img = document.createElement('img');
    img.src = 'qrcode-whatsapp.png';
    img.alt = 'QR Code WhatsApp Carff';
    img.width  = 120;
    img.height = 120;
    qrBox.appendChild(img);
  }
}