from rest_framework import viewsets, status
from rest_framework.response import Response
from django.shortcuts import get_object_or_404
from .models import Order, OrderItem
from .serializers import OrderSerializer, OrderCreateSerializer
from .services import ProductService

# Create your views here.
class OrderViewSet(viewsets.ModelViewSet):
    queryset = Order.objects.all().order_by('-created_at')
    
    def get_serializer_class(self):
        if self.action == 'create':
            return OrderCreateSerializer
        return OrderSerializer
    
    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        
        # Проверяем доступность всех продуктов
        items = request.data.get('items', [])
        for item in items:
            product_id = item.get('product_id')
            quantity = item.get('quantity', 1)

            product = ProductService.get_product(product_id)
            if not product:
                return Response(
                    {"error": f"Product with id {product_id} not found"},
                    status=status.HTTP_400_BAD_REQUEST
                )

            if not ProductService.check_product_availability(product_id, quantity):
                return Response(
                    {"error": f"Not enough stock for product {product_id}"},
                    status=status.HTTP_400_BAD_REQUEST
                )
            
            item['product_name'] = product['name']
            item['price'] = product['price']

        order = serializer.save()

        for item in items:
            product_id = item.get('product_id')
            quantity = item.get('quantity', 1)
            ProductService.update_product_stock(product_id, quantity)

        return Response(
            OrderSerializer(order).data,
            status=status.HTTP_201_CREATED
        )
    
    def update(self, request, *args, **kwargs):
        partial = kwargs.pop('partial', False)
        instance = self.get_object()
        serializer = self.get_serializer(instance, data=request.data, partial=partial)
        serializer.is_valid(raise_exception=True)
        self.perform_update(serializer)
        return Response(serializer.data)
    
    def destroy(self, request, *args, **kwargs):
        instance = self.get_object()
        self.perform_destroy(instance)
        return Response(status=status.HTTP_204_NO_CONTENT)