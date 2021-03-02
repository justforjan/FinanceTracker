# Finance Tracker with the feature to assign transactions to trips
#### Video Demo:  https://youtu.be/aA5bLuLiqWE
#### Description:

This is an expenses tracking application. I am yet to find an application, that lets me assign expenses to two categories e.g. to 'Travel' and 'Transport' at the same time.
So, until now, while travelling I had to decide what category assign e.g. my transport expenses to.

Splitting these categories into 2 dimensions makes the expense tracking at lot more overseeable in my opinion.
The first dimension are categories like 'Transport', 'Education', 'Freetime' and 'Food'. The second dimension's categories are 'At Home' and your trips.

This brings many advantages. You can track how much you spent in one trip covering all categories of the first dimension 
or you can look how much you spent in one category of the first dimensions throughout all your trips.
Additionally, you can check your expenses of one first-dimension-category in a certain trip.
So, overall, you get a better overview over your expenses and you do not have to struggle with chosing which category to assign the expense to.

It brings other advantages like the possibility to calculate your daily average expense during a certain trip.


### Adding transactions and trips
You can always add transactions and trips by hovering over the floating button at the bottom right and then selecting the respective option.


### Start Page _(index.html)_
The start page is an overview of your expenses and incomes. At first you see the transactions of the current month but you can switch through the months easily. This is done with AJAX. The transactions are sorted by day. This gives you the opportunity to check how much you earned and spent each day. On top you can see the same data but for wohle month. Whenever you see you transactions sorted like this, you have the opportunity to edit or delete them by clicking the respective button. You'll see this presentation of thr transations a few times. It is always used the same html document for this (_indexAJAX.html_). The name is a little bit misleading as it is not only used for the index part of the web application.


### Statistics _(statistics.html)_
On the second tab called "statistics" you get a litte overview of your expense per month shown as a pie chart. I used the JacaScript library "Charts.js" for that. You expenses are sorted by category and you see how high you expenses are absolutly and relatively to you total expenese per month. Here as well, you can skip through the monhts. By clicking on one of the category's name you access an overview of you transactions assinged to this category, similarly to the start page. The _categories.html_ file is used for that, but it is in fact just just the _indexAJAX.html_ with some extra parts to demonstrate that only expenses of the selected category are displayed.


### Trips _(trips.html)_
The third tab is an overview of you trips. You see all you trips sorted by start date with. Baisc information like the title, start and end date and the first few flags of the coutries you have added to this trip are shown. To get to know more detail about the trip you can click on "Go to trip". On this page (_trip.html_) you are shown more details like total expenses, duration and daily average expenses throughout your trip. In case you trip has not ended yet, the daily average expenses are calculated using the current date as the end date. To make the user aware of this, a little badge sayoing "Current" is displayed next to the daily average expenses. The flags of the countries that were added to the trip are displayed on top.
To make this work, I used to API's. "restcountries.eu" to get all the names and 2-digit codes and "countryflags.io" to display the flags.


And this is it. This is my way to sophisticated final project for the best lecture I have ever taken. Thank you, cs50 staff!!


