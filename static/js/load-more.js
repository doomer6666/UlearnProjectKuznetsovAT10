document.addEventListener("DOMContentLoaded", function() {
    // Обработка обычных таблиц
    document.querySelectorAll(".loadMore").forEach(button => {
        button.addEventListener("click", function() {
            var contentBlock = this.parentElement;
            var hiddenRows = contentBlock.querySelectorAll("tr.hidden");
            var count = 0;
            for (var i = 0; i < hiddenRows.length; i++) {
                if (count < 10) {
                    hiddenRows[i].classList.remove("hidden");
                    count++;
                }
            }
            if (hiddenRows.length <= 10) {
                this.style.display = 'none';  // Скрываем кнопку, если больше нет скрытых строк
            }
        });
    });

    // Обработка таблиц с навыками
    document.querySelectorAll(".skills-button").forEach(button => {
        button.addEventListener("click", function() {
            var parentDiv = this.closest(".content-block");
            var hiddenRows = parentDiv.querySelectorAll("tr.hidden");
            var count = 0;
            for (var i = 0; i < hiddenRows.length; i++) {
                if (count < 10) {
                    hiddenRows[i].classList.remove("hidden");
                    count++;
                }
            }
            if (hiddenRows.length <= 10) {
                this.style.display = 'none';  // Скрываем кнопку, если больше нет скрытых строк
            }
        });
    });
});
