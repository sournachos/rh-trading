<div align="center"><img width="100px" height="100px" src="./demo_imgs/flag.gif"> <strong>RH-Trading</strong> &ensp;<img width="100px" height="100px" src="./demo_imgs/flag.gif"></div>
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
### *** ***Work in progress.*** *** ### 
<br>

## :seedling: Requirements To Use
- Python is installed
- Clone repositoty
- Install deps -> `pip install -r requirements.txt`
- As of 9/28:
  - A couple Robinhood strategies in `/trading_strategies`
  - Skeleton for `jesse` trading bot in `/jesse_bot` using [docker](https://docs.docker.com/get-started/get-docker/)
- To run `jesse` on docker:
  - `cd /jesse_bot/docker`
  - `docker-compose up -d` -- to start
  - open http://localhost:9000/#/ on your browser
  - `docker-compose down` -- to stop
- It's important to import the candles of historical data for the timeframe you want to backtest strategies on:
  - Do so on the `Import Candles` section of the menu once you're running on docker.


## :rocket: Technologies 

The project was created using the following external libraries:

- [robin_stocks](https://github.com/jmfernandes/robin_stocks)
- [jesse](https://github.com/jesse-ai/jesse)

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