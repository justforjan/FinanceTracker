**Track your expenses more easily!**

This is an expenses tracking application. I am yet to find an application, that lets me assign expenses to two categories e.g. to 'Travel' and 'Transport' at the same time.
So, until now, while travelling I had to decide what category assign e.g. my transport expenses to.

Splitting these categories into 2 dimensions makes the expense tracking at lot more overseeable in my opinion.
The first dimension are categories like 'Transport', 'Education', 'Freetime' and 'Food'. The second dimension's categories are 'At Home' and your trips.

This brings many advantages. You can track how much you spent in one trip covering all categories of the first dimension 
or you can look how much you spent in one category of the first dimensions throughout all your trips.
Additionally, you can check your expenses of one first-dimension-category in a certain trip.
So, overall, you get a better overview over your expenses and you do not have to struggle with chosing which category to assign the expense to.

It brings other advantages like the possibility to calculate you daily average expense during a certain trip.


The start page is an overview of your expenses and icomes. At first you see the transactions of the current month but you can switch through the months easily. This is done with AJAX. Whenever you see you transactions sorted like this, you have the opportunity to edit or delete them by clicking the respective button. You can always add transactions by hovering over the floating button at the bottom right and then selecting "Add expense" or "Add income".

On the second tab called "statistics" you get a litte overview of your expense per month shown as a pie chart. I used the JacaScript library "Charts.js" for that. You expenses are sorted by category and you see how high you expenses are absolutly and relatively to you total expenese per month. Here as well, you can skip through the monhts. By clicking on one of the category's name you access an overvie of you transactions assinged to this category, similarly to the start page.

The third trip is an overview of you trips. By clicking on the "Go to trip" button you are shown more details about the selected trip like total expenses, average expenses per day and duration. Furthermore, there is a litte piechart, showing how much you proportionally spent in the categories during the selected trip. Beneith that, you see the expenses that you assigned to this trip. To add a trip you also have to hover over the floating button and select "Add trip". You can give your trip a name, start and end date an if you want you can chose the countries you are travelling through this trip. As a nice feature the flags of these countries are shown on top of the trip detail page as well as on the trip overview page.

And this is it. This is my way to sophisticated final project for the best lecture I have ever taken. Thank you, cs50 staff!!


