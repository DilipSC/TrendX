# Twitter Trends Scraper

A web application that scrapes Twitter trends using Selenium and displays them in a Next.js frontend with a dark/light theme.

## Project Structure 
project/
├── client/ # Next.js frontend
│ └── src/
│ └── app/
│ ├── api/ # API routes
│ ├── page.tsx # Main page
│ └── layout.tsx # Root layout
└── TwitterScraping/ # Python backend
├── server.py # Flask server
├── twitter_scraper.py # Scraping logic
├── config.py # MongoDB config
└── .env.local # Environment variables


## Prerequisites

- Python 3.8+
- Node.js 16+
- MongoDB
- Chrome browser

## Installation

1. **Clone the repository**
bash
git clone https://github.com/DilipSC/TrendX.git
cd TrendX


2. **Set up Python backend**
bash
cd TwitterScraping
Install Python dependencies
pip install flask flask-cors selenium python-dotenv pymongo
Create .env.local file with your credentials
cp .env.example .env.local

3. **Set up Next.js frontend**
bash
cd client
Install Node dependencies
npm install


4. **Configure environment variables**

Create `TwitterScraping/.env.local` with:

env
TWITTER_USERNAME=your_username
TWITTER_PASSWORD=your_password
PROXY_URL=your_proxy_url # Optional
MONGO_URI=mongodb://localhost:27017/
MONGO_DB_NAME=twitter_trends
MONGO_COLLECTION_NAME=trends

## Running the Application

1. **Start MongoDB**
Use MongoDB Compass to connect to the database and collection.

2. **Run the Flask server**
bash
cd TwitterScraping
python server.py

3. **Run the Next.js frontend**
bash
cd client
npm run dev

The frontend will run on http://localhost:3000

## Usage

1. Open http://localhost:3000 in your browser
2. Click "Start New Scrape" to fetch current Twitter trends
3. Use the refresh button to update the displayed trends
4. Toggle between dark/light theme using the theme button

## Features

- Real-time Twitter trend scraping
- MongoDB storage for trend history
- Dark/Light theme support
- Responsive design
- Loading states and error handling
- Proxy support for avoiding rate limits

## Troubleshooting

- If you get proxy errors, try commenting out the `PROXY_URL` in `.env.local`
- Make sure MongoDB is running before starting the application
- Check Chrome WebDriver is compatible with your Chrome version
- Ensure all environment variables are properly set

## Dependencies

### Backend
- Flask
- Selenium
- PyMongo
- python-dotenv
- flask-cors

### Frontend
- Next.js
- Tailwind CSS
- Radix UI
- Lucide React

## Notes

- The scraper uses Selenium with Chrome, ensure Chrome is installed
- Proxy configuration is optional but recommended for production use
- MongoDB must be running for the application to work properly