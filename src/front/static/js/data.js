let url = "http://127.0.0.1/report/1"

async function sendRequest(url){
    let response = await fetch(url)
    if (response.ok) {
        return response.json();
    } else {
        alert("Ошибка HTTP: " + response.status);
        return Promise.reject(response.status)
    }
}

async function render() {
    let data = await sendRequest(url);

    let groupedData = groupByActivity(data.activities)
    let convertedToChartData = convertToChartData(groupedData)

    renderDate(new Date(data.date))
    renderChart(convertedToChartData);
}

render();
