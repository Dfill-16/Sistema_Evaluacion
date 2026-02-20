(function () {
    "use strict";

    /**
     * Hace que los checkboxes "es_correcta" dentro de cada grupo de respuestas
     * se comporten como radio buttons: al marcar uno, desmarca los otros del mismo grupo.
     *
     * Funciona con cualquier prefijo de formset que genere django-nested-admin.
     * El atributo name sigue el patrón: <cualquier_prefix>-N-es_correcta
     * El "grupo" se identifica por el prefijo común (todo antes del último índice N).
     */
    function enforceRadio(changedCheckbox) {
        var name = changedCheckbox.name;
        // Captura el prefijo del grupo: todo antes del último "-NÚMERO-es_correcta"
        // Ejemplo: "preguntas-0-respuestas-2-es_correcta" → prefix = "preguntas-0-respuestas-"
        var match = name.match(/^(.*-)\d+-es_correcta$/);
        if (!match) return;
        var groupPrefix = match[1];

        document
            .querySelectorAll(
                'input[type="checkbox"][name^="' + groupPrefix + '"][name$="-es_correcta"]'
            )
            .forEach(function (cb) {
                if (cb !== changedCheckbox) {
                    cb.checked = false;
                }
            });
    }

    function attachListeners() {
        document
            .querySelectorAll('input[type="checkbox"][name$="-es_correcta"]')
            .forEach(function (cb) {
                if (!cb.dataset.radioAttached) {
                    cb.dataset.radioAttached = "1";
                    cb.addEventListener("change", function () {
                        if (this.checked) enforceRadio(this);
                    });
                }
            });
    }

    document.addEventListener("DOMContentLoaded", function () {
        attachListeners();
        // Re-ejecutar cuando se agreguen preguntas/respuestas dinámicamente
        var observer = new MutationObserver(function () {
            attachListeners();
        });
        observer.observe(document.body, { childList: true, subtree: true });
    });
})();
