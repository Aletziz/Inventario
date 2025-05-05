// Sistema de temas mejorado
class ThemeManager {
    constructor() {
        this.html = document.documentElement;
        this.themeToggle = document.getElementById('themeToggle');
        this.themeIcon = document.getElementById('themeIcon');
        this.themeText = document.getElementById('themeText');
        this.currentTheme = localStorage.getItem('theme') || 'light';
    }

    init() {
        // Establecer tema inicial
        this.setTheme(this.currentTheme);

        // Solo agregar event listeners si estamos en una página con controles de tema
        if (this.themeToggle && this.themeIcon && this.themeText) {
            this.themeToggle.addEventListener('click', () => this.toggleTheme());
        }
    }

    setTheme(theme) {
        this.currentTheme = theme;
        this.html.setAttribute('data-bs-theme', theme);
        localStorage.setItem('theme', theme);

        // Solo actualizar UI si los elementos existen
        if (this.themeIcon && this.themeText && this.themeToggle) {
            this.updateUI();
        }
    }

    toggleTheme() {
        const newTheme = this.currentTheme === 'light' ? 'dark' : 'light';
        this.setTheme(newTheme);
    }

    updateUI() {
        if (!this.themeIcon || !this.themeText || !this.themeToggle) return;

        // Actualizar icono
        this.themeIcon.className = this.currentTheme === 'dark' 
            ? 'bi bi-moon-fill' 
            : 'bi bi-sun-fill';

        // Actualizar texto
        this.themeText.textContent = this.currentTheme === 'dark' 
            ? 'Modo Oscuro' 
            : 'Modo Claro';

        // Actualizar clases del botón
        if (this.currentTheme === 'dark') {
            this.themeToggle.classList.remove('btn-outline-light');
            this.themeToggle.classList.add('btn-outline-secondary');
        } else {
            this.themeToggle.classList.remove('btn-outline-secondary');
            this.themeToggle.classList.add('btn-outline-light');
        }
    }
}

// Inicializar el sistema de temas cuando el DOM esté listo
document.addEventListener('DOMContentLoaded', () => {
    const themeManager = new ThemeManager();
    themeManager.init();
}); 