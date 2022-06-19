# Star Jeans Database

![star](https://user-images.githubusercontent.com/75986085/157313911-2b5306f4-4ab2-4542-b755-7bb655baa186.png)

<a href='https://github.com/xGabrielR/Star-Jeans-Database/blob/main/notebooks/h%26m_webscraping.ipynb'>Full Documentation PT-BR</a>

<h2>0. Star Jeans</h2>
<p>Star Jeans is a fictional company that was used as a case study, where two entrepreneurs named Eduardo and Marcelo are Brazilians and entrepreneurial friends who are starting in the US fashion retail area after several successful businesses. The initial idea is to enter the market with a specific product, which is jeans for the male audience, but even with the well-defined audience, they do not have experience in the fashion retail market, so they hired a data consultancy to answer some questions..</p>

<h2>1. Bussiness Problem</h2>
<p>Eduardo and Marcelo need awser for this questions.</p>
<p>they are two entrepreneurs and they want to enter the menswear market but they are having some difficulties related to the start of the venture</p>

> *What is the best selling price for the jeans pants?*
> 
> *How many types of pants and their cores for the initial product?*
> 
> *What raw material is needed to make these pieces?*

<p><strong>What is a Retail?</strong></p>
<p>It is a type of business model where the product is sold directly to the consumer, for example a market, it is a Retail, where it sells products according to demand and in small quantities directly to the consumer, where the money comes mainly from the quality of the service. face-to-face customer service, product exhibition, infrastructure quality, among others.</p>

<p><strong>What is an E-Commerce?</strong></p>
<p>It's a business model similar to retail, let's say, where I have a website that sells products online, in this style of business model, the consumer enters a funneling process, when the consumer knows the brand, registers on the site, order and purchase by becoming a customer. In this process, there are no employees or the infrastructure of the physical store does not exist, as sales are made automatically on the Website. Therefore, it is necessary to have a good website, with colors that match the brand, quality of online service, or in other words, the money comes with the experience and the purchase process.</p>

![market_funnel](https://user-images.githubusercontent.com/75986085/157315368-8861c694-4634-4312-b079-f9489cb28130.jpg)

<h2>1. Solution Strategy</h2>
<ul>
  <li>A database with the Median of competitors' prices by type and color in the next 30 days.</li>
  <li>This Average will be available in a web application.</li>
</ul>

<p>Solution Steps</p>
<ol>
  <li>Complete WebScraping of H&M Jeans Website.</li>
  <li>Storing Daily data on Heroku Clound.</li>
  <li>Usind a API to Feed Data from Heroku on Two Apps.</li>
  <li>Streamlit is a Web Based Plataform for Web Apps.</li>
  <li>Executable TKinter App.</li>
</ol>

<p>Steps to Improve:</p>
<ul>
  <li>Need more Days to collect for better plots.</li>
  <li>Need Pagination products (Only 36 Daily Web Scraping).</li>
  <li>Add product name (The Produt Name is Just fit column, but withou 'Fit', Eg: 'slim_fit' => 'slim_jeans' in website)</li>
</ul>

https://user-images.githubusercontent.com/75986085/157462075-529328d1-3b43-4378-9164-47d94e33f5bc.mp4

<p>Second Deployment is a executable app :)</p>

![img_app](https://user-images.githubusercontent.com/75986085/157460350-7a2ddd17-0428-4c33-950e-8dc4476b1a9d.png)

