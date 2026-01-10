<!-- Improved compatibility of back to top link: See: https://github.com/othneildrew/Best-README-Template/pull/73 -->
<a id="readme-top"></a>
<!--
*** Thanks for checking out the Best-README-Template. If you have a suggestion
*** that would make this better, please fork the repo and create a pull request
*** or simply open an issue with the tag "enhancement".
*** Don't forget to give the project a star!
*** Thanks again! Now go create something AMAZING! :D
-->



<!-- PROJECT SHIELDS -->
<!--
*** I'm using markdown "reference style" links for readability.
*** Reference links are enclosed in brackets [ ] instead of parentheses ( ).
*** See the bottom of this document for the declaration of the reference variables
*** for contributors-url, forks-url, etc. This is an optional, concise syntax you may use.
*** https://www.markdownguide.org/basic-syntax/#reference-style-links
-->


<!-- PROJECT LOGO -->
<br />
<div align="center">
  <a href="https://github.com/Max-labs/Tableau Mini">
    <img src="assets/mini-logo.jpeg" alt="Logo" width="120" height="100">
  </a>

<h3 align="center">Tableau Mini</h3>

  <p align="center">
    A Semantic Data ingestion extension for Tableau 
    <br />
    <a href="https://github.com/Olutoye-lab/Tableau-Mini"><strong>Explore the docs »</strong></a>
    <br />
    <br />
    <a href="https://github.com/Olutoye-lab/Tableau-Mini">View Demo</a>
    &middot;
    <a href="https://github.com/Olutoye-lab/Tableau-Mini/issues/new?labels=bug&template=bug-report---.md">Report Bug</a>
  </p>
</div>



<!-- TABLE OF CONTENTS -->
<details>
  <summary>Table of Contents</summary>
  <ol>
    <li>
      <a href="#about-the-project">About The Project</a>
      <ul>
        <li><a href="#built-with">Built With</a></li>
      </ul>
    </li>
    <li>
      <a href="#getting-started">Getting Started</a>
      <ul>
        <li><a href="#prerequisites">Prerequisites</a></li>
        <li><a href="#installation">Installation</a></li>
      </ul>
    </li>
    <li><a href="#usage">Usage</a></li>
    <li><a href="#roadmap">Roadmap</a></li>
    <li><a href="#contributing">Contributing</a></li>
    <li><a href="#license">License</a></li>
    <li><a href="#contact">Contact</a></li>
    <li><a href="#acknowledgments">Acknowledgments</a></li>
  </ol>
</details>



<!-- ABOUT THE PROJECT -->
## About The Project

<img src="assets\Product-image.png" alt="Tableau Dashboard" width="700" height="400">

This is a project acting as the server side component for the Tableau Mini extension. 

### Project Archtecture

<img src="assets\Tableau Mini Framework.jpeg" alt="Logo" width="700" height="400">


The extension architecture is split into three stages each with varying classes:

* Ingestion Layer
  * Data Ingestor
  * Metadata Scanner
* Semantic Core
  * Intent Decoder
  * Semantic Mapper
  * Entity Resolver
* Execution Engines
  * Confidence Analyzer
  * Hyper API
  * Publish Tableau

<p align="right">(<a href="#readme-top">back to top</a>)</p>



### Built With

* <a href="https://github.com/Max-labs/Tableau Mini">
    <img src="https://login.salesforce.com/img/logo214.svg" alt="Logo" width="120" height="100">
    <p>Salesforce Platform</p>
  </a>
* <a href="https://github.com/Max-labs/Tableau Mini">
    <img src="https://logos-world.net/wp-content/uploads/2021/10/Python-Emblem.png" alt="Logo" width="100" height="60">
    <p>Python</p>
  </a>
* <a href="https://github.com/Max-labs/Tableau Mini">
    <img src="https://www.tableau.com/sites/default/files/styles/scale_175_wide/public/2021-08/ExtensionsAPI.png?itok=Nt7mjuYq" alt="Logo" width="100" height="100">
    <p>Tableau Extenstions API</p>
  </a>


<p align="right">(<a href="#readme-top">back to top</a>)</p>



<!-- GETTING STARTED -->
## Getting Started

To Run this project locally:

### Prerequisites

**Sales Force Set Up**
1. Create a Sales Force Account
2. Add a connected app by following the Agent Force Developer Guide. [Sales Force Developer Guide][SF-dev-guide]
3. Add ENV variables:
* SF_CLIENT_KEY
* SF_CLIENT_SECRET
* SF_REDIRCT_URL

4. Set Up agents

|       | DECODER_AGENT| ENTITY_AGENT|
|-------|--------------|-------------|
|Template| Analytics and Visualisation|Analytics and Visualisation|
|Topics| None| None|
|Description|Identify and merge entity name variants across datasets that refer to the same real-world entity (e.g., “IBM”, “I.B.M.”, “International Business Machines”).| Decode the intent of the user through semantic categorisation of user data.|
| Role|Task: Normalize names (case, punctuation, common suffixes). Detect duplicates using string, acronym, and semantic similarity. Group names referring to the same entity. Choose a canonical name (most common or clearest).|Match the user's intent and the available data columns to the correct Data Standard. You will be given: User Request, Available Data Columns, All Available ontology Standards|
|Company|Large General Company. In: a list of names with variations in abbreviations, punctuation, casing, or legal suffixes Out: Return a dictionary mapping canonical names to their variants { "IBM": [ "IBM corp", "I.B.M.", "International Business Machines", ],}| General Large company 1. Analyse the User Request to understand the domain (Finance vs HR vs Sales). 2. Look at the Data Columns to see which Standard fits best physically. 3. Return ONLY the text of the best matching Standard.|
| Language| English | English|
| Tone | Neutral | Neutral |

5. Add ENV variables:
* DECODER_AGENT_ID
* ENTITY_AGENT_ID

_**Note: Get the AGENT ID from the agent URL -> (Sample) org-185bfwega89f.my.salesforce-setup.com/lightning/setup/EinsteinCopilot/0Xxbm000000yqlXCPQ <- (AGENT ID)/edit**_

**.env File**
| ENV variables| 
|--------------|
DECODER_AGENT_ID
ENTITY_AGENT_ID
SF_DOMAIN_URL
SF_CLIENT_KEY
SF_CLIENT_SECRET
SF_REDIRECT_URL
TB_SERVER_URL 
TB_SITE_NAME
TB_TOKEN ```# Tableau PAT token```
TB_TOKEN_NAME
REDIS_URL


### Installation

1. Clone the repo
   ```sh
   git clone https://github.com/Olutoye-lab/Tableau Mini.git
   ```

2. Place the redis url of the remote/local server within an env variable (REDIS_URL)
    ```sh
    # For local deployment
    docker pull redis:latest
    docker run -d --name redis -p 6379:6379 redis:latest
    # in env -> REDIS_URL=redis://localhost:6379/0
    # OR
    # REDIS_URL=<your redis remote url>
    ```

**Run Locally**

3. Create a virtual environment (pip)
    ```sh
    python -m venv .venv
    .venv/Scripts/activate
    ```

4. Install requirements to the environment 
    ```sh
    pip install -r requirements.txt
    ```
5. Change git remote url to avoid accidental pushes to base project
   ```sh
   git remote set-url origin github_username/Tableau Mini
   git remote -v # confirm the changes
   ```
6. Run tests by uncommenting the required test.
   ```
   # To run the full pipeline uncomment test_pipeline.pytest
   # The default dataset is finance.csv in tests\sample_data\normal_data\finance.csv  
    
   cd tests
   pytest -s
   ```
    


<p align="right">(<a href="#readme-top">back to top</a>)</p>



<!-- USAGE EXAMPLES -->
## Usage

This project can be demoed on Tableau through the Tableau through the extension Market Place. [Extensions Market Place][tableau-extensions-api]
- Install the Extension
- Open the Dashboad
- Move to the pannel
- Select a sample dataset
- Enter tableau Credentials and Start!!

This project can also be run locally for both server and client components. __Steps provided above.__


<p align="right">(<a href="#readme-top">back to top</a>)</p>


<!-- ROADMAP -->
## Roadmap

- [x] Intergrate headless client panel into Main dashboard.
- [ ] Working with the Tableau R&D team, to utilise tableau connections architecture into Mini, for seamless and robust data ingestion.
- [ ] Implement a feature to automatically validate and score datasets based on specified business logic.
    - e.g.  sales pipeline must be Lead → Qualified → Demo → Proposal → Closed (Won). 
    - If a dataset violates this it is negatively scored (-2)
- [ ] Implementing caching to remove re-entering credentials per ingestion.

See the [open issues](https://github.com/Max-labs/Tableau-Mini/issues) for a full list of proposed features (and known issues).

<p align="right">(<a href="#readme-top">back to top</a>)</p>



<!-- CONTRIBUTING -->
## Contributing

Contributions are what make the open source community such an amazing place to learn, inspire, and create. Any contributions you make are **greatly appreciated**.

If you have a suggestion that would make this better, please fork the repo and create a pull request. You can also simply open an issue with the tag "enhancement".
Don't forget to give the project a star! Thanks again!

1. Fork the Project
2. Create your Feature Branch (`git checkout -b feature/AmazingFeature`)
3. Commit your Changes (`git commit -m 'Add some AmazingFeature'`)
4. Push to the Branch (`git push origin feature/AmazingFeature`)
5. Open a Pull Request

<p align="right">(<a href="#readme-top">back to top</a>)</p>

### Top contributors:

<a href="https://github.com/Olutoye-lab/Tableau-Mini/graphs/contributors">
  <img src="https://avatars.githubusercontent.com/u/180702992?s=48&v=4" alt="contrib.rocks image"
  width="50" height="50"  />
</a>



<!-- LICENSE -->
## License

Distributed under the project_license. See `LICENSE.txt` for more information.

<p align="right">(<a href="#readme-top">back to top</a>)</p>



<!-- ACKNOWLEDGMENTS -->
## Acknowledgments

Thank you to the Tableau Hackathon team for providing a platform to build skill driven projects. 

<p align="right">(<a href="#readme-top">back to top</a>)</p>



<!-- MARKDOWN LINKS & IMAGES -->
<!-- https://www.markdownguide.org/basic-syntax/#reference-style-links -->
[contributors-shield]: https://img.shields.io/github/contributors/Olutoye-lab/Tableau-Mini.svg?style=for-the-badge
[contributors-url]: https://github.com/Olutoye-lab/Tableau-Mini/graphs/contributors
[forks-shield]: https://img.shields.io/github/forks/Olutoye-lab/Tableau-Mini.svg?style=for-the-badge
[forks-url]: https://github.com/Olutoye-lab/Tableau-Mini/network/members
[stars-shield]: https://img.shields.io/github/stars/Olutoye-lab/Tableau-Mini.svg?style=for-the-badge
[stars-url]: https://github.com/Olutoye-lab/Tableau-Mini/stargazers
[issues-shield]: https://img.shields.io/github/issues/Olutoye-lab/Tableau-Mini.svg?style=for-the-badge
[issues-url]: https://github.com/Olutoye-lab/Tableau-Mini/issues
[license-shield]: https://img.shields.io/github/license/Olutoye-lab/Tableau-Mini.svg?style=for-the-badge
[license-url]: https://github.com/Olutoye-lab/Tableau-Mini/blob/master/LICENSE.txt
[-shield]: https://img.shields.io/badge/--black.svg?style=for-the-badge&logo=&colorB=555
[-url]: https://.com/in/Olutoye-lab
[product-screenshot]: assets/product-image.png
<!-- Shields.io badges. You can a comprehensive list with many more badges at: https://github.com/inttter/md-badges -->
[Next.js]: https://img.shields.io/badge/next.js-000000?style=for-the-badge&logo=nextdotjs&logoColor=white
[Next-url]: https://nextjs.org/
[python]: https://logos-world.net/wp-content/uploads/2021/10/Python-Emblem.png
[python-url]: https://www.python.org/
[React.js]: https://img.shields.io/badge/React-20232A?style=for-the-badge&logo=react&logoColor=61DAFB
[React-url]: https://reactjs.org/
[tableau-extensions-api]: https://www.tableau.com/sites/default/files/styles/scale_175_wide/public/2021-08/ExtensionsAPI.png?itok=Nt7mjuYq
[tableau-url]: https://www.tableau.com/developer/tools/extensions-api
[salesforce]: https://login.salesforce.com/img/logo214.svg 
[salesforce-url]: https://developer.salesforce.com/docs/einstein/genai/guide/agent-api-get-started.html

<!-- Custom -->
[SF-dev-guide]: https://developer.salesforce.com/docs/ai/agentforce/guide/agent-api-get-started.html#add-connected-app-to-agent
