# Medicare-Part-D-Webscraper
Webscraping script designed to work with https://q1medicare\.com

This was my first impactful project I wrote back in 2017.  There are layers upon layers of nested for loops due to... inexperience.  It works.  Suprisingly https://q1medicare\.com does not have much utility towards automated tools making many requests from their servers, which came to my benefit as well.

Output is a csv file listing al Medicare Part D plans across the United States, along with premium, deductible, gap coverage, price, and an unordered list of drugs by generic, brand, and application.

Note:  Primary script searches 2014 only, while 2009 script of course... searches legacy 2009 data.

This project provided prelim data for our Center Director where this project won the Sternfels Price for Drug Safety Discoveries.
https://www.prnewswire.com/news-releases/the-sternfels-prize-for-drug-safety-discoveries-announces-2020-winner-301006148.html
