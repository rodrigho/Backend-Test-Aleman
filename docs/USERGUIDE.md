# Backend-Test-Aleman

This guide tells users what they can do regarding their role <admin/employee>

### Admin
With this user, Nora or other Nora's employee can manage the entire app.
The user can create a menu for whatever day. The current day is the default.
The user must fill all fields. If there are not dishes, she can add more dishes in the below link `+Add more dishes?`.
Those dishes are global to avoid reinserting each time a menu is required.

After the menu is created, she can edit it using `Edit menu?` button.
Each time the menu is edited, SHE CAN NOTIFY USERS, so users will be aware of the new menu changes. 

When the menu is ready for current the, she can notify all user using `Notify employee` button and this
will send a slack message using a Slack bot.
If the slack has not been configured, and an error message is going to tell her.

When employees have ordered, she can see their orders in the menu option `See orders` 

### Employee
With this role, users only can order, see their order, and edit the order.
If the CLT time is over 11, users can not edit or order a dish.
They are two ways to go here. One of them is using the menu option `Order`
and the second one is using the link shared in the slack channel.
Employees can not see others' orders here.

### No Logged In
Only the home page is available. If you want to order, you will be redirected to the Login page.