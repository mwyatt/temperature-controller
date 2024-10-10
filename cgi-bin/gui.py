#!/usr/bin/env python3

import os
import sqlite3
import sys

sys.path.append('/home/martin/Sites/temperature-controller/')
from constants import *

# get settings from the database    
con = sqlite3.connect(DB_NAME)
cur = con.cursor()

# get all settings stored
cur.execute("SELECT * FROM settings")
settings = dict(cur.fetchall())

print(
    f"""\
Content-Type: text/html

<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="utf-8">
  <meta name="viewport" content="width=device-width, initial-scale=1">
  <title>Hello from a CGI Script</title>
  <script src="https://cdn.tailwindcss.com"></script>
</head>
<body>
    <p class="relative bg-white px-4 pt-4 pb-4 shadow-md ring-1 ring-gray-900/5 sm:mx-auto sm:max-w-lg rounded-sm m-4 text-center text-gray-600">Current temp is <span id="current-temp"></span>&deg;C</p>
    <form id="temp_form" class="relative bg-white px-4 pt-4 pb-4 shadow-md ring-1 ring-gray-900/5 sm:mx-auto sm:max-w-lg rounded-sm m-4 text-center text-gray-600">
        <p><label>Target<input type="number" name="target_temp" class="block w-full rounded-sm border-0 p-1.5 px-3 text-gray-900 ring-1 ring-inset ring-gray-300 placeholder:text-gray-400 focus:ring-2 focus:ring-inset focus:ring-indigo-600 sm:text-sm sm:leading-6" value="{settings['target_temp']}"></label></p>
        <span class="bg-gray-300 inline-block my-2 p-1 px-3 rounded-md js-temp-shortcut">10</span>
        <span class="bg-gray-300 inline-block my-2 p-1 px-3 rounded-md js-temp-shortcut">24</span>
        <p><label>Buffer<input type="number" name="buffer_temp" class="block w-full rounded-sm border-0 p-1.5 px-3 text-gray-900 ring-1 ring-inset ring-gray-300 placeholder:text-gray-400 focus:ring-2 focus:ring-inset focus:ring-indigo-600 sm:text-sm sm:leading-6" value="{settings['buffer_temp']}"></label></p>
        <button type="submit" class="bg-gray-300 inline-block my-2 p-1 px-3 rounded-md">Set</button>
    </form>
    <p class="relative bg-white px-4 pt-4 pb-4 shadow-md ring-1 ring-gray-900/5 sm:mx-auto sm:max-w-lg rounded-sm m-4 text-center text-gray-600">Heater is <span id="heater_status"></span></p>

<form id="temp_history" class="relative bg-white px-4 pt-4 pb-4 shadow-md ring-1 ring-gray-900/5 sm:mx-auto sm:max-w-lg rounded-sm m-4 text-center text-gray-600">
<input type="datetime-local" id="start_time" class="rounded-sm border-0 p-1.5 px-3 text-gray-900 ring-1 ring-inset ring-gray-300 placeholder:text-gray-400 focus:ring-2 focus:ring-inset focus:ring-indigo-600 sm:text-sm sm:leading-6" name="start_time" min="2018-01-01" max="2018-12-31" />
<input type="datetime-local" id="end_time" class="rounded-sm border-0 p-1.5 px-3 text-gray-900 ring-1 ring-inset ring-gray-300 placeholder:text-gray-400 focus:ring-2 focus:ring-inset focus:ring-indigo-600 sm:text-sm sm:leading-6 ml-2" name="end_time" min="2018-01-01" max="2018-12-31" />
<button type="submit" class="bg-gray-300 inline-block my-2 p-1 px-3 rounded-md ml-2">Search</button>
<button type="submit" class="bg-gray-300 inline-block my-2 p-1 px-3 rounded-md ml-2 js-reset">Reset</button>
</form>

<canvas id="myChart" class="m-4">
</canvas>

  <script src="https://cdn.jsdelivr.net/npm/chart.js"></script>
  <script 
  <script>
    let myChart;

    document.querySelectorAll('.js-temp-shortcut').forEach((el) => {{
        el.addEventListener('click', (e) => {{
            document.querySelector('input[name="target_temp"]').value = e.target.innerHTML;
            document.querySelector('#temp_form').dispatchEvent(new Event('submit'));
        }});
    }});

    document.querySelectorAll('.js-reset').forEach((el) => {{
        el.addEventListener('click', (e) => {{
            document.querySelector('input[name="start_time"]').value = '';
            document.querySelector('input[name="end_time"]').value = '';
            document.querySelector('#temp_history').dispatchEvent(new Event('submit'));
        }});
    }});

    document.querySelector('#temp_history').addEventListener('submit', (e) => {{
        e.preventDefault();
        const start_time = document.querySelector('input[name="start_time"]').value;
        const end_time = document.querySelector('input[name="end_time"]').value;
        fetch(`/cgi-bin/get-temp-history.py?start_time=${{start_time}}&end_time=${{end_time}}`)
            .then(response => response.json())
            .then(data => {{
                myChart.data.labels = data.labels;
                myChart.data.datasets[0].data = data.data;
                myChart.data.datasets[1].data = data.dataHeater;
                myChart.update();
            }});
    }});


    document.querySelector('#temp_form').addEventListener('submit', (e) => {{
        e.preventDefault();
        const target_temp = document.querySelector('input[name="target_temp"]').value;
        const buffer_temp = document.querySelector('input[name="buffer_temp"]').value;
        fetch(`/cgi-bin/set-temp.py?target_temp=${{target_temp}}&buffer_temp=${{buffer_temp}}`)
            .then(response => response.json())
    }});

    setInterval(() => {{
        fetch('/cgi-bin/get-temp-history.py?latest=true')
            .then(response => response.json())
            .then(response => {{
                const current_temp = response.data[0];
                const last_reading_date = response.labels[0];
                const heater_status = response.dataHeater[0];
                
                document.querySelector('#heater_status').innerHTML = heater_status ? 'ON' : 'OFF';

                document.querySelector('#current-temp').innerHTML = current_temp;

                // move labels
                myChart.data.labels.shift()
                myChart.data.labels.push(last_reading_date)

                // move data
                myChart.data.datasets[0].data.shift()
                myChart.data.datasets[0].data.push(current_temp)
                myChart.data.datasets[1].data.shift()
                myChart.data.datasets[1].data.push(heater_status)

                myChart.update();
            }});
    }}, 5000);



    fetch('/cgi-bin/get-temp-history.py')
        .then(response => response.json())
        .then(response => {{
            const ctx = document.getElementById('myChart');

            myChart = new Chart(ctx, {{
                type: 'line',
                data: {{
                labels: response.labels,
                datasets: [
                    {{
                        label: 'Temperature',
                        data: response.data,
                        borderWidth: 1
                    }},
                    {{
                        label: 'Heater',
                        data: response.dataHeater,
                        borderWidth: 1
                    }}
                ]
                }},
                options: {{
                scales: {{
                    y: {{
                    padding: 10
                    }}
                }}
                }}
            }});
        }});

  </script>
</body>
</html>

"""
)