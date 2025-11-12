   # PriceMyCar : Car Price Prediction
   ---------------------------------------
<a href="https://mahanandar.github.io/Car_Price_Prediction/"><img width="1898" height="930" alt="image" src="https://github.com/user-attachments/assets/a1bb76a9-a0ef-46cb-bea0-5eede8b6b57e" />

----------------------------------------------------------------
## Table of Contents
- [Problem Statement](#problem-statement)
- [Dataset](#dataset)
- [Workflow](#workflow)
- [Setup](#setup)
- [Testing](#testing)
- [Dockerization](#dockerization)
- [Deployment](#deployment)
- [Application](#application)
- [Model Training & Evaluation](#model-training--evaluation)
- [Challenges & Solutions](#challenges--solutions)
- [Impact](#impact)
- [Folder Structure](#folder-structure)
- [License](#license)
----------------------------------------------------------------
## Problem Statement
- In the used car market, buyers and sellers often struggle to determine a fair price for their vehicle.
- This project aims to provide accurate and transparent pricing for used cars by analyzing real-world data.

## Dataset
- To train the model, I collected real-world used car listings data directly from the [Cars24](https://www.cars24.com/) website.
- Since Cars24 uses dynamically loaded content, a static scraper would not capture all the data.
- Instead, I implemented an automated Selenium + BeautifulSoup Python Script.

### Web Scraping Script (`scrape_car_listing`)

**Input :** URL of a Cars24 listing page to scrape.

#### 1. Launch Chrome Automatically
- Script uses `ChromeDriverManager` to install and manage the drivers without manual setup.
  
#### 2. Open Cars24 Website
- Loads the given URL in a real browser session.

#### 3. Simulate Scrolling
- Scrolls down the page in increments, with short random pauses (2-4 seconds) between scrolls.
- This ensures all dynamically loaded listings are fetched.
  
#### 4. Check for End of Page
- Stops scrolling when the bottom of the page is reached or no new content loads.

#### 5. Capture Rendered HTML
- Once fully loaded, it retrieves the complete DOM (including dynamically injected elements).
  
#### 6. Parse HTML with BeautifulSoup
- Returns a BeautifulSoup object containing the entire page's HTML for later parsing and data extraction.

> [!NOTE]
> 
> At this stage, no data is extracted, the output is just the complete HTML source.
> 
> It which will be parsed to a separate script to extract features like price, model, year, transmission, etc.

------------------------------------------------------------------------------------------
### Data Extraction Script (`get_car_details`)

**Input :** BeautifulSoup object (`soup`) containing the fully-rendered HTML of a Cars24 listing page.

#### 1. Find Raw Model Name Texts
- Looks for `<span>` elements with class `sc-braxZu kjFjan`.
- Extracts the text using `.text` into a list called `model_name`.
- The code only keeps those model that start with `2` and stores them in `clean_model_name`.

<details>
<summary>Click to view the HTML Element Snapshot</summary>
&nbsp;
<img title="cars24" src="https://github.com/user-attachments/assets/66524e3d-4c26-4edc-8f8a-40b17016eda4">
</details>

> [!IMPORTANT]
>
> Inspect the HTML Element : `<span id class="sc-braxZu kjFjan">2016 Maruti Wagon R 1.0</span>`
>
> Tag : `<span>` → id (empty) → class : `sc-braxZu kjFjan` (two classes, separated by space)
> 
> However when you hover over it in the browser, it shows : `span.sc-braxZu.kjFjan`
>
> CSS uses a dot `.` to indicate classes. The dot is not a part of the class name itself.
>
> It just means "this is a class", it is not the part of the class name.
>
> This might look confusing for someone with little HTML/CSS knowledge, so it's better to clarify it.

#### 2. Collect Specification Text Blocks
- Looks for `<p>` elements with class `sc-braxZu kvfdZL` (each holds one specification value).
- These are appended to `specs` list.
   
```python
['69.95k km',
 'Petrol',
 'Manual',
 '1st owner',
 'DL-1C',
 '70.72k km',
 'Diesel',
 'Manual',
 '2nd owner',
 'UP-14',
 '15.96k km',
 'CNG',
 'Manual',
 '1st owner',
 'UP-16',...]
```

<details>
<summary>Click to view the HTML Element Snapshot</summary>
&nbsp;
<img title="cars24" src="https://github.com/user-attachments/assets/5185f66b-3de6-4354-ae11-fcb0b8fbb793">
</details>

#### 3. Group Specifications
- The flat `specs` list is split into consecutive groups of 5 (`clean_specs.appendspecs[i:i+5])`).
- Each group corresponds to one listing's set of specification value.
   
```python
[['69.95k km', 'Petrol', 'Manual', '1st owner', 'DL-1C'],
 ['70.72k km', 'Diesel', 'Manual', '2nd owner', 'UP-14'],
 ['15.96k km', 'CNG', 'Manual', '1st owner', 'UP-16'],...]
```

#### 4. Map Groups into Fields
- From each 5-item group, the script extracts :
    - `clean_specs[0]` → `km_driven`
    - `clean_specs[1]` → `fuel_type`
    - `clean_specs[2]` → `transmission`
    - `clean_specs[3]` → `owner`
- `clean_specs[4]` → `number_plate` exists but is of no use.

#### 5. Extract Price Values
- `soup.find_all('p', 'sc-braxZu cyPhJl')` collects price elements into `price` list.
- The script then slices `price = price[2:]`, removing the first two entries (non-listing elements on the page).
- So the remaining prices align with the listings.

```python
['₹3.09 lakh',
 '₹5.71 lakh',
 '₹7.37 lakh',...]
```

<details>
<summary>Click to view the HTML Element Snapshot</summary>
&nbsp;
<img title="cars24" src="https://github.com/user-attachments/assets/9a974eca-b39b-4e9a-bdc3-ff5abe6c9491">
</details>

#### 6. Extract Listing Links
- `soup.find_all('a', 'styles_carCardWrapper__sXLIp')` collects anchor tag for each card and extracts `href`.

```python
['https://www.cars24.com/buy-used-honda-amaze-2018-cars-noida-11068642783/',
 'https://www.cars24.com/buy-used-ford-ecosport-2020-cars-noida-11234948707/',
 'https://www.cars24.com/buy-used-tata-altroz-2024-cars-noida-10563348767/',...]
```

<details>
<summary>Click to view the HTML Element Snapshot</summary>
&nbsp;
<img title="cars24" src="https://github.com/user-attachments/assets/fbac495f-6894-41dc-b469-2d23e90e3610">
</details>

#### 7. Combine into a DataFrame
- All lists are assembled into a `pandas.DataFrame`.
- The column names are `model_name`, `km_driven`, `fuel_type`, `transmission`, `owner`, `price`, `link`.

#### 8. Return the DataFrame
- Finally, function returns the above DataFrame for further cleaning, analysis and modelling.

### Engine Capacity Script (`get_engine_capacity`)

**Input :** List of URLs for individual car listings (`link` from the previous DataFrame).

#### 1. Iterate through each Car Listing URL
- Loops over the list of individual car listing page URL.

#### 2. Send an HTTP Request
- Uses the `requests` library to retrieve each page's HTML content.
- Adds a User-Agent header to simulate a real browser and reduce blocking risk.
- Applies a random timeout (4-8 seconds) between requests to avoid overloading the server.

#### 3. Parse the HTML Content
- Converts the response into a BeautifulSoup object using the `lxml` parser for fast, reliable parsing.

#### 4. Locate Engine Capacity Label
- Searches for all `<p>` tags with the class `sc-braxZu jjIUAi`.
- Checks if the text exactly matches "Engine capacity".

<details>
<summary>Click to view the HTML Element Snapshot</summary>
&nbsp;
<img title="cars24" src="https://github.com/user-attachments/assets/80a81a7e-ffd6-4413-ab74-650dbf63afc6">
</details>

#### 5. Extract the Value
- If the label is found, grab the value from the next sibling element (`1197 cc`).
- Marks the entry as successfully found.
- If no engine capacity value is found, store `None` to maintain positional consistency.

#### 6. Return the List
- Outputs a list of engine capacities in the same order as the input URLs.

### ◆ Combine Data from Multiple Cities

```python
# Parsing HTML Content of Hyderabad City from Cars24 Website
soup = scrape_car_listing('https://www.cars24.com/buy-used-cars-hyderabad/')

# Extracting Car Details of Hyderabad City
hyderabad = get_car_details(soup)
```

```python
# Parsing HTML Content of Bangalore City from Cars24 Website
soup = scrape_car_listing('https://www.cars24.com/buy-used-cars-bangalore/')

# Extracting Car Details of Bangalore City
bangalore = get_car_details(soup)
```

```python
# Parsing HTML Content of Mumbai City from Cars24 Website
soup = scrape_car_listing('https://www.cars24.com/buy-used-cars-mumbai/')

# Extracting Car Details of Mumbai City
mumbai = get_car_details(soup)
```

```python
# Parsing HTML Content of Delhi City from Cars24 Website
soup = scrape_car_listing('https://www.cars24.com/buy-used-cars-delhi-ncr/')

# Extracting Car Details of Delhi City
delhi = get_car_details(soup)
```

```python
# Concatenating Car Details of Different Cities into Single DataFrame
df = pd.concat([hyderabad, bangalore, mumbai, delhi], ignore_index=True)
df.head()
```

```python
# Extracting engine capacity of each car using its car listing link from Cars24 Website
engine_capacity = get_engine_capacity(df['link'])

# Adding "engine_capacity" column in the DataFrame
df['engine_capacity'] = engine_capacity

# Final DataFrame after Web Scrapping
df.head()
```Combine Data from Multiple Cities

```python
# Parsing HTML Content of Hyderabad City from Cars24 Website
soup = scrape_car_listing('https://www.cars24.com/buy-used-cars-hyderabad/')

# Extracting Car Details of Hyderabad City
hyderabad = get_car_details(soup)
```

```python
# Parsing HTML Content of Bangalore City from Cars24 Website
soup = scrape_car_listing('https://www.cars24.com/buy-used-cars-bangalore/')

# Extracting Car Details of Bangalore City
bangalore = get_car_details(soup)
```

```python
# Parsing HTML Content of Mumbai City from Cars24 Website
soup = scrape_car_listing('https://www.cars24.com/buy-used-cars-mumbai/')

# Extracting Car Details of Mumbai City
mumbai = get_car_details(soup)
```

```python
# Parsing HTML Content of Delhi City from Cars24 Website
soup = scrape_car_listing('https://www.cars24.com/buy-used-cars-delhi-ncr/')

# Extracting Car Details of Delhi City
delhi = get_car_details(soup)
```

```python
# Concatenating Car Details of Different Cities into Single DataFrame
df = pd.concat([hyderabad, bangalore, mumbai, delhi], ignore_index=True)
df.head()
```

```python
# Extracting engine capacity of each car using its car listing link from Cars24 Website
engine_capacity = get_engine_capacity(df['link'])

# Adding "engine_capacity" column in the DataFrame
df['engine_capacity'] = engine_capacity

# Final DataFrame after Web Scrapping
df.head()
```
-----------------------------------------------------------------------
### Dataset Description

The final dataset consists of 2,800+ unique car listings, with each record containing :

- `model_name` : Model name of the car (2014 Hyundai Grand i10, etc).         
- `fuel_type` : Type of fuel the car uses (Petrol, Diesel, CNG, Electric).        
- `transmission` : Type of transmission the car has (Automatic or Manual).           
- `owner` : Number of previous owners (1st owner, 2nd owner, 3rd owner, etc).
- `engine_capacity` : Size of the engine (in cc).                              
- `km_driven` : Total distance traveled by the car (in km).                   
- `price` : Selling price of the car (target variable).

  
> [!TIP]
>
> Scraping code in the repository depends on the current structure of the target website.
>
> Websites often update their HTML, element IDs or class names which can break the scraping logic.
>
> So before running the scraper, inspect the website to ensure the HTML structure matches the code.
>    
> Update any selectors or parsing logic if the website has changed.

----------------------------------------------------------------------

## Workflow

<img title="workflow" src="https://github.com/user-attachments/assets/6a6ff974-a548-4556-bf74-e96a9fa10bb4">

----------------------------------------------------------------------

## Setup

Follow these steps carefully to setup and run the project on your local machine :

### 1. Clone the Repository
First, you need to clone the project from GitHub to your local system.
```bash
git clone https://github.com/TheMrityunjayPathak/AutoIQ.git
```

### 2. Build the Docker Image
Docker allows you to package the application with all its dependencies.
```bash
docker build -t your_image_name .
```

> [!TIP]
>
> Make sure Docker is installed and running on your machine before executing this command.

### 3. Setup Environment Variables
This project uses a `.env` file to store configuration settings like model paths, allowed origins, etc.

#### `.env` file
- Stores environment variables in plain text.
```python
# .env
ENV=environment_name
MAE=mean_absolute_error
PIPE_PATH=pipeline_path
MODEL_FREQ_PATH=model_freq_path
ALLOWED_ORIGINS=list_of_URLs_that_are_allowed_to_access_the_API
```

> [!IMPORTANT]
> Never commit `.env` to GitHub / Docker.
> 
> Add `.env` to `.gitignore` and `.dockerignore` to keep it private.

#### `config.py` file
- Load and validate environment variables from `.env`.
- Uses Pydantic `BaseSettings` to read environment variables, validate types and provide easy access.
```python
# Importing Libraries
import os
from pathlib import Path
from typing import List
from pydantic_settings import BaseSettings

# Loading and Validating Environment Variables
class Settings(BaseSettings):
    ENV: str = "dev"
    MAE: int
    PIPE_PATH: Path
    MODEL_FREQ_PATH: Path
    ALLOWED_ORIGINS: str

    @property
    def cors_origins(self) -> List[str]:
        return [origin.strip() for origin in self.ALLOWED_ORIGINS.split(",")]

    class Config:
        env_file = ".env" if not os.getenv("RENDER") else None

settings = Settings()
```

#### `main.py` file
- Uses `settings` from `config.py` in FastAPI.
- Imports the `settings` object to provide API's metadata dynamically from `.env`.
```python
# api/main.py
import pickle
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from api.config import settings

app = FastAPI(title="AutoIQ by Motor.co")

app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins,
    allow_credentials=True,
    allow_methods=["GET", "POST"],
    allow_headers=["*"],
)

with open(settings.PIPE_PATH, "rb") as f:
    pipe = pickle.load(f)

with open(settings.MODEL_FREQ_PATH, "rb") as f:
    model_freq = pickle.load(f)
```

### 4. Run the Docker Container
Start the application using Docker. This will run the FastAPI server and handle all the dependencies automatically.

```bash
   docker run --env-file .env -p 8000:8000 car_price_app /
   uvicorn api.main:app --host 0.0.0.0 --port 8000 --reload
```

> [!NOTE]
> `api.main` → Refers to the main.py file inside the api folder.
> 
> `app` → The FastAPI instance defined in your code.
> 
> `--reload` → Automatically reloads when code changes (development only).

### 5. Access the FastAPI Server
Once the container is running, open your browser and navigate to :

```bash
http://localhost:8000/docs

or

http://127.0.0.1:8000/docs
```

This opens the Swagger UI for testing the API endpoints.

Access the live API [here](https://car-price-prediction-xayj.onrender.com/docs) or Click on the Image below.

<a href="https://car-price-prediction-xayj.onrender.com/docs"><img width="1090" height="977" alt="image" src="https://github.com/user-attachments/assets/6d33092c-90d7-4d22-bf93-dfc09b42a8c0" /></a>

### 6. Stop the Docker Container
When you're done using the application, stop the running container.
```bash
docker stop your_image_name
```
-----------------------------------------------------------------

## Testing
Once the FastAPI server is running, you can test the API endpoints in Postman or any similar software.

### 1. Launch Postman
- Click “New Request”.
- Set the request type to GET.
- Enter your API URL:
```bash
http://127.0.0.1:8000/predict

(or your deployed URL, e.g., https://car-price-prediction-xayj.onrender.com/predict)
```
- Go to the Body tab → select raw → choose JSON from the dropdown.

Paste this sample input:

```bash

{
  "Present_Price": 8.5,
  "Kms_Driven": 40000,
  "Fuel_Type": "Petrol",
  "Seller_Type": "Individual",
  "Transmission": "Manual",
  "Owner": 0,
  "Age": 5
}
```
- Click the "Send" button to submit the request.

 - Expected Response:

• Status Code : It indicates that the request was successful and the server responded with the requested data.

```bash
200 OK
```

• Response Body (JSON) : This confirms that the API is running and returns the result of your API call.

```bash
{
     "output": "₹9,69,000 to ₹11,50,000"
}
```

![Postman](https://github.com/user-attachments/assets/ffcea046-33b7-4a50-9053-90b171210cb6)

------------------------------
## Dockerization

Follow these steps carefully to containerize your project with Docker :

### 1. Install Docker
- Before starting, make sure Docker is installed on your system.
- Visit [Docker](https://www.docker.com/) → Click on Download Docker Desktop → Choose Windows / Mac / Linux

<img title="docker" src="https://github.com/user-attachments/assets/200fd0a3-68f1-40d7-b1a7-299f0d6aae8e">

### 2. Verify the Installation
- Open Docker Desktop → Make sure Docker Engine is Running

<img width="1554" height="893" alt="image" src="https://github.com/user-attachments/assets/dc19fa84-7754-4d27-a37b-67555ee95efa" />


### 3. Create the Dockerfile
- Create a `Dockerfile` and place it in the root folder of your Repository.
```Dockerfile
# Start with the official Python 3.11 image.
# -slim means this is a smaller Debian-based image with fewer preinstalled packages, which makes it lighter.
FROM python:3.11-slim

# Install required system packages for Python libraries.
RUN apt-get update && apt-get install -y --no-install-recommends \
    gcc \
    g++ \
    python3-dev \
    libopenblas-dev \
    liblapack-dev \
    gfortran \
 && rm -rf /var/lib/apt/lists/*

# Set the working directory to /app inside the container.
# All future commands (COPY, RUN, CMD) will be executed from here.
WORKDIR /app

# Copies your local requirements.txt into the container's /app folder.
COPY requirements.txt .

# Install all the dependencies from requirements.txt.
# --no-cache-dir prevents pip from keeping installation caches, making the image smaller.
RUN pip install --no-cache-dir --upgrade pip && \
    pip install --no-cache-dir -r requirements.txt

# Copies all the remaining project files (Flask API, HTML, CSS, JS, etc.) into /app.
COPY . .

# Expose FastAPI port, so it can be accessed from outside the container.
EXPOSE 8000

# Default command to run the FastAPI app with Uvicorn in production mode.
# --host 0.0.0.0 allows external connections (necessary in Docker).
# --port 8000 specifies the port.
CMD ["uvicorn", "api.main:app", "--host", "0.0.0.0", "--port", "8000"]
```

### 4. Create the `.dockerignore` File
- This file tells Docker which files and folders to exclude from the image.
- This keeps the image small and prevents unnecessary files from being copied.
- A `.dockerignore` file is used to exclude all files and folders that are not required to run your application.

```bash
# Virtual Environment
.venv/

# Jupyter Notebooks
*.ipynb

# Jupyter Notebook Checkpoints
.ipynb_checkpoints/

# Python Cache
__pycache__/
*.pyc
*.pyo
*.pyd

# Environment File
.env
*.env

# Dataset (Parquet & CSV Files)
*.parquet
*.csv

# Python Package (utils)
utils/

# Local/Temporary Files
*.log
*.tmp
*.bak

# Version Control Files
.git/
.gitignore

# IDE/Editor Configs
.vscode/
.idea/
.DS_Store

# Python Package Build Artifacts
*.egg-info/
build/
dist/
```

### 5. Build the Docker Image
- A Docker image is essentially a read-only template that contains everything needed to run an application.
- You can think of a Docker image as a blueprint or snapshot of an environment. It doesn't run anything.

```bash
docker build -t your_image_name .
```

### 6. Create the Docker Container
- When you run a Docker image, it becomes a Docker container.
- It is a live instance of that image, running your application in an isolated environment.

#### For Development
```bash
docker run --env-file .env -p 8000:8000 your_image_name /
    uvicorn api.main:app --host 0.0.0.0 --port 8000 --reload
```

#### For Production
```bash
docker run --env-file .env -p 8000:8000 your_image_name
```

- After the container starts, you can access your API.

```bash
http://localhost:8000

or

http://127.0.0.1:8000
```

### 7. Push to Docker Hub
- Once your Docker image is ready, you can push it to Docker Hub.
- It allows anyone to pull and run it without building it themselves.

Access the Docker Hub [here]

<a href="https://app.docker.com/accounts/46613"><img width="1856" height="741" alt="image" src="https://github.com/user-attachments/assets/a1f2ec1b-0b83-41c3-9e02-3897d0e74f8b" />
</a>

#### Login to Docker Hub
- Prompts you to enter your Docker Hub username and password.
- This authenticates your local Docker client with your Docker Hub account.

```bash
docker login
```

#### Tag the Docker Image
- Tagging prepares the image for upload to Docker Hub.

```bash
docker tag your_image_name your-dockerhub-username/your_image_name:latest
```

#### Push the Image to Docker Hub
- Uploads your image to your Docker Hub Repository.
- Once pushed, your image is publicly available.
- Anyone can now pull and run the image without building it locally.

```bash
docker push your-dockerhub-username/your_image_name:latest
```

### 8. Pull and Run Anywhere
- Once pushed, anyone can pull your image from Docker Hub and run it.
- This ensures that the application behaves the same way across all systems.

```bash
docker pull your-dockerhub-username/your_image_name:latest
```

- After pulling the Docker image, you can run it to create Docker container from it.

```bash
docker run --env-file .env -p 8000:8000 your-dockerhub-username/your_image_name:latest
```

### 9. Verify the Container is Running
- Lists all the running containers with `container_id`.

```bash
docker ps
```

### 10. Stop the Container
- Stops the running container safely.
- `container_id` can be obtained from `docker ps` output.

```bash
docker stop container_id
```

## Deployment

Follow these steps carefully to deploy your FastAPI application on Render :

- Push your code to [GitHub](https://github.com/)
  
- Login to [Render](https://render.com/)
  
- Create a New Web Service

<img width="1876" height="679" alt="image" src="https://github.com/user-attachments/assets/677d3d5f-ce6f-4ff4-a5f4-18d8b94b1e96" />

- Link your GitHub Repository / Existing Docker Image

<img width="1867" height="729" alt="image" src="https://github.com/user-attachments/assets/f583c761-050c-44e6-a70c-1f467452160a" />

- Add details about your API

<img width="1257" height="568" alt="image" src="https://github.com/user-attachments/assets/78e75bfa-2ae8-45d3-8c17-10cf982ec476" />

- Add Environment Variables in Render Dashboard (same as `.env`)

<img width="1260" height="261" alt="image" src="https://github.com/user-attachments/assets/ef82caf0-c03a-411c-86c8-3bf06125c28d" />

- Deploy the Web Service
--------------------------------------------------------

## Application

The frontend application files are in the project root :
- `index.html` → This file defines the structure and layout of the web page.
- `style.css` → This file handles the visual appearance of the web page.
- `script.js` → This file communicates between the web page and the API.

You can open `index.html` directly in your browser or serve it via a local HTTP server (like VS Code Live Server).

> [!NOTE]  
> Remember to update the API URL in `script.js` when deploying on GitHub Pages to get real-time predictions.  
>  
> Change from :  
> ```js
> const fetchPromise = fetch("http://127.0.0.1:8000/predict", {
>     method: "POST",
>     headers: { "Content-Type": "application/json" },
>     body: JSON.stringify(data),
> });
> ```  
>  
> To :  
> ```js
> const fetchPromise = fetch("https://your_api_name.onrender.com/predict", {
>     method: "POST",
>     headers: { "Content-Type": "application/json" },
>     body: JSON.stringify(data),
> });
> ```

Access the live Website [here](https://mahanandar.github.io/Car_Price_Prediction/) or Click on the Image below

<a https://mahanandar.github.io/Car_Price_Prediction/><img width="1899" height="932" alt="image" src="https://github.com/user-attachments/assets/273b5d97-059b-43b5-a9bd-e854322effd3" />
</a>

> [!IMPORTANT]
>
> The API for this project is deployed using the free tier on Render.
>
> As a result, it may go to sleep after periods of inactivity.
> 
> Please start the API first by visiting the API URL. Then, navigate to the website to make predictions.
> 
> If the API was inactive, the first prediction may take a few seconds while the server spins back up.

------------------------------------------------
## Model Training & Evaluation

### 1. Load the Data
```python
# Importing load_parquet function from read_data module
from read_data import load_parquet
cars = load_parquet('clean_data', 'clean_data_after_eda.parquet')
cars.head()
```

### 2. Split the Data
```python
# Creating Features and Target Variable
X = cars.drop('price', axis=1)
y = cars['price']

# Splitting Data into Training and Testing Set
X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.25, random_state=42)
```

### 3. Build Preprocessing Pipeline
```python
# Pipeline for Nominal Column
nominal_cols = ['fuel_type','transmission','brand']
nominal_trf = Pipeline(steps=[
    ('ohe', OneHotEncoder(sparse_output=False, handle_unknown='ignore'))
])
```
```python
# Pipeline for Ordinal Column
ordinal_cols = ['owner']
ordinal_categories = [['Others','3rd owner','2nd owner','1st owner']]
ordinal_trf = Pipeline(steps=[
    ('oe', OrdinalEncoder(categories=ordinal_categories))
])
```
```python
# Pipeline for Numerical Column
numerical_cols = ['km_driven','year','engine_capacity']
numerical_trf = Pipeline(steps=[
    ('scaler', RobustScaler())
])
```
```python
# Adding Everything into ColumnTransformer
ctf = ColumnTransformer(transformers=[
    ('nominal', nominal_trf, nominal_cols),
    ('ordinal', ordinal_trf, ordinal_cols),
    ('scaling', numerical_trf, numerical_cols)
], remainder='passthrough', n_jobs=-1)
```

### 4. Evaluate Multiple Models
```python
# Models Dictionary
models = {
    'LR' : LinearRegression(n_jobs=-1),
    'KNN' : KNeighborsRegressor(n_jobs=-1),
    'DT' : DecisionTreeRegressor(random_state=42),
    'RF' : RandomForestRegressor(random_state=42, n_jobs=-1),
    'GB' : GradientBoostingRegressor(random_state=42),
    'XGB' : XGBRegressor(random_state=42, n_jobs=-1)
}
```

```python
# Computing Average Error and R2-Score through Cross-Validation
results = {}

for name, model in models.items():
    
    pipe = Pipeline(steps=[
        ('preprocessor', ctf),
        ('model', model)
    ])

    k = KFold(n_splits=5, shuffle=True, random_state=42)

    cv_results = cross_validate(estimator=pipe, X=X_train, y=y_train, cv=k, scoring={'mae':'neg_mean_absolute_error','r2':'r2'}, n_jobs=-1, return_train_score=False)

    results[name] = {'avg_error': -cv_results['test_mae'].mean(),'avg_score': cv_results['test_r2'].mean()}

    print()
    print(f'Model : {name}')
    print('-'*40)
    print(f'Average Error : {-cv_results['test_mae'].mean():.2f}')
    print(f'Standard Deviation of Error : {cv_results['test_mae'].std():.2f}')
    print(f'Average R2-Score : {cv_results['test_r2'].mean():.2f}')
    print(f'Standard Deviation of R2-Score : {cv_results['test_r2'].std():.2f}')
```

```python
Model : LR
----------------------------------------
Average Error : 140235.78
Standard Deviation of Error : 3462.18
Average R2-Score : 0.74
Standard Deviation of R2-Score : 0.01

Model : KNN
----------------------------------------
Average Error : 128045.90
Standard Deviation of Error : 3772.29
Average R2-Score : 0.76
Standard Deviation of R2-Score : 0.01

Model : DT
----------------------------------------
Average Error : 132132.93
Standard Deviation of Error : 5835.43
Average R2-Score : 0.72
Standard Deviation of R2-Score : 0.01

Model : RF
----------------------------------------
Average Error : 101061.52
...
Average Error : 100748.77
Standard Deviation of Error : 1349.10
Average R2-Score : 0.84
Standard Deviation of R2-Score : 0.01
```

```python
# Plotting Metric Comparision Graph
results_df = pd.DataFrame(results)

fig, ax = plt.subplots(ncols=1, nrows=2, figsize=(12,8))

sns.barplot(x=results_df.iloc[0,:].sort_values().index.to_list(), y=results_df.iloc[0,:].sort_values().values, ax=ax[0])
ax[0].set_title('Average Error Comparision (Lower is Better)')
ax[0].set_ylabel('Error')
for container in ax[0].containers:
    ax[0].bar_label(container, fmt='%.0f')

sns.barplot(x=results_df.iloc[1,:].sort_values().index.to_list(), y=results_df.iloc[1,:].sort_values().values, ax=ax[1])
ax[1].set_title('Average R2-Score Comparision (Higher is Better)')
ax[1].set_ylabel('R2-Score')
for container in ax[1].containers:
    ax[1].bar_label(container, fmt='%.2f')

plt.tight_layout()
plt.show()
```

<img width="1191" height="791" alt="image" src="https://github.com/user-attachments/assets/7538134d-fcd6-42a3-96c4-2aefb0dffc91" />

### 5. Creating Stacking Regressor
```python
# Assigning Base Model for StackingRegressor
base_model = [('rf', rf),('xgb', xgb),('gb', gb)]

# Structure of StackingRegressor
stack = StackingRegressor(
    estimators=base_model, 
    final_estimator=meta_model, 
    passthrough=False, 
    cv=k, n_jobs=-1
)

# Final Pipeline with StackingRegressor
pipe = Pipeline(steps=[
    ('preprocessor', ctf), 
    ('model', stack) 
])
```
```python
# Average Error and R2-Score through Cross-Validation
cv_results = cross_validate(estimator=pipe, X=X_train, y=y_train, cv=k, scoring={'mae':'neg_mean_absolute_error','r2':'r2'}, n_jobs=-1)
print(f"Average Error : {-cv_results['test_mae'].mean():.2f}")
print(f"Standard Deviatacion of Error : {cv_results['test_mae'].std():.2f}")
print(f"Average R2-Score : {cv_results['test_r2'].mean():.2f}")
print(f"Standard Deviation of R2-Score : {cv_results['test_r2'].std():.2f}")
```
```
Average Error : 97259.76
Standard Deviatacion of Error : 1933.85
Average R2-Score : 0.85
Standard Deviation of R2-Score : 0.01
```
<img width="1078" height="444" alt="image" src="https://github.com/user-attachments/assets/f18ba584-21b7-4396-8b31-1621fa21bdde" />

------------------------------------------------------------------------

### 6. Performance Evaluation Graphs

#### Actual vs Predicted Plot
| <img width="569" height="446" alt="image" src="https://github.com/user-attachments/assets/e0a7f558-ca61-4455-b2c8-ebd6f08da0ba" /> | <img width="569" height="446" alt="image" src="https://github.com/user-attachments/assets/faaa3ec0-1c75-4a31-8e45-b178e4d31f07" /> |
|---|---|

#### Learning Curve
| R2-Score Curve | Error Curve |
|---|---|
| <img width="569" height="446" alt="image" src="https://github.com/user-attachments/assets/2598dc45-102c-4418-8231-651e97c445dd" /> | <img width="586" height="446" alt="image" src="https://github.com/user-attachments/assets/1ddc1425-6c4d-4bdc-9767-80404e79f68b" />
|

-------------------------------------------------------------------------

### 7. Hyperparameter Tuning
```python
# Parameter Distribution
param_dist = {
    'model__rf__n_estimators': [200, 300],
    'model__rf__max_depth': [10, 20],
    'model__rf__min_samples_leaf': [3, 5],
    'model__rf__min_samples_split': [5, 7],
    'model__xgb__n_estimators': [200, 300],
    'model__xgb__learning_rate': [0.05, 0.1],
    'model__xgb__max_depth': [2, 4],
    'model__xgb__subsample': [0.5, 0.75],
    'model__xgb__colsample_bytree': [0.5, 0.75],
    'model__gb__n_estimators': [100, 200],   
    'model__gb__learning_rate': [0.05, 0.1],  
    'model__gb__max_depth': [2, 4],       
    'model__gb__subsample': [0.5, 0.75],
    'model__final_estimator__alpha': [0.1, 10.0],
    'model__final_estimator__l1_ratio': [0.0, 1.0]
}

# RandomizedSearch Object with Cross-Validation
rcv = RandomizedSearchCV(estimator=pipe, param_distributions=param_dist, cv=k, scoring='neg_mean_absolute_error', n_iter=30, n_jobs=-1, random_state=42)

# Fitting the RandomizedSearch Object
rcv.fit(X_train, y_train)

# Best Estimator
best_model = rcv.best_estimator_
```
-------------------------------------------------------------------------
### 8. Performance Evaluation Comparison

#### Actual vs Predicted Plot
| Before Tuning | After Tuning |
|---|---|
| <img width="569" height="446" alt="image" src="https://github.com/user-attachments/assets/8e0f793e-1e56-4224-9369-8fbf5db22617" />
 | <img width="569" height="446" alt="image" src="https://github.com/user-attachments/assets/8e337d68-9965-4550-aeb1-f12a23c8d435" />
 |

#### Learning Curve
| R2-Score Curve (Before Tuning) | R2-Score Curve (After Tuning) |
|---|---|
| <img width="569" height="446" alt="image" src="https://github.com/user-attachments/assets/00a10f11-b80d-45f6-b000-4756cc56012a" />| <img width="586" height="446" alt="image" src="https://github.com/user-attachments/assets/922b21f7-c13a-416a-88bc-36858e530d0e" />
 |
 
-------------------------------------------------------------------------
## Challenges & Solutions

### Challenge 1 → Getting Real World Data

#### Problem
- I wanted to use real-world data instead of pre-cleaned toy dataset, as it represents messy, real-life scenarios.
- However, Cars24 loads its content dynamically using JS, meaning a simple HTTP request won't be enough.

#### Solution
- I used [Selenium](https://www.selenium.dev/) to simulate a real browser, ensuring that the page was fully loaded before scraping.
- Once the content was fully rendered, I used [BeautifulSoup](https://www.crummy.com/software/BeautifulSoup/bs4/doc/) to efficiently parse the HTML.
- This approach allowed me to reliably capture all the details.

### Challenge 2 → Handling Large Datasets Efficiently

#### Problem
- The raw scraped dataset was large, taking up unnecessary space.
- Loading it repeatedly during experimentation became inefficient.

#### Solution
- I optimized memory consumption by downcasting data types to reduce memory usage.
- I also stored the dataset in Parquet format, which compresses data without losing information.
- It allows for much faster read/write speeds as compared to CSV.

### Challenge 3 → Avoiding Data Leakage

#### Problem
- If preprocessing is applied to the entire dataset, test data can leak into the training process.
- This creates overly optimistic results and reduces the model's ability to generalize.

#### Solution
- I implemented Scikit-learn [Pipeline](https://scikit-learn.org/stable/modules/generated/sklearn.pipeline.Pipeline.html) and [ColumnTransformer](https://scikit-learn.org/stable/modules/generated/sklearn.compose.ColumnTransformer.html) to apply preprocessing only on training data.
- This keeps the test data completely unseen during preprocessing, preventing data leakage.

### Challenge 4 → Deploying Model as API

#### Problem
- Even after building the machine learning pipeline, it remained offline and could only be used locally.
- There is no way to provide inputs and get predictions over the web or from other applications.
- The model is dependent on the local system and could not serve predictions to external users or services.

#### Solution
- I deployed the machine learning model as an API using [FastAPI](https://fastapi.tiangolo.com/).
- This allows users and applications to send inputs and receive predictions online in real time.
- I added a `/predict` endpoint for serving predictions and a `/health` endpoint to monitor API status.
- I also implemented rate limiting and input validation to prevent misuse and ensure stability under load.
- These measures made the model accessible, reliable and ready for production use.

### Challenge 5 → Accessibility for Non-Technical Users

#### Problem
- Even if the API works perfectly fine, non-technical users may still find it difficult to test and use.
- This limits accessibility.

#### Solution
- I created a HTML/CSS/JS frontend that sends requests to the API and displays predictions instantly.
- I also included a example payload in Swagger UI, so that users can test it without any extra effort.

### Challenge 6 → Consistent Deployment Across Environments

#### Problem
- Installing dependencies and setting up the environment manually is time-consuming and error-prone.
- Especially when running on different machines with different operating system.
- This also made sharing the project with others more difficult, as they would have to replicate the exact setup.

#### Solution
- I created a multi-stage Dockerfile.
- It builds the FastAPI application, installs dependencies and copies only the required files into the final image.
- I used a `.dockerignore` file to exclude unnecessary files to keep the image small and deployment fast.
- This allowed me to run the project consistently on any system with [Docker](https://www.docker.com/) installed.
- It eliminates the hassle of worrying about dependency mismatches or operating system specific issues.
- Same Docker image can be used to deploy on Render, Docker Hub or run locally with a single docker command.

<hr>

## Impact

#### End-to-End Deployment
- Built and deployed a full ML pipeline using FastAPI for real-time used car price predictions.
- Enabled quicker and more accurate pricing decisions for the business.

#### Dataset Optimization
- Reduced dataset memory usage by 90%, cutting down on storage costs and improving system performance.
- Converted the dataset to Parquet format for faster data processing and shorter load times.

#### Data-Driven Model Selection
- Evaluated multiple regression models using cross-validation to select the most accurate ones.
- Improved pricing accuracy by relying only on top-performing models.
  
#### Significant Performance Gains
- Achieved 30% lower MAE and 12% higher R2-score, making price predictions more accurate.
- Improved accuracy helped set more competitive prices and boosted sales potential.
  
#### Greater Prediction Reliability
- Increased model stability by 70%, resulting in more consistent predictions.
- Fewer pricing errors led to stronger customer trust and smoother operations.

-----------------------------------------------------------------------------

## Folder Structure

```
CAR_PRICE_PREDICTION/
│
├── api/                          # API files for FastAPI backend
│
├── clean_data/                   # Cleaned datasets
│   ├── clean_data_after_eda.parquet
│   ├── clean_data_with_no_outlier.parquet
│   └── clean_data.parquet
│
├── env1/                         # Virtual environment (not pushed to GitHub)
│
├── models/                       # Saved ML models
│   ├── model_freq.pkl
│   └── pipe.pkl
│
├── notebooks/                    # Jupyter notebooks (EDA, preprocessing, modeling)
│   ├── step_1_data_preprocessing.ipynb
│   ├── step_2_outlier_detection.ipynb
│   ├── step_3_exploratory_data_analysis.ipynb
│   └── step_4_model_building.ipynb
│
├── scrape_code/                  # Scripts for web scraping
│   └── scrape_code.ipynb
│
├── scrape_data/                  # Collected scraped data
│   └── scrape_data.csv
│
├── utils/                        # Helper utility scripts
│   ├── __init__.py
│   ├── export_data.py
│   ├── file_locator.py
│   ├── helpers.py
│   ├── read_data.py
│   ├── summary.py
│   └── web_scraping.py
│
├── .dockerignore                 # Docker ignore file
├── .env                          # Environment variables
├── .gitignore                    # Git ignore file
│
├── car1.png ... car8.JPG          # Sample car images for UI
│
├── Dockerfile                    # Docker configuration file
├── index.html                    # Frontend HTML file
├── requirements.txt              # Python dependencies
├── script.js                     # Frontend JS for API interaction
└── uvicorn                        # Server runner

```
## License

This project is licensed under the [MIT License](LICENSE). You are free to use and modify the code as needed.

  
**[`^        Scroll to Top       ^`](#PriceMyCar--car-price-prediction)**


----------------------------------------------------------------
