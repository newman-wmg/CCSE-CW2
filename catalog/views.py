# This file contains views for displaying products and categories in the catalog.

from django.shortcuts import render, get_object_or_404
from django.views.generic import ListView, DetailView
from django.db.models import Q
from .models import Product, MainCategory, SubCategory

class ProductListView(ListView):
    model = Product
    template_name = 'catalog/product_list.html'
    context_object_name = 'products'
    paginate_by = 12

    def get_queryset(self):
        queryset = Product.objects.all()
        
        # Category filtering
        category_slug = self.kwargs.get('category_slug')
        subcategory_slug = self.kwargs.get('subcategory_slug')
        
        if subcategory_slug:
            queryset = queryset.filter(subcategory__slug=subcategory_slug)
        elif category_slug:
            queryset = queryset.filter(subcategory__main_category__slug=category_slug)
        
        # Price filtering
        min_price = self.request.GET.get('min_price')
        max_price = self.request.GET.get('max_price')
        
        if min_price:
            queryset = queryset.filter(price__gte=min_price)
        if max_price:
            queryset = queryset.filter(price__lte=max_price)
            
        # Search functionality
        search_query = self.request.GET.get('q')
        if search_query:
            queryset = queryset.filter(
                Q(name__icontains=search_query) |
                Q(description__icontains=search_query)
            )
            
        # Sorting
        sort = self.request.GET.get('sort')
        if sort == 'price_asc':
            queryset = queryset.order_by('price')
        elif sort == 'price_desc':
            queryset = queryset.order_by('-price')
            
        return queryset

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['categories'] = MainCategory.objects.all()
        
        # Add category and subcategory information
        category_slug = self.kwargs.get('category_slug')
        subcategory_slug = self.kwargs.get('subcategory_slug')
        
        context['current_category'] = category_slug
        context['current_subcategory'] = subcategory_slug
        
        # Retrieve and store names of the current category and subcategory if they exist
        if subcategory_slug and category_slug:
            subcategory = get_object_or_404(SubCategory, 
                                          slug=subcategory_slug, 
                                          main_category__slug=category_slug)
            context['current_subcategory_name'] = subcategory.name
        elif category_slug:
            category = get_object_or_404(MainCategory, slug=category_slug)
            context['current_category_name'] = category.name
            
        return context

class ProductDetailView(DetailView):
    model = Product
    template_name = 'catalog/product_detail.html'
    context_object_name = 'product'
    slug_url_kwarg = 'product_slug'

def category_list(request):
    # Render the list of main categories
    categories = MainCategory.objects.all()
    return render(request, 'catalog/category_list.html', {'categories': categories})