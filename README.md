# Stock Market with ChatGpt

In today's market, there is an abundance of stock information websites and applications, making access to stock market data faster and more convenient than ever before. Navigating popular platforms such as Yahoo Finance has become a straightforward task for virtually anyone. Nevertheless, for newcomers, the initial entry into these websites can be quite overwhelming, as they grapple with the question of where to commence their exploration.

For example, even experienced users may find it a time-consuming challenge to configure their settings for the comparative analysis of stock information across various companies. Fortunately, with the advancements in natural language processing models like ChatGPT, we are witnessing remarkable improvements in user experiences applied across diverse domains.

By envisioning the integration of ChatGPT into a stock information application, we have the potential to enhance its user-friendliness significantly. Such an implementation would empower a broader audience to effortlessly and expeditiously access the wealth of stock information available.

This comprehensive project encompasses a range of functionalities, including web scraping, data storage, task scheduling, orchestration, web server hosting, and the development of web applications, all powered by AWS cloud services. Moreover, a chat-based interface has been skillfully incorporated to allow users to interact with the stock information database through ChatGPT.


## Overview

- **Web Crawler**: An automated web crawler using AWS Lambda gathers stock market data from Yahoo Finance and stores it in an AWS S3 bucket.

- **ChatGPT API**: The system integrates with the OpenAI ChatGPT API, allowing users to send queries and receive AI-generated responses.

- **Backend Server**: A backend server application acts as an intermediary between the client and the ChatGPT API. It receives user queries, fetches relevant data from the crawler's database, sends the query to the ChatGPT API, and returns the AI-generated response to the client.

- **Client Interface**: A user-friendly web or mobile interface allows users to enter queries and engage in chat-based conversations. The interface communicates with the backend server to send queries and display responses.

- **Query Processing**: The backend server processes user queries to understand intent and extract relevant information. It retrieves stock market data from the crawler's database based on user queries.

## Components

### 1. Web Crawler
For web crawling, we employed multiple Lambda functions to gather stock information. Specifically, we collected stock summary and company profiles for the top 100 companies in terms of market capitalization within each of the 11 sectors through Yahoo Finance. To expedite the process, we utilized a total of 33 Lambda functions, distributing them across the sectors, with three Lambda functions dedicated to each sector.

To maintain efficiency and timeliness, we implemented a scheduling system using Apache Airflow. This scheduling system enabled web crawling at 30-minute intervals, commencing at the opening of the U.S. stock market and concluding at its closure. The orchestration of these 33 Lambda functions was managed through AWS Step Functions.

All the collected data is meticulously stored in CSV format within AWS S3 for easy access and future analysis.


### 2. Backend Server

The backend server is implemented using AWS EC2. When Lambda functions perform web crawling and save the data to an S3 bucket, this data is subsequently retrieved and stored within a MySQL database hosted on the EC2 instance. Furthermore, a web server has been established using Django to facilitate seamless interactions and serve the collected data. Also, the backend server functions as an intermediary between the client interface and the ChatGPT API. It is responsible for managing user requests, handling query processing, retrieving pertinent information from the database, communicating with the ChatGPT API to submit queries, and ultimately delivering responses back to the client

### 2. ChatGPT API

The system leverages the OpenAI ChatGPT API to provide natural language processing capabilities. Users can interact with the system by sending queries and receiving responses generated by the AI model.


![ddd drawio](https://github.com/hotzan0301/stockmarket/assets/59554674/00730b11-2af1-4e0c-9cbd-9f0abdcab757)


