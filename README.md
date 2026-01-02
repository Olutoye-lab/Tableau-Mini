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
[![Contributors][contributors-shield]][contributors-url]
[![Forks][forks-shield]][forks-url]
[![Stargazers][stars-shield]][stars-url]
[![Issues][issues-shield]][issues-url]
[![project_license][license-shield]][license-url]



<!-- PROJECT LOGO -->
<br />
<div align="center">
  <a href="https://github.com/github_username/Tableau Mini">
    <img src="assets/mini-logo.jpeg" alt="Logo" width="120" height="100">
  </a>

<h3 align="center">Tableau Mini</h3>

  <p align="center">
    A Semantic Data ingestion extension for Tableau 
    <br />
    <a href="https://github.com/github_username/Tableau Mini"><strong>Explore the docs »</strong></a>
    <br />
    <br />
    <a href="https://github.com/github_username/Tableau Mini">View Demo</a>
    &middot;
    <a href="https://github.com/github_username/Tableau Mini/issues/new?labels=bug&template=bug-report---.md">Report Bug</a>
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

[![Tableau Mini dashboard][product-screenshot]](https://example.com)

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

* [![salesforce][salesforce]][salesforce-url]
* [![python][python]][python-url]
* [![Tableau Extensions API][tableau-extensions-api]][tableau-url]


<p align="right">(<a href="#readme-top">back to top</a>)</p>



<!-- GETTING STARTED -->
## Getting Started

To get a local copy up and running follow these simple example steps.

### Prerequisites

**Sales Force Set Up**
1. Create a Sales Force Account
2. Add a connected app by following the Agent Force Developer Guide. [Sales Force Developer Guide][SF-dev-guide]
3. Add ENV variables:
* SF_DOMAIN_URL
* SF_CLIENT_KEY
* SF_CLIENT_SECRET

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


### Installation

1. Clone the repo
   ```sh
   git clone https://github.com/github_username/Tableau Mini.git
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

**Deploy on Serverless Architecture**
3. 


<p align="right">(<a href="#readme-top">back to top</a>)</p>



<!-- USAGE EXAMPLES -->
## Usage

To use this project:
- Can be used within the Tableau through the extension Market Place. [Extensions Market Place][tableau-extensions-api]
- Can be run locally. Steps provided above.


<p align="right">(<a href="#readme-top">back to top</a>)</p>


<!-- ROADMAP -->
## Roadmap

- [ ] Feature 1
- [ ] Feature 2
- [ ] Feature 3
    - [ ] Nested Feature

See the [open issues](https://github.com/github_username/Tableau Mini/issues) for a full list of proposed features (and known issues).

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

<a href="https://github.com/github_username/Tableau Mini/graphs/contributors">
  <img src="https://avatars.githubusercontent.com/u/180702992?s=48&v=4" alt="contrib.rocks image"
  width="50" height="50"  />
</a>



<!-- LICENSE -->
## License

Distributed under the project_license. See `LICENSE.txt` for more information.

<p align="right">(<a href="#readme-top">back to top</a>)</p>



<!-- ACKNOWLEDGMENTS -->
## Acknowledgments

Thank you to the Tableau Hackathon team for providing a platform to build projects like this. 

<p align="right">(<a href="#readme-top">back to top</a>)</p>



<!-- MARKDOWN LINKS & IMAGES -->
<!-- https://www.markdownguide.org/basic-syntax/#reference-style-links -->
[contributors-shield]: https://img.shields.io/github/contributors/github_username/Tableau Mini.svg?style=for-the-badge
[contributors-url]: https://github.com/github_username/Tableau Mini/graphs/contributors
[forks-shield]: https://img.shields.io/github/forks/github_username/Tableau Mini.svg?style=for-the-badge
[forks-url]: https://github.com/github_username/Tableau Mini/network/members
[stars-shield]: https://img.shields.io/github/stars/github_username/Tableau Mini.svg?style=for-the-badge
[stars-url]: https://github.com/github_username/Tableau Mini/stargazers
[issues-shield]: https://img.shields.io/github/issues/github_username/Tableau Mini.svg?style=for-the-badge
[issues-url]: https://github.com/github_username/Tableau Mini/issues
[license-shield]: https://img.shields.io/github/license/github_username/Tableau Mini.svg?style=for-the-badge
[license-url]: https://github.com/github_username/Tableau Mini/blob/master/LICENSE.txt
[-shield]: https://img.shields.io/badge/--black.svg?style=for-the-badge&logo=&colorB=555
[-url]: https://.com/in/_username
[product-screenshot]: images/screenshot.png
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
