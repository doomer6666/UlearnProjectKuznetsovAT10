// Когда пользователь прокручивает вниз 20px от верхней части документа, покажите кнопку
window.onscroll = function() {scrollFunction()};

function scrollFunction() {
    const toTopBtn = document.getElementById("toTopBtn");
    if (document.body.scrollTop > 20 || document.documentElement.scrollTop > 20) {
        toTopBtn.style.display = "block";
    } else {
        toTopBtn.style.display = "none";
    }
}

// Когда пользователь нажимает на кнопку, плавно прокрутите до верхней части документа
document.getElementById("toTopBtn").addEventListener("click", function() {
    window.scrollTo({
        top: 0,
        behavior: 'smooth' // Добавляем плавный переход
    });
});
