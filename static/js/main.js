/**
 * 屏南龙潭非遗数字化年轻化平台 - 全局JS
 * 风格：莫奈柔雾 + shadcn/ui 交互模式
 */

// ============ 导航栏滚动效果 ============
document.addEventListener('DOMContentLoaded', function() {
  const navbar = document.querySelector('.navbar');
  const mobileToggle = document.querySelector('.nav-mobile-toggle');
  const navLinks = document.querySelector('.nav-links');

  window.addEventListener('scroll', function() {
    if (window.scrollY > 10) {
      navbar.classList.add('scrolled');
    } else {
      navbar.classList.remove('scrolled');
    }
  });

  if (mobileToggle) {
    mobileToggle.addEventListener('click', function() {
      navLinks.classList.toggle('open');
    });
  }

  // ============ 滚动动画 ============
  const fadeElements = document.querySelectorAll('.fade-in');
  const observer = new IntersectionObserver(function(entries) {
    entries.forEach(function(entry) {
      if (entry.isIntersecting) {
        entry.target.classList.add('visible');
        observer.unobserve(entry.target);
      }
    });
  }, {
    threshold: 0.1,
    rootMargin: '0px 0px -30px 0px'
  });

  fadeElements.forEach(function(el) {
    observer.observe(el);
  });

  // ============ 统计数字动画 ============
  const statNumbers = document.querySelectorAll('.stat-number[data-target]');
  if (statNumbers.length > 0) {
    const statObserver = new IntersectionObserver(function(entries) {
      entries.forEach(function(entry) {
        if (entry.isIntersecting) {
          animateNumber(entry.target);
          statObserver.unobserve(entry.target);
        }
      });
    }, { threshold: 0.5 });

    statNumbers.forEach(function(el) {
      statObserver.observe(el);
    });
  }

  function animateNumber(el) {
    const target = parseInt(el.getAttribute('data-target'));
    const suffix = el.getAttribute('data-suffix') || '';
    const duration = 1200;
    const step = target / (duration / 16);
    let current = 0;

    function update() {
      current += step;
      if (current >= target) {
        el.textContent = target + suffix;
        return;
      }
      el.textContent = Math.floor(current) + suffix;
      requestAnimationFrame(update);
    }
    update();
  }

  // ============ 平滑锚点跳转 ============
  document.querySelectorAll('a[href^="#"]').forEach(function(anchor) {
    anchor.addEventListener('click', function(e) {
      const targetId = this.getAttribute('href');
      if (targetId === '#') return;
      const targetEl = document.querySelector(targetId);
      if (targetEl) {
        e.preventDefault();
        targetEl.scrollIntoView({ behavior: 'smooth', block: 'start' });
        if (navLinks) navLinks.classList.remove('open');
      }
    });
  });

  // ============ 当前页面导航高亮 ============
  const currentPage = window.location.pathname;
  document.querySelectorAll('.nav-links a').forEach(function(link) {
    if (link.getAttribute('href') === currentPage) {
      link.classList.add('active');
    }
  });

  // ============ Accordion 初始化 ============
  initAccordions();

  // ============ 侧边导览滚动监听 ============
  initSidenav();
});

// ============ Accordion 手风琴 ============
function initAccordions() {
  document.querySelectorAll('.accordion-trigger').forEach(function(trigger) {
    trigger.addEventListener('click', function() {
      var item = this.closest('.accordion-item');
      var isOpen = item.getAttribute('data-state') === 'open';

      // 关闭同组其他项
      var group = item.closest('.accordion');
      if (group) {
        group.querySelectorAll('.accordion-item[data-state="open"]').forEach(function(i) {
          if (i !== item) setAccordionState(i, false);
        });
      }

      setAccordionState(item, !isOpen);
    });
  });
}

function setAccordionState(item, open) {
  var content = item.querySelector('.accordion-content');
  if (!content) return;
  item.setAttribute('data-state', open ? 'open' : 'closed');
  if (open) {
    content.style.maxHeight = content.scrollHeight + 'px';
  } else {
    content.style.maxHeight = '0';
  }
}

// ============ 侧边导览滚动监听 ============
function initSidenav() {
  var sidenav = document.querySelector('.page-sidenav');
  if (!sidenav) return;

  var dots = sidenav.querySelectorAll('.page-sidenav-dot');
  var sectionIds = [];
  dots.forEach(function(d) {
    sectionIds.push(d.getAttribute('data-nav'));
  });
  var sections = [];
  sectionIds.forEach(function(id) {
    var el = document.getElementById(id);
    if (el) sections.push(el);
  });

  if (sections.length === 0) return;

  var observer = new IntersectionObserver(function(entries) {
    entries.forEach(function(entry) {
      if (entry.isIntersecting) {
        var id = entry.target.id;
        dots.forEach(function(dot) {
          var isActive = dot.getAttribute('data-nav') === id;
          dot.classList.toggle('active', isActive);
        });
      }
    });
  }, { threshold: 0.2, rootMargin: '-80px 0px -40% 0px' });

  sections.forEach(function(s) { observer.observe(s); });
}

// ============ Toast通知 ============
function showToast(message, type) {
  type = type || 'success';
  var container = document.querySelector('.toast-container');
  if (!container) {
    container = document.createElement('div');
    container.className = 'toast-container';
    document.body.appendChild(container);
  }

  var toast = document.createElement('div');
  toast.className = 'toast toast-' + type;
  toast.textContent = message;
  container.appendChild(toast);

  setTimeout(function() {
    toast.style.opacity = '0';
    toast.style.transform = 'translateX(30px)';
    setTimeout(function() {
      if (toast.parentNode) toast.parentNode.removeChild(toast);
    }, 300);
  }, 3000);
}

// ============ Alert Dialog（替代原生 confirm） ============
function showAlertDialog(options) {
  var title = options.title || '确认操作';
  var description = options.description || '';
  var confirmText = options.confirmText || '确认';
  var cancelText = options.cancelText || '取消';
  var onConfirm = options.onConfirm;
  var onCancel = options.onCancel;
  var destructive = options.destructive || false;

  var overlay = document.createElement('div');
  overlay.className = 'alert-dialog-overlay';

  var content = document.createElement('div');
  content.className = 'alert-dialog-content';

  var header = document.createElement('div');
  header.className = 'alert-dialog-header';
  header.innerHTML = '<div class="alert-dialog-title">' + title + '</div>' +
    (description ? '<div class="alert-dialog-description">' + description + '</div>' : '');

  var footer = document.createElement('div');
  footer.className = 'alert-dialog-footer';

  var cancelBtn = document.createElement('button');
  cancelBtn.className = 'btn btn-outline btn-sm';
  cancelBtn.textContent = cancelText;
  cancelBtn.addEventListener('click', function() {
    document.body.removeChild(overlay);
    if (onCancel) onCancel();
  });

  var confirmBtn = document.createElement('button');
  confirmBtn.className = destructive ? 'btn btn-accent btn-sm' : 'btn btn-primary btn-sm';
  confirmBtn.textContent = confirmText;
  confirmBtn.addEventListener('click', function() {
    document.body.removeChild(overlay);
    if (onConfirm) onConfirm();
  });

  footer.appendChild(cancelBtn);
  footer.appendChild(confirmBtn);
  content.appendChild(header);
  content.appendChild(footer);
  overlay.appendChild(content);
  document.body.appendChild(overlay);

  overlay.addEventListener('click', function(e) {
    if (e.target === overlay) {
      document.body.removeChild(overlay);
      if (onCancel) onCancel();
    }
  });
}

// ============ 内容读取工具 ============
function getContentValue(key, defaultVal) {
  defaultVal = defaultVal || '';
  if (typeof siteContents !== 'undefined' && siteContents[key]) {
    return siteContents[key];
  }
  return defaultVal;
}

// ========== 画廊渲染 ==========
function escapeHtml(str) {
  if (!str) return '';
  return str.replace(/&/g, '&amp;').replace(/</g, '&lt;').replace(/>/g, '&gt;').replace(/"/g, '&quot;').replace(/'/g, '&#39;');
}

function renderGallery(containerId, category, append) {
  const container = document.getElementById(containerId);
  if (!container) return;

  fetch('/api/uploads?category=' + category)
    .then(r => r.json())
    .then(items => {
      if (!items || items.length === 0) {
        if (!append) container.innerHTML = '<div class="gallery-empty">暂无图片素材</div>';
        return;
      }
      var html = items.map(item => `
        <div class="gallery-item">
          ${item.type === 'video'
            ? `<video src="${item.url}" muted loop playsinline></video>`
            : `<img src="${item.url}" alt="${item.description || ''}" loading="lazy">`
          }
          ${item.description ? `<div class="gallery-desc">${escapeHtml(item.description)}</div>` : ''}
        </div>
      `).join('');

      if (append) {
        container.insertAdjacentHTML('beforeend', html);
      } else {
        container.innerHTML = html;
      }

      // Video hover to play
      container.querySelectorAll('video').forEach(v => {
        v.parentElement.addEventListener('mouseenter', () => v.play());
        v.parentElement.addEventListener('mouseleave', () => { v.pause(); v.currentTime = 0; });
      });
    })
    .catch(() => {
      if (!append) container.innerHTML = '<div class="gallery-empty">加载失败</div>';
    });
}

// 页面加载后初始化画廊（仅在对应容器存在的页面生效）
document.addEventListener('DOMContentLoaded', function() {
  renderGallery('general-gallery', 'general');
  // 非遗画廊：追加图片，不覆盖已有视频
  renderGallery('wine-media-gallery', 'wine', true);
  renderGallery('opera-media-gallery', 'opera', true);
});
