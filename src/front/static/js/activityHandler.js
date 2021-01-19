function groupByActivity(data) {
    let groupedByActivity = {};

    for (let key in data) {
        let activity = data[key].activityName;
        if (!groupedByActivity[activity]) {
            groupedByActivity[activity] = [];
        }
        groupedByActivity[activity].push(data[key]);
    }

    return groupedByActivity;
}

function convertToChartData(groupedData) {
    let convertedData = []

    for (let activityName in groupedData) {
        let activityData = convertActivityData(groupedData[activityName])
        let convertedDataElem = {
            name: activityName,
            data: activityData
        };
        convertedData.push(convertedDataElem);
    }

    return convertedData;
}

function convertActivityData(activityData) {
    let convertedActivityData = []

    for (let data in activityData) {
        let activityDataElem = {
            x: activityData[data].serviceName,
            y: [
                new Date(activityData[data].fromTime).getTime(),
                new Date(activityData[data].toTime).getTime()
            ]
        };
        convertedActivityData.push(activityDataElem);
    }

    return convertedActivityData;
}
