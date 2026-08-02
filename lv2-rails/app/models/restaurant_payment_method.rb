class RestaurantPaymentMethod < ApplicationRecord
  belongs_to :restaurant
  belongs_to :payment_method

  validates :payment_method_id, uniqueness: { scope: :restaurant_id }
end
