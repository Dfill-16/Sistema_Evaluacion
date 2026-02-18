let tiempoInactividad = 0;
let intervaloInactividad = null;
const TIEMPO_LIMITE = 120; // 2 minutos en segundos


function resetearInactividad() {
    tiempoInactividad = 0;
}


function iniciarMonitoreoInactividad() {

    document.addEventListener('mousemove', resetearInactividad);
    document.addEventListener('keypress', resetearInactividad);
    document.addEventListener('click', resetearInactividad);
    document.addEventListener('scroll', resetearInactividad);
    document.addEventListener('touchstart', resetearInactividad);

    // Incrementar el contador cada segundo
    intervaloInactividad = setInterval(() => {
        tiempoInactividad++;
        
        // Mostrar advertencia a los 90 segundos (1.5 minutos)
        if (tiempoInactividad === 90) {
            mostrarAdvertencia();
        }
        
        // Completar examen por inactividad a los 120 segundos (2 minutos)
        if (tiempoInactividad >= TIEMPO_LIMITE) {
            completarPorInactividad();
        }
    }, 1000);
}

// Mostrar advertencia de inactividad
function mostrarAdvertencia() {
    alert('⚠️ Advertencia: Has estado inactivo por 1.5 minutos. El examen se completará automáticamente en 30 segundos si no realizas ninguna acción.');
    document.dispatchEvent(new Event('inactividad:advertencia'));
}

// Completar examen por inactividad
function completarPorInactividad() {
    // Detener el intervalo
    clearInterval(intervaloInactividad);
    
    // Obtener el token CSRF
    const csrftoken = document.querySelector('[name=csrfmiddlewaretoken]').value;
    
    // Hacer petición AJAX para marcar el examen como completado
    fetch('/examenes/verificar-inactividad/', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
            'X-CSRFToken': csrftoken
        },
        body: JSON.stringify({})
    })
    .then(response => response.json())
    .then(data => {
        if (data.status === 'completado') {
            alert(`⏱️ El examen ha sido completado automáticamente por inactividad.\nTu puntaje: ${data.puntaje}`);
            // Redirigir a la página de inicio o resultados
            window.location.href = '/';
        }
    })
    .catch(error => {
        console.error('Error al completar examen:', error);
        alert('El examen ha sido completado por inactividad. Serás redirigido.');
        window.location.href = '/';
    });
}

// Prevenir que el usuario cierre o recargue la página sin advertencia
window.addEventListener('beforeunload', (event) => {
    event.preventDefault();
    event.returnValue = '¿Estás seguro de que deseas salir? El examen se marcará como completado.';
});

// Iniciar el monitoreo cuando la página cargue
document.addEventListener('DOMContentLoaded', () => {
    iniciarMonitoreoInactividad();
    console.log('Monitoreo de inactividad iniciado. Tiempo límite: 2 minutos');
});
