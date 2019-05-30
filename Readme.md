# Project-Logs-Analysis

This is Project Logs Analysis for udacity.com for Full Stack Web Developer Nanodegree. Your task is to creat a reporting tool that prints out reports. Reporting based on tables in PostgreSQL database. 

## Question:

## 1. What are the most popular three articles of all time?
Which articles have been accessed the most? Present this information as a sorted list with the most popular article at the top.


Example:

"Princess Shellfish Marries Prince Handsome" — 1201 views

"Baltimore Ravens Defeat Rhode Island Shoggoths" — 915 views

"Political Scandal Ends In Political Scandal" — 553 views


## 2. Who are the most popular article authors of all time? 
That is, when you sum up all of the articles each author has written, which authors get the most page views? Present this as a sorted list with the most popular author at the top.

Example:

Ursula La Multa — 2304 views

Rudolf von Treppenwitz — 1985 views

Markoff Chaney — 1723 views

Anonymous Contributor — 1023 views


## 3. On which days did more than 1% of requests lead to errors? 
The log table includes a column status that indicates the HTTP status code that the news site sent to the user's browser. (Refer to this lesson for more information about the idea of HTTP status codes.)

Example:

July 29, 2016 — 2.5% errors

## Technologies

- the virtual machine
- vagrant 
- psycopg2 

## Setup 
- [newsdat.sql](https://d17h27t6h515a5.cloudfront.net/topher/2016/August/57b5f748_newsdata/newsdata.zip) 
- vagrant up
- vagrant ssh
- sudo su - postgres
- psql 
- psql -d news -f newsdata.sql
- \ctest 

## Run

- python3 project_logs_analysis.py or
- ./project_logs_analysis.py

## Output
