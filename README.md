# Stock Market with ChatGPT

In today's market, there is an abundance of stock information websites and applications, making access to stock market data faster and more convenient than ever before. Navigating popular platforms such as Yahoo Finance has become a straightforward task for virtually anyone. Nevertheless, for newcomers, the initial entry into these websites can be quite overwhelming, as they grapple with the question of where to commence their exploration.

For example, even experienced users may find it a time-consuming challenge to configure their settings for the comparative analysis of stock information across various companies. Fortunately, with the advancements in natural language processing models like ChatGPT, we are witnessing remarkable improvements in user experiences applied across diverse domains.

By envisioning the integration of ChatGPT into a stock information application, we have the potential to enhance its user-friendliness significantly. Such an implementation would empower a broader audience to effortlessly and expeditiously access the wealth of stock information available.

This comprehensive project encompasses a range of functionalities, including web scraping, data storage, task scheduling, orchestration, web server hosting, and the development of web applications, all powered by AWS cloud services. Moreover, a chat-based interface has been skillfully incorporated to allow users to interact with the stock information database through ChatGPT.

## Overview

- **Web Crawler**: An automated web crawler using AWS Lambda gathers stock market data from Yahoo Finance and stores it in an AWS S3 bucket.

- **Backend Server**: The AWS EC2-based backend server manages web-crawled data from Lambda functions, storing it in an EC2-hosted MySQL database. It utilizes Django to serve data, acting as an intermediary for client interactions with the ChatGPT API, handling requests, and processing queries.

- **ChatGPT API**: The system integrates with the OpenAI ChatGPT API, allowing users to send queries and receive AI-generated responses.

## Architecture

![ddd drawio](https://github.com/hotzan0301/stockmarket/assets/59554674/00730b11-2af1-4e0c-9cbd-9f0abdcab757)

## Components

### 1. Web Crawler
For web crawling, we employed multiple Lambda functions to gather stock information. Specifically, we collected stock summary and company profiles for the top 100 companies in terms of market capitalization within each of the 11 sectors, total 1100 companies, through Yahoo Finance. To expedite the process, we utilized a total of 33 Lambda functions, distributing them across the sectors, with three Lambda functions dedicated to each sector.

To maintain efficiency and timeliness, we implemented a scheduling system using Apache Airflow. This scheduling system enabled web crawling at 30-minute intervals, commencing at the opening of the U.S. stock market and concluding at its closure. The orchestration of these 33 Lambda functions was managed through AWS Step Functions.

All the collected data is meticulously stored in CSV format within AWS S3 for easy access and future analysis.


### 2. Backend Server

The backend server is implemented using AWS EC2. When Lambda functions perform web crawling and save the data to an S3 bucket, this data is subsequently retrieved and stored within a MySQL database hosted on the EC2 instance. Furthermore, a web server has been established using Django to facilitate seamless interactions and serve the collected data. Also, the backend server functions as an intermediary between the client interface and the ChatGPT API. It is responsible for managing user requests, handling query processing, retrieving pertinent information from the database, communicating with the ChatGPT API to submit queries, and ultimately delivering responses back to the client

### 3. ChatGPT API

This system leverages ChatGPT to enable users to easily obtain desired information through simple natural language queries. ChatGPT translates user questions into SQL queries, extracts data from the database tailored to the users' needs, and then presents the extracted data in a user-friendly format for user consumption.

## Future Developments

### 1. More Lambda Functions For More Information
The current system is capable of crawling stock information for 1,100 companies. However, by merely scaling up the number of Lambda functions for each sector, we can easily expand the coverage to include data for even more companies. The current approach employs three Lambda functions for each sector to retrieve stock information for the top 100 companies. Assuming this structure remains the same, to collect stock information for 11,000 companies, we would require a total of 330 Lambda functions.

### 2. Data Visualization With BI Tool
The current format of ChatGPT responses visible to users is essentially text-based, resembling SQL query results. To enhance user convenience further, incorporating a Business Intelligence (BI) tool such as Power BI is essential. This integration would empower users to analyze the received data in various ways, providing a versatile toolkit for data exploration and interpretation.

### 3. Fine Tuning For ChatGPT
The current performance of the ChatGPT API for user interactions is suboptimal in terms of response time. Recently, with the introduction of Fine-tuning capabilities by OpenAI, it is now possible to train the model on anticipated user queries and responses. This holds the promise of achieving a significantly faster ChatGPT performance, which is highly anticipated.

### 4. Diversity of Data
Currently, the system only provides stock summaries for individual companies. However, diversifying the data can be achieved by incorporating historical data and company-related news into the crawling process. While the system currently relies solely on an RDBS, the inclusion of various data types such as company news necessitates the integration of a NoSQL database. This expansion would enable users to access a broader range of data resources easily
