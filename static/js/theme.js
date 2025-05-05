// Función para inicializar el tema
function initTheme() {
    const html = document.documentElement;
    const savedTheme = localStorage.getItem("theme") || "light";
    html.setAttribute("data-bs-theme", savedTheme);
}

// Inicializar el tema básico
initTheme(); 