function renderDate(currentDate) {
    let formatDate = function(date) {
        let day = date.getUTCDate().toString().padStart(2, '0');
        let month = (date.getUTCMonth() + 1).toString().padStart(2, '0');
        let year = date.getUTCFullYear().toString();

        return `${day}.${month}.${year}`;
    }

    document.querySelector(".date").innerHTML = formatDate(currentDate);
}
