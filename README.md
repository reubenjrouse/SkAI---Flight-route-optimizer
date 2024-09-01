
# SkAI

The Flight Route Optimization Program was developed for the Datathon 2.0 hackathon hosted by Analytika. This project aims to optimize flight routes for Air India by predicting weather and traffic conditions at various airports. Using a Multi-Layer Perceptron (MLP) classifier, the program forecasts these conditions and then reroutes flight paths according to safety levels and efficiency. The program employs Dijkstra's algorithm to determine the most efficient routes, enhancing flight safety and operational efficiency. This solution advanced us to the final round of the competition, outperforming over 300 teams.


## Problem Statement


![Screenshot 2024-08-31 004348](https://github.com/user-attachments/assets/e74a94e6-f64b-43da-ab04-dc607fc62fca)


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

![11](https://github.com/user-attachments/assets/82ce397b-d08b-4eef-abfd-bb67d388bcda)

### Weather Conditions and Rerouting

Here, you can view the weather conditions for all cities. If, for example, Delhi has adverse weather conditions by the time the flight is scheduled to arrive, the system will suggest rerouting through Mumbai instead. Note that the map is not to scale.

![12](https://github.com/user-attachments/assets/6b6cf99a-e589-46c1-b903-b8f5579873f7)

### Visualize the Map

Finally, visualize the optimized flight path on the map, reflecting the new route taken to avoid bad weather.

![13](https://github.com/user-attachments/assets/4effa3be-d418-4406-b32b-8bc0943cee09)

## Authors

- [@AryaanPe](https://github.com/AryaanPe)
- [@Arman-02](https://github.com/Arman-02)
- [@reubenjrouse](https://github.com/reubenjrouse)



## Acknowledgements

 - Anlytika for hosting Datathon 2.0 hackathon
 - Air India for the problem statement and support.

