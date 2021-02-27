var backgroundColor = [
                'rgba(255, 99, 132)',
                'rgba(54, 162, 235)',
                'rgba(255, 206, 86)',
                'rgba(75, 192, 192)',
                'rgba(153, 102, 255)',
                'rgba(255, 159, 64)'
            ];

var backgroundColorLight = [
                'rgba(255, 99, 132, 0.4)',
                'rgba(54, 162, 235, 0.4)',
                'rgba(255, 206, 86, 0.4)',
                'rgba(75, 192, 192, 0.4)',
                'rgba(153, 102, 255, 0.4)',
                'rgba(255, 159, 64, 0.4)'
            ];


console.log(data);

var myChart = new Chart(ctx, {
    type: 'doughnut',
    data: {
        datasets : [{
            data: data,
            backgroundColor: backgroundColor
        }],
        labels: labels
    },
    options: {
        responsive: true,
        legend: {
            position: 'bottom',
        },
        cutoutPercentage: '15',
        plugins: {
            datalabels: {
                color: '#fff',
                anchor: 'end',
                align: 'start',
                offset: '-5',
                borderWidth: '2',
                borderColor: '#fff',
                borderRadius: '25',
                backgroundColor: (context) => {
                    return context.dataset.backgroundColor;
                },
                font: {
                    weight: 'bold',
                    size: '13'
                },
                formatter: (value) => {
                    return value + '%'
                },
                clip: true,
                display: 'auto',
            }
        },
        tooltips: {
            callbacks: {
                label: function(tooltipItems, data) {
                    return data.labels[tooltipItems.index];
                }
            }
        }
    }
})






function setBackgroundColor(){
    if (numberOfCategories > 0) {
        for (var i = 0; i < numberOfCategories; i++) {
            document.getElementById('cat_' + i).style.backgroundColor = backgroundColorLight[i]
        }
    }
}
























/*
var myChart = new Chart(ctx2, {
    type: 'doughnut',
    data: {
        datasets : [{
            data: data,
            backgroundColor: backgroundColor
        }],
        labels: labels
    },
    options: {
        responsive: true,
        legend: {
            position: 'bottom'
        },

        plugins: {
            datalabels: {
                color: 'blue',
                display: 'auto',
                clip: false,
                borderWidth: '2',
                borderColor: '#fff',
                borderRadius: '25',
                backgroundColor: (context) => {
                    return context.dataset.backgroundColor;
                },
                font: {
                    weight: 'bold',
                    size: '13'
                },
                labels: {
                    title: {
                        color: '#fff',
                        anchor: 'center',
                        align: 'center',
                        offset: '10',
                        formatter: (value) => {
                            return value + '%'
                        },
                    },
                    value: {
                        color: '#000',
                        anchor: 'end',
                        formatter: function(value, context) {
                            return context.chart.data.labels[context.dataIndex];
                        }
                    }
                }
            }
        }
    }
})
*/

