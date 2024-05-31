import pandas as pd
import numpy as np
from django.core.management.base import BaseCommand
from django.contrib.auth.models import User
from store.models import Product, UserInteraction, UserProfile
from scipy.sparse import coo_matrix
from implicit.als import AlternatingLeastSquares

class Command(BaseCommand):
    help = 'Generate product recommendations for users'

    def handle(self, *args, **kwargs):
        # Prepare the interaction data
        interactions = UserInteraction.objects.all()
        data = [(interaction.user.id, interaction.product.id, 1) for interaction in interactions]  # Assuming interaction weight is 1
        df = pd.DataFrame(data, columns=['user_id', 'product_id', 'weight'])

        user_ids = df['user_id'].unique()
        product_ids = df['product_id'].unique()

        user_map = {id: index for index, id in enumerate(user_ids)}
        product_map = {id: index for index, id in enumerate(product_ids)}

        rows = df['user_id'].map(user_map).values
        cols = df['product_id'].map(product_map).values
        data = df['weight'].values

        interaction_matrix = coo_matrix((data, (rows, cols)), shape=(len(user_ids), len(product_ids)))

        # Train the model
        model = AlternatingLeastSquares(factors=50, regularization=0.01, iterations=20)
        model.fit(interaction_matrix.T)

        # Generate recommendations
        recommendations = {}
        for user_id, user_index in user_map.items():
            recommended_product_indices = model.recommend(user_index, interaction_matrix, N=10)
            recommended_products = [product_ids[i] for i, _ in recommended_product_indices]
            recommendations[user_id] = recommended_products

        # Save recommendations
        for user_id, recommended_products in recommendations.items():
            user = User.objects.get(id=user_id)
            user_profile, created = UserProfile.objects.get_or_create(user=user)
            user_profile.recommended_products.set(recommended_products)

        self.stdout.write(self.style.SUCCESS('Successfully generated recommendations'))
