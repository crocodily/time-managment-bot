function renderChart(data) {
    let options = {
        series: data,
        chart: chartSettings,
        plotOptions: plotOptionsSettings,
        colors: colorsSettings,
        stroke: strokeSettings,
        fill: fillSettings,
        grid: gridSettings,
        xaxis: xAxisSettings,
        legend: legendSettings,
        tooltip: tooltipSettings,
        id: chartId
    };

    let chartRender = new ApexCharts(document.querySelector(".chart"), options);
    chartRender.render();
}
