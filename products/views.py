from django.shortcuts import render, redirect, reverse, get_object_or_404
from django.db.models import Q
from django.contrib.auth.decorators import login_required
from django.db.models.functions import Lower
from django.core.paginator import Paginator
from django.contrib import messages
from .models import Product, Category, Wishlist, Review
from .forms import ProductForm, ReviewForm
from checkout.models import OrderLineItem
from django.views import View
from django.utils import timezone


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
    product = get_object_or_404(Product, pk=product_id)
    stars_range = range(1, 6)
    reviews = Review.objects.filter(product=product, status='approved')

    # Check if the user has purchased the product
    has_purchased = (
    OrderLineItem.objects.filter(
        order__user_profile__user=request.user,  # Ensure this matches your model relationships
        product=product
    ).exists()
    if request.user.is_authenticated else False
    )

    # Handle review form submission
    form = None
    if request.method == 'POST' and has_purchased:
        form = ReviewForm(request.POST)
        if form.is_valid():
            # Save the review
            review = form.save(commit=False)
            review.product = product
            review.user = request.user
            review.status = 'approved'  # Optional: Mark as pending for moderation
            review.save()
            messages.success(request, "Your review has been submitted!")
            return redirect('product_detail', product_id=product.id)

    elif has_purchased:
        form = ReviewForm()

    context = {
        'product': product,
        'reviews': reviews,
        'form': form,
        'has_purchased': has_purchased,
    }
    return render(request, 'products/product_detail.html', context)


@login_required
def add_product(request):
    """ Add a product to the store """
    if not request.user.is_superuser:
        messages.error(request, 'Sorry, only store owners can do that.')
        return redirect(reverse('home'))

    if request.method == 'POST':
        form = ProductForm(request.POST, request.FILES)
        if form.is_valid():
            product = form.save()
            messages.success(request, 'Successfully added product!')
            return redirect(reverse('product_detail', args=[product.id]))
        else:
            messages.error(request, 'Failed to add product. Please ensure the form is valid.')
    else:
        form = ProductForm()
        
    template = 'products/add_product.html'
    context = {
        'form': form,
    }

    return render(request, template, context)


@login_required
def edit_product(request, product_id):
    """ Edit a product in the store """
    if not request.user.is_superuser:
        messages.error(request, 'Sorry, only store owners can do that.')
        return redirect(reverse('home'))

    product = get_object_or_404(Product, pk=product_id)
    if request.method == 'POST':
        form = ProductForm(request.POST, request.FILES, instance=product)
        if form.is_valid():
            form.save()
            messages.success(request, 'Successfully updated product!')
            return redirect(reverse('product_detail', args=[product.id]))
        else:
            messages.error(request, 'Failed to update product. Please ensure the form is valid.')
    else:
        form = ProductForm(instance=product)
        messages.info(request, f'You are editing {product.name}')

    template = 'products/edit_product.html'
    context = {
        'form': form,
        'product': product,
    }

    return render(request, template, context)


@login_required
def delete_product(request, product_id):
    """ Delete a product from the store """
    if not request.user.is_superuser:
        messages.error(request, 'Sorry, only store owners can do that.')
        return redirect(reverse('home'))

    product = get_object_or_404(Product, pk=product_id)
    product.delete()
    messages.success(request, 'Product deleted!')
    return redirect(reverse('products'))


@login_required
def view_wishlist(request):
    wishlist, created = Wishlist.objects.get_or_create(user=request.user)
    products = wishlist.products.all().order_by('id')  # Add ordering here
    # Pagination logic
    paginator = Paginator(products, 8)  # Show 8 products per page
    page_number = request.GET.get('page')
    page_products = paginator.get_page(page_number)

    context = {
        'products': page_products,  # Pass the paginated products
    }
    paginated_products = paginator.get_page(page_number)
    return render(request, 'products/wishlist/view_wishlist.html', {'products': paginated_products})

@login_required
def add_to_wishlist(request, product_id):
    product = get_object_or_404(Product, id=product_id)
    wishlist, created = Wishlist.objects.get_or_create(user=request.user)
    
    # Add the product to the wishlist
    if product in wishlist.products.all():
        messages.info(request, f"{product.name} is already in your wishlist.")
    else:
        wishlist.products.add(product)
        messages.success(request, f"{product.name} has been added to your wishlist!")
    
    # Redirect to the products page to avoid navigating away
    return redirect('products')  # Use the name of the products page URL

@login_required
def remove_from_wishlist(request, product_id):
    product = get_object_or_404(Product, id=product_id)
    wishlist, created = Wishlist.objects.get_or_create(user=request.user)
    wishlist.products.remove(product)
    return redirect('view_wishlist')


@login_required
def add_to_bag(request, product_id):
    """ Add a quantity of the specified product to the shopping bag """
    product = get_object_or_404(Product, pk=product_id)
    bag = request.session.get('bag', {})  # Retrieve the shopping bag from the session

    # Add product to the bag
    if product_id in bag:
        bag[product_id] += 1  # Increase quantity if already in bag
    else:
        bag[product_id] = 1  # Add product with quantity 1 if not in bag

    request.session['bag'] = bag  # Save the updated bag back to the session
    messages.success(request, f'{product.name} added to your bag!')
    return redirect('view_wishlist')  # Redirect back to the wishlist page


@login_required
def submit_review(request, product_id):
    product = get_object_or_404(Product, id=product_id)

    if request.method == 'POST':
        rating = request.POST['rating']
        review_text = request.POST['review_text']

        # Check if the user has already purchased the product
        if not has_purchased_product(request.user, product):  # Define this check based on your order logic
            messages.error(request, "You can only review products you have purchased.")
            return redirect('product_detail', product_id=product.id)

        # Create the review (pending approval)
        Review.objects.create(
            user=request.user,
            product=product,
            rating=rating,
            review_text=review_text,
        )
        messages.success(request, "Your review has been submitted and is awaiting approval.")
        return redirect('product_detail', product_id=product.id)

    return render(request, 'submit_review.html', {'product': product})


def calculate_discounted_price(product):
    category_discounts = product.category.discounts.filter(
        start_date__lte=timezone.now(),
        end_date__gte=timezone.now()
    )
    if category_discounts.exists():
        discount = category_discounts.first()
        discounted_price = product.price * (1 - discount.discount_percentage / 100)
        return round(discounted_price, 2)
    return product.price
