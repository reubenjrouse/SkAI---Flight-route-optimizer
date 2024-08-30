
# SkAI

The Flight Route Optimization Program was developed for the Datathon 2.0 hackathon hosted by Analytika. This project aims to optimize flight routes for Air India by predicting weather and traffic conditions at various airports. Using a Multi-Layer Perceptron (MLP) classifier, the program forecasts these conditions and then reroutes flight paths according to safety levels and efficiency. The program employs Dijkstra's algorithm to determine the most efficient routes, enhancing flight safety and operational efficiency. This solution advanced us to the final round of the competition, outperforming over 300 teams.


## Problem Statement



![App Screenshot](https://via.placeholder.com/468x300?text=App+Screenshot+Here)


## Installation

### 1. Clone the Repository

```bash
  git clone https://github.com/reubenjrouse/SkAI---Flight-route-optimizer.git
  cd SkAI---Flight-route-optimizer
```

### 2. Create a virtual environment to manage project dependencies:

```bash
  python -m venv venv
```

### 3. Activate the Virtual Environment

1 . On Windows:

```bash
  venv\Scripts\activate
```

2 . On macOS/Linux:
```bash
  source venv/bin/activate
```

### 4. Install Dependencies

```bash
  pip install -r requirements.txt
```

    
## Demo

### Choose Flight ID

In this step, you select the Flight ID from the available options.



![App Screenshot](https://via.placeholder.com/468x300?text=App+Screenshot+Here)

### Weather Conditions and Rerouting

Here, you can view the weather conditions for all cities. If, for example, Delhi has adverse weather conditions by the time the flight is scheduled to arrive, the system will suggest rerouting through Mumbai instead. Note that the map is not to scale.




![App Screenshot](https://via.placeholder.com/468x300?text=App+Screenshot+Here)

### Visualize the Map

Finally, visualize the optimized flight path on the map, reflecting the new route taken to avoid bad weather.



![App Screenshot](https://via.placeholder.com/468x300?text=App+Screenshot+Here)
## Acknowledgements

 - Anlytika for hosting Datathon 2.0 hackathon
 - Air India for the problem statement and support.

