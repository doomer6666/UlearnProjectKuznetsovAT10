document.getElementById("loadMore").addEventListener("click", function() {
    var hiddenRows = document.querySelectorAll("tr.hidden");
    var count = 0;
    for (var i = 0; i < hiddenRows.length; i++) {
        if (count < 15) {
            hiddenRows[i].classList.remove("hidden");
            count++;
        }
    }
    if (hiddenRows.length <= 15) {
        this.style.display = 'none';  // Скрываем кнопку, если больше нет скрытых строк
    }
});
