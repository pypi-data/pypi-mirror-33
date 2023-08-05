Manage Product Template in Front End Point Of Sale
==================================================

Functionality:
--------------
    * In Point Of Sale Front End - Products list:
        * Display only one product per template;
        * Display template name instead of product name;
        * Display products quantity instead of price;
        * Click on template displays an extra screen to select Variant;

    * In Point Of Sale Front End - Variants list:
        * Display all the products of the selected variant;
        * Click on a attribute value filters products;
        * Click on a product adds it to the current Order or display normal
          extra screen if it is a weightable product;

Technical Information:
----------------------
    * Load extra model in Point Of Sale Front End:
        * product.template;
        * product.attribute;
        * product.attribute.value;

Copyright, Authors and Licence:
-------------------------------
    * Copyright: 2014-Today, Akretion;
    * Author:
        * Sylvain LE GAL (https://twitter.com/legalsylvain);
    * Licence: AGPL-3 (http://www.gnu.org/licenses/);

