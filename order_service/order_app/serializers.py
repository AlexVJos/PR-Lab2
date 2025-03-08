from rest_framework import serializers
from .models import Order, OrderItem
from .services import ProductService

class OrderItemSerializer(serializers.ModelSerializer):
    product_id = serializers.IntegerField()
    product_name = serializers.CharField()
    price = serializers.DecimalField(max_digits=10, decimal_places=2)
    quantity = serializers.IntegerField()
    class Meta:
        model = OrderItem
        fields = ['id', 'product_id', 'product_name', 'price', 'quantity']

class OrderSerializer(serializers.ModelSerializer):
    items = OrderItemSerializer(many=True, read_only=True)
    
    class Meta:
        model = Order
        fields = ['id', 'customer_name', 'customer_email', 'status', 'items', 'created_at', 'updated_at']

class OrderItemInputSerializer(serializers.Serializer):
    product_id = serializers.IntegerField()
    quantity = serializers.IntegerField()

    def validate(self, data):
        product_id = data['product_id']
        product = ProductService.get_product(product_id)
        if not product:
            raise serializers.ValidationError(f"Продукт с id {product_id} не найден")
        data['product_name'] = product['name']
        data['price'] = product['price']
        return data

class OrderCreateSerializer(serializers.ModelSerializer):
    items = OrderItemInputSerializer(many=True, write_only=True)

    class Meta:
        model = Order
        fields = ['customer_name', 'customer_email', 'items']

    def create(self, validated_data):
        items_data = validated_data.pop('items')
        order = Order.objects.create(**validated_data)

        for item_data in items_data:
            OrderItem.objects.create(
                order=order,
                product_id=item_data['product_id'],
                product_name=item_data['product_name'],
                price=item_data['price'],
                quantity=item_data['quantity']
            )
        return order