class PaymentMethod < ApplicationRecord
  has_many :restaurant_payment_methods, dependent: :destroy
  has_many :restaurants, through: :restaurant_payment_methods

  validates :name, presence: true, uniqueness: true
end
