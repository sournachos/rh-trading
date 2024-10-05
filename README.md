<div align="center"><img width="100px" height="100px" src="flag.gif"> <strong>RH-Trading</strong> &ensp;<img width="100px" height="100px" src="flag.gif"></div>
<br/>

<p align="center">
  <img alt="GitHub last commit" src="https://img.shields.io/github/last-commit/sournachos/rh-trading">
  <img src="https://img.shields.io/github/issues/sournachos/rh-trading">
  <img alt="GitHub top language" src="https://img.shields.io/github/languages/top/sournachos/rh-trading">
  <a href="LICENSE">
    <img alt="License" src="https://img.shields.io/badge/license-MIT-%23F8952D">
  </a>
    </br>
  <a href="https://www.linkedin.com/in/joseriverathedev/">
    <img alt="My Linkedin" src="https://img.shields.io/badge/Jose Rivera-%230077B5?style=social&logo=linkedin">
  </a>
</p>

___

<h3 align="center">
  <a href="#information_source-about">About</a>&nbsp;|&nbsp;
  <a href="#seedling-requirements-to-use">Requirements To Use</a>&nbsp;|&nbsp;
  <a href="#rocket-technologies">Technologies Used</a>&nbsp;|&nbsp;
  <a href="#link-contributing">How To Contribute</a>&nbsp;|&nbsp;
  <a href="#license">License</a>
</h3>

___


## :information_source: About

The project aims to facilitate access to buying and selling option contracts through Robinhood for profit (or at least that's the goal lol)<br>
It also leverages the visualization and backtesting capabilities of the [jesse](https://github.com/jesse-ai/jesse) tool
### *** ***Work in progress.*** *** ### 
<br>

## :seedling: Requirements To Use
- Python is installed
- Clone repository
- Install deps -> `pip install -r requirements.txt`
- As of 10/05:
  - A couple Robinhood strategies in `/trading_strategies`
  - Leveraging the [jesse](https://github.com/jesse-ai/jesse) tool in `/data_visualization` using [docker](https://docs.docker.com/get-started/get-docker/)

- To import historical candle data for a ticker of your choice:
  - Go to `/data-visualization/.env-example`
  - Copy the contents into a `.env` in that same folder
  - Edit values if/as needed.
  - Go to `/data-visualization/import_candles.py`
  - Edit the `start_date`, `end_date` and `ticker` values as desired to customize the retrieval of historical candle data

- To run [jesse](https://github.com/jesse-ai/jesse) on docker:
  - `cd /data_visualization/docker`
  - `docker-compose up -d` -- to start
  - open http://localhost:9000/#/ on your browser
  - `docker-compose down` -- to stop
<!-- - It's important to import the candles of historical data for the timeframe you want to backtest strategies on:
  - Do so on the `Import Candles` section of the menu once you're running on docker. -->

- With the docker container running:
  - Your local port 5432 is forwarded to the Postgres DB so you can use something like [DBViz](https://www.dbvis.com/download/) to get visibility into the data by using the .env postgres username and password


## :rocket: Technologies 

The project was created using the following external resources:

- [robin_stocks](https://github.com/jmfernandes/robin_stocks)
- [jesse](https://github.com/jesse-ai/jesse)
- [Docker](https://docs.docker.com/get-started/)
- [MarketDataApp](https://www.marketdata.app/docs/)

## :link: Contributing 

- Fork the repository
- Clone it to your local machine
- Create a branch with your new feature
- Add, commit, and push your changes to your branch
- Create a pull request on this project with your branch changes

## License 

This project is using an MIT license. Click here [LICENSE](LICENSE) for more details.

### Contributors
[Jose](https://github.com/sournachos)<br/>
[Dave](https://github.com/davechamp50)