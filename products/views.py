from django.shortcuts import render, redirect, reverse, get_object_or_404
from django.db.models import Q
from django.core.paginator import Paginator
from django.contrib import messages
from .models import Product, Category
from .forms import ProductForm



def all_products(request):
    """ A view to show all products, including sorting and search queries """
    
    # Start with all products
    products = Product.objects.all()

    # Get sorting and filtering parameters from the request
    sort_option = request.GET.get('sort', 'name')  # Default sorting by name
    category_filter = request.GET.get('category', None)
    price_min = request.GET.get('price_min')
    price_max = request.GET.get('price_max')
    rating_max = request.GET.get('rating_max')
    rating_min = request.GET.get('rating_min')
    
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
    if rating_min:
        try:
            products = products.filter(rating__gte=float(rating_min))
        except ValueError:
            messages.error(request, "Invalid minimum rating provided.")
    
    if rating_max:
        try:
            products = products.filter(rating__lte=float(rating_max))
        except ValueError:
            messages.error(request, "Invalid maximum rating provided.")

    # Sorting logic
    if sort_option == 'price-asc':
        products = products.order_by('price')
    elif sort_option == 'price-desc':
        products = products.order_by('-price')
    elif sort_option == 'rating-desc':
        products = products.order_by('-rating')
    elif sort_option == 'rating-asc':
        products = products.order_by('rating')
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
        'rating_max': rating_max,
        'rating_min': rating_min,
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


def add_product(request):
    """ Add a product to the store """
    if request.method == 'POST':
        form = ProductForm(request.POST, request.FILES)
        if form.is_valid():
            form.save()
            messages.success(request, 'Successfully added product!')
            return redirect(reverse('add_product'))
        else:
            messages.error(request, 'Failed to add product. Please ensure the form is valid.')
    else:
        form = ProductForm()
        
    template = 'products/add_product.html'
    context = {
        'form': form,
    }

    return render(request, template, context)