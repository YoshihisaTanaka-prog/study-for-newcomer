class Review < ApplicationRecord
  belongs_to :restaurant

  validates :body, presence: true
  validates :rating, inclusion: { in: 1..5 }, allow_blank: true
end
