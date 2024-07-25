<!-- Improved compatibility of back to top link: See: https://github.com/othneildrew/Best-README-Template/pull/73 -->
<a name="readme-top"></a>
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
<!--[![Contributors][contributors-shield]][contributors-url]
[![Forks][forks-shield]][forks-url]
[![Stargazers][stars-shield]][stars-url]
[![Issues][issues-shield]][issues-url]
[![MIT License][license-shield]][license-url]
[![LinkedIn][linkedin-shield]][linkedin-url]-->



<!-- PROJECT LOGO -->
<br />
<div align="center">
  

<h3 align="center">Robotics Question Answering LLM bot</h3>

  <p align="center">
    This repo includes the source code for the developing a Question answering LLM bot using the  OpenAI API. The Milvus lite database is used to store the generated RAPTOR index from three robotics textbooks given in the reference section. 

   
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
      <a href="#prerequisites and installation">Prerequisites and Installation</a>
    </li>
    <li><a href="#Steps Involved - Without Argo Rollouts">Steps Involved - Without Argo Rollouts </a></
  
    <li><a href="#license">License</a></li>
    <li><a href="References">References</a></li>
  </ol>
</details>



<!-- ABOUT THE PROJECT -->
## About The Project

In this project, a question answering LLM chatbot is build from a RAPTOR index Milvus lite vecotr database of a collection of three textbooks related to robotics. The content extraction and chunking process of the textbooks are done using the file `extract_and_chunk_embed.ipynb` and the combined textbook chunks are stored as `Content_extraction_and_chunking_embed/combined_textbook_chunk_metadata.pkl`. Using the saved file, the RAPTOR indexing is done using the code in  `RAPTOR_indexing/raptor-index_final_kaggle.ipynb`.
For the summarization step, `gpt-4o-mini` from OpenAI is used. The hierarchial tree structure is build with 5 depths or levels  and stored as `RAPTOR_indexing/rec_results_full.pkl`. This file is used to build the Milvus lite vector database with SBERT Embeddings (`multi-qa-MiniLM-L6-cos-v1`) and the implement the retrieval and Question answering bot creation in the file `QA-Retrieval-final.ipynb`. For the Hybrid retriever BM25 with the vector store retriever is used. Further FlashRank is used for the reranking and for Query expansion,`gpt-4o-mini` based Stepback prompting is used. Finally the QA model is build again using `gpt-4o-mini` OpenAI API model. All of the three `.ipynb` files can be run on Goggle Colab or kaggle for faster execution. 


![User proflie web app](results/webapp_latest.png)




<p align="right">(<a href="#readme-top">back to top</a>)</p>



### Built With

* [![Kubernetes][Kubernetes.io]][Kubernetes-url]
* [![Docker][Docker.com]][Docker-url]
* [![MongoDB][MongoDB.com]][MongoDB-url]
* [![JavaScript][JavaScript.com]][JavaScript-url]

<p align="right">(<a href="#readme-top">back to top</a>)</p>



<!-- GETTING STARTED -->
### Prerequisites and Installation

 The below points describe the key installations that is needed to run this project:
* The installation of `Kubernetes` or 'kubectl' and `Docker` can be followed from their official websites links given in the above section. 
* For installing the `Minikube` cluster on my local machine, I have followed the steps from the [official documentation](https://minikube.sigs.k8s.io/docs/start/). In this project, I have used the cluster as a container, so the driver I am using to start the cluster is `Docker`.
* Next in the `Minikube`cluster, Argo CD is installed following the [official documentation](https://argo-cd.readthedocs.io/en/stable/getting_started/). 
* Since one of the aims of this project is to include a canary release strategy, Argo Rollouts is also installed in the cluster following the [official documentation](https://github.com/argoproj/argo-rollouts/blob/master/docs/installation.md#kubectl-plugin-installation). I have also installed the Kubectl plugin, so that it is possible to visualize and manage the plugins from the command line.
In the next section, the steps involved to create this project is defined.
<!-- * npm
  ```sh
  npm install npm@latest -g
  ```

### Installation

1. Get a free API Key at [https://example.com](https://example.com)
2. Clone the repo
   ```sh
   git clone https://github.com/DOOMNOVA/A_p_test.git
   ```
3. Install NPM packages
   ```sh
   npm install
   ```
4. Enter your API in `config.js`
   ```js
   const API_KEY = 'ENTER YOUR API';
   ``` -->
## Steps Involved - Without Argo Rollouts
* The initial step involves pushing a docker container image of the web application to `DockerHub`. So, the docker files - `Dockerfile` and`docker-compose.yaml` is created. Further, in order to streamline the process a github actions workflow file - `main.yaml` is created to push a new image to `DockerHub` everytime there is change to this source code repo.

* Next in the `Minikube` cluster I have initially created, a new namespace `myapp` is created for the web application and the config files will be run inside this. The Kubernetics manifest files in the  [Config repo](https://github.com/DOOMNOVA/A_P_config_argocd.git) uses the image - `doomnova/webapp-argocd:latest` , which was  prevoiusly pushed to the `Dockerhub` . This image will be know as the initial  web app container image in this project.
* Since I am using a `MongoDB` database for the webapp, the Config files in the [repo](https://github.com/DOOMNOVA/A_P_config_argocd.git)- `mongo.yaml`, `mongo-secret.yaml` and `mongo-config.yaml` are used to define database in the cluster.  The `webappdeployment.yaml` is used to deploy the user profile page app developed in this project. For the  web application, there are two `replicas:2` defined in this project. Further, in order to access the app in the browser, the `NodePort` service is defined in the  `webappdeployment.yaml`. Note that inorder to use the file for this task, uncomment  code for the kubernetes resource type `Deployment` and comment the kubernetes resource type `Rollout` in the latest `webappdeployment.yaml`file in the Config repo.
* Finally, the `application.yaml` is used to defined the entire application in the `Minikube` cluster. In this file, we can specify the Config file repo that should be watched  by `Argo CD` to makes changes to the application in the cluster. 

<p align="right">(<a href="#readme-top">back to top</a>)</p>


<!-- USAGE EXAMPLES -->
## Results - Without Argo Rollouts
Now to deploy the web application using the initial image, the below code can run in the terminal:
 ```sh
  kubectl -f apply application.yaml
  ```
we can see the deployed webapp user profile page below.

![alt text](results/webapp_latest.png)

Further as shown in below figure, using the Argo CD UI we can see the deployed application with its different components.

![alt text](results/inital_app_latest.png)


<p align="right">(<a href="#readme-top">back to top</a>)</p>





## Steps Involved - With Argo Rollouts
In this section, we will look at the steps taken to change the current web application to include a canary release rollout strategy using Argo CD Rollouts.

* Most of the files are similar to the previous task. Only difference is in the config file `webappdeployment.yaml`, in which a kubernetes `Rollout` resource type is used to control the canary release. The rollout will be triggered by updating the web app image from `doomnova/webapp-argocd:latest` to `doomnova/webapp-argocd:v1`. In the new image, the profile photo has been changed.
 This image will be known as the canary image in this project.
* The rollout strategy is based on the one defined in the official docs of [canary release](https://argo-rollouts.readthedocs.io/en/stable/getting-started/). 
The rollout here utilizes a canary update strategy which sends 20% of the traffic to the canary. Then followed by a manual promotion and finally gradual automated traffic increases for the rest of the upgrade. The canary strategy is given below:
```spec:
  replicas: 5
  strategy:
    canary:
      steps:
      - setWeight: 20
      - pause: {}
      - setWeight: 40
      - pause: {duration: 10}
      - setWeight: 60
      - pause: {duration: 10}
      - setWeight: 80
      - pause: {duration: 10}
```




<!-- LICENSE -->
## License

Distributed under the MIT License. See `LICENSE.txt` for more information.

<p align="right">(<a href="#readme-top">back to top</a>)</p>




<!-- ACKNOWLEDGMENTS -->
## References

* [Introduction-to-Robotics-3rd-edition](https://www.changjiangcai.com/files/text-books/Introduction-to-Robotics-3rd-edition.pdf)
* [Introduction to Autonomous Mobile Robots book](https://www.ucg.ac.me/skladiste/blog_13268/objava_56689/fajlovi/Introduction%20to%20Autonomous%20Mobile%20Robots%20book.pdf)
* [Mataric-primer(The robotics primer)](https://pages.ucsd.edu/~ehutchins/cogs8/mataric-primer.pdf)
* [Langchain cookbook-RAPTOR](https://github.com/langchain-ai/langchain/blob/master/cookbook/RAPTOR.ipynb)

<p align="right">(<a href="#readme-top">back to top</a>)</p>



<!-- MARKDOWN LINKS & IMAGES -->
<!-- https://www.markdownguide.org/basic-syntax/#reference-style-links -->

[license-shield]: https://img.shields.io/github/license/DOOMNOVA/A_p_test.svg?style=for-the-badge
[license-url]: https://github.com/DOOMNOVA/A_p_test/blob/master/LICENSE.txt


[Kubernetes.io]: https://img.shields.io/badge/kubernetes-%23326ce5.svg?style=for-the-badge&logo=kubernetes&logoColor=white
[Kubernetes-url]: https://kubernetes.io/
[Docker.com]: https://img.shields.io/badge/docker-%230db7ed.svg?style=for-the-badge&logo=docker&logoColor=white
[Docker-url]: https://www.docker.com/
[MongoDB.com]: https://img.shields.io/badge/MongoDB-%234ea94b.svg?style=for-the-badge&logo=mongodb&logoColor=white
[MongoDB-url]: https://www.mongodb.com/
[JavaScript.com]:https://img.shields.io/badge/javascript-%23323330.svg?style=for-the-badge&logo=javascript&logoColor=%23F7DF1E
[JavaScript-url]: https://www.javascript.com/
