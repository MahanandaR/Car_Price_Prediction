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

Access the live API [here](https://autoiq.onrender.com/docs) or Click on the Image below.

<a href="https://autoiq.onrender.com/docs"><img title="swagger-ui" src="https://github.com/user-attachments/assets/fe5432df-6a68-4e2d-ad83-279ce895251b"></a>
