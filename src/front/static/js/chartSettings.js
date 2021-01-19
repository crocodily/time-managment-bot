let chartSettings = {
    height: 250,
    type: 'rangeBar'
};

let plotOptionsSettings = {
    bar: {
        horizontal: true,
        barHeight: '70%',
        rangeBarGroupRows: true
    }
};

let colorsSettings = ["#00E396", "#775DD0", "#008FFB", "#FF4560", "#008FFB"];

let strokeSettings = {
    width: 2
};

let fillSettings = {
    type: 'solid',
    opacity: 0.7
};

let gridSettings = {
    show: true,
    borderColor: '#ededed',
    strokeDashArray: 0,
    position: 'back',
    xaxis: {
        lines: {
            show: true
        }
    }
};

let xAxisSettings = {
    type: 'datetime'
};

let legendSettings = {
    position: 'bottom',
    fontSize: '13px',
    height: 55,
    formatter: function(seriesName, opts) {
        return [seriesName, "(", opts.w.globals.series[opts.seriesIndex].length, ")"];
    },
    offsetX: -255,
    offsetY: 15,
    markers: {
        radius: 3
    },
    itemMargin: {
        horizontal: 10
    }
};

let tooltipSettings = {
    custom: function(opts) {
        const fromTime = new Date(opts.y1);
        const toTime = new Date(opts.y2);

        let formatDate = function(date) {
            return date.getUTCHours().toString().padStart(2, '0') + ':' +
                   date.getUTCMinutes().toString().padStart(2, '0');
        }

        const formFromTime = formatDate(fromTime);
        const formToTime = formatDate(toTime);

        return formFromTime + ' - ' + formToTime;
    }
};

let chartId = 1;
