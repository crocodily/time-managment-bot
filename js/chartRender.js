let options = {
    series: convertedToChartData,
    chart: chartSettings,
    plotOptions: plotOptionsSettings,
    colors: colorsSettings,
    stroke: strokeSettings,
    fill: fillSettings,
    grid: gridSettings,
    xaxis: xAxisSettings,
    legend: legendSettings,
    id: chartId
};

let chartRender = new ApexCharts(document.querySelector(".chart"), options);
chartRender.render();
