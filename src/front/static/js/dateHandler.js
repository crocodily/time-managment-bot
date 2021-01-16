let formatDate = function(date) {
    let day = date.getUTCDate().toString().padStart(2, '0');
    let month = (date.getUTCMonth() + 1).toString().padStart(2, '0');
    let year = date.getUTCFullYear().toString();

    return `${day}.${month}.${year}`;
}

let currentDate = data.date;
let formattedDate = formatDate(currentDate)

document.querySelector(".date").innerHTML = formattedDate;