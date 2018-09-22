import re
import logging
import requests
from .models import Product, Favorite, User


def create_user_list(user):
    """
    Create a user list for products page
    :param user: The user
    :return: List of products for the user
    """

    pairs = []
    for i in range(Favorite.objects.filter(user=user).count()):
        pair = []
        product = Favorite.objects.filter(user=user)[i].product
        pair.append(product)

        substitute = Favorite.objects.filter(user=user)[i].substitute
        pair.append(substitute)
        pairs.append(pair)
    print(f"Pairs : {pairs} Pairs !")
    return pairs


def get_product_array(query, product_code=None):
    """
    Get product array
    :param query:
    :param product_code:
    :return:
    """
    if query:
        print(f"Searching for {query} ")
        return search_product(query)
    elif product_code is not None:
        return search_product(product_code)
    else:
        return None


def get_products_id(product):
    """
    Get product id
    :param product:
    :return: product id
    """
    url = f"https://fr.openfoodfacts.org/cgi/search.pl?search_terms={product}"
    print(url)

    try:
        # Getting the id
        products_id = fetch_products_id(url)
        print(products_id)
        return products_id
    except KeyError:
        print(f"It doesn't work with {product} (get_product:logic)")
        return None


def search_product(products_id):
    """
    Search product
    :param products_id: Requested product(s)
    :return: Product array : stored_product, stored_category, product_id, stored_grade, stored_categories
    """
    print(f"Getting {products_id} ...")

    if type(id) == int:
        print(id)
    else:
        products_id = get_products_id(products_id)
        print(products_id)

    i = 0
    product_array = None
    while product_array is None and len(products_id) > i:
        print(f"Product array : {product_array}")
        print(f"Length after : {len(products_id) > i}")
        product_array = get_product(products_id[i])
        i += 1
    return product_array


def fetch_products_id(url):
    """
    Fetch products in txt
    :param url: Page
    :return: products_id
    """
    data = requests.get(url)
    results = data.text
    products_id = re.findall(r'<a href="/produit/(\d+)/', results)
    return products_id


def save_product(product_array):
    """
    Save product in database
    :param product_array:
    :return: bool for success
    """

    [name, code, grade, image, categories, nutriments] = product_array

    if Product.objects.filter(code=code).exists():
        return True
    else:
        product = Product(name=name, image=image, categories=categories, grade=grade, nutriments=nutriments, code=code)

        try:
            product.save()
            return True

        except ValueError:
            return False


def stare_product(user, product_array, substitute_array):
    """
    Staring product
    :param user:
    :param product_array:
    :param substitute_array:
    :return: bool for success
    """

    product_code = product_array[1]
    substitute_code = substitute_array[1]

    product = Product.objects.get(code=product_code)
    substitute = Product.objects.get(code=substitute_code)

    try:
        Favorite.objects.get_or_create(user=user, product=product, substitute=substitute)
        print("Product stared !")
        return True

    except ValueError:
        return False


def delete_product(user, product_code, substitute_code):
    """
    Delete favorite product
    :param user:
    :param product_code:
    :param substitute_code:
    :return: bool for success
    """

    print(f"Product code : {product_code}")
    print(f"Substitute code : {substitute_code}")
    print(user.id)

    user = User.objects.filter(id=user.id)
    print(user)
    if user.exists():
        favorites = Favorite.objects.all()

        for favorite in favorites:

            if favorite.product.id == product_code:
                print("True")

                if favorite.substitute.id == substitute_code:
                    print("True")

                    if favorite.user == user[0]:
                        print("Delete !")
                        favorite.delete()
                        return True

    print("Delete failed!")
    return False


def in_database(product_id):
    """
    Check if in database
    :param product_id: product id
    :return: product
    """
    stored_products = Product.objects.filter(code=product_id).count()

    for stored_product in range(stored_products):
        if stored_product > 1:
            print(f"The product seems to have more than one existence")
            print("Destroy...")
            stored_product.delete()
        elif stored_product == 1:
            print(f"The product is already in database : {product_id} (logic)")
            return stored_product
        else:
            print(f"The product will be saved : {product_id} (logic)")
            return False


def get_product(product_id):
    """
    Get product array
    :param product_id: Requested product
    :return: product_array : Product, Category, Code, Grade, List of categories
    """
    if in_database(product_id):
        product_object = Product.objects.get(code=product_id)
        name = product_object.name
        code = product_object.code
        grade = product_object.grade
        image = product_object.image
        category = product_object.category
        categories = product_object.categories
        nutriments = product_object.nutriments
        product_array = [name, code, grade, image, category, categories, nutriments]
        return product_array

    else:
        product_array = pull_product(product_id)

        if product_array is not None:
            return product_array

        else:
            return None


def pull_product(product_id, product_code=None):
    """
    Save product
    :param product_id: Requested product
    :param product_code: If fetching substitutes this is the product to substitute
    :return: Product array : Product queryset, Category, List of categories, Grade, Id
    """
    page = f"https://world.openfoodfacts.org/api/v0/product/{product_id}.json"
    print(f"Pulling out product : {page} (logic)")

    data = requests.get(page).json()
    print("We are requested the page")

    if data:
        print(f"Data : {data}")

        if data['product']:
            product = data['product']
            print(f"Product : {product}")
            try:
                if product_code is not None:
                    print("Product code is not None so we are fetching subs !")
                    # We are fetching substitutes
                    product_array = fetch_product_array(product, product_code)
                else:
                    print("Product code is None so we are fetching product !")
                    # We are fetching product
                    product_array = fetch_product_array(product)

                if product_array is not None:
                    categories = product_array[0]
                    image = product_array[1]
                    name = product_array[2]
                    code = product_array[3]
                    grade = product_array[4]
                    nutriments = product_array[5]
                    print(f"...{categories}...")
                    print(f"...{image}...")
                    print(f"...{name}...")
                    print(f"...{code}...")
                    print(f"...{grade}...")
                    print(f"...{nutriments}...")
                    print(f"Pulling out the product ... {name} (logic)")
                    return name, code, grade, image, categories, nutriments

                else:
                    return None

            except IndexError:
                return None

    else:
        return None


def fetch_product_array(product, product_code=None):
    """
    Fetch product array
    :param product:
    :param product_code:
    :return: product array
    """
    categories, image, name, code, grade, nutriments = 0, 0, 0, 0, 0, 0

    if 'code' in product:

        if product_code is not None:

            if product['code'] != product_code:
                code = product['code']
                print(f"{code}!={product_code}")
                print(f"Code is {code}")
            else:
                print("This is the product we try to substitute !")
                return None
        else:
            code = product['code']
            print(f"Code is {code}")

    if 'categories_hierarchy' in product:
        categories = product['categories_hierarchy']
        print(f"Categories are")
        print(categories)

    if 'image_url' in product:
        image = product['image_url']
        print(f"Image is {image}")

    if 'product_name' in product:
        name = product['product_name']
        print(f"Name is {name}")

    if 'nutrition_grades' in product:
        grade = product['nutrition_grades']
        print(f"Grade is {grade}")

    if 'nutriments' in product:
        nutriments = product['nutriments']
        print(f"Nutriments ...")
        print(nutriments)
        print("That was the nutriments")

    if categories and image and name and grade and nutriments:
        print("Fetching product array has worked !")
        return [categories, image, name, code, grade, nutriments]
    else:
        print("Fetching product array didn't worked !")
        return None


def get_substitutes(categories, product_code, minimal_grade):
    """
    Get substitutes for product
    :param categories: The requested list of categories
    :param product_code: The product code
    :param minimal_grade: The minimal grade
    :return:
    """
    print("get substitutes (logic)")

    substitutes = None
    while substitutes is None:
        category = get_category(categories)
        substitutes = search_substitutes(category, minimal_grade, product_code)
        categories = categories.pop()
    return substitutes


def search_substitutes(category, minimal_grade, product_code):
    """
    Search substitutes
    :param category:
    :param minimal_grade:
    :param product_code:
    :return: substitutes
    """
    url = url_category_for_grade(category, minimal_grade)
    [url, category] = try_url_redirection(url, category)

    if url is not None:

        print(" We will use this URL to fetch substitutes ")
        print(f"{url} (get_substitutes:logic)")

        nutrition_score = ord('a')
        substitutes = None

        i = -1

        # TEST : While conditions
        # print(chr(98 + i))
        # print(98 + i >= ord(minimal_grade) - 1)
        # print(ord(minimal_grade) - 1)

        while substitutes is None and 5 > i and 97 + i <= ord(minimal_grade) - 1:
            i += 1

            # TEST
            # print(chr(97 + i))

            print(f"Product grade : {chr(nutrition_score+i).upper()}")
            print(f"Minimal grade : {minimal_grade.upper()}")
            print(f"In the while loop for the {i} time (get substitutes)")

            url = url_category_for_grade(category, grade=chr(nutrition_score + i))
            substitutes = fetch_substitutes(url, product_code, minimal_grade=nutrition_score + i)
        return substitutes

    else:
        print(f"We didn't get the right URL to fetch substitutes !...")
        return None


def fetch_substitutes(url, product_code, minimal_grade):
    """
    Fetch substitutes
    :param url: Products url
    :param minimal_grade: Minimal grade
    :param product_code: Product code
    :return:
    """
    substitutes = []
    minimal_grade = chr(minimal_grade)

    print(f"We are searching for {minimal_grade.upper()} products")
    print(url)
    products_id = fetch_products_id(url)
    print(f"products id : {products_id}")

    if products_id:

        for product_id in range(len(products_id)):
            print(f"Id du produit : {products_id[product_id]}")
            product_array = pull_product(products_id[product_id], product_code)

            if product_array:
                print(f"We are getting subs array")
                print(f"{product_array}")

                substitutes.append(product_array)

            if len(substitutes) >= 6:
                return substitutes

        return substitutes

    else:
        print("Product range is None")
        return None


def try_url_redirection(url, category):
    """
    Getting URL by following the open food facts redirection
    :return: url
    """
    print(f"Try url redirection")

    try:
        # Getting the id
        req = requests.get(url)
        if req.history:
            print("Request was redirected")
            if req.status_code == 200:
                print("Status = 200")
                url = req.url
                category = url.rsplit('/', 1)[-1]
                print(req.url)
                return [req.url, category]

            else:
                print("Status != 200")
                url = req.url
                category = url.rsplit('/', 1)[-1]
                print(req.url)
                category = req.url
                return [req.url, category]
        else:
            print("Request was not redirected")
            print(url)
            return [url, category]

    except KeyError:
        print(f"It doesn't work with {category} (get_product:logic)")
        return None


def get_category(categories):
    """
    Get the category of product
    :return: category
    """
    category = try_category_redirection(categories[-1])
    category_url = f"https://fr.openfoodfacts.org/category/{category}"
    [url_for_category, category] = try_url_redirection(category_url, category)
    print(f"This is the url for category {url_for_category}")
    print(f"This is the category {category} (get_substitutes)")
    return category


def select_category(categories):
    """
    Select category for template
    :param categories:
    :return:
    """

    category = categories

    try:
        category = category[-1]
        print(f"Select last category in list works {category}!")
    except IndexError:
        print(f"Select last category in list didn't works {category}!")

    return category


def try_category_redirection(category):
    url = f"https://fr.openfoodfacts.org/category/{category}"

    category_url = try_url_redirection(url, category)

    if category_url:
        [url, category] = category_url
        print(category)
        print(url)

    print(f"Searching in {category}")
    return category


def url_category_for_grade(category, grade):
    api_search = "https://fr.openfoodfacts.org/cgi/search.pl?action=process"
    category_as_first_filter = "&tagtype_0=categories&tag_contains_0=contains"
    grade_as_second_filter = "tagtype_1=nutrition_grades&tag_contains_1=contains"
    url_params = '&sort_by=unique_scans_n&page_size=20&axis_x=energy&axis_y=products_n'
    display_method = "action=display"

    url = f"{api_search}{category_as_first_filter}&tag_0={category}" \
          f"&{grade_as_second_filter}&tag_1={grade}{url_params}" \
          f"&{display_method}"
    print(url)
    return url


def int_code(product_code):
    """
    Check if code is an integer for template
    :param product_code:
    :return:
    """
    if not type(product_code) == int:
        product_code = int(product_code)
    else:
        product_code = product_code

    return product_code
