/**
 * Scripts Globales del Sistema de Evaluación
 * ============================================
 * Funciones JavaScript compartidas por todas las vistas
 */

// Esperar a que el DOM esté completamente cargado
document.addEventListener('DOMContentLoaded', function() {
    
    // ============================================
    // AUTO-DISMISS DE MENSAJES FLASH
    // ============================================
    const alerts = document.querySelectorAll('[data-alert-dismiss]');
    
    alerts.forEach(alert => {
        // Auto-cerrar después de 5 segundos
        setTimeout(() => {
            alert.style.transition = 'opacity 0.5s ease';
            alert.style.opacity = '0';
            
            setTimeout(() => {
                alert.remove();
            }, 500);
        }, 5000);
        
        // Cerrar al hacer clic en el botón X
        const closeBtn = alert.querySelector('[data-dismiss-btn]');
        if (closeBtn) {
            closeBtn.addEventListener('click', () => {
                alert.style.transition = 'opacity 0.3s ease';
                alert.style.opacity = '0';
                
                setTimeout(() => {
                    alert.remove();
                }, 300);
            });
        }
    });
    
    // ============================================
    // NAVEGACIÓN MÓVIL (Hamburger Menu)
    // ============================================
    const mobileMenuBtn = document.getElementById('mobile-menu-button');
    const mobileMenu = document.getElementById('mobile-menu');
    
    if (mobileMenuBtn && mobileMenu) {
        mobileMenuBtn.addEventListener('click', function() {
            const isHidden = mobileMenu.classList.contains('hidden');
            
            if (isHidden) {
                mobileMenu.classList.remove('hidden');
                mobileMenu.classList.add('animate-fade-in');
            } else {
                mobileMenu.classList.add('hidden');
                mobileMenu.classList.remove('animate-fade-in');
            }
            
            // Cambiar icono del hamburger (opcional)
            this.setAttribute('aria-expanded', isHidden ? 'true' : 'false');
        });
    }
    
    // ============================================
    // DROPDOWN DE USUARIO
    // ============================================
    const userMenuBtn = document.getElementById('user-menu-button');
    const userMenu = document.getElementById('user-menu');
    
    if (userMenuBtn && userMenu) {
        userMenuBtn.addEventListener('click', function(e) {
            e.stopPropagation();
            userMenu.classList.toggle('hidden');
        });
        
        // Cerrar dropdown al hacer clic fuera
        document.addEventListener('click', function(e) {
            if (!userMenuBtn.contains(e.target) && !userMenu.contains(e.target)) {
                userMenu.classList.add('hidden');
            }
        });
    }
    
    // ============================================
    // CONFIRMACIÓN DE ELIMINACIÓN
    // ============================================
    const deleteButtons = document.querySelectorAll('[data-confirm-delete]');
    
    deleteButtons.forEach(button => {
        button.addEventListener('click', function(e) {
            const message = this.getAttribute('data-confirm-message') || 
                          '¿Estás seguro de que deseas eliminar este elemento?';
            
            if (!confirm(message)) {
                e.preventDefault();
                return false;
            }
        });
    });
    
    // ============================================
    // VALIDACIÓN DE FORMULARIOS
    // ============================================
    const forms = document.querySelectorAll('form[data-validate]');
    
    forms.forEach(form => {
        form.addEventListener('submit', function(e) {
            const requiredFields = form.querySelectorAll('[required]');
            let isValid = true;
            
            requiredFields.forEach(field => {
                if (!field.value.trim()) {
                    isValid = false;
                    field.classList.add('border-red-500');
                    
                    // Remover clase de error al escribir
                    field.addEventListener('input', function() {
                        this.classList.remove('border-red-500');
                    });
                }
            });
            
            if (!isValid) {
                e.preventDefault();
                alert('Por favor, completa todos los campos requeridos.');
            }
        });
    });
    
    // ============================================
    // TOOLTIP SIMPLE (opcional)
    // ============================================
    const tooltips = document.querySelectorAll('[data-tooltip]');
    
    tooltips.forEach(element => {
        element.addEventListener('mouseenter', function() {
            const text = this.getAttribute('data-tooltip');
            const tooltip = document.createElement('div');
            tooltip.className = 'fixed bg-gray-800 text-white text-xs rounded py-1 px-2 z-50';
            tooltip.textContent = text;
            tooltip.id = 'tooltip-' + Date.now();
            
            document.body.appendChild(tooltip);
            
            const rect = this.getBoundingClientRect();
            tooltip.style.top = (rect.top - tooltip.offsetHeight - 5) + 'px';
            tooltip.style.left = (rect.left + (rect.width / 2) - (tooltip.offsetWidth / 2)) + 'px';
            
            this._tooltipId = tooltip.id;
        });
        
        element.addEventListener('mouseleave', function() {
            const tooltip = document.getElementById(this._tooltipId);
            if (tooltip) {
                tooltip.remove();
            }
        });
    });
    
    // ============================================
    // SCROLL SUAVE PARA ANCLAS
    // ============================================
    const anchorLinks = document.querySelectorAll('a[href^="#"]');
    
    anchorLinks.forEach(link => {
        link.addEventListener('click', function(e) {
            const href = this.getAttribute('href');
            
            if (href !== '#' && href !== '') {
                e.preventDefault();
                const target = document.querySelector(href);
                
                if (target) {
                    target.scrollIntoView({
                        behavior: 'smooth',
                        block: 'start'
                    });
                }
            }
        });
    });
    
    // ============================================
    // PREVENIR DOUBLE SUBMIT EN FORMULARIOS
    // ============================================
    const submitForms = document.querySelectorAll('form');
    
    submitForms.forEach(form => {
        form.addEventListener('submit', function() {
            const submitBtn = this.querySelector('button[type="submit"]');
            
            if (submitBtn && !submitBtn.disabled) {
                submitBtn.disabled = true;
                submitBtn.classList.add('opacity-50', 'cursor-not-allowed');
                
                const originalText = submitBtn.textContent;
                submitBtn.textContent = 'Procesando...';
                
                // Rehabilitar después de 3 segundos por seguridad
                setTimeout(() => {
                    submitBtn.disabled = false;
                    submitBtn.classList.remove('opacity-50', 'cursor-not-allowed');
                    submitBtn.textContent = originalText;
                }, 3000);
            }
        });
    });
    
    // ============================================
    // SCROLL TO TOP BUTTON
    // ============================================
    const scrollToTopBtn = document.getElementById('scroll-to-top');
    
    if (scrollToTopBtn) {
        // Mostrar/ocultar según scroll
        window.addEventListener('scroll', function() {
            if (window.pageYOffset > 300) {
                scrollToTopBtn.classList.remove('hidden');
                scrollToTopBtn.classList.add('show');
            } else {
                scrollToTopBtn.classList.remove('show');
                scrollToTopBtn.classList.add('hidden');
            }
        });
        
        // Scroll suave al hacer clic
        scrollToTopBtn.addEventListener('click', function() {
            window.scrollTo({
                top: 0,
                behavior: 'smooth'
            });
        });
    }
    
    // ============================================
    // LOG DE CONSOLA (Solo en desarrollo)
    // ============================================
    console.log('✅ Sistema de Evaluación Virtual - Scripts cargados correctamente');
    
});

// ============================================
// FUNCIONES GLOBALES EXPORTABLES
// ============================================

/**
 * Mostrar notificación toast personalizada
 * @param {string} message - Mensaje a mostrar
 * @param {string} type - Tipo: 'success', 'error', 'warning', 'info'
 */
function showToast(message, type = 'info') {
    const toast = document.createElement('div');
    const colors = {
        success: 'bg-green-500',
        error: 'bg-red-500',
        warning: 'bg-yellow-500',
        info: 'bg-blue-500'
    };
    
    toast.className = `fixed top-4 right-4 ${colors[type]} text-white px-6 py-3 rounded-lg shadow-lg z-50 animate-fade-in`;
    toast.textContent = message;
    
    document.body.appendChild(toast);
    
    setTimeout(() => {
        toast.style.transition = 'opacity 0.5s ease';
        toast.style.opacity = '0';
        
        setTimeout(() => {
            toast.remove();
        }, 500);
    }, 3000);
}

/**
 * Copiar texto al portapapeles
 * @param {string} text - Texto a copiar
 */
function copyToClipboard(text) {
    navigator.clipboard.writeText(text).then(() => {
        showToast('Copiado al portapapeles', 'success');
    }).catch(() => {
        showToast('Error al copiar', 'error');
    });
}
