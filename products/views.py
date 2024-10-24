from django.shortcuts import render, redirect
from django.db.models import Q
from django.core.paginator import Paginator
from django.contrib import messages
from .models import Product, Category

def all_products(request):
    """ A view to show all products, including sorting and search queries """
    
    # Start with all products
    products = Product.objects.all()

    # Get sorting and filtering parameters from the request
    sort_option = request.GET.get('sort', 'name')  # Default sorting by name
    category_filter = request.GET.get('category', None)
    price_min = request.GET.get('price_min')
    price_max = request.GET.get('price_max')
    rating_filter = request.GET.get('rating')

    # Initialize query with a default value
    query = request.GET.get('q', '')

    # Search logic
    if query:
        queries = Q(name__icontains=query) | Q(description__icontains=query)
        products = products.filter(queries)

    # Category filtering logic
    if category_filter:
        categories = category_filter.split(',')  # Assuming multiple categories can be selected
        products = products.filter(category__name__in=categories)

    # Price filtering logic
    if price_min:
        try:
            price_min = float(price_min)  # Ensure price_min is a float
            products = products.filter(price__gte=price_min)
        except ValueError:
            messages.error(request, "Invalid minimum price provided.")
    
    if price_max:
        try:
            price_max = float(price_max)  # Ensure price_max is a float
            products = products.filter(price__lte=price_max)
        except ValueError:
            messages.error(request, "Invalid maximum price provided.")
    
    # Rating filtering logic
    if rating_filter:
        try:
            rating_filter = float(rating_filter)  # Ensure rating_filter is a float
            products = products.filter(rating__gte=rating_filter)
        except ValueError:
            messages.error(request, "Invalid rating provided.")

    # Sorting logic
    if sort_option == 'price-asc':
        products = products.order_by('price')
    elif sort_option == 'price-desc':
        products = products.order_by('-price')
    elif sort_option == 'rating':
        products = products.order_by('-rating')
    else:
        products = products.order_by('name')  # Default sorting by name

    # Pagination logic
    paginator = Paginator(products, 8)  # Show 8 products per page
    page_number = request.GET.get('page')
    page_products = paginator.get_page(page_number)

    context = {
        'products': page_products,  # Pass the paginated products
        'sort_option': sort_option,
        'category_filter': category_filter,
        'price_min': price_min,
        'price_max': price_max,
        'rating_filter': rating_filter,
        'search_term': query,  # Pass the query safely
        'categories': Category.objects.all(),  # Pass all categories for the filter dropdown
    }

    return render(request, 'products/products.html', context)


def product_detail(request, product_id):
    """ A view to show a specific product in detail """

    product = get_object_or_404(Product, pk=product_id)

    context = {
        'product': product,
    }

    return render(request, 'products/product_detail.html', context)
